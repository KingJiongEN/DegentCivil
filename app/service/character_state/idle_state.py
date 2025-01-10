from .base_state import BaseState
from .register import register
from ...constants import CharacterState, PromptType
from ...models.location import BuildingList
from ...models.character import Character, CharacterList


@register(name='IDLE', type="state")
class IdleState(BaseState):
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,
                 on_change_state,
                 followed_states=[CharacterState.IDLE],
                 main_prompt = None,
                 state_name = CharacterState.IDLE,
                 state_duration_tolerance = 1,
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
                         state_duration_tolerance=state_duration_tolerance,
                         llm_calls=llm_calls,
                         enter_calls=enter_calls, 
                        exit_calls=exit_calls, 
                       update_calls=update_calls, 
                        post_calls=post_calls,
                        arbitrary_obj=arbitrary_obj,
                         arbitrary_wm=arbitrary_wm,           
                        )   
    
    def change_state(self, overduration):
        if overduration:
            self.turn_on_states()
        return super().change_state(overduration)
    
