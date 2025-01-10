import copy
import os
import random
import json
from time import sleep
from ...utils.gameserver_utils import add_msg_to_send_to_game_server
from .base_state import BaseState
from .register import register
from ...communication.websocket_server import WebSocketServer
from ...constants import CharacterState
from ...models.location import BuildingList
from ...models.character import Character, CharacterList
from ...constants import PromptType


from ...utils.log import LogManager
from typing import Dict
import json
import asyncio

@register(name='DRAW', type="state")
class DrawState(BaseState):
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,
                 on_change_state,
                 followed_states=[CharacterState.APPRECIATE],
                 main_prompt = PromptType.DRAW,
                 state_name = CharacterState.DRAW,
                 enter_calls=None, 
                 exit_calls=None, 
                 update_calls=None, 
                 llm_calls=None,
                 post_calls=None,
                 arbitrary_obj=None,
                 arbitrary_wm=dict(),
                 ):
        super().__init__(character=character, 
                         main_prompt=main_prompt, 
                         character_list=character_list, 
                         building_list=building_list,
                         followed_states=followed_states,
                         on_change_state=on_change_state,
                         state_name=state_name,
                         llm_calls=llm_calls,
                         enter_calls=enter_calls, 
                        exit_calls=exit_calls, 
                        update_calls=update_calls, 
                        post_calls=post_calls,                       
                        arbitrary_obj=arbitrary_obj,
                        arbitrary_wm=arbitrary_wm,                       
                        )     
        self.post_llm_call_chain.add(self.push_state_to_game_server, 0)    
        self.post_llm_call_chain.add(self.link_drawing_to_gallery, 1)
    
    def call_llm(self, prompt, prompt_type: PromptType):
        self.llm_task = asyncio.create_task(self.character.drawing_agent.a_process_then_reply(message=prompt, sender=self.character.drawing_agent, restart=True)) 
    
    def push_state_to_game_server(self, result):
        msg = {'agent_guid': self.character.guid, 'url': f"nft/{result['img_id']}.png", 'artwork_id': result['img_id']}
        self.character.working_memory.store_memory('img_id', result['img_id'])
        return self.push_msg_to_game_server(msg)
        
    def exit_state(self):
        super().exit_state()
        
    def build_prompt(self):
        # prompt: Dict = self.character.get_latest_response(PromptType.DRAWINIT)
        # prompt = prompt.get("drawing_description", 'Randomly draw a picture like you are in a nightmare.')
        prompt = self.get_character_wm_by_name('drawing_description')
        return False, { "prompt": prompt }
   
    def tailor_response_to_wm(self, result):
        for ky in ['img_id', 'img_url']:
            self.character.working_memory.store_memory( ky, copy.deepcopy(result[ky]))
        return False, dict()
   
    
    def link_drawing_to_gallery(self, result):
        '''
        Deprecated, implemented by sql
        '''
        # agent can glance drawings at the gallery then appreciate one of them
        act_obj = self.get_character_wm_by_name('act_obj')
        obj_agent = self.get_agent_by_name(act_obj)
        assert obj_agent.name == 'Artwork', f' The agent should be using Artwork, but now it is using {obj_agent.name}'
        
        img_id = result['img_id']
        img_url = result['img_url']
        drawing = self.character.drawings.get(img_id)
        obj_agent.painting.append({"drawing": drawing.description, 
                                    "owner": drawing.owner.name, 
                                    "img_id": img_id, 
                                    "img_url":img_url, 
                                    "price": drawing.price})
        
        return False, dict()
    
    def push_state_change_to_server(self, **kwargs):
        super().push_state_change_to_server()

        msg = {
            'content': f'{self.character.name} is drawing',
            'agent_guid': self.character.guid,
            'content_type': 2,
            'display_duration': 1000
        }
        msg = f"1002@{json.dumps(msg)}"
        add_msg_to_send_to_game_server(msg)
        return False, dict()