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


from diskcache import Cache
from ...utils.log import LogManager
from autogen.agentchat.contrib.img_utils import _to_pil, get_image_data
from PIL import Image
import os
import asyncio

@register(name='APPRECIATE', type="state")
class AppreciateState(BaseState):
    
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,
                 on_change_state,
                 followed_states=[CharacterState.EMOTION],
                 main_prompt = PromptType.APPRECIATE,
                 state_name = CharacterState.APPRECIATE,
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
        self.prompt_type = PromptType.APPRECIATE
        self.enter_state_chain.add(self.retrieve_external_obs, 0)
        self.enter_state_chain.add(self.retrieve_knowledge, 1)
        self.enter_state_chain.add(self.retrieve_emotion, 2)
        self.enter_state_chain.add(self.retrieve_preferenced_art, 3)
        self.enter_state_chain.add(self.get_img, 4)
        # self.default_client = ['gpt-4-vision-preview']
         
    def enter_state(self):
        super().enter_state()
            
    def exit_state(self):
        super().exit_state()
    
    # def call_llm(self, prompt, prompt_type: PromptType):
    #     # send message from character to appreciate_agent
    #     self.character._prepare_chat(recipient=self.character.appreciate_agent,clear_history=True)
    #     self.character.appreciate_agent._process_received_message(prompt, sender=self.character, silent=True)
    #     self.llm_task = asyncio.create_task(self.character.appreciate_agent.a_generate_reply(sender=self.character))
    #     return False, dict()
    
    def retrieve_external_obs(self, *args, **kwargs):
        '''
        request external and internal status 
        '''
        ext_obs = {
            "people":
                {},
        }
        
        percepted_chars = self.character_list.perspect_surrounding_char(self.character)
        for char in percepted_chars:
            ext_obs["people"][char.name] = f'{char.name} is {char.state} with {char.working_memory.retrieve_by_name("act_obj") if char.working_memory.retrieve_by_name("act_obj") else "no one"}'
             
        in_building = self.character.in_building
        if in_building:
            building_status = { in_building.name : in_building.description} # TODO: dynamic building status
            ext_obs["building"] = building_status
            for eqp_n, eqp_v in in_building.equipments.items():
                ext_obs['building'].update( {eqp_n: eqp_v.status})
        
        # process pre most discrepancy
        pre_disc = self.character.working_memory.retrieve_by_name('MostDiscrepancy')
        if pre_disc:
            # if pre most discrepancy is in AnalyseExternalObservations, add it to obs to reanalysis the discrepancy
            if pre_disc['aspect'] == 'AnalyseExternalObservations':
                category = pre_disc['perception']['category']
                object = pre_disc['perception']['object']
                pre_description = pre_disc['perception']['description']
                ext_obs[category][object] = pre_description
        
        # FIXME: need to get the image id from proper place
        image_id = self.get_character_wm_by_name("img_id")
        img_url = self.get_character_wm_by_name("img_url")
        return False, {"external_obs": ext_obs, "img_id": image_id, "img_url": img_url}
    
    def get_img(self, img_id, img_url):
        img_data = _to_pil(get_image_data(img_url))
        smaller_img = img_data.resize((128, 128), Image.Resampling.LANCZOS)
        tmp_img_path = os.path.join(os.getcwd(), ".cache", f"img{img_id}.png")
        smaller_img.save(tmp_img_path)
        return False, {"artwork": f"<img {tmp_img_path}>"}

    def retrieve_knowledge(self, external_obs):
        # TODO retrieve more relevant knowledge
        knowledge_dict = {}
        for main_k, main_v in external_obs.items(): 
            #{building: {name: obs}}
            knowledge_dict[main_k] = {}
            for k, v in main_v.items():
                # {name: obs}
                knowledge = self.character.longterm_memory.get_memory(main_k,k)
                knowledge_dict[main_k][k] = knowledge
        
        return False, {"world_model": knowledge_dict}
    
    def retrieve_emotion(self, ):
        # TODO: implement emotion module
        return False, {"emotion": self.character.emotion}
    
    def retrieve_preferenced_art(self, ):
        preferenced_art = self.character.art_preference.favorite_arts
        return False, {"preferenced_art": preferenced_art}
    
    def build_prompt(self, world_model, external_obs, emotion, preferenced_art, artwork):
        prompt = None
        perception = {
            "name": self.character.name,
            "world_model": world_model, 
            "external_obs": external_obs,
            "emotion": emotion,
            "preferenced_art": preferenced_art,
            "artwork": artwork
            }
        if self.prompt_type:
            prompt = self.prompt_class.create_prompt(perception)
            
        return  False, {"prompt": prompt}
    
    def tailor_response_to_wm(self, result):
        resource_id = self.get_character_wm_by_name("img_id")
        self.character.working_memory.store_memory("appreciate_id", resource_id)
        if resource_id:
            image = self.character.drawings.get(resource_id)
            if image: # the artwork belongs to the character self
                image.set_price(result.get("estimate_art_value", 1000))
        super().tailor_response_to_wm(result)
        return False, dict()

    def state_router(self):
        resource_id = self.get_character_wm_by_name("img_id")
        return self.turn_on_states(CharacterState.EMOTION)
        # return self.turn_on_states() # TODO: need to implement the logic of the state router 
        if self.character.drawings.get(resource_id) is not None: # the drawing belongs to the character self
            # image = self.character.drawings.get(resource_id)
            return self.turn_on_states(CharacterState.PERSP)
        else: # the drawing belong to another character, bargain
            return self.turn_on_states(CharacterState.BARGAIN)
    
    def push_state_change_to_server(self, **kwargs):
        super().push_state_change_to_server()

        msg = {
            'content': f'{self.character.name} is appreciating the artwork.',
            'agent_guid': self.character.guid,
            'content_type': 2,
            'display_duration': 1000
        }
        msg = f"1002@{json.dumps(msg)}"
        add_msg_to_send_to_game_server(msg)
        return False, dict()
            