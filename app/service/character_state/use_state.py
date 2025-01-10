import asyncio
import json

from time import sleep
from ...utils.gameserver_utils import add_msg_to_send_to_game_server
from .base_state import BaseState
from ...constants import PromptType
from ...models.location import BuildingList, Building, InBuildingEquip
from ...models.character import Character, CharacterList, CharacterState
from ...utils.globals import RESOURCE_SEPARATOR
from ...repository.agent_repo import get_agent_from_db
from .register import register
import autogen
@register(name='USE', type="state")
class UseState(BaseState):
    '''
    use an equipment in a building.
    Change the digital internal properties of the character.
    '''
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,  on_change_state, 
                 followed_states=[CharacterState.SUM, CharacterState.APPRECIATE],
                 main_prompt = PromptType.USE,
                 state_name = CharacterState.USE,
                 enter_calls=None, 
                 exit_calls=None, 
                 update_calls=None, 
                 llm_calls=None,
                 post_calls=None,
                 arbitrary_obj = None,
                default_client = 'gpt-4-1106-preview-official', # only the official api supports func tool
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
                        default_client = default_client,
                        )
        # self.post_llm_call_chain.add(self.modify_property, 0 )
        self.exit_state_chain.add(self.restore_system_prompt, 0)
        self.exit_state_chain.add(self.del_inside_tool, 1)
        
    def register_inside_tools(self, in_bldng_equip:InBuildingEquip):
        # if in_bldng_equip.functions:
        #     # reset_executor(self.character)
        #     for func in in_bldng_equip.functions:
        #             autogen.agentchat.register_function(
        #                 func,
        #                 caller=self.building,
        #                 executor=self.character,
        #                 description=in_bldng_equip.name,
        #             )
        self.building.register_equip_functions(in_bldng_equip)
     
    def call_llm(self, prompt, prompt_type: PromptType):
        act_obj = self.get_character_wm_by_name('act_obj') 
        building: Building = self.building_list.get_building_by_name(act_obj.split(EQUIPSPLITER)[0])
        self.building = building
        in_bldng_equip: InBuildingEquip = building.equipments[act_obj]
        self.register_inside_tools(in_bldng_equip)
            
        init_message = building.equipment_instr(act_obj)
       
        self.character.update_system_message(self.character.system_message + f'You are ins {building.name}. \
            Your impression on this building is {self.character.longterm_memory.get_building_memory(building.name) }\
            You are operating {in_bldng_equip.name} in this building. If you want to stop, please say "TERMINATE" ')
        building.update_system_message(building.system_message + f' {self.character.name} is using {in_bldng_equip.name} in this building. \
                                       The characteristics of him/her is {self.character.internal_status } .') 
        self.llm_task = asyncio.create_task( building.a_initiate_chat(recipient=self.character,
                                            message = f'{init_message}, your are in {building.description}', 
                                           clear_history=True, )
                                            )

    def restore_system_prompt(self):
        self.character.update_system_message(self.character.build_sys_message())
        self.building.update_system_message(self.building.build_sys_message())
        return False, dict()
    
    def del_inside_tool(self):
        act_obj = self.get_character_wm_by_name('act_obj') 
        # building: Building = self.building_list.get_building_by_name(act_obj.split(EQUIPSPLITER)[0])
        in_bldng_equip: InBuildingEquip = self.building.equipments[act_obj]
        if in_bldng_equip.functions:
            for func in in_bldng_equip.functions: # corre
                if func.__name__ in self.character.function_map:
                    del self.character.function_map[func.__name__]
                self.building.clean_equipment_functions(in_bldng_equip)
        return False, dict()
    
    
    def push_attr_change_to_server(self, **kwargs):
        obj = self.character.working_memory.retrieve_by_name('act_obj')
        msg = {
            'content' : f'I interacted with {obj}',
            'agent_guid' : self.character.guid,
            'content_type': 1,
            'display_duration': 3
        }
        msg = f"1002@{json.dumps(msg)}"

        add_msg_to_send_to_game_server(msg)
        sleep(3)
        return super().push_attr_change_to_server()
    
    def push_state_change_to_server(self, **kwargs):
        super().push_state_change_to_server()
        act_obj = self.character.working_memory.retrieve_by_name("act_obj")
        
        msg = {
            'content': f'{self.character.name} is interacting with {act_obj}',
            'agent_guid': self.character.guid,
            'content_type': 2,
            'display_duration': 1000
        }
        msg = f"1002@{json.dumps(msg)}"
        add_msg_to_send_to_game_server(msg)
        return False, dict()