from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType
from ...service.character_state import FuncName2Registered, PromptName2Registered, StateName2Registered
from ...utils.serialization import serialize

@register(name=PromptType.EMOTION, type='prompt')
class EmotionPrompt(BasePrompt):
    # TODO: add more categories of emotions such as jealous, pride.
    # TODO: pass emotion list to the prompt
    '''
        - agreesiveness = anticipation + anger
        - contempt = disgust + anger
        - remorse = sadness + disgust
        - disapproval = surprise + sadness
        - awe = fear + surprise
        - submission = trust + fear
        - love = joy + trust
        - optimism = anticipation + joy
    '''
    
    PROMPT = '''
        Describe the emotion you are currently experiencing.
        Your emotion is built based on the theory of robert plutchik's wheel of emotions, which includes these basic emotions: {emotion_options}.
        More complex emotions can be represented using combinations of the above emotions, for example:

        Select 3 kinds of emotions from the above eight basic emotions to best describe your current emotion.
        For each emotion, describe the change of the emotion intension on a scale of -5 to 5. 

        
        Your previous emotion: {prev_emotion}
        Your understanding of the world: {world_understanding}
        Your interaction history : {history}
        
        You must follow the following criteria: 
        1) Return the sentence in the JSON format as this example:
        {EXAMPLE}
        2) You should associate the emotion with the current situation, describe the intensity of the emotion carefully and explain the emotion change.
        3) 0 means no emotion, 10 means the most intense emotion, 6 means a neutral state. e.g. anger:10 means very angry, sadness:3 means a little bit sad.

    '''
    
    EXAMPLE = {
        "emotions": [
            {
                "emotion": "joy",
                "change": 4,
                "explanation": "I feel much happy beacause I get a gift from my friend Jay."
            },
            {
                "emotion": "trust",
                "change": 3,
                "explanation": "I trust my Jay, he is a kind man."
            },
            {
                "emotion": "supprise",
                "change": 2,
                "explanation": "I am supprised that Jay gives me a gift. I didn't expect that. And the gift happend to be on my gift list."
            }
        ]
    }
    
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type, state)
        self.set_recordable_key('emotions')
         
    def create_prompt(self, env_kwargs):
        return self.format_attr(**env_kwargs)