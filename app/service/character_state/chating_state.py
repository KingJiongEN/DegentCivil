import asyncio
from functools import partial
from .base_state import BaseState
from ...constants import CharacterState, PromptType
from ...models.character import Character, CharacterList
from ...models.location import BuildingList
from ...models.trade import Trade, TradeRecord
from .register import register
from autogen.agentchat.chat import ChatResult

@register(name='CHATING', type="state")
class ChatingState(BaseState):
    '''
    In the process of chatting
    '''
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,  on_change_state, 
                 followed_states=[CharacterState.SUM],
                 main_prompt = PromptType.CHATING,
                 state_name = CharacterState.CHATING,
                 enter_calls=None, 
                 exit_calls=None, 
                 update_calls=None, 
                 llm_calls=None,
                 post_calls=None,
                 arbitrary_obj=None,
                 arbitrary_wm=dict(),
                ):        
        super().__init__(character=character, 
                         main_prompt=main_prompt, 
                         character_list=character_list, 
                         building_list=building_list,
                         followed_states=followed_states,
                         on_change_state=on_change_state,
                         state_name=state_name,
                         llm_calls=llm_calls,
                         enter_calls=enter_calls, 
                         exit_calls=exit_calls, 
                         update_calls=update_calls, 
                         post_calls=post_calls,
                         arbitrary_obj=arbitrary_obj,
                         arbitrary_wm=arbitrary_wm,
                        )
        self.default_client = 'gpt-3.5-turbo-0125-chatgpt-3.vip'
        self.exit_state_chain.add(self.restore_system_prompt, 0)
   
    # def enter_state(self, *args, **kwargs):
    #     self.character.set_state(self) 
    #     print(f'enter state: {self.state_name}')
    #     self._state_duration = 0

    #     self.loop_duration += self._circle_tolerance
        
    #     for state in self.followed_states: # reset next states
    #         self.followed_states[state] = False

    #     self.execute_func_chain( func_chain=self.enter_state_chain ,  obj=self ,**kwargs)
    #     return super().enter_state(*args, **kwargs)
   
    def update_state(self, msg, date, *args, **kwargs):
        return super().update_state(msg, date, *args, **kwargs)
    
    def call_llm(self, *args, **kwargs):
        act_obj = self.get_character_wm_by_name('act_obj')
        recipient = self.character_list.get_character_by_name(act_obj)
        self.recipient = recipient
        # interaction with building is now in use_state
        # if recipient is None: # is building 
        #     recipient = self.building_list.get_building_by_name(act_obj)
        #     mem_on_rec = self.character.longterm_memory.get_building_memory(act_obj)
        #     mem_on_send = None # DEBUG
        # else: 
        assert type(recipient) is Character, f" recipient {recipient} is not a Character object, but {type(recipient)}"
        mem_on_rec = self.character.longterm_memory.get_people_memory(act_obj)
        mem_on_send = recipient.longterm_memory.get_people_memory(self.character.name)
            
        recipient.update_system_message(recipient.system_message + f' Your current status: {recipient.internal_status}. You are chatting with {self.character.name}. Your impression on him/her is {mem_on_send}. If you are purchasing something, calculate the final price carefully. You can not reply more than 30 words at a time.')
        self.character.update_system_message(self.character.system_message + f'Your current status: {self.character.internal_status}. You are chatting with {recipient.name}. Your impression of him/her is {mem_on_rec }. If you are purchasing something, calculate the final price carefully. You can not reply more than 30 words at a time.')
        
        
        self.llm_task = asyncio.create_task(self.character.a_initiate_chat(recipient=recipient,
                                            message=self.get_character_wm_by_name('init_conversation'),
                                            clear_history=True, )
                                            )
    def restore_system_prompt(self):
        self.character.update_system_message(self.character.build_sys_message())
        self.recipient.update_system_message(self.recipient.build_sys_message())
        
        return False, dict()