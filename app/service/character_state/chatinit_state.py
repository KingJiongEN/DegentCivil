import asyncio
from functools import partial
from .base_state import BaseState
from ...constants import CharacterState, PromptType
from ...models.character import Character, CharacterList
from ...models.location import BuildingList
from .register import register
from autogen import Agent

@register(name='CHATINIT', type="state")
class ChatInitState(BaseState):
    '''
    consider how to init a conversation.
    '''
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,  on_change_state, 
                 followed_states=[CharacterState.CHATING],
                 main_prompt = PromptType.CHATINIT,
                 state_name = CharacterState.CHATINIT,
                 enter_calls=None, 
                 exit_calls=None, 
                 update_calls=None, 
                 llm_calls=None,
                 post_calls=None,
                 arbitrary_obj=None,):        
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
                        )    
        self.target_agent_ready = False
        self.update_state_chain.add(self.monitor_chat_target_state, 2)
        self.enter_state_chain.add(self.hang_state_to_target_agent, 2)
        
    def hang_state_to_target_agent(self):
        '''
        hang the state to the target agent
        '''
        act_obj = self.get_character_wm_by_name('act_obj')
        agent:Character = self.get_agent_by_name(act_obj)
        if agent is not None and type(agent) is Character:
            agent.hang_states.append(CharacterState.RECEIVECHAT)
            print(f'### RECEIVECHAT is hanged to {agent.name} ')
        return False, {}

    def monitor_chat_target_state(self):
        '''
        do not start chatting until the target agent state is ready
        '''
        act_obj = self.get_character_wm_by_name('act_obj')
        agent:Character = self.get_agent_by_name(act_obj)
        if agent is not None:
            if agent.state == CharacterState.RECEIVECHAT:
                agent.working_memory.store_memory('act_obj', self.character.name)
                self.target_agent_ready = True 
        
        return False, {}

    def change_state(self, overduration):
        
        for state, ready in self.followed_states.items():
            if ready and self.target_agent_ready: # add an extra condition to check if the target agent is ready
                self.on_change_state(state)
                break
     
        return False, dict()
