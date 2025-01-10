import json
from .base_state import BaseState
from .register import register
from ...constants import CharacterState, PromptType
from ...models.location import BuildingList
from ...models.character import Character, CharacterList
from ...utils.globals import RESOURCE_SEPARATOR
from ...utils.gameserver_utils import add_msg_to_send_to_game_server

@register(name='SUM', type="state")
class SummarizeState(BaseState):
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,
                 on_change_state,
                 followed_states=[CharacterState.EMOTION],
                 main_prompt = PromptType.SUM,
                 state_name = CharacterState.SUM,
                 enter_calls=None, 
                 exit_calls=None, 
                 update_calls=None, 
                 llm_calls=None,
                 post_calls=None,
                 description='Summarize the takeaway from the previous interaction. \
                 Modify the internal properties of the character.',
                 arbitrary_obj = None,
                arbitrary_wm = dict(),
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
                        description=description,
                         arbitrary_obj=arbitrary_obj,
                         arbitrary_wm=arbitrary_wm,  
                        )
        
        self.post_llm_call_chain.add(self.change_char_properties, 2 )
        
    def change_char_properties(self, result):
        modified_prop = result['modified_properties']
        for name, prop in modified_prop.items():
            stakeholder = self.get_agent_by_name(name)
            if stakeholder is None: continue # FIXME
            if 'job' in prop:
                building =  prop['job'].split(EQUIPSPLITER)[0] # TODO defined by string may have bugs
                job =  prop['job'].split(EQUIPSPLITER)[1]
                building_agent = self.building_list.get_building_by_name(building)
                job_obj = building_agent.job_positions.get(job,)
                assert building_agent is not None, f'building: {building} is not found in the building list'
                assert job_obj is not None, f'job: {job} is not found in the building: {building}'
                prop['job'] = job_obj 
            if 'agenda' in prop:
                if type(prop['agenda']) is list:
                    for agenda in prop['agenda']:
                        assert 'specific_date' in agenda and 'event' in agenda, f'each agenda is a dict, must have specific_date and event as keys. Your agenda.agenda: {prop["agenda"]}'
                elif type(prop['agenda']) is dict:
                    assert 'specific_date' in prop['agenda'] and 'event' in prop['agenda'], f'the agenda is a dict, must have specific_date and event as keys. Your agenda.agenda: {prop["agenda"]}'
                else: 
                    AssertionError('agenda should be a list or a dict, your agenda.agenda: {prop["agenda"]}')
            stakeholder.modify_internal_properties(prop)
            
        # self.push_msg_to_game_server({
        #     'content' : f'{self.character.name} changed attr',
        #     'agent_guid' : self.character.guid,
        #     'duration' : 1,
        #     'attr_chagne' : result['modified_properties'],
        # })
        return False, dict()
    
    def get_act_stakeholders(self) -> list[Character]:
        '''
        return stakeholders of the current action, including the character itself, act_obj and interactable objects
        '''
        act_obj_name = self.get_character_wm_by_name('act_obj')
        act_obj_agent = self.get_agent_by_name(act_obj_name)    
        if EQUIPSPLITER in act_obj_name:
            act_bldg_agent = self.get_agent_by_name(act_obj_name.split(EQUIPSPLITER)[0])
            return [self.character, act_bldg_agent, act_obj_agent]
        else:
            return [self.character, act_obj_agent]
        # act_obj_agent = self.character_list.get_character_by_name(act_obj_name) 
        # if act_obj_agent is None: # TODO act_obj is a building or facility
        #     if EQUIPSPLITER in act_obj_name:
        #         building_name = act_obj_name.split(EQUIPSPLITER)[0]
        #         building = self.building_list.get_building_by_name(building_name) 
        #         act_obj_agent = building.equipments[act_obj_name] 
        #     else:
        #         act_obj_agent = self.building_list.get_building_by_name(act_obj_name) 
            
    
    
    def build_prompt(self):
        stake_holders = self.get_act_stakeholders()
        
        stake_holders_modifiable_properties = dict( (obj.name, obj.modifiable_status) for obj in stake_holders)
       
        prompt = self.prompt_class.create_prompt(stake_holders_modifiable_properties=stake_holders_modifiable_properties) 
            
        return False, { "prompt": prompt}

    def push_state_change_to_server(self, **kwargs):
        super().push_state_change_to_server()
        act_obj = self.character.working_memory.retrieve_by_name("act_obj")
        
        msg = {
            'content': f'{self.character.name} is summarizing the takeaway from the previous interaction with {act_obj}',
            'agent_guid': self.character.guid,
            'content_type': 2,
            'display_duration': 1000
        }
        msg = f"1002@{json.dumps(msg)}"
        add_msg_to_send_to_game_server(msg)
        return False, dict()