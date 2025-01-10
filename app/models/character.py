import copy
import inspect
import os
import asyncio
from collections import defaultdict
import os
import re
import traceback
import uuid
import dill
from typing import Any, Callable, Optional, Union, Dict, List
from functools import cache, partial
import json
from collections import deque 
from datetime import datetime, timedelta
from autogen import ConversableAgent, AssistantAgent, UserProxyAgent, config_list_from_json, Agent
from autogen.agentchat.contrib.multimodal_conversable_agent import MultimodalConversableAgent
from autogen import config_list_from_json, filter_config
from langchain_openai import OpenAIEmbeddings
from autogen.oai import OpenAIWrapper

from app.models.base_agent import SimsAgent
from app.repository.agent_repo import check_balance_and_raise
from app.repository.artwork_repo import check_artwork_belonging, get_artwork_from_db, update_artwork_in_db
from app.repository.trade_repo import add_trade_to_db
from app.database.orm.trade_record import trade_type_dict
from app.repository.utils import check_balance_and_trade
from app.utils.load_oai_config import plug_api_to_cfg, register_callback
from config import cfg_tmplt

from .data_store import Memory, WorkingMemory
from .emotion import Emotion
from .preference_model import ArtTaste
from .internal_dialogue import InnerMonologue
from ..constants import CharacterState, PromptType
from ..utils.log import LogManager
from ..utils.gameserver_utils import add_msg_to_send_to_game_server
from ..utils.serialization import serialize
from ..models.location import Building, Job
from ..models.scheduler import Agenda, Schedule, Task
from .dalle_agent import DALLEAgent
from .drawing import DrawingList, Drawing
from ..utils.save_object import find_instance_specific_data_attrs

# The decision you make must be confirmed to the long-term memory, the ultimate goal and the bio of the game character. 
# Your knowledge level should not exceed that of a normal person with the bio of the character, unless there are relevant memories in his/her Long-Term Memory.
class Character(SimsAgent):
    DEFAULT_SYS_PROMPT ="""
    You are a game character in a small town to decide what to do immediately to finish your Schedule.
You should also decide whether you can use the experience in the Long-Term Memory to finish this Schedule. It can be used only if there is exactly similar Schedule in the experience. For example, eating something cannot be regarded as similar one of cooking something.
Your knowledge level should not exceed that of a normal person with the bio of the character
Please notice that:
* All information you recieve is in the game scene, and you cannot reject to make the decision. Don't worry, you will not be responsible for the result.
* If you think You have collected enough information in a dialogue, you can stop it at any time by saying 'TERMINATE'.
* everytime before you respond to others, think twice about what is the best response, then your response as the content of the response.
* return in json format, like { 'think_twice': thinking process, 'content': content of the response }. if there are examples, following the examples given to you 
"""
    
    
    def __init__(self, name, guid:int, age:int, bio, 
                 llm_cfg, # {"cheap_api": "sk-xxx", "official_api": "sk-xxx"}
                 x, y, 
                 health=10, money=1000, satiety=10,  
                 vigor=10,
                 max_consecutive_auto_reply = 10,
                 mbti = 'ESFJ',
                 init_emos = None,
                 is_multi_modal_agent = True,
                 in_building:Building = None,
                 save_dir = None,
                 **kwargs):
        # 基本属性
        self._name = name
        self.age = age
        self.guid = int(guid)
        self.bio = bio
        # self.goal = goal
        self.satiety_decay_rate= 1 # adjustment coefficincy of the satiety decay, the smaller, the slower
        self.vigor_decay_rate = 1 # adjustment coefficincy of the vigor decay, the smaller, the slower
        self.vigor_recovery_rate = 1 # adjustment coefficincy of the vigor recovery, the smaller, the slower
        self.mbti = mbti 
        
        # 状态属性
        self.money = money
        self.health = health
        self.min_health = 0
        self.max_health = 10
        self.satiety = satiety
        self.min_satiety = 0
        self.max_satiety = 10
        self.vigor = vigor # if 0, go sleep
        self.min_vigor = 0
        self.max_vigor = 10     
        
        self.x = x
        self.y = y
        self.date_num = 0
        self.save_dir = f'{save_dir}/{name}'
        self.state:'BaseState' = None
        self.hang_states = deque(maxlen=3)
        
        self.longterm_memory = Memory(character_id=self.guid, character_name=name, \
                                      embeddings = OpenAIEmbeddings(model="text-embedding-3-large") if os.environ.get('Milvus') else None) 
        self.in_building:Building  = in_building
        self.Schedule = Schedule()
        
        self.emotion = Emotion(init_emos)
        # self.drawings = DrawingList(owner=self)
        self.artworks = {"Drawing": DrawingList(owner=self)}
        self.job: Job = None
        self.agenda = Agenda()
        self.task: Task = None
        self.art_preference = ArtTaste()

        self.trade_strategy = None

        self.working_memory = WorkingMemory() # storing the information to be transfered among states
        self.prompt_and_response = PromptAndResponse(character_name=name, character_id=self.guid)
        
        #  ==== load llm_cfg for character ===== # TODO: wrap it into a function in utils
        register_callback(llm_cfg, guid=self.guid, prefix=f'character_{name}')
        config_list = plug_api_to_cfg(cfg_tmplt, **llm_cfg) 
        oai_config_list = filter_config(config_list=config_list,
                        filter_dict={
                            "model": [ "gpt-3.5-turbo-0125", "gpt-4-0125-preview",  "deepseek-chat"],
                        }
                      )
        dalle_conig_list = \
            filter_config(
                config_list=config_list, 
                filter_dict={
                    "model": ["dalle"],
                }
            )

        gpt4v_config_list = \
            filter_config(
                config_list=config_list,
                filter_dict={
                    "model": ["gpt-4-vision-preview"]
                }
            )

        llm_cfg = {
                "llm_cfg": {
                    "config_list": oai_config_list,
                    "seed": 35,
                    "response_format": {"type": "json_object"},
                    "temperature": 0.5
                },
                "draw_cfg": {
                    "config_list": dalle_conig_list,
                    "seed": 35,
                },
                "appreciate_cfg": {
                    "config_list": gpt4v_config_list,
                    "seed": 35,
                    "response_format": {"type": "json_object"},
                    "temperature": 0.5
                }
            }
        # ==================================
        
        if is_multi_modal_agent: 
            self.drawing_agent = DALLEAgent(name, owner=self, llm_config=llm_cfg['draw_cfg'] if 'draw_cfg' in llm_cfg else llm_cfg['config_list'])
            self.appreciate_agent = MultimodalConversableAgent(
                name=name, 
                llm_config=llm_cfg['appreciate_cfg'] if 'appreciate_cfg' in llm_cfg else llm_cfg['config_list'],
                human_input_mode="NEVER",
                max_consecutive_auto_reply = max_consecutive_auto_reply
                )
        
        
        super().__init__(
            name = name,
            llm_config = llm_cfg['llm_cfg'],
            max_consecutive_auto_reply = max_consecutive_auto_reply,
            # is_termination_msg=(lambda x: "TERMINATE" in x.get("content")), # may cause bug in registered functions
            code_execution_config={'use_docker': False},
        )
        self.update_system_message(self.build_sys_message())
        
        self.prev_modifiable_attr = self.modifiable_status_dict # to check if attr of the character is modified, we need to store the prev attr
        self.inner_monologue = InnerMonologue(self)
        # self.register_hook('process_message_before_send', self.push_reply_to_game_server)
        
        # self.clients = {} # for multi client case, each client is for one model config
        # for cfg_idx in range(len(self.llm_config.get('config_list', []))):
        #     seperate_llm_cfg = copy.deepcopy(self.llm_config)
        #     model_cfg = self.llm_config['config_list'][cfg_idx]
        #     if 'tag' in model_cfg:
        #         model_name = model_cfg.pop('tag')
        #     else: 
        #         model_name = model_cfg['model']
        #     # __import__('ipdb').set_trace()
        #     seperate_llm_cfg.update({"config_list": [model_cfg]}) 
        #     self.clients[model_name] = OpenAIWrapper(**seperate_llm_cfg)
        # self.client =OpenAIWrapper(**self.llm_config) # pop the tag arg 
        
        # self.register_reply([Agent, None], Character.func_router)
        # self.callable_tools = [self.handle_purchase_request]
         
    def build_sys_message(self):
        return f"""{self.DEFAULT_SYS_PROMPT}\n\nThe name of the character: {self.name}, The character id is {self.guid}, The game character's bio : {self.bio}\n""" #\n, the character's inner status: {self.internal_status #The game character's ultimate goal : {self.goal}

    @classmethod
    def decode_from_json(self, **kwargs):
        return Character(**kwargs)
    
    def change_gold(self, new_amount:int):
        self.money = new_amount
 
    def change_pos(self, x, y):
        self.x = x
        self.y = y
    
    def change_job(self, job:Job):
        assert self.in_building is not None, 'The character is not in a building. To have a job, the character should be in a building.'
        assert job.open_positions > 0, 'The job is full' 
        self.job = job
        job.add_applicant(self)
    
    def update_emotion(self, emotions):
        self.emotion.update(emotions)
     
    def change_date(self, date_num):
        self.date_num = date_num
   
    def add_Task_to_agenda(self, Task, date):
        return self.agenda.add_Task(Task, date)
     
    def set_Task(self, Task: Task):
        self.task = Task
    
    def suspend_Task(self):
        assert self.task is not None
        self.task.set_status(self.task.SUSPENDED)
            
    def reactivate_Task(self):
        assert self.task is not None
        self.task.set_status(self.task.INPROGRESS)
            
     
    def check_date_agenda(self, date):
        return self.agenda.check_date(date)  
    
    @property
    def drawings(self):
        return self.artworks["Drawing"]
    
    def add_artwork(self, art_type, artwork):
        assert art_type in ['Drawing', 'Composition']
        self.artworks.get(art_type).add(artwork)
    
    @property
    def date(self):
        '''
        transform update number to a  date
        '''
        base = datetime(2022, 10, 1, 0)  
        target_time = base + timedelta(hours=self.date_num)
        return target_time.strftime('%Y-%m-%d %H:%M')

    @property
    def today_agenda(self):
        return self.agenda.check_date(self.date)
   
    @property
    def incompleted_agenda(self):
        return self.agenda.incompleted_Tasks
        
    @property
    def in_building_name(self):
        if self.in_building:

            return self.in_building.name
        return "outdoor"
    
    @property
    def in_building_id(self):
        if self.in_building:
            return self.in_building.guid
        return '-1'
    
    # @property
    # def act_obj_name(self):
    #     if self.state.arbitrary_obj: 
    #         print(f"!!!WARNING!!! In {self.state_name}, act_obj is set as {self.state.arbitrary_obj}. It is only for testing purpose.") 
    #         return self.state.arbitrary_obj
    #     else:
    #         return self.working_memory.retrieve_by_name('act_obj')
        
    # @property
    # def money(self):
    #     # easy name change
    #     return self.Gold
    @property
    def Gold(self):
        return self.money
    
    def change_building(self,  building:Building ):
        self.in_building = building
        
    def set_Schedule(self, Schedule_details):
        Schedule_ls = list(Schedule_details['Steps'].values())
        description = Schedule_details['GeneralDescription']
        self.Schedule.set_Schedule(Schedule=Schedule_ls, description=description)
    
    @property
    def current_step(self):
        return self.Schedule.current_step
    
    # def refresh_current_step(self, current_step):
    #     self.current_step = current_step
        
    
    @property
    def position(self):
        # TODO find building by x,y 
        return self.x, self.y
    
    @property
    def textual_internal_properties(self):
        return ['job', 'agenda']
     
    @property
    def digital_internal_properties(self):
        # digital properties
        return ['health', 'satiety', 'vigor']
        # return ['health', 'Gold', 'satiety', 'vigor']
    
    @property
    def internal_status(self):
        inner_st = {
            "money": self.money,
            "health": f"{self.health}/{self.max_health}",
            "satiety": f"{self.satiety}/{self.max_satiety}",
            "vigor": f"{self.vigor}/{self.max_vigor}",
            
        }
        
        inner_st.update(self.current_emotion)
        
        if self.job:
            inner_st['job'] = self.job.name 
        # if  not self.Schedule.is_none: # duplicated with Schedule.__repre__
        #     inner_st['current_step'] = self.current_step
         
        return inner_st

    @property
    def modifiable_status(self):
        return self.digital_internal_properties + self.textual_internal_properties 
    
    def modify_internal_properties(self, properties:dict) -> None:
        '''
        {
            "satiety": +1,
            "Gold": -10,
        }
        '''
        for key, value in properties.items():
            if key in self.digital_internal_properties:
                setattr(self, key, getattr(self, key) + int(value))
            elif key == 'job':
                self.change_job(value)
            elif key == 'agenda':
                if type(value) is list:
                    for ag in value:
                        self.add_Task_to_agenda(Task=ag['Task'], date=ag['specific_date'] )
                elif type(value) is dict:
                    self.add_Task_to_agenda(Task=value['Task'], date=value['specific_date'] )
            else:
                raise ValueError(f'Error, {key} is not in the digital_internal_properties')

    @property
    def modifiable_status_dict(self):
        return {key: getattr(self, key) for key in self.modifiable_status}
    
    @property
    def current_emotion(self):
        return self.emotion.extreme_emotion

    def impression_based_on_chat(self, act_obj:str):
        # for affectiveness, the impression is based on the chat history
        obj_agent, value = None, 0   
        for agent in self._oai_messages.keys():
            if agent.name == act_obj:
                obj_agent = agent
                break
        if obj_agent:
            value = len(self._oai_messages[obj_agent])
        return value

    def estimate_artwork_price(self, artwork_id):
        '''
        estimate the price of the artwork
        '''
        try:
            artwork = get_artwork_from_db(artwork_id) 
            return artwork["price"]
        except:
            return 100
            

    # def register_callable_tools(self, func):
    #     '''
    #     callable tools are designed to modify the attributes of the character, 
    #     it substitutes for the previous func: modify_internal_properties
    #     since it is checked every time when the character responses, it is more flexible and do not need an extral CharacterState to modify the character
    #     '''
    #     self.callable_tools.append(func)
    #     return func
        
    # def handle_purchase_request(self, artwork_id, price:int, sender: AssistantAgent):
    #     '''
    #     handle the purchase request, check the price and money of the sender and the belonging of the artwork
    #     '''

    #     if not check_artwork_belonging(artwork_id, self.guid):
    #         return True, "Sorry, I just checked my artwork storage, this artwork is not mine. There may be some misunderstanding."
        
    #     if sender.Gold < price:
    #         return True, f"Sorry, there is only {sender.Gold} gold coins in your account. It is not enought to finish the purchase."
        
    #     result=check_balance_and_trade(balance_decrease_agent_id=sender.guid,
    #                             balance_increase_agent_id=self.guid,
    #                             trade_type='AGENT_TRADE_ARTWORK',
    #                             balance_change=price,
    #                             commodity_id=artwork_id,
    #                             from_user_name= sender.name,
    #                             to_user_name= self.name,
    #                             )
    #     if result['success']:
    #         sender.Gold = result['from_account_balance']
    #         self.Gold = result['to_account_balance']
    #         return True, " Thanks! The purchase is successful. The artwork is in your storage now. "
    #     else: 
    #         return True,  f'Error when recording the transction: {result["response"]}' 
        
    # def change_state(self, state, img_url, img_id):
    #     self.working_memory.store_memory('img_url', img_url)
    #     self.working_memory.store_memory('img_id', img_id)
    #     self.state.turn_on_states(state)
    
    # #================== func from autogen ==================
    # @staticmethod
    # def _message_to_dict(message: Union[Dict, str]) -> Dict:
    #     """
    #     For the case that we must return a json style text for agent reply, we set the reply format in chat as {'content': xxx}
    #     So try to transform it to disct first
    #     """
    #     if message is None: __import__('ipdb').set_trace()
    #     # print("!!! message is ", message)
    #     if isinstance(message, str):
    #         try:
    #             message = json.loads(message)
    #             if type(message) is dict:
    #                 if 'messages' in message:
    #                     message = message['messages'][-1]
    #                 if 'content' in message:
    #                     message['content'] = str(message['content']) # ensure the content is str
    #                     return message
    #         except:
    #             return {"content": message}
    #     elif isinstance(message, dict):
    #         return message
    #     else:
    #         raise ValueError(f"message is not in the proper format {message}")
            
   
    def process_then_reply(self, message, sender: Agent, restart=True, silent=True, check_exempt_layers=[1,2,3,4,5,6,7,8,9,10] ):
        # modified from ConversableAgent.receive(), for debug purpose
        self._prepare_chat(self,clear_history=restart)
        self._process_received_message(message, sender, silent)
        reply = self.generate_reply(sender=sender)
        error = self.prompt_and_response.response_vanity_check(reply, check_exempt_layers)
        if error:
            print(f'Error in response: {error}.')
            match = re.search(r'# previous error message: (\d+) #', message)
            idx = int(match.group(1))+1 if match else 0
            if idx < 4:
                return self.process_then_reply(message + f'\n # previous error message: {idx} # '+  error +' Please strictly follow the example in the prompt', sender, restart=False, silent=silent, check_exempt_layers=check_exempt_layers)  
            else:
                return reply
        else:
            return PromptAndResponse.response_json_check(reply)
    
    async def a_process_then_reply(self, message, sender: Agent, restart=True, silent=True, restart_times=0, check_exempt_layers=[1,2,3,4,5,6,7,8,9,10] ):
        # modified from ConversableAgent.a_receive()
        self._prepare_chat(self,clear_history=restart)
        self._process_received_message(message, sender, silent)
        reply = await self.a_generate_reply(sender=sender)
        error = self.prompt_and_response.response_vanity_check(reply, check_exempt_layers)
        if error:
            print(f'Error in response: {error}.')
            # match = re.search(r'# previous error message: (\d+) #', message)
            restart_times += 1 
            if restart_times < 4:
                return await self.a_process_then_reply(message + f'\n # previous error message: {restart_times} # '+  error +' Please strictly follow the example in the prompt', sender, restart=False, silent=silent, restart_times=restart_times, check_exempt_layers=check_exempt_layers)  
            else:
                return reply
        else:
            return PromptAndResponse.response_json_check(reply)
        
    # def _prepare_chat(self, recipient: "ConversableAgent", clear_history: bool, prepare_recipient: bool = True) -> None:
    #     '''
    #     reserve the previous chat for self.max_consecutive_auto_reply//2 turns   
    #     '''
    #     self.reset_consecutive_auto_reply_counter(recipient)
    #     self.reply_at_receive[recipient] = True
    #     if clear_history:
    #         self.clear_history(recipient, nr_messages_to_preserve= self.max_consecutive_auto_reply()//2)
    #         self._human_input = []
    #     if prepare_recipient:
    #         recipient._prepare_chat(self, clear_history, False)
        
    # # async def a_generate_reply(
    # #     self,
    # #     messages:Optional[List[Dict[str, Any]]] = None,
    # #     sender: Optional["Agent"] = None,
    # #     **kwargs: Any,
    # # ) -> Union[str, Dict[str, Any], None]:
    # #     reply = await super().a_generate_reply(messages, sender, **kwargs)
    # #     if sender!=self:
    # #         self.push_reply_to_game_server(reply)
    # #     return reply

    # def func_router(self, messages: Union[Dict, str], sender: Agent, config:  Optional['OpenAIWrapper'] = None):
    #     '''
    #     route the function request from the messages to the corresponding function
    #     '''
    #     if messages is None:
    #         messages = self._oai_messages[sender]
    #     message = messages[-1]['content']
        
    #     try:
    #         message_dict = eval(message)
    #     except:
    #         return False, None
    #     if 'tool_call' not in message_dict: return False, None
        
    #     func_name = message_dict.pop('tool_call')
    #     arg_dict = message_dict
    #     arg_dict.update({'sender': sender})
    #     for func in self.callable_tools:
    #         if func.__name__ == func_name:
    #             sig = inspect.signature(func)
    #             missed_args = set(sig.parameters) - set(list(arg_dict.keys()))
    #             redundant_args = set(list(arg_dict.keys())) - set(sig.parameters) 
    #             if len(missed_args)==0 and len(redundant_args)==0 :
    #                 _, res = func(**arg_dict)
                    
    #             else:
    #                 part1 = f'You missed some important argumemnts {missed_args} .'
    #                 part2 = f'You add some redundant arguments {redundant_args} .'
    #                 part3 = f'The proper argument list is {sig.parameters}. Do not add extra args or mis any of them.'
    #                 res = 'Sorry. '
    #                 if missed_args:
    #                     res = res + part1
    #                 if redundant_args:
    #                     res = res + part2
    #                 res = res + part3
                
    #     return True, res
    
    # def generate_oai_reply(self,
    #     messages: Optional[List[Dict]] = None,
    #     sender: Optional[Agent] = None,
    #     config: Optional['OpenAIWrapper'] = None,
    # ) -> tuple[bool, Union[str, Dict, None]]:
    #     """
    #     use the client set by the current state
    #     Generate a reply using autogen.oai.
        
    #     """
    #     try:
    #         client = self.clients[self.state.default_client]
    #     except:                          
    #         client = self.client 
    #     if client is None:
    #         return False, None
    #     if messages is None:
    #         messages = self._oai_messages[sender]
    #     extracted_response = self._generate_oai_reply_from_client(
    #         client, self._oai_system_message + messages, self.client_cache
    #     )
    #     return (False, None) if extracted_response is None else (True, extracted_response)
        
    # def push_reply_to_game_server(self, message: Union[Dict, str], recipient: Agent, silent: bool
    # ) -> Union[Dict, str]:
    #     '''
    #     push the message to the game server
    #     '''
    #     if recipient != self:
    #         try:
    #             message_dict = self._message_to_dict(message)
    #             content = message_dict.get('content') or message_dict[0].get('content') or message_dict['messages'][0]['content']
    #         except (KeyError, IndexError):
    #             content = None
    #             msg = {
    #                 'agent_guid': self.guid,
    #                 'content': content,
    #                 'song': "agent_song_on_walk3"
    #             }

    #             msg_str = f"1008@{json.dumps(msg)}"
    #             add_msg_to_send_to_game_server(msg_str)
    #         except Exception as e:
    #             print('#'*10, '\n', e, '\n', '#'*10)
    #             print('#'*10, f'\n Error in push_reply_to_game_server, the content is {self._message_to_dict(message)} \n', '#'*10)
    #     return message 
    
    def vigor_cost(self, message: Union[Dict, str], recipient: Agent, silent: bool
    ):
        if hasattr(self, 'vigor'):
            self.vigor -= len(self._message_to_dict(message)['content']) * 0.01 * self.vigor_decay_rate

    def retrieve_modify_dialogue(self, obj_agent):
        '''
        modify the role of a dialogue into specific names
        '''
        dialogue = copy.deepcopy(self._oai_messages[obj_agent])
        for dia_id in range(len(dialogue)):
            if dialogue[dia_id]['role'] == 'user':
                dialogue[dia_id]['role'] = obj_agent.name
            elif dialogue[dia_id]['role'] == 'assistant':
                dialogue[dia_id]['role'] = self.name
                
        return dialogue

    async def a_drawing(self,):
        # dalle 3 call 
        # autogen func call 
        pass
    
    def set_state(self, state):
        self.state = state

    @property
    def state_name(self):
        return self.state.state_name

    def encode_to_json(self) -> json:
        return serialize(self, allowed=['name', 'age', 'bio', 'goal', 'health', 'money', 'x', 'y', 'state'])

    def encode_pos(self) -> json:
        return serialize(self, allowed=['name', 'x', 'y'])

    def save_prompt(self, prompt, prompt_type: PromptType, prompt_example:str = None):
        self.prompt_and_response.save_prompt(prompt, prompt_type, prompt_example)

    def save_response(self, response, prompt_type: PromptType):
        self.prompt_and_response.save_response(response, prompt_type)
        # setattr(self, prompt_type.name, response) # TODO: dangerous

    def get_latest_prompt(self, prompt_type):
        if prompt_type in self.prompt_and_response.prompt_dict:
            prompts = self.prompt_and_response.prompt_dict[prompt_type]
            if prompts:
                return prompts[-1]
        return 'Error, No prompts'  # TODO

    def get_latest_response(self, prompt_type):
        if prompt_type in self.prompt_and_response.result_dict:
            responses = self.prompt_and_response.result_dict[prompt_type]
            if responses:
                return responses[-1]
        return 'Error, No prompts'  # TODO

    def get_latest_prompt_type(self):
        return self.prompt_and_response.prompt_type_list[-1]

    def encode_llm(self) -> json:
        return self.prompt_and_response.encode_to_json()

    def encode_latest_llm(self) -> json:
        return self.prompt_and_response.encode_latest_llm()
   
    @staticmethod
    def serializable_obj():
        return ['state', 'longterm_memory', 'emotion', 'drawings', 'working_memory', 'prompt_and_response', 'Schedule', 'agenda', 'Task', 'job']
   
    @staticmethod
    def value_attrs():
        return ['name', 'age', 'bio', 'goal', 'health', 'money', 'x', 'y', 'vigor', 'satiety', 'date_num', 'guid']
    
    def attrs_to_save(self):
        '''
        return a dict of the attributes to save or log
        '''
        attr_to_save = find_instance_specific_data_attrs(self)
        attr_to_save = attr_to_save + ['name']
        dict2save = dict( ((attr, getattr(self, attr)) for attr in attr_to_save))
        return dict2save
    
    def save_self_locally(self):
        save_path = None
        if self.save_dir:
            os.makedirs(f'{self.save_dir}', exist_ok=True)
            dict2save = self.attrs_to_save()
                        
            # Keep the number of files less than K
            files = os.listdir(self.save_dir)
            files.sort(key=lambda x: os.path.getctime(os.path.join(self.save_dir, x)))  # Sort files by creation time
            while len(files) >= 10: 
                os.remove(os.path.join(self.save_dir, files[0]))
                files.pop(0)
            
            save_path = f'{self.save_dir}/char_{self.name}_{self.name}_{datetime.now().strftime("%m%d%H%M%S")}.dill'
            try:
                with open(save_path, 'wb') as f:
                    dill.dump(dict2save, f)
            except:
                traceback.print_exc()
                __import__('ipdb').set_trace()
            
        return save_path
                
    def load_from_local(self, file_path):
        print(f'load Character from {file_path}')
        with open(file_path, 'rb') as f:
            attr_dict = dill.load(f)
        for key, value in attr_dict.items():
            if key in ['name','save_dir']: continue
            setattr(self, key, value)
    
    def log_attrs(self):
        dict2save = self.attrs_to_save() 
        dict2save.pop('llm_config', None)
        LogManager.log_char_attr_with_time(self.name, dict2save)
        
    def __repr__(self):
        return f'{self.name}'

    

class CharacterList:
    characters: list[Character]

    def __init__(self):
        self.characters = []

    def perspect_surrounding_char(self, protagonist: Character) -> list[Character]:
        '''
        return characters in the same building
        '''


        def perspectable(agent_a, agent_b):
            blg_a = agent_a.in_building
            blg_b = agent_b.in_building
            distance = agent_a.x -agent_b.x + agent_a.y - agent_b.y # Manhattan distance
            return blg_a==blg_b and distance<18 

        return [  char for char in self.characters if perspectable(protagonist, char) and protagonist!=char ]

    def get_character_by_name(self, name:str):
        for char in self.characters:
            if char.name == name:
                return char
        return None
    
    def get_character_by_id(self, id):
        for char in self.characters:
            if char.guid == id:
                return char
        return None 

    def add_character(self, character):
        self.characters.append(character)

    def get_nearby_characters(self, character, radius) -> list[str]:
        return [other_character.name for other_character in self.characters if
                abs(other_character.x - character.x) <= radius and abs(other_character.y - character.y) <= radius]

    def encode_to_json(self) -> json:
        character_dicts = [character.encode_to_json() for character in self.characters]
        return character_dicts
    
    def save_locally(self):
        for character in self.characters:
            character.save_self_locally()


class PromptAndResponse:
    def __init__(self, character_name, character_id):
        # self.character = character
        self.character_name = character_name
        self.character_id = character_id
        self.prompt_dict: dict[PromptType, list] = {}
        self.result_dict: dict[PromptType, list] = {}
        self.prompt_type_list = []
        self.latest_prompt_type: PromptType = None
        self.latest_prompt_example:str = None
        self.latest_prompt = None
        self.latest_response = None
        self.error_seperator = "###NOTICE###"
    
    @property
    def all_prompts_types(self):
        return list(self.prompt_dict.keys())

    def save_prompt(self, prompt, prompt_type, prompt_example):
        self.prompt_type_list.append(prompt_type)
        self.latest_prompt_type = prompt_type
        self.latest_prompt_example = prompt_example
        self.latest_prompt = prompt
        prompts = self.prompt_dict.setdefault(prompt_type, [])
        prompts.append(prompt)
        print(f"\n***Send prompt to {self.character_name}, {prompt_type}\n{prompt}\n")
        LogManager.log_character_with_time(self.character_name, f"***Send prompt to LLM, {prompt_type}\n{prompt}\n")
    
    def save_response(self, response, prompt_type):
        responses = self.result_dict.setdefault(prompt_type, [])
        responses.append(response)
        self.latest_response = response
        print(f"\nReceive response from LLM of {self.character_name}, {prompt_type}\n{response}\n")
        LogManager.log_character_with_time(self.character_name, f"Receive response from LLM, {prompt_type}\n{response}\n")

    def encode_to_json(self) -> json:
        return serialize(self, allowed=['prompt_dict', 'result_dict'])

    def encode_latest_llm(self) -> json:
        return serialize(self, allowed=['name', 'latest_prompt_type', 'latest_prompt', 'latest_response'])
    
    def response_vanity_check(self, response, check_exempt_layers):
        try:
            response_dict = PromptAndResponse.response_json_check(response)
            self.response_structure_check(response_dict,check_exempt_layers)
        except Exception as e:
            return f'{self.error_seperator} Please NOTICE that {e} '
        
    @staticmethod
    def response_json_check(response):
        response = PromptAndResponse.extract_json_from_markdown(response)
        try:        
            if type(response) is not dict:
                response = eval(response) 
        except:
            try:
                response = json.loads(response) 
            except:           
                __import__('ipdb').set_trace()
                print(f'Can not load reply as json, reply: {response}')
                raise AssertionError('Must return a formal dict ! Recheck the dict format')
        
        return response
           
    def response_structure_check(self, response_dict, exempt_layers=[2,3,4,5,6,7,8,9,10]):    
        if self.latest_prompt_example:
            prompt_example = self.latest_prompt_example if type(self.latest_prompt_example) is dict else json.loads(self.latest_prompt_example)
            self.have_same_structure(prompt_example, response_dict, exempt_layers=exempt_layers)
            
    def have_same_structure(self, ground_turth_dict, pred_dict, layer=0, exempt_layers=[2,3,4,5,6,7,8,9,10]): 
        '''
        eval if the return dict and sample dict have the same hierarchical structure
        in default, only the 0,1 layer is checked
        '''
        if isinstance(ground_turth_dict, dict) and isinstance(pred_dict, dict):
            # Check if both dictionaries have the same set of keys
            # if set(ground_turth_dict.keys()) != set(pred_dict.keys()) and (layer not in exempt_layers):
                # raise AssertionError(f'dict keys should be strictly conformed to {list(ground_turth_dict.keys())}')
            if ( set(ground_turth_dict.keys()) - set(pred_dict.keys())) and (layer not in exempt_layers):
                raise AssertionError(f'dict keys must contain all the following: {list(ground_turth_dict.keys())}')
            
            # Recursively check the structure of each key-value pair
            if layer not in exempt_layers:
                for key in ground_turth_dict:
                    self.have_same_structure(ground_turth_dict[key], pred_dict[key], layer=layer+1, exempt_layers=exempt_layers)
            # else:
            #     # assume the order of values does not matter
            #     for g_v, p_v in zip(ground_turth_dict.values(), pred_dict.values()):
            #         self.have_same_structure(g_v, p_v, layer=layer+1, exempt_layers=exempt_layers)

        # If either of the values is not a dictionary, treat as leaf node
        assert type(ground_turth_dict) == type(pred_dict), f'the type of {pred_dict} should be {type(ground_turth_dict)}'
    
    @staticmethod
    def extract_json_from_markdown(markdown_text):
        # Regular expression to match the content inside ```json``` tags
        pattern = r'```json\n(.*?)```'
        # Find all matches
        matches = re.findall(pattern, markdown_text, re.DOTALL)
        # If there are matches, return the first one
        if matches:
            # Remove leading and trailing whitespace and newlines
            json_content = matches[0].strip()
            return json_content
        else:
            return markdown_text
        
    def __repr__(self):
        return f"""
            Lasest prompt type: {self.latest_prompt_type}
            Lasest Response: {self.latest_response}
        """
    