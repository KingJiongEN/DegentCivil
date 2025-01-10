import asyncio
from bdb import set_trace
from collections import deque
import copy
from functools import partial
import json
import os
from typing import Dict
from pprint import pprint
from collections.abc import Iterable
from app.utils.globals import RESOURCE_SPLITER

from config import config
from ..character_state import FuncName2Registered, PromptName2Registered, StateName2Registered
from ...communication.websocket_server import WebSocketServer
from ...constants import StateName2State, PromptType, State2PushMsgId, State2RecieveMsgId, InterruptableStates
from ...llm.caller import LLMCaller
from ...llm.prompt.base_prompt import BasePrompt
from ...models.location import BuildingList
from ...models.character import Character, CharacterList, CharacterState
from ...utils.function_chain import FunctionChain
from ...utils.gameserver_utils import add_msg_to_send_to_game_server
#from ipdb import set_trace

class BaseState:
    '''
    describe the state of a character, centred on a llm_call, 
    we define a state by ONE prompt & llm_call
    
    character: Character
    on_change_state: callable
    llm_caller: LLMCaller
    state_duration_tolerance: int
    finish_state: bool
    circle_tolerance: int, if the len of a circle in the state machine > circle tolerance, it will be deemed as a circle
    loop_tolerance: int, if the node in a circle is visited more than loop_tolearnce, the cirlce will be forced to be quit (directed to another state) 
    '''

    def __init__(self, character: Character, main_prompt, character_list: CharacterList, building_list: BuildingList,
                 followed_states, 
                 on_change_state, 
                 circle_tolerance:int=4,
                 loop_tolerance:int=5,
                 state_duration_tolerance:int = 10,
                 state_name:str=None, 
                 enter_calls=None, 
                 exit_calls=None, 
                 update_calls=None, 
                 llm_calls=None,
                 post_calls=None,
                 description=None,
                #  default_client = 'gpt-4-0125-preview-chatgpt-3.vip', #  select client by its name, if None, use default ConversableAgent.client
                 default_client = 'deepseek-chat-official', #  select client by its name, if None, use default ConversableAgent.client
                 arbitrary_obj=None,
                 arbitrary_wm= None, 
                 previous_state=None,
                 ):

        self.state_name = state_name if state_name is not None else self.__name__
        self.character: Character = character
        self.description = description
        self.on_change_state: callable = on_change_state
        self.llm_caller = LLMCaller(config.llm_model) # deprecated , but keep it for now, since it is more flexible
        self.default_client = default_client
        self._state_duration:int = 0
        self.state_duration_tolerance:int = state_duration_tolerance
        self._circle_tolerance:int = circle_tolerance
        self.loop_duration = 0 
        self._loop_tolerance:int = loop_tolerance
        self.previous_state = previous_state        
        
        self.arbitrary_obj = arbitrary_obj
        self.arbitrary_wm:dict = arbitrary_wm if arbitrary_wm is not None else dict()
        if arbitrary_obj:
            self.arbitrary_wm['act_obj'] = arbitrary_obj
            assert os.getenv('DEBUG'), 'arbitrary_obj is only for debug purpose'

        self.character_list: CharacterList = character_list
        self.building_list:BuildingList = building_list
        assert isinstance(followed_states,Iterable) and len(followed_states), f'followed_states: {followed_states} should be iterable and  not be none' 
        # TODO: define a class for followed states, [CharacterState, condition]]
        self.followed_states: Dict[CharacterState, bool] = dict( [( StateName2State[state] if type(state) is str else state, False) for state in followed_states]) # ordered states that change_state can call 
        self.followed_states[self.state_name] = False
        self.followed_states[CharacterState.RECEIVECHAT] = False

        self.prompt_type = main_prompt  # name of the main prompt
        self.prompt_class = PromptName2Registered.get(self.prompt_type, BasePrompt)(prompt_type=self.prompt_type, state=self) if main_prompt else None

        self.enter_state_chain = FunctionChain([self.change_char_building,
                                                self.push_state_change_to_server,
                                                self.build_prompt,
                                                self.save_llm_prompt, 
                                                self.call_main_prompt])
        self.exit_state_chain = FunctionChain([self.log_char_attr, self.push_attr_change_to_server])
        self.update_state_chain = FunctionChain([ self.change_date, self.monitor_server_msg, self.passive_update,self.state_timeout, self.change_state])
        self.post_llm_call_chain = FunctionChain( [ self.save_llm_response, self.tailor_response_to_wm, self.store_memory, self.state_router])
        self.post_exit_chain = FunctionChain().add(self.loop_duration_decay) 
        
        # register func calls 
        for funchain, call_ls in ((self.enter_state_chain, enter_calls), 
                                (self.exit_state_chain, exit_calls), 
                                (self.update_state_chain, update_calls), 
                                (self.post_llm_call_chain, llm_calls),
                                (self.post_exit_chain, post_calls)
                                ):

            if call_ls:
                for call in call_ls:
                    index = None
                    assert type(call) in [tuple, list, str], 'pass a tuple or list with [call_name, index] or a single call_name'
                    if type(call) is tuple or type(call) is list:
                        assert len(call) == 2 and type(call[0]) is str and type(call[1]) is int, 'pass a tuple or list with [call_name, index] or a single call_name'
                        index = call[1]
                        call = call[0]
                    
                    if type(call) is str and call in FuncName2Registered:
                        call = FuncName2Registered[call]
                    assert callable(call), f'{call} is not callable. Please pass a callable object to call list.' 
                                       
                    funchain.add(call, index)
                    
    @property
    def next_state(self):
        # if sum(list(self.followed_states.values())) > 1:
#            __import__('ipdb').set_trace()
        assert sum(list(self.followed_states.values())) <= 1, f' followed states should have at most one initiated state, but now the sum is {sum(list(self.followed_states.values())) },  {self.followed_states}'

        for state, bl in self.followed_states.items(): 
            if bl:
                return state 
    
    def set_previous_state(self, state):
        self.previous_state = state

    def execute_func_chain(self, func_chain:FunctionChain, *args, **kwargs):
        '''
        execute func chain and post process
        '''
        success, msg = func_chain.execute( *args ,**kwargs)
        if not success:
            if self.prompt_type:
                self.prompt_class.add_warning_msg(msg)
                self.turn_on_states(self.state_name)
            else:
                set_trace()
        return msg
    
    def state_timeout(self, overduration: bool):
        if overduration and self.state_name != CharacterState.PERSP:
            if self.prompt_type and self.llm_task.done():
                print('Warning!  Overduaration and LLM task done but no states on. Perspect again.')
                self.on_change_state(CharacterState.PERSP)
            return True, dict()
        else:
            return False, dict()

     
    def change_state(self, overduration):
        '''
        monitor the self.followed_states and change the state if any of the states is true
        '''
        
        for state, ready in self.followed_states.items():
            if ready:
                # handle hang states like receivechat
                if state in InterruptableStates and self.character.hang_states:
                    state = self.character.hang_states.pop()
                    assert state in self.followed_states, f'{state} is not a legal followed states, followed states: {self.followed_states}'
                self.on_change_state(state)
                break
       
        return False, dict()

    def enter_state(self, *args, **kwargs):
        self.character.set_state(self) 
        print(f'enter state: {self.state_name}')
        self._state_duration = 0

        self.loop_duration += self._circle_tolerance
        
        for state in self.followed_states: # reset next states
            self.followed_states[state] = False

        # self.execute_func_chain( func_chain=self.enter_state_chain ,  obj=self ,**kwargs)

        success, msg = self.enter_state_chain.execute(obj=self, *args, **kwargs)
        if not success:
            if self.prompt_type:
                self.prompt_class.add_warning_msg(msg)
                self.turn_on_states(self.state_name)
            else:
                set_trace()

    def exit_state(self, **kwargs):
        return self.exit_state_chain.execute( obj=self, **kwargs)

    def post_exit(self, *args, **kwargs):
        '''
        operations happens after the state is exited.
        '''
        self.post_exit_chain.execute(*args, obj=self, **kwargs)

    def update_state(self, msg, date, *args, **kwargs):
        self._state_duration += 1
        
        overduration = self._state_duration > self.state_duration_tolerance        
        
        overlooped = self.loop_duration > self._loop_tolerance
        
        return_dict = self.update_state_chain.execute(*args, msg=msg, date=date, overduration=overduration, overlooped=overlooped, obj=self, **kwargs)
        
        return return_dict

    def check_attr_chage(self):
        if any([  getattr(self.character, attr)==self.character.prev_modifiable_attr.get(attr) for attr in self.character.digital_internal_properties ]):
            self.character.prev_modifiable_attr = self.character.modifiable_status_dict

            msg = {
                'content' : f'{self.character.name} changed attr',
                'agent_guid' : self.character.guid,
                'duration' : 1,
                'attr_change':  self.character.digital_internal_attr2value,
            }
            msg = f"1002@{json.dumps(msg)}"

            add_msg_to_send_to_game_server(msg)

        return False, dict()
    

    def wrap_up_msg(self, msg:dict):
        if self.state_name in State2PushMsgId:
            msg_id = str(State2PushMsgId[self.state_name])
            return msg_id + '@' + json.dumps(msg)
     

    def change_date(self, date):
        self.character.change_date(date)
        return False, dict()
    
    def push_msg_to_game_server(self, msg):
        msg = self.wrap_up_msg(msg)
        # print(f'push msg to game server: {msg}')
        add_msg_to_send_to_game_server(msg)
        return False, dict()

    def handle_server_attr_change_msg(self, msg):
        msg = json.loads(msg)
        if int(msg['attr_id']) == 102:
            setattr(self.character, 'Gold', int(msg['attr_value']))
   
    def monitor_server_msg(self, msg=None):
        if not msg: return False, dict()
        if int(msg['msg_id']) == 2003: 
            self.handle_server_attr_change_msg(msg['msg'])
            return False, {}

        if int(msg['msg_id']) == int(State2RecieveMsgId.get(self.state_name, 0)):
            msg = msg['msg']
            return self.handle_server_msg(msg)
        return False, dict()
    
    def handle_server_msg(self, msg):
        return False, dict()
    
    def change_char_building(self):
        building = self.building_list.get_building_by_pos(self.character.x, self.character.y)
        self.character.change_building(building)
        
        return False, dict()
    
    def loop_duration_decay(self,):
        self.loop_duration -= 1
        return False, dict(loop_duration=self.loop_duration)


    def call_main_prompt(self, prompt):
        if self.prompt_type:
            self.call_llm(prompt, self.prompt_type)
            self.llm_task.add_done_callback(lambda task: self.execute_post_llm_chain(result=task.result(), prompt_type=self.prompt_type))
            
        return False, dict()
        
    def build_prompt(self):
        prompt = None
        if self.prompt_type:
            prompt = self.prompt_class.create_prompt() 
        return  False, {"prompt": prompt}
            
        
    def execute_post_llm_chain(self, result, prompt_type):
        self.post_llm_call_chain.store_dict_result(result)
        success, msg = self.post_llm_call_chain.execute(result=result,
                                         obj=self, 
                                         prompt_type=prompt_type)
        if not success:
            if self.prompt_type:
                self.prompt_class.add_warning_msg(msg)
                self.turn_on_states(self.state_name)
            else:
                set_trace()

        
    def turn_on_states(self, next_state_names=None):
        # always happen when llm call finishes, handle next state based on the llm response
        # set transferable states 
        if sum(list(self.followed_states.values())): return False, dict()
        if next_state_names is not None and not isinstance(next_state_names, Iterable):
            next_state_names = [next_state_names]
        if next_state_names is None: 
            next_state_names = list(self.followed_states.keys())[0:1]
        
        for name in next_state_names:
            assert name in self.followed_states, f'{name} is not a legal followed states, followed states: {self.followed_states}'
            self.followed_states[name] = True
            # print(f'{self.character.name} turn on state: {self.next_state}')
        return True, dict()    
    
    def state_router(self, **kwargs):
        '''
        default transfer to the first state in followed_state
        '''
        return self.turn_on_states()
     
    def call_llm(self, prompt, prompt_type: PromptType):
        """
        Create an LLM task with a given prompt and assign a callback.
        """
        self.llm_task = asyncio.create_task(self.character.a_process_then_reply(message=prompt, sender=self.character, restart=True, check_exempt_layers=self.prompt_class.check_exempt_layers))

    def get_character_wm_by_name(self, mem_name, default=None):
        if mem_name in self.arbitrary_wm:
            print(f"!!!WARNING!!! In {self.state_name}, {mem_name} is set as {self.arbitrary_wm.get(mem_name)}. It is only for testing purpose.") 
            assert os.getenv('DEBUG')
            self.character.working_memory.store_memory(mem_name, self.arbitrary_wm.get(mem_name))
            return self.arbitrary_wm.get(mem_name)
        
        return self.character.working_memory.retrieve_by_name(mem_name, default=default)

    def get_agent_by_name(self, obj_name):
        '''
        find name from character first, then building, if is equipment return equipment
        '''
        obj_agent = self.character_list.get_character_by_name(obj_name) 
        if obj_agent is None: 
            if RESOURCE_SPLITER in obj_name: # equipment
                building_name = obj_name.split(RESOURCE_SPLITER)[0]
                building = self.building_list.get_building_by_name(building_name) 
                obj_agent = building.equipments[obj_name] 
            else:
                obj_agent = self.building_list.get_building_by_name(obj_name) 

        return obj_agent
        
   
    def save_llm_response(self, result,):
        if self.prompt_type:
            self.character.save_response(result, self.prompt_type)
            WebSocketServer.broadcast_message("character_update_llm", self.character.encode_latest_llm())
        return False, dict()
    
    def tailor_response_to_wm(self, result): 
        if self.prompt_class.recordable_key:
            key = self.prompt_class.recordable_key
            if type(key) is str: key = [key]
            for ky in key:
                self.character.working_memory.store_memory( ky, copy.deepcopy(result[ky]))
            
        return  False, dict()
    
    def save_llm_prompt(self, prompt):
        self.character.save_prompt(prompt, self.prompt_type, getattr(self.prompt_class, 'EXAMPLE', None))
        return False, dict()
        
    def store_reflection(self, result):
        '''
        store textualized reflection, which is modified by agents
        '''
        self.character.longterm_memory.store(result)
        return False, dict()
    
    def log_char_attr(self):
        self.character.log_attrs()
        return False, dict()

    def store_memory(self, result):
        asyncio.create_task(self.insert_memory_item(result))
        return False, dict()

    async def insert_memory_item(self, result, text=None, scale_dict=None):
        if text is not None and scale_dict is not None and os.getenv('Milvus'):
            await self.character.longterm_memory.insert_milvus_memory(text=text, scale_dict=scale_dict)

    def retrieve_memory(self, obj_name, text):
        memos = []
        if os.getenv('Milvus'):
            memos = self.character.longterm_memory.name_specific_memory_retrieve_from_milvus(obj_name=obj_name, query=text)
        return memos
   
    def passive_update(self):
        self.update_character_emotion()
        self.update_art_preference
        return False, dict()
    
    def update_character_emotion(self):
        # TODO: 3.9 just the first version api; other state can override this method for more reasonable emtion update.
        self.character.emotion.passive_update()
        return False, dict()
    
    def update_art_preference(self):
        self.character.art_preference.passive_update()
    
    def build_scale_dict(self, obj_agent, memory):
        scale_dict = {
            "act_name": self.character.name,
            "act_id": self.character.guid,
            "obj_name": obj_agent.name,
            "obj_id": obj_agent.guid,
            "in_building_name": self.character.in_building_name,
            "in_building_id": self.character.in_building_id,
            "money": self.character.money,
            "emotion": self.character.emotion.extreme_emotion_name,
            "emotion_level": self.character.emotion.extreme_emotion_value,
            "timestamp": self.character.date_num,
            "memory": memory
        }
        for k in scale_dict:
            if k == 'timestamp': continue
            scale_dict[k] = str(scale_dict[k])
            
        return scale_dict
    
    def __repr__(self) -> str:
        return self.state_name.name

    def push_state_change_to_server(self, **kwargs):
        from time import sleep
        state_name = f'{self.state_name}'.split('.')[-1]
        msg = {
            'content': f'{self.character.name} entered state {state_name}',
            'agent_guid': self.character.guid,
            'content_type': 2,
            'display_duration': 3,
        }
        msg = f"1002@{json.dumps(msg)}"

        add_msg_to_send_to_game_server(msg)
        sleep(3)
        return False, dict()
    
    def push_attr_change_to_server(self, **kwargs):
        from time import sleep
        state_name = str(self.state_name).split(".")[-1]
        msg = {
            'content': f'{state_name} ends',
            'agent_guid': self.character.guid,
            'content_type': 2,
            'display_duration': 2
        }
        msg = f"1002@{json.dumps(msg)}"
        sleep(2)
        return False, dict()