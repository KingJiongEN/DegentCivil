from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType
from ...service.character_state import FuncName2Registered, PromptName2Registered, StateName2Registered
from ...utils.serialization import serialize

@register(name=PromptType.ACT, type='prompt')
class ActPrompt(BasePrompt):
    PROMPT = '''
        You total plan is {BestPlan}
        Now your are at {current_step}
        
        Your understanding of the world: {memory}
        
        Your current emotion is: {emotion}
        
        Please decide what to do next and return the json dict for the following options
        
        Here are the candidate actions, each key-value pair indicates an action (key) and the action object (value)
        {candidate_acts}
        
        You must follow the following criteria: 
        * return an action, the object of the action, the purpose of your action and the emoji of the action
        * you can only choose one key-value pair from the candidate actions
        * return in json format, begins with \{ and ends with \}
        * your current emotions affect your decision making. In detail,
            - When and only when you are in an extreme mood (e.g. anger value or disgust value is above 8), there is a small probability (about 5%) that you will choose art-related decisions to help regulate your mood, such as use the workshop to draw.
            - The actions matching your current feeling will have a higher probability to be chosen. \
                For example, when you are depressed, you are more likely to choose behaviors that can relieve your emotions, e.g. if you like art exhibitions, you are more likely to choose to move to an art museum to see an exhibition
        * the chosen action should be in line with your current state. In detail,
            - When your vigor value is low, you are intend to eat or drink sth.
            - When your health value is low, you should choose to go to the hospital as early as possible.
        Here is an example
        {EXAMPLE}
    '''
    
    EXAMPLE = {
            "action": "USE",
            "act_obj": "cafe.menu",
            "purpose": "feed my stomach",
            "emoji": "🍔"
    }
    
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type, state)
        self.set_recordable_key(['act_obj', 'emoji'])
         
    def create_prompt(self, **env_kwargs):
        assert 'candidate_acts' in env_kwargs, f' current env kwargs {env_kwargs}'
        
        return self.format_attr(**env_kwargs)