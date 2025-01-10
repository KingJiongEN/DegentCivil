from .base_prompt import BasePrompt
from ...service.character_state.register import register
from ...constants.prompt_type import PromptType

@register(name=PromptType.CHATINIT, type='prompt')
class ChatInitPrompt(BasePrompt):
    PROMPT = '''
        Your game character is going to start a conversation with another character {act_obj} . 

    Considering the following elements
    {act_obj_job}
    Your impression on the this character: {impression}
    Your whole plan: {BestPlan}
    Your current stage: {current_step}
    Your current emotion: {current_emotion}


    Write the first sentence to start the conversation.

    You must follow the following criteria: 
    1) Return the init sentence in the JSON format as this example:
    {EXAMPLE}
    2) Your sentence should be related to the current situation or match your plan/expectation.
    3) Your sentence should not be longer than 30 words.
    4) Your sentence needs to match your current emotion, the emotion value less than 6 usually means your character is in a bit of such emotion. The value bigger than 6 means your character is in an extreme emotion. For example:
    Your current emotion is anger:8, meaning you are extreme angry. So your sentence might be: "What the hell with you? Where is my coffee?"
    '''
    EXAMPLE = {"init_conversation": "Hi, how about your recent work?"}
    
    
    def __init__(self, prompt_type, state) -> None:
        super().__init__(prompt_type, state)
        self.recordable_key = 'init_conversation'
    
    def create_prompt(self):
        act_obj = self.state.get_character_wm_by_name('act_obj')
        act_obj_job = ''
        obj_agent = self.character_list.get_character_by_name(act_obj)
        if obj_agent:
            act_obj_job = "" if obj_agent.job is None else f"The character's job {obj_agent.job}"
        impression = self.character.longterm_memory.get_people_memory(act_obj) 
        return self.format_attr(impression=impression, act_obj=act_obj, act_obj_job=act_obj_job)
    
    