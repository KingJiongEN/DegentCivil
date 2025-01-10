from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType

@register(name=PromptType.APPRECIATE, type='prompt')
class AppreciatePrompt(BasePrompt):
    PROMPT = '''
You are a helpful assistant that help a game character appreciate an artwork.
When appreciating artworks, it's crucial to resonate with the character's persona and values.
Your knowledge level should not exceed that of a normal person with the bio of the character, unless there are relevant memories in his/her Long-Term Memory.

I will give you the following information: 

The game character's bio : {bio}
The game character's Long-Term Memory: {memory}
The game character's emotional state: {emotion}
The game character's preference taste of art: {preferenced_art}

Here is the artwork that the game character wants to appreciate:
{artwork}

   You must follow the following criteria: 
 1) You should tell me with JSON format as follows:
{EXAMPLE}
2) Your appreciation should express your feelings and reasons for appreciating the artwork in no more than 40 words.
3) Like score should be in the range of 0-10.
4) Improvement should describe areas for improvement in the artwork, within 20 words.

    '''
    EXAMPLE = {
        "appreciation": "I adore the captivating depth and emotive atmosphere of this smudged oil painting; its blurred strokes evoke a poignant sense of nostalgia and introspection.", 
        "like_score": 8, 
        "improvement": "Enhance clarity, refine details, balance composition, and deepen contrasts to amplify the impact and coherence of the artwork.", 
        }
    
    
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type, state)
        self.set_recordable_key(['appreciation', 'like_score', 'improvement'])
    
    def create_prompt(self, perception):
        '''
        
        perception: {
            "bio":
            "goal": 
            "memory":
            "artwork":
            "emotion":
            "preferenced_art":
        }
        '''
        return self.format_attr(**perception)
    
    