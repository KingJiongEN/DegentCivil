import copy
import os
import re
import traceback
from typing import List, Optional, Union

from ...models.building import BuildingList
from ...models.character import Character, CharacterList
from ...utils.log import LogManager
from ...service.character_state import FuncName2Registered, PromptName2Registered, StateName2Registered
from ...utils.serialization import serialize

class BasePrompt:
    '''
    prompt = prompt text + candidate followed states(text explaination) + data format for each followed states
    '''
    
    PROMPT = '''
    '''
    
    def __init__(self, prompt_type, state) -> None:
        '''
        recordable_key: store the value of this key from the llm response to character.working_memory
        '''
        self.prompt_type = prompt_type
        self.state = state
        self.character:Character = state.character
        self.character_list: CharacterList = state.character_list
        self.building_list: BuildingList = state.building_list
        self.followed_state_format = '({sid}) {state_des}: {state_requirments}\n\n'
        self.entire_prompt_format = '{PROMPT}\n\n Please decide what to do next and return the json dict from the following options\n\n{followed_states_text}'
        self.waring_message = ['Warning: in previous attempts, the returned response met the following errors:\n']
        self.warning_added = False
        self.check_exempt_layers = [1,2,3,4,5,6,7,8,9]
        
        self.recordable_key = None 
    
    def set_recordable_key(self, key: Union[str, List[str]]):
        if type(key) is str : 
            self.recordable_key = key
        elif type(key) is list:
            assert all([ type(ky) is str for ky in key]), f' all elements in keys list should be str, current key is {key}'
            self.recordable_key = key
        else:
            raise NotImplemented
        
    def create_prompt(self):
        return self.format_attr()
   
    def add_warning_msg(self, warning_message):
        self.warning_added += 1
        if self.warning_added > 3: # limit the length of warning message
           self.waring_message.remove(self.waring_message[1]) 
        self.waring_message.append(warning_message + '\n')
        
    def format_attr(self, 
                    # character: Character, 
                    # character_list: CharacterList,
                    # building_list: BuildingList,
                    **kwargs,
                    ) -> str:
        # find prompt by prompt_type in llm/prompt folder
        # if cannot find, return error message
        # replace placeholder with character info and building list
        # return prompt
        prompt_file_path = os.path.join(os.path.dirname(__file__), self.prompt_type.to_str() + '.txt')
        if os.path.exists(prompt_file_path):
            with open(prompt_file_path, 'r', encoding='utf-8') as file:
                    base_prompt = file.read()
        elif hasattr(self, 'PROMPT'):
            base_prompt = self.PROMPT
        
        att_dict = dict()
        att_dict.update({'buildings': self.building_list.get_building_descriptions()})
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
        
        
        base_prompt = base_prompt.replace('TERMINATE','') # in case that interaction history has 'TERMINATE'. TODO: make it more elegant
        if self.warning_added:
            base_prompt = base_prompt + ' '.join(self.waring_message)
        return base_prompt
        
