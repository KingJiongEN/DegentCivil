import random

from .base_state import BaseState
from .register import register
from ...communication.websocket_server import WebSocketServer
from ...constants import CharacterState
from ...models.location import BuildingList
from ...models.character import Character, CharacterList
from ...constants import PromptType


from diskcache import Cache
from ...utils.log import LogManager
import asyncio

@register(name='DRAWINIT', type="state")
class DrawInitState(BaseState):
    
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,
                 on_change_state,
                 followed_states=[CharacterState.DRAW],
                 main_prompt = PromptType.DRAWINIT,
                 state_name = CharacterState.DRAWINIT,
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
        self.prompt_type = PromptType.DRAWINIT
        self.enter_state_chain.add(self.retrieve_external_obs, 0)
        self.enter_state_chain.add(self.retrieve_knowledge, 1)
        self.enter_state_chain.add(self.retrieve_emotion, 2)
        self.enter_state_chain.add(self.retrieve_preference_art, 3)
        self.enter_state_chain.add(self.get_impressive_event, 4) 
        
    def enter_state(self):
        super().enter_state()
        
    def retrieve_external_obs(self, *args, **kwargs):
        '''
        request external and internal status 
        '''
        # Copied from `PerspectState`
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
        
        return False, {"external_obs": ext_obs}

    def get_impressive_event(self):
        event, emotion = self.character.emotion.most_impressive_event
        return False, {"impressive_events": event}
        

    def get_impressive_event(self):
        event, emotion = self.character.emotion.most_impressive_event
        return False, {"impressive_events": event}
        

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
        emotion = self.character.emotion.extreme_emotion
        return False, {"emotion": emotion}
    
    def retrieve_preference_art(self, ):
        # TODO: design preference art form of characters
        return False, {"preference_art": self.character.art_preference.favorite_arts[0]}
    
    def build_prompt(self, world_model, external_obs, emotion, preference_art, impressive_events):
        prompt = None
        perception = {
            "name": self.character.name,
            "world_model": world_model, 
            "external_obs": external_obs,
            "emotion": emotion,
            "preference_art": preference_art,
            "impressive_events": impressive_events,
            }
        if self.prompt_type:
            prompt = self.prompt_class.create_prompt(perception)
            
        return  False, {"prompt": prompt}
