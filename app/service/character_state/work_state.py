from .base_state import BaseState
from .idle_state import IdleState
from .register import register
from ...constants import CharacterState, PromptType
from ...models.location import BuildingList
from ...models.character import Character, CharacterList


@register(name='WORK', type="state")
class WorkState(BaseState):
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,
                 on_change_state,
                 followed_states=[CharacterState.PERSP],
                 main_prompt = None,
                 state_name = CharacterState.WORK,
                 state_duration_tolerance = 24, # TODO can be reset by the job
                 enter_calls=None, 
                 exit_calls=None, 
                 update_calls=None, 
                 llm_calls=None,
                 post_calls=None,
                 descrption="Working state. The character is working for a job and can not take active actions. "
                 ):        
        super().__init__(character=character, 
                         main_prompt=main_prompt, 
                         character_list=character_list, 
                         building_list=building_list,
                         followed_states=followed_states,
                         on_change_state=on_change_state,
                         state_duration_tolerance = state_duration_tolerance,
                         state_name=state_name,
                         llm_calls=llm_calls,
                         enter_calls=enter_calls, 
                        exit_calls=exit_calls, 
                        update_calls=update_calls, 
                        post_calls=post_calls,
                        description=descrption,
                        
                        )
        
        self.enter_state_chain.add(self.update_system_prompt, 0)
        self.exit_state_chain.add(self.recover_system_prompt, 0)
        
    def update_system_prompt(self):
        character_job = self.character.job
        character_job.add_job_des_to_agent_messge(self.character)
        return False, dict()    
    
    def recover_system_prompt(self):
        self.character.update_system_message(self.build_sys_message())
        self.character.job = None
        return False, dict()
