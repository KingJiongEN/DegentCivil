import json
import os
import random
from app.models.boss_agent import Boss
from .base_state import BaseState
from ...constants import PromptType
from ...models.location import BuildingList, Building, InBuildingEquip
from ...models.character import Character, CharacterList, CharacterState
from .register import register
from ...constants import StateName2State
from ...utils.gameserver_utils import add_msg_to_send_to_game_server

@register(name='ACT', type="state")
class ActState(BaseState):
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,  on_change_state, 
                 followed_states=[CharacterState.USE, CharacterState.CHATINIT, CharacterState.MOVE, CharacterState.DRAWINIT],
                 main_prompt = PromptType.ACT,
                 state_name = CharacterState.ACT,
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
        
        self.enter_state_chain.add( self.request_candidate_actions, 0)
        self.post_llm_call_chain.add(self.push_state_to_game_server,0)
        
    def request_candidate_actions(self):
        candidate_acts = []
        
        for blg in self.building_list.buildings:
            if self.character.in_building and  blg.name == self.character.in_building.name:
                continue    
            blg_impression = self.character.longterm_memory.get_building_memory(blg.name)
            candidate_acts.append( {'action': "MOVE", 
                                    'act_obj': blg.name, 
                                    'obj_description': f'{blg.description}, personal impression: {blg_impression}' 
                                    } )
        
        percepted_chars = self.character_list.perspect_surrounding_char(self.character)
        for char in percepted_chars:
            char_impression = self.character.longterm_memory.get_people_memory(char.name)
            candidate_acts.append( {'action': "CHATINIT", 
                                    'act_obj': char.name, 
                                    'obj_description': f' personal impression: {char_impression}' 
                                    } )
            
        if self.character.in_building:
            jobs = self.character.in_building.occupied_jobs
            for job in jobs:
                for employee in job.applicants:
                    candidate_acts.append( {'action': "CHATINIT", 
                            'act_obj': employee.name,
                            'occupation': job.name, 
                            'obj_description':
                                f' personal impression: {self.character.longterm_memory.get_people_memory(employee.name)}' 
                            } )
                    
            equips = self.character.in_building.equipments
            for eq_n, eq_v in equips.items():
                if eq_v.interactable:
                    candidate_acts.append( {'action': eq_v.interactable, 
                                            'act_obj': eq_n, 
                                            'obj_description': f' {eq_v.instruction}' 
                                            } )
            # candidate_acts.append( {'action': "CHATINIT",
            #                         'act_obj': self.character.in_building.name,
            #                         'obj_description':
            #                             f' personal impression: {self.character.longterm_memory.get_building_memory(self.character.in_building.name)}' 
            #                         })
        # random.shuffle(candidate_acts)
        return False, {"candidate_acts": candidate_acts}
    
    def build_prompt(self, candidate_acts):
        
        prompt = self.prompt_class.create_prompt(candidate_acts=candidate_acts) 
                                            
        return  False, {"prompt": prompt}
    
    
    def state_router(self, result):
        next_state_str = result['action']
        next_state = StateName2State[next_state_str]
        assert next_state in self.followed_states, f" {next_state} not in {self.followed_states.keys()} ! Your choice is strictly limited to the candidate actions."
        assert self.get_agent_by_name(self.get_character_wm_by_name('act_obj') ) is not None, f"act_obj_name {self.get_character_wm_by_name('act_obj')} not exists ! Your choice is strictly limited to the candidate actions."
        return  self.turn_on_states(next_state)

    def push_state_to_game_server(self,result):
        '''
            this.pos = pos;
            this.agent_guid = agent_guid;
            this.speed_rate = speed_rate;
            this.emoji_on_the_way = emoji_on_the_way;
            this.emoji_interval = emoji_interval;
            this.emoji_show_duration = emoji_show_duration;
            this.song = song`;
        '''
        if result['action'] == "MOVE": # handle the move action in move state
            return False, dict()
        act_obj = result['act_obj']
        act_agent = self.get_agent_by_name(act_obj)
        if type(act_agent) in (Character, Boss): # LLM_MSG_WALK_TO
            msg = {
                "pos": {'x': int(act_agent.x), 'y': int(act_agent.y)}, 
                "agent_guid": self.character.guid,
                "speed_rate": 4,
                "emoji_on_the_way": self.get_character_wm_by_name('emoji'),
                "emoji_interval": 1,
                "emoji_show_duration": 2,
                "song": "agent_song_on_walk2"

            }
            msg = f'1007@{json.dumps(msg)}'
        elif type(act_agent) == InBuildingEquip: # LLM_MSG_WALK_TO_DO
            msg = {
                "target_place_guid": act_agent.random_choose(), # TODO: need to change the name of the building 
                "agent_guid": self.character.guid,
                "speed_rate": 4,
                "emoji_on_the_way": self.get_character_wm_by_name('emoji'),
                "emoji_interval": 1,
                "emoji_show_duration": 2,
                "song": "agent_song_on_walk1"

            } 
            msg = f"1001@{json.dumps(msg)}"
        else:
            if os.getenv('DEBUG'):
                __import__('ipdb').set_trace()
            return False, dict()
        
        add_msg_to_send_to_game_server(msg)
        return False, dict() 
    
    def push_attr_change_to_server(self, **kwargs):
        action = self.character.working_memory.retrieve_by_name("action")
        act_obj = self.character.working_memory.retrieve_by_name("act_obj")
        if action in ["USE"]:
            msg = {
                'content': f'{self.character.name} will interact with {act_obj}',
                'agent_guid': self.character.guid,
                'content_type': 2,
                'display_duration': 3
            }
            msg = f"1002@{json.dumps(msg)}"
            add_msg_to_send_to_game_server(msg)
            
        elif action in ["MOVE"]:
            msg = {
                'content': f'{self.character.name} is going to {act_obj}',
                'agent_guid': self.character.guid,
                'content_type': 2,
                'display_duration': 3
            }
            msg = f"1002@{json.dumps(msg)}"
            add_msg_to_send_to_game_server(msg)
        return False, dict()
    
    def push_state_change_to_server(self, **kwargs):
        import json
        super().push_state_change_to_server(**kwargs)
        msg = {
            'content': f'{self.character.name} is thinking about what to do next',
            'agent_guid': self.character.guid,
            'content_type': 2,
            'display_duration': 1000
        }
        msg = f"1002@{json.dumps(msg)}"

        add_msg_to_send_to_game_server(msg)
        return False, dict()