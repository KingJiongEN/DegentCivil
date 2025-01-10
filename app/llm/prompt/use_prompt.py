from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType

@register(name=PromptType.USE, type='prompt')
class UsePrompt(BasePrompt):
    PROMPT = '''
        The character's inter status are {internal_status}.
        
    '''
    
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type, state)