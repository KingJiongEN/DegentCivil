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

@register(name='EMOTION', type="state")
class EmotionState(BaseState):
    
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,
                 on_change_state,
                 followed_states=[CharacterState.ACTREFLECTION, CharacterState.BARGAIN, CharacterState.PERSP],
                 main_prompt = PromptType.EMOTION,
                 state_name = CharacterState.EMOTION,
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
        self.enter_state_chain.add(self.retrieve_prev_emotions, 0)
        self.enter_state_chain.add(self.retrieve_external_obs, 1)
        self.enter_state_chain.add(self.retrieve_world_understanding, 2)
        self.enter_state_chain.add(self.retrieve_interaction_history, 3)
        self.post_llm_call_chain.add(self.save_emotions, 1)
        self.post_llm_call_chain.add(self.update_numerical_impression, 2)
         
    def save_emotions(self, result):
        # save emotions
        self.character.emotion.update(result['emotions'])
        return False, dict()
    
    def update_numerical_impression(self, result):
        '''
        update numerical impression of favorability
        '''
        emotions = result['emotions']
        agent = self.character_list.get_character_by_name(self.get_character_wm_by_name('act_obj'))
        if agent is not None and type(agent) is Character:
            affact_change = 0 
            for emo in emotions:
                if emo['emotion'] in self.character.emotion.positive_emotions:
                    affact_change += emo['change']
                elif emo in self.character.emotion.negative_emotions:
                    affact_change -= emo['change']
            self.character.longterm_memory.update_people_numerical_memory(value_change=affact_change, name=self.get_character_wm_by_name('act_obj'))
            
        return False, dict()
     
    def retrieve_interaction_history(self, *args, **kwargs):
        act_obj = self.get_character_wm_by_name('act_obj')
        obj_agent = self.get_agent_by_name(act_obj)
        
        return False, {"history": self.character.retrieve_modify_dialogue(obj_agent)}
         

    def retrieve_external_obs(self, *args, **kwargs):
        '''
        request external and internal status 
        '''
        # TODO data structure 
        test_obs = {
            "building":
                {
                    "ABC_Cafe": "The cafe is crowed.",
                },
            "people":
                {
                    "David": "David is drinking a cup of beer at the bar.",
                    "Jim": "Jim is taking a beef."
                }
        }
        
        return False, {"external_obs": test_obs}

    def retrieve_world_understanding(self, external_obs):
        # TODO retrieve more relevant knowledge
        knowledge_dict = {}
        for main_k, main_v in external_obs.items(): 
            #{building: {name: obs}}
            knowledge_dict[main_k] = {}
            for k, v in main_v.items():
                # {name: obs}
                knowledge = self.character.longterm_memory.get_memory(main_k,k)
                knowledge_dict[main_k][k] = knowledge
        
        return False, {"world_understanding": knowledge_dict}
    
    def retrieve_prev_emotions(self, ):
        return False, {"prev_emotion": self.character.emotion.impression}
    
    def build_prompt(self, prev_emotion, world_understanding, history):
        prompt = None
        perception = {
            "prev_emotion": prev_emotion,
            "world_understanding": world_understanding,
            "history": history,
            "emotion_options": self.character.emotion.emotional_options
            }
        if self.prompt_type:
            prompt = self.prompt_class.create_prompt(perception)
            
        return  False, {"prompt": prompt}
    
        
    def state_router(self, **kwargs):
        if self.previous_state in [CharacterState.SUM, CharacterState.MOVE]: # TODO: Judge condition may not the CharacterState class, confirm it.
            return self.turn_on_states(CharacterState.ACTREFLECTION)
        elif self.previous_state == CharacterState.APPRECIATE:
            # TODO: design the router for PERSP and BARGAIN
            return self.turn_on_states(CharacterState.BARGAIN)
        else:
            return self.turn_on_states()
    
    def push_attr_change_to_server(self, **kwargs):
       
        if "monologue_emotion" in self.character.inner_monologue.content.keys() and "emoji" in self.character.inner_monologue.content.keys():
            emo = random.sample([self.character.inner_monologue.content["monologue_emotion"], self.character.inner_monologue.content["emoji"]], 1)[0]
            msg = {
                'content': f'{emo}',
                'agent_guid': self.character.guid,
                'content_type': 1,
                'display_duration': 3
            }
        else:
            msg = {
                'content': f' Feeling {self.character.emotion.extreme_emotion_name}',
                'agent_guid': self.character.guid,
                'content_type': 1,
                'display_duration': 3
            }
        msg = f"1002@{json.dumps(msg)}"

        add_msg_to_send_to_game_server(msg)
        sleep(3)
        return False, dict()
    
    def push_state_change_to_server(self, **kwargs):
        super().push_state_change_to_server()
        
        msg = {
            'content' : f'emotional turmoil happens to {self.character.name}',
            'agent_guid' : self.character.guid,
            'content_type': 2,
            'display_duration': 1000
        }
        msg = f"1002@{json.dumps(msg)}"
        add_msg_to_send_to_game_server(msg)
        return False, dict()
        
            

