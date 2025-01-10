import asyncio
import random
import os
import re
import traceback
from ..service.character_state.register import register
from ..constants.prompt_type import PromptType

@register(name=PromptType.INNER_MONOLOGUE, type="prompt")
class MonologuePrompt:
    '''
    Based on different inputs, build different monologue prompts.
    '''
    PROMPT = '''
        You're a character in a game.
        Your name is {name}.
        Your bio is {bio}.
        
        Your understanding of the world: {memory}
        
        Your internal status is: {internal_status}
        
        Your total plan is {BestPlan}
        and you are now at {current_step}
        
        Your current emotion is: {emotion}.
        
        Please each generate an inner monologue for understanding of the world, your current internal status, your current plan and your memories. 
        Then tell me your emotion with an emoji. 
        
        You must follow the following criteria:
        * each inner monologue should be within 20 words.
        * the monologue about understanding of the world should be related to your impression on other people or buildings.
        * the monologue about your internal status should summarize from these values. Use the first person narration.
        * the monologue about your plan should be related to what you are going to do. Use the first person narration.
        * the monologue about your emotion should summarize your current feeling in a consistent tone. Use the first person narration.
        
        Here is an example
        {EXAMPLE}
    
    '''
    
    EXAMPLE = {
        "monologue_understanding": "Jack is busy, I should not bother him.",
        "monologue_status": "I'm feeling tired and hungry.",
        "monologue_plan": "I should go to the library to find the book.",
        "monologue_emotion": "Feeling so sad, god damn.",
        "emoji": "😟"
    }
    
    def __init__(self, character) -> None:
        self.character = character
        self.prompt_type = PromptType.INNER_MONOLOGUE
        # self.set_recordable_key(['monologue_understanding', 'monologue_status', 'monologue_plan', 'monologue_memory', 'monologue_emotion', 'emoji'])
    
    def create_prompt(self, **kwargs):
        return self.format_attr(**kwargs)
    
    
    def format_attr(self, **kwargs) -> str:
        base_prompt = self.PROMPT
        att_dict = dict()
        att_dict.update({'memory': self.character.longterm_memory.to_json()})
        att_dict.update(self.character.working_memory.serialize())
        att_dict.update(kwargs)
        
        attributes = re.findall('\{([a-zA-Z_]+)\}', base_prompt) 
        for att in attributes:
            if att in att_dict:
                att_val = att_dict[att]
            elif hasattr(self, att):
                att_val = getattr(self, att)
            elif hasattr(self.character, att):
                att_val = getattr(self.character, att)
            elif att in self.character.working_memory.wm: # TODO
                att_val = self.character.working_memory.get(att)   
            else:
                raise  AssertionError(f'Missing attribute: {att} . Current prompt: {self.prompt_type}')
            try:
                base_prompt = base_prompt.replace('{'+att+'}', str(att_val))
            except:
                traceback.print_exc()
                if os.getenv('DEBUG'):
                    __import__('ipdb').set_trace()
                pass        
        
        return base_prompt

class InnerMonologue():
    """
    Character's inner monologue, decided by character's current perception, plans, memories or emotions.
    The content is a dict
    """
    def __init__(self, character):
        self.character = character
        self.content = dict()
        self.prompt = MonologuePrompt(character)
    
    @property
    def inner_monologue(self):
        return self.content
    
    @property
    def emoji(self):
        if "emoji" in self.content:
            return self.content["emoji"]
        return None
    
    def sample_monologue(self, size=2):
        if self.content:
            return random.sample(self.content.items(), size)
    
    def set_monologue(self, content):
        self.content.update(content)
        self.save_llm_response(content)
        
    def build_prompt(self):
        return self.prompt.create_prompt(emotion=self.character.emotion.impression)
    
    def call_llm(self):
        message = self.build_prompt()
        self.save_llm_prompt(message)
        self.llm_task = asyncio.create_task(self.character.a_process_then_reply(message=message, sender=self.character, restart=True))
        self.llm_task.add_done_callback(lambda task: self.set_monologue(task.result()))
        
    def save_llm_prompt(self, prompt):
        self.character.save_prompt(prompt, PromptType.INNER_MONOLOGUE, getattr(InnerMonologue, 'EXAMPLE', None))
        
    def save_llm_response(self, response):
        self.character.save_response(response, PromptType.INNER_MONOLOGUE)