from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType

@register(name=PromptType.DRAWINIT, type='prompt')
class DrawInitPrompt(BasePrompt):
    '''
        the observations of external circumstance are {external_obs}.
        your understanding of the world: {world_model}.
    '''
    PROMPT = '''
        Your name is {name} and you are going to draw a picture.
        
        From your perception, 

        your current emotion: {emotion}.
        the most impressive event that effects your emotion is {impressive_events}.
        your preference taste of art: {preference_art}.
        
        Considering information above, describe the picture you are going to draw. 
        
        You must follow the following criteria: 
        1) Return the init sentence in the JSON format as this example:
        {EXAMPLE}
        2) You should describe the picture in detail, including the content, style, and the emotion you want to express.
    '''
    
    EXAMPLE = {
        "drawing_description": "Highly detailed widetechnical drawing of a Tyrannosaurus rex skeleton, showcasing its intricate bone structure."
    }
    
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type, state)
    
    def create_prompt(self, perception):
        '''
        
        perception: {
            "external_obs":
            "internal_status": 
            "world_model":
        }
        '''
        return self.format_attr(**perception)
    
    