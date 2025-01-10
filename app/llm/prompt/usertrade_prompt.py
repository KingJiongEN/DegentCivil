from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType

@register(name=PromptType.USERTRADE, type='prompt')
class UsertradePrompt(BasePrompt):
    PROMPT=''' 
        Summarize the takeaway from the previous interaction with {act_obj}.
        Previous interaction: {dialogue}
        Do not add any introductory phrases. If the intended request is NOT properly addressed, please point it out.
        Describe if the properties in {digital_internal_properties} are modified.

        Please notice that
        * only need to return the delta value of the properties that are modified, don't need to return the final value of the properties.
        * return in json format, begins with \{ and ends with \}
        
        {EXAMPLE}
        '''
        