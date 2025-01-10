import os
import random
import json
from time import sleep
from ...utils.gameserver_utils import add_msg_to_send_to_game_server
from ...constants import State2RecieveMsgId
from .base_state import BaseState
from .register import register
from ...communication.websocket_server import WebSocketServer
from ...constants import CharacterState
from ...models.location import BuildingList, Building
from ...models.character import Character, CharacterList
from ...utils.log import LogManager

@register(name='MOVE', type="state")
class MoveState(BaseState):
    target_x: int
    target_y: int

    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,
                 on_change_state,
                 followed_states=[CharacterState.PERSP, CharacterState.EMOTION],
                 main_prompt = None,
                 state_name = CharacterState.MOVE,
                 enter_calls=None, 
                 exit_calls=None, 
                 update_calls=None, 
                 llm_calls=None,
                 post_calls=None,
                 arbitrary_obj=None,
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
                        )     
        self.enter_state_chain.add( self.push_state_to_game_server, 1) 
        self.enter_state_chain.add( self.reset_plan_step, 2) 
        self.exit_state_chain.add(self.reset_ismoving, 0)
        self.is_moving = False
        
       
    def handle_server_msg(self, msg):
        # arrive at the new place
        msg = json.loads(msg)
        assert all( k in msg.keys() for k in ['agent_guid', 'cur_place_guid', 'cur_area', 'cur_pos'] ), 'The msg should contain agent_guid, cur_place, cur_area, cur_pos, your msg is: ' + str(msg)
        agent_guid = int(msg['agent_guid'])
        if agent_guid != self.character.guid:
            return False, dict()
        cur_place = msg['cur_place_guid']
        cur_area = msg['cur_area']
        cur_pos_x = msg['cur_pos']['x']
        cur_pos_y = msg['cur_pos']['y']
        self.turn_on_states()
        self.character.change_pos(cur_pos_x, cur_pos_y)
        self.change_char_building()
        if self.get_character_wm_by_name('step_complete') is not None:
            self.character.working_memory.store_memory('step_complete', True)    
        return False, dict() 

    # debug version for running locally
    # def monitor_server_msg(self, msg=None):
    #     if not msg and os.getenv("DEBUG"):
    #         building_name = self.character.working_memory.retrieve_by_name("act_obj")
    #         in_building = self.building_list.get_building_by_name(building_name)
    #         cur_pos_x, cur_pos_y = (in_building.xMin + in_building.xMax)/2, (in_building.yMin + in_building.yMax)/2
    #         self.turn_on_states()
    #         self.character.change_pos(cur_pos_x, cur_pos_y)
    #         self.character.change_building(in_building)
    #         if self.character.working_memory.retrieve_by_name('step_complete') is not None:
    #             self.character.working_memory.store_memory('step_complete', True)  
    #         return False, dict()
          
    #     elif int(msg['msg_id']) == int(State2RecieveMsgId.get(self.state_name, 0)):
    #         msg = msg['msg']
    #         return self.handle_server_msg(msg)

    def speed_rate(self):
        return 1

    def get_target_pos(self):
        act_obj = self.character.working_memory.retrieve_by_name('act_obj')
        # if self.building_list.get_building_by_name(act_obj) is not None: 
        #     return act_obj +'_Entrance'
        # else: # inbuilding equip , set in arbitary destination
        #     return act_obj
        obj_agent = self.get_agent_by_name(act_obj)
        assert type(obj_agent) is Building, f"act_obj should be a building, but got {act_obj}, { type(act_obj) }"
        (x, y) = obj_agent.random_pos_inside
        return {'x': x, 'y': y}

    def song_decision(self):
        if random.random() > 0.66:
            return "agent_song_on_walk3"
        elif random.random() > 0.33:
            return "agent_song_on_walk2"
        else:
            return "agent_song_on_walk1"

    def push_state_to_game_server(self):
        if self.is_moving: return False, dict()
        
        msg = { "pos": self.get_target_pos(), 
                "agent_guid": self.character.guid,
                "speed_rate": self.speed_rate(),
                "emoji_on_the_way": self.character.working_memory.retrieve_by_name('emoji'),
                "emoji_interval": 1.0,
                "emoji_show_duration": 1.0,
                "song": self.song_decision(),
                }
     
        if os.getenv('DEBUG'):
            self.character.change_building(self.building_list.get_building_by_name(self.get_character_wm_by_name('act_obj'))) 
            self.character.change_pos(self.building_list.get_building_by_name(self.get_character_wm_by_name('act_obj')).xMin, self.building_list.get_building_by_name(self.get_character_wm_by_name('act_obj')).yMin)
            self.turn_on_states()
        self.is_moving = True
        return self.push_msg_to_game_server(msg)
    
    def reset_plan_step(self):
        # Since MOVE->PERSP, and step_complete is used in PERSP, we need to reset it here
        if self.get_character_wm_by_name('step_complete') is not None:
            self.character.working_memory.forget_by_name('step_complete') # TODO: better wm forget,
        return False, dict() 
    
    def passive_update(self):
        self.character.satiety -= 0.1 * self.character.satiety_decay_rate
        self.character.satiety = max(0, self.character.satiety)
        return super().passive_update()
    
    def reset_ismoving(self):
        self.is_moving = False
        return False, dict()
        
    def check_attr_chage(self):
        if self.is_moving: return False, dict()
        return super().check_attr_chage()
    
    def push_state_change_to_server(self, **kwargs):
        return False, dict()
    
    def push_attr_change_to_server(self, **kwargs):
        super().push_attr_change_to_server()
        if "monologue_status" in self.character.inner_monologue.content.keys():
            try:
                msg = {
                    'content': self.character.inner_monologue.content["monologue_status"],
                    'agent_guid': self.character.guid,
                    'content_type': 1,
                    'display_duration': 3
                }
            except:
                msg = {
                    'content': f' I have moved to {self.get_character_wm_by_name("act_obj")}',
                    'agent_guid': self.character.guid,
                    'content_type': 1,
                    'display_duration': 3
                }
            msg = f"1002@{json.dumps(msg)}"

            add_msg_to_send_to_game_server(msg)
            sleep(3)
        return False, dict()
    
    