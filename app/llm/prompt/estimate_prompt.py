from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType
from ...service.character_state import FuncName2Registered, PromptName2Registered, StateName2Registered
from ...utils.serialization import serialize

@register(name=PromptType.ESTIMATE, type='prompt')
class EstimatePrompt(BasePrompt):
    PROMPT = '''
        You are a character in a virtual world. You are thinking about buying something from another character.
        You need to tell how much you are willing to pay for it at most based on your trading strategy, your emotions, basic market price, your like score to it and your history trading records.

        Note that:
        1. You buy things driven by your emotions.
        2. You should take all into consideration. 
        3. If you really like something, you will be willing to pay a lot more than the market price. If not that much, you will only like to pay around the market price.
        4. If you think it may sell a good price in the future, you will be more willing to pay more.
        5. Your budget is limited.
        6. If you don't like it, which means like score is below 5, you will not consider it from the beginning.
        
        Your current emotion: {emotion}
        Basic market price: {basic_price}
        Your like score to it: {like_score}
        Your remaining budget: {budget}
        Your relevent history trading records: {history}

        Tell how much you are willing to pay for it at most.
        
        You must follow the following criteria: 
        1) Return the result in the JSON format as this example:
        {EXAMPLE}
        2) You should associate the price with the current situation, make your final decision carefully.
    '''
    
    EXAMPLE = {
        "expected_price": 4000,
    }
    
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type, state)
        self.set_recordable_key(['expected_price'])
         
    def create_prompt(self, env_kwargs):
        return self.format_attr(**env_kwargs)