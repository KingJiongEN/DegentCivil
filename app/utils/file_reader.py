'''
Read different files
'''

import os

def read_prompts(file:str):
    assert type(file) is str , f'{file} should be a str indicating a prompt filename' 
    assert os.path.exists(file), f'{file} does not exist'
    assert file.startswith('prompt') , f'{file} should be a prompt filename starting with "prompt" ' 
    with open(file) as f:
        prop = f.read()
    return prop