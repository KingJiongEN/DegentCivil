from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType

@register(name=PromptType.BARGAIN, type='prompt')
class BargainPrompt(BasePrompt):
    PROMPT = '''
        Your name is {name} and you are thinking about buying {item} from the seller {seller}.
        
        From your perception, 
        the observations of external circumstance are {external_obs}.
        your understanding of the world: {world_model}.
        your current emotion: {emotion}.
        the price of the {item}: {price}.
        your preference for {item}: {preference}.
        your impression of the seller: {impression}.
        your remaining money: {Gold}.
        
        Considering information above, Write the first sentence to start the conversation.
        
        You must follow the following criteria: 
        1) Return the init sentence in the JSON format as this example:
        {EXAMPLE}
        2) You should tell the seller you want to buy it or bargain with the seller for a better price.
        3) If you really like or you really need it, you would like to buy it at the original price.
        4) You should mention the original price in case the seller forgets.
    '''
    
    EXAMPLE = {
        "init_conversation": "I like your painting, but I think the price is a little bit high. Can you give me a discount?",
    }
    
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type, state)
        # self.recordable_key = 'init_conversation'
    
    def create_prompt(self, information):
        '''
        information: {
            "name": str,
            "item": str,
            "seller": str,
            "external_obs": str,
            "world_model": str,
            "emotion": str,
            "preference": str,
            "impression": str,
            "money": int
        }
        '''
        return self.format_attr(**information)