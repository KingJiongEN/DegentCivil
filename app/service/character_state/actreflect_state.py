import asyncio
from functools import partial
import json
from time import sleep
from ...utils.gameserver_utils import add_msg_to_send_to_game_server
from .base_state import BaseState
from ...constants import CharacterState, PromptType
from ...models.character import Character, CharacterList
from ...models.location import BuildingList
from .register import register
from autogen import Agent

@register(name='ACTREFLECTION', type="state")
class ActReflection(BaseState):
    '''
    summarize the contents of a chat
    '''
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,  on_change_state, 
                 followed_states=[CharacterState.PERSP, CharacterState.WORK],
                 main_prompt = PromptType.ACTREFLECTION,
                 state_name = CharacterState.ACTREFLECTION,
                 enter_calls=None, 
                 exit_calls=None, 
                 update_calls=None, 
                 llm_calls=None,
                 post_calls=None,):        
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
                        )    
        self.post_llm_call_chain.add(self.store_reflection,2 )
    
    def call_main_prompt(self, prompt):
        return super().call_main_prompt(prompt)

    def tailor_response_to_wm(self, result):
        return super().tailor_response_to_wm(result)
   
    def store_reflection(self, result):
        new_understand = result['new_understanding']
        return super().store_reflection(new_understand)
    
    def state_router(self):
        if self.character.job is not None:
            return self.turn_on_states(CharacterState.WORK)
        
        return self.turn_on_states(CharacterState.PERSP)
    
    def push_state_change_to_server(self, **kwargs):
        super().push_state_change_to_server()

        msg = {
            'content': f'{self.character.name} is reflecting on his recent behaviors',
            'agent_guid': self.character.guid,
            'content_type': 2,
            'display_duration': 1000
        }
        msg = f"1002@{json.dumps(msg)}"
        add_msg_to_send_to_game_server(msg)
        return False, dict()
    
    