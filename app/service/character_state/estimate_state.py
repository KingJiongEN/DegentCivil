import random
import os

from .base_state import BaseState
from .register import register
from ...communication.websocket_server import WebSocketServer
from ...constants import CharacterState
from ...models.location import BuildingList
from ...models.character import Character, CharacterList
from ...constants import PromptType


@register(name='ESTIMATE', type="state")
class EstimateState(BaseState):
    
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,
                 on_change_state,
                 followed_states=[CharacterState.PERSP],
                #  followed_states=[CharacterState.PLAN, CharacterState.ACT, CharacterState.DRAWINIT],
                 main_prompt = PromptType.ESTIMATE,
                 state_name = CharacterState.ESTIMATE,
                 enter_calls=None, 
                 exit_calls=None, 
                 update_calls=None, 
                 llm_calls=None,
                 post_calls=None,
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
                        )
        self.enter_state_chain.add(self.retrieve_market_price, 0)
        self.enter_state_chain.add(self.retrieve_appreciation, 1)
        self.enter_state_chain.add(self.retrieve_trade_record, 2)
    
    def retrieve_market_price(self, *args, **kwargs):
        basic_price = random.randint(100, 1000)
        return False, {"basic_price": basic_price}
    
    def retrieve_appreciation(self, ):
        like_score = self.character.working_memory.retrieve_by_name("like_score")
        if not like_score:
            like_score = random.randint(6, 10)
        return False, {"like_score": like_score}
    
    def retrieve_trade_record(self, basic_price, like_score):
        # build the query text
        # query text should match trade record format as similar as possible
        resource_id = self.character.working_memory.retrieve_by_name("resource_id")
        seller = self.character.working_memory.retrieve_by_name("seller")
        query = f'[resource_id]: {resource_id}\n[seller]: {seller}\n[market_price]: {basic_price}\n[emotion]: {self.character.emotion.extreme_emotion}\n[like score]: {like_score}'
        records = []
        if os.getenv('Milvus'):
            records = self.character.longterm_memory.buyer_specific_memory_retrieve_from_milvus(obj_name=self.character.name, query=query)
        else:
            # FIXME: remove records ref below
            records = [
                "[seller]: Emma Smith\n[remaining_budget]: 4400\n[market_price]: 1000\n[emotion]: {'joy': 6, 'trust': 9, 'fear': 6, 'surprise': 4, 'sadness': 6, 'disgust': 4, 'anger': 4, 'anticipation': 7}\n [like score]: 6\n[expected_price]: 1000\n[final_price]: 950",
                "[seller]: Jasper Hale\n[remaining_budget]: 3700\n[market_price]: 1800\n[emotion]: {'joy': 9, 'trust': 7, 'fear': 4, 'surprise': 7, 'sadness': 4, 'disgust': 4, 'anger': 4, 'anticipation': 5}\n [like score]: 9\n[expected_price]: 2500\n[final_price]: 2700",
                "[seller]: Alice Cullen\n[remaining_budget]: 3200\n[market_price]: 2000\n[emotion]: {'joy': 6, 'trust': 8, 'fear': 4, 'surprise': 7, 'sadness': 4, 'disgust': 4, 'anger': 4, 'anticipation': 5}\n [like score]: 7\n[expected_price]: 2200\n[final_price]: 2000",
                "[seller]: Edward Cullen\n[remaining_budget]: 10000\n[market_price]: 1500\n[emotion]: {'joy': 6, 'trust': 6, 'fear': 4, 'surprise': 8, 'sadness': 4, 'disgust': 4, 'anger': 4, 'anticipation': 6}\n [like score]: 7\n[expected_price]: 1400\n[final_price]: 1500",
            ]
        return False, {"records": records}
    
    def build_prompt(self, basic_price, like_score, records):
        prompt = None
        kwargs = {
            "emotion": self.character.emotion.impression,
            "basic_price": basic_price,
            "like_score": like_score,
            "budget": self.character.Gold,
            "history": records if len(records) > 0 else "no history"
        }
        prompt = self.prompt_class.create_prompt(kwargs)
        return False, {"prompt": prompt}