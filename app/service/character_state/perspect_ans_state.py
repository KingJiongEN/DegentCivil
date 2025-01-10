from .base_state import BaseState
from ...constants import CharacterState, PromptType
from ...models.location import BuildingList
from ...models.character import Character, CharacterList
from .register import register

@register(name='PERSPA', type="state")
class PerspectAnsState(BaseState):
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList, 
                 on_change_state, 
                 state_name: str = CharacterState.PERSPA, 
                 main_prompt=PromptType.Perspect_Ans,
                 followed_states=[CharacterState.PLAN],
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
    # def enter_state(self):
    #     super().enter_state()
    #     self.qa_first_time()

    # def update_state(self):
    #     super().update_state()
    #     if self.finish_state:
    #         self.on_change_state()

    # def exit_state(self):
    #     super().exit_state()

    # def qa_first_time(self):
    #     self.call_llm(PromptType.QA_FRAMEWORK_QUESTION, self.qa_second_time)

    # def qa_second_time(self, task):
    #     self.call_llm(PromptType.QA_FRAMEWORK_ANSWER, self.on_qa_done)

    # def on_qa_done(self, task):
    #     self.finish_state = True
