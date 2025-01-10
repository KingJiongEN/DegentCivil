import copy
from .base_state import BaseState
from ...constants import CharacterState, PromptType
from ...models.character import Character, CharacterList
from ...models.location import BuildingList
from .register import register

@register(name='PLAN', type="state")
class PlanState(BaseState):
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,  on_change_state, 
                 followed_states=[ CharacterState.ACT,],
                 main_prompt = PromptType.PLAN,
                 state_name = CharacterState.PLAN,
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
        self.post_llm_call_chain.add(self.update_inner_monologue, -1)
     
      
    def tailor_response_to_wm(self, result):
        super().tailor_response_to_wm(result)
        
        self.character.set_plan(result['BestPlan'])
        self.character.working_memory.store_memory('current_step', self.character.plan.current_step)

        most_dis_info = self.get_character_wm_by_name('MostDiscrepancy')
        # Handling Agenda
        if most_dis_info['aspect'] == 'AnalyseIncompleteAgenda':
            eve_time = most_dis_info['perception']['scheduled_time']
            eve = self.character.check_date_agenda(eve_time)
            eve.update_plan(result)
            self.character.set_event(eve)
        elif most_dis_info['aspect'] != 'AnalysePlanAction':
            #  if aspect is about external or internal perception, suspend event
            if self.character.event:
                self.character.suspend_event() 
            
            
        return False, dict()
    
    def update_inner_monologue(self):
        self.character.inner_monologue.call_llm()
        return False,  dict()
    
    def push_attr_change_to_server(self, **kwargs):
        import json
        from time import sleep
        from ...utils.gameserver_utils import add_msg_to_send_to_game_server
        if "monologue_plan" in self.character.inner_monologue.content.keys():
            msg = {
                'content' : f' I plan to {self.character.inner_monologue.content["monologue_plan"]}',
                'agent_guid' : self.character.guid,
                'content_type': 1,
                'display_duration': 3
            }
        else:
            msg = {
                'content' : f' I plan to {self.character.plan.current_step}',
                'agent_guid' : self.character.guid,
                'content_type': 1,
                'display_duration': 3
            }
        msg = f"1002@{json.dumps(msg)}"

        add_msg_to_send_to_game_server(msg)
        sleep(3)
        return super().push_attr_change_to_server()
    
    def push_state_change_to_server(self, **kwargs):
        import json
        from ...utils.gameserver_utils import add_msg_to_send_to_game_server
        # super().push_state_change_to_server(**kwargs)
        msg = {
            'content': f'{self.character.name} is making a plan',
            'agent_guid': self.character.guid,
            'content_type': 2,
            'display_duration': 1000
        }
        msg = f"1002@{json.dumps(msg)}"

        add_msg_to_send_to_game_server(msg)
        return False, dict()