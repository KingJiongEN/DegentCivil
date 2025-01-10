import copy
from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType
from ...utils.globals import RESOURCE_SPLITER

@register(name=PromptType.ACTREFLECTION, type='prompt')
class ActRlectPrompt(BasePrompt):
    PROMPT = '''
    Compared with your previous understanding of the buildings and other characters, summarize the new understanding from the conversation. 
    Your understanding of the world:  {impression_memory},
    The the interaction happened with {act_obj}
    Your current plan: {plan}
    The interaction history : {dialogue}
    Do not add any introductory phrases.
    
    Please note that
    * first judge if the previous interaction successfully achieves your purpose of current step
    * recognize the entities involved in the interaction
    * compare if the previous interaction achieves your purpose of current step
    * summarize the new understanding of these entities
    * return the final version of the new understanding
    * only return the buildings and people that you have new understanding on. No need to return all buildings and people
    * return in json format, begins with \{ and ends with \}
   
    Here is an example: 
    {EXAMPLE} 
   
    '''
        
    EXAMPLE = {
            "step_complete": True,
            "entities":{
              "people": "Jim",
              "building": "cafe",
            },
            "new_understanding":{
                "people": {
                    "Jim": {
                        "impression": "Jim is much rich."
                    }
                },
                "building":{
                    "cafe":{
                        "impression": "Have some delicious foods."
                    }
                }
            }
        }
    
    
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type, state)
        self.set_recordable_key(['step_complete', ])
        self.check_exempt_layers = [1,2,3,4,5,6,7,8,9]
    
    def create_prompt(self):
        impression_memory = self.character.longterm_memory.impression_memory
        act_obj = self.state.get_character_wm_by_name('act_obj') # Emma or cafe.menu
        obj_agent = self.character_list.get_character_by_name(act_obj)
        if obj_agent is None:
            obj_agent = self.building_list.get_building_by_name(act_obj.split(RESOURCE_SPLITER)[0]) 
        dialogue =  self.character.retrieve_modify_dialogue(obj_agent)
       
        interaction_summary = self.state.get_character_wm_by_name('interaction_summary')
        return super().format_attr(impression_memory=impression_memory, dialogue=dialogue, act_obj=act_obj,
                                   interaction_summary=interaction_summary)