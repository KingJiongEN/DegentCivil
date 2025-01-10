from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType
from ...utils.globals import RESOURCE_SPLITER

@register(name=PromptType.SUM, type='prompt')
class SumPrompt(BasePrompt):
    PROMPT=''' 
        Current time: {date}
        Summarize the takeaway from the previous interaction with {act_obj}.
        Previous interaction: {dialogue}
        Do not add any introductory phrases. If the intended request is NOT properly addressed, please point it out.
        The modified properties of the characters and buildings are as follows:
            {stake_holders_modifiable_properties}



        Please notice that
        * first summary the interaction history
        * analyse the modified values for all the characters and buildings mentioned in the interaction history
        * only need to return the value that needs to be modified
        * only need to return the delta value of the properties that are modified, don't need to return the final value of the properties.
        * if the interaction history mentions about scheduling a future event, please add it to the agenda of the character
        * inference the spcific date for the future event in the format of "YYYY-MM-DD", write the event in the agenda detailedly
        * modified_properties is a dictionary, the key is the name of the property, the value is the delta value of the property. The delta value can be positive or negative number.
        * return in json format, begins with \{ and ends with \}
        An example of returned dict:
        {EXAMPLE}
        '''
        
    EXAMPLE={  
        "interaction_summary": 'I have a good time in the cafe', 
        "act_obj": "cafe.menu",
        "modified_properties":{
            "Emma":{
                "satiety": +1,
                "money": -10,
                "job": "Cafe.Waitress",
            },
            "Jack":{
                "money": +10,
                "agenda":{
                    "specific_date": "2021-10-10",
                    "event": "being a waiter in the cafe",
                }
            }
        }
    }
    
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type, state)
        self.set_recordable_key('interaction_summary')
        
        
    def create_prompt(self, stake_holders_modifiable_properties):
        act_obj = self.state.get_character_wm_by_name('act_obj')
        obj_agent = self.character_list.get_character_by_name(act_obj)
        if obj_agent is None:
            obj_agent = self.building_list.get_building_by_name(act_obj.split(RESOURCE_SPLITER)[0]) 
        dialogue =  self.character.retrieve_modify_dialogue( obj_agent)
        return self.format_attr(dialogue=dialogue, 
                                act_obj=act_obj,
                                stake_holders_modifiable_properties=stake_holders_modifiable_properties)