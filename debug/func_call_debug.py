from functools import partial
from typing import Literal

from pydantic import BaseModel, Field
from typing_extensions import Annotated

import autogen
from autogen.cache import Cache
import asyncio
from pathlib import Path
import sys
sys.path += [str(Path(__file__).resolve().parent.parent), './', '../']
import os
from app.models.character import Character
from app.service.simulation import Simulation
from autogen import config_list_from_json
from config import building_data_table, character_data_table
from random import random


async def main():
    config_list = autogen.config_list_from_json(
        "OAI_CONFIG_LIST",
        file_location='config',
        filter_dict={
            "model": ["gpt-4-0125-preview", "gpt-3.5-turbo", "gpt-3.5-turbo-16k"],
        },
    )

    llm_config = {
        "config_list": config_list,
        "timeout": 120,
    }

    chatbot = autogen.AssistantAgent(
        name="chatbot",
        system_message="Here your can play the Roulette. Make your prediction about the final landing position of the ball, particularly red or black. And place your bet. If your prediction is right, your bet will be doubled, otherwise, you lose all your bet.",
        llm_config=llm_config,
    )

    character = autogen.AssistantAgent(
        name="Allen",
        system_message="A solicitor in a small town, like gambling",
        llm_config=llm_config,
    )

    # create a UserProxyAgent instance named "user_proxy"
    user_proxy = autogen.UserProxyAgent(
        name="user_proxy",
        system_message="For currency exchange tasks, only use the functions you have been provided . Reply TERMINATE when the task is done.",
        is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
        human_input_mode="NEVER",
        max_consecutive_auto_reply=10,
        code_execution_config={'use_docker': False},
        llm_config=llm_config,
    )

    character_dict = list(character_data_table.values())[0]
        
    llm_cfg = Simulation.load_llm_config()['char_llm_cfg']
    char = Character( name=character_dict["name"],
                        guid=1,
                        age=character_dict["age"],
                        bio=character_dict["bio"],
                        goal=character_dict["goal"],
                        llm_cfg=llm_cfg,
                        health=100,
                        money=100,
                        staiety=2,
                        x=30,
                        y=30,
                        ) 

    PRDSYM = Literal["RED", "BLACK"]


    def Roulette(agent:Character, bet:float , prediction:PRDSYM) -> float:
        if float(agent.Gold) < bet:
            return {
                'result':0, 
                'response': f'Sorry, You only have {agent.Gold}. You can not bet more money than you have.'
                }
        if random() <0.5 and prediction == 'RED':
            return {
                'result':1, 
                'response': (getattr(agent, 'money', 0), bet)
                }
        
        elif random() > 0.5 and prediction == 'BLACK':
            return {
                'result':1, 
                'response': (getattr(agent, 'money', 0), bet)
                }
            
        else:
            return {
                'result':1, 
                'response': (getattr(agent, 'money', 0), -bet)
                }
            
            
    executor = char
    caller = chatbot

    # @executor.register_for_execution()
    # @caller.register_for_llm(description="Roulette simulator.")
    def currency_calculator(
        bet: Annotated[float, "Amount of bet"],
        prediction: Annotated[PRDSYM, "The color the player bet on. Black or Red."],
    ) -> str:
        result = Roulette(executor, bet, prediction)
        if result['result']:
            current_money, quote_amount = result['response']
            expression = "You win " if quote_amount>0 else "You lose "
            return f'{expression} {abs(quote_amount)}, now your money is {current_money + quote_amount}'
        else:
            return result['response']

    autogen.agentchat.register_function(
        currency_calculator,
        caller=caller,
        executor=executor,
        description="Roulette simulator.",
    )

    print(caller.llm_config["tools"])
    
    del executor.function_map['currency_calculator']

    
    llm_task = asyncio.create_task(caller.a_initiate_chat(
                                    executor,
                                    message="Here your can play the Roulette. Make your prediction about the final landing position of the ball, particularly red or black. And place your bet. If your prediction is right, your bet will be doubled, otherwise, you lose all your bet.",
                                ))

    # llm_task.add_done_callback(lambda task: print(task.result()))
    await llm_task
    
asyncio.run(main())