import asyncio
import json
from pathlib import Path
import sys
sys.path += [str(Path(__file__).resolve().parent.parent), './', '../']
import os
from app.llm.llm_expends.gpt35 import GPT35Caller
from app.llm.llm_expends.gpt4 import GPT4Caller
from app.llm.llm_expends.dalle3 import DALLE3Caller
# caller = GPT35Caller()
caller = GPT4Caller()

# content = '''
# write 2 random English names and return in json format, like {'names': ['name1', 'name2', 'name3', ...]}
# '''

# messages = {'model': "gpt-3.5-turbo-0125", 'messages': [{'role': 'user', 'content': "write 50 random different English names and return in json format, each name must have a first name and a family name, middle name is optional, like {'names': ['Sophia Smith', 'Olivia Jeff', 'Mia Brown', ...]}"}] }
messages = {'model': "deepseek-chat", 'messages': [{'role': 'user', 'content': "write 50 random different English names and return in json format, each name must have a first name and a family name, middle name is optional, like {'names': ['Sophia Smith', 'Olivia Jeff', 'Mia Brown', ...]}"}] }
from openai import OpenAI
client = OpenAI(api_key="sk-proj-",)
unique_names = set()
tims = 0
while len(unique_names) < 2000 and tims < 100:
        try:
                response = client.chat.completions.create(**messages)
                res = response.choices[0].message.content
                print(res)
                res_dict = eval(res)
                names = res_dict['names']
                unique_names = (unique_names | set(names))
                print(f'{tims}: a llm call finished, num of unique names is {len(unique_names)}')
                tims +=1
        except Exception as e:
                print('Error:', e)
                pass

with open('unique_names.json', 'w') as f:
        json.dump(list(unique_names), f, indent=4)


# async def main():

#     caller = GPT35Caller()
#     llm_task = asyncio.create_task(caller.ask(content))

#     llm_task.add_done_callback(lambda task: print(task.result()))
#     await llm_task
    
# asyncio.run(main())