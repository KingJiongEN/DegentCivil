import asyncio
from pathlib import Path
import sys
sys.path += [str(Path(__file__).resolve().parent.parent), './', '../']
import os
from app.models.character import Character
from app.service.simulation import Simulation
from autogen import config_list_from_json
from config import building_data_table, character_data_table
from app.utils.save_object import find_instance_specific_data_attrs
from app.database.base_database import init_db
content = ''' 
        This is a test message for you .
        '''



async def main():

    # config_list = config_list_from_json(
    #         "OAI_CONFIG_LIST",
    #         file_location='config',
    #         filter_dict={
    #             # "model": ["gpt-3.5-turbo-0125" ],# gpt-3.5-turbo-0125,gpt-4-1106-preview,gpt-4-32k ，"gpt-4-1106-preview"
    #             "model": ["gpt-4-0125-preview" ],# gpt-3.5-turbo-0125,gpt-4-1106-preview,gpt-4-32k ，"gpt-4-0125-preview"
    #         },
    #     )
    # llm_cfg = {"config_list": config_list,
    #                "seed": 3,
    #                "response_format": { "type": "json_object" },
    #                "temperature": 0.5
    #                }
    character_dict = list(character_data_table.values())[0]
    # init_db() 
    llm_cfg = Simulation.load_llm_config()['char_llm_cfg']
    print(llm_cfg[-1])
    agent = Character.decode_from_json(llm_cfg=llm_cfg[-1],is_multi_modal_agent=False, **{"guid": 6,
                                                      "name": "Liam Wilson",
                                                      "age": 42,
                                                      "bio": "Volunteer firefighter, outdoor adventurer",
                                                      "goal": "Save lives and protect nature",
                                                      "mbti": "ESFJ",
                                                      'health': 100,
                                                      'money': 100,
                                                      'staiety': 2,
                                                      'x': 30,
                                                      'y': 30,
                                                      'save_dir': 'tmp',})
    # agent = Character( name=character_dict["name"],
    #                   guid=1,
    #                     age=character_dict["age"],
    #                     bio=character_dict["bio"],
    #                     goal=character_dict["goal"],
    #                     llm_cfg=llm_cfg[-1],
    #                     town_id=1,
    #                     health=100,
    #                     money=100,
    #                     staiety=2,
    #                     x=30,
    #                     y=30,
    #                     save_dir='tmp',
    #                     # is_multi_modal_agent=False
    #                   )
    # agent2 = Character( name="Emma2",
    #                   guid=2,
    #                     age=character_dict["age"],
    #                     bio=character_dict["bio"],
    #                     goal=character_dict["goal"],
    #                     llm_cfg=llm_cfg,
    #                     town_id=1,
    #                     health=100,
    #                     money=100,
    #                     staiety=2,
    #                     x=30,
    #                     y=30,
    #                     save_dir='tmp',
    #                     # is_multi_modal_agent=False
    #                   )  
    # agent._oai_messages[agent] = [{'content': 
    #                                content, 'role': 'user'}]
   
    # ===== chat log test =======
    # llm_task = asyncio.create_task(agent.a_process_then_reply(message=content,sender=agent))
 
    # llm_task.add_done_callback(lambda task: print(task.result()))
    res = agent.process_then_reply(message=content, sender=agent)
    print(res)
    
    # await llm_task
    # agent.log_attrs()
    
    # ===== sql test ======
    # flag, res = agent2.handle_purchase_request(artwork_id="a8c50360-1405-4e9f-a300-1f25d80d7e53", price=100, sender=agent)
    # print(res)
    
    
    # ======= save and load test ==========
    # succes = agent.save_self_locally()
    # if succes:
    #     print(f'save in {succes}')
    #     agent2 = Character( name=character_dict["name"],
    #                   guid=1,
    #                     age=character_dict["age"],
    #                     bio=character_dict["bio"],
    #                     goal=character_dict["goal"],
    #                     llm_cfg=llm_cfg,
    #                     town_id=1,
    #                     health=100,
    #                     money=100,
    #                     staiety=2,
    #                     x=30,
    #                     y=30,
    #                     save_dir='tmp',
    #                     is_multi_modal_agent=True
    #                   ) 
    #     agent2.load_from_local(succes)
    #     print(agent2._oai_messages)
    
asyncio.run(main())