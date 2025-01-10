"""
Deprecated, replaced by ACTREFLECT
"""
from functools import partial
from .base_state import BaseState
from ...constants import CharacterState, PromptType
from ...models.character import Character, CharacterList
from ...models.location import BuildingList
from .register import register

@register(name='CRITIC', type="state")
class CriticState(BaseState):
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,  on_change_state, 
                 followed_states=[CharacterState.PLAN, CharacterState.ACT],
                 main_prompt = PromptType.CRITIC,
                 state_name = CharacterState.CRITIC,
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
                        arbitrary_obj=arbitrary_obj,
                         arbitrary_wm=arbitrary_wm,           
                        )   
        
    def turn_on_states(self, result, *args, **kwargs):
        result = result.get("result", "fail")
        if result == "success" or result == "fail":
            self.store_reflection(partial(super().turn_on_states,
                                      next_state_names=CharacterState.PLAN))
            return False, dict()
        else:
#            # __import__('ipdb').set_trace()
            return super().turn_on_states(next_state_names=CharacterState.ACT)

