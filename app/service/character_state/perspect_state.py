import asyncio
import copy
import os
from .base_state import BaseState
from .register import register
from ...constants import CharacterState, PromptType
from ...models.location import BuildingList
from ...models.character import Character, CharacterList


@register(name='PERSP', type="state")
class PerspectState(BaseState):
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,
                 on_change_state,
                 state_name: str = CharacterState.PERSP,
                 main_prompt=PromptType.PERSPECT,
                 followed_states=[CharacterState.PLAN, CharacterState.ACT, CharacterState.EMOTION],
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
    
        self.enter_state_chain.add(self.request_perception, 1)
        self.enter_state_chain.add(self.retrieve_knowledge, 2)
        self.post_llm_call_chain.add(self.add_internal_perception, 1)
         
    def request_perception(self, *args, **kwargs):
        '''
        request external and internal status 
        '''
        
        # TODO data structure 
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
                if eqp_v.interactable:
                    ext_obs['building'].update( {eqp_n: eqp_v.status})
        
        # process pre most discrepancy
        pre_disc = self.get_character_wm_by_name('MostDiscrepancy')
        if pre_disc:
            # if pre most discrepancy is in AnalyseExternalObservations, add it to obs to reanalysis the discrepancy
            try:
                if pre_disc['aspect'] == 'AnalyseExternalObservations':
                    category = pre_disc['perception']['category']
                    object = pre_disc['perception']['object']
                    pre_description = pre_disc['perception']['description']
                    ext_obs[category][object] = pre_description
            except:
                pass
            # if pre most discrepancy is AnalyseInternalPerceptions, it will be automatically added to the obs to reanalysis the discrepancy
            # if pre most discrepancy is AnalysePlanAction, not need to be reanalysed
         
        return False, {"external_obs": ext_obs}

        
    def retrieve_knowledge(self, external_obs):
        # TODO retrieve more relevant knowledge
        knowledge_dict = {}
        for main_k, main_v in external_obs.items(): 
            #{building: {name: obs}}
            if main_k in ['building', 'people']:
                knowledge_dict[main_k] = {}
                for k, v in main_v.items():
                    # {name: obs}
                    knowledge = self.character.longterm_memory.get_memory(main_k,k)
                    memos = self.retrieve_memory(obj_name=k, text=v)  
                    ttl_mem = knowledge + memos
                    knowledge_dict[main_k][k] = ttl_mem if ttl_mem else None
        
        return False, {"world_model": knowledge_dict}
    
    
    def build_prompt(self, world_model, external_obs):
        if not self.character.plan.is_none :
            plan_description = f'''your current plan is {self.character.plan}. '''
            if  PromptType.ACT in self.character.prompt_and_response.result_dict:
                plan_description =  plan_description + f"your previous action is {self.character.prompt_and_response.result_dict[PromptType.ACT][-1]} "
            if  self.get_character_wm_by_name('interaction_summary') is not None:
                plan_description =  plan_description + f"and the interaction_summary is {self.get_character_wm_by_name('interaction_summary')}. "
        else:
            plan_description = "you have no plan and relevant actions"
                         
        perception = {"world_model": world_model, "external_obs": external_obs, "plan_description": plan_description}
        
        prompt = self.prompt_class.create_prompt(perception)
        
        return False, {"prompt": prompt}
    
    def add_internal_perception(self, result):
        '''
        add internal perception to results
        '''
        AnalyseInternalPerceptions = []
        for prop in self.character.digital_internal_properties:
            value = getattr(self.character, prop)
            inner_persp = {
                "perception": {
                    "attribute": prop,
                    "value": value,
                },
                "difference_level": 10-  value,
            }
            if prop == 'satiety' and value < 5:
                inner_persp['perception']['word_understanding'] = "I am hungry. I need to eat more food."
            if prop == 'health' and value < 5:
                inner_persp['perception']['word_understanding'] = "Unhealthy status. I need to go to the hospital."
            if prop == 'vigor' and value < 4:
                inner_persp['perception']['word_understanding'] = "Low vigor. I need to recover the vigor."
            AnalyseInternalPerceptions.append(inner_persp)
        
        
        
        extreme_emotion_name = self.character.emotion.extreme_emotion_name
        extreme_emotion_value = self.character.emotion.extreme_emotion_value
        emo_persp = {
                "perception": {
                    "attribute": extreme_emotion_name,
                    "value": extreme_emotion_value,
                },
                "word_understanding": f"I am in a {extreme_emotion_name} status. I need to calm down.",
                "difference_level": abs(extreme_emotion_value-5),
            }
        AnalyseInternalPerceptions.append(emo_persp) 
        
            
        result['AnalyseInternalPerceptions'] = AnalyseInternalPerceptions
       
        return False, dict()
    
    def tailor_response_to_wm(self, result):
        '''
         if discrepancy level is higher than previous, update it, otherwise, plan.forward(), skip plan state and go to act state 
         
        "MostDiscrepancy":{
                    "aspect": "AnalysePlanAction",
                    "perception":{
                        "current_step": "go to the library to collect information about tables",
                        "previous_action": {"action": "USE", "act_obj": "library.counter", "purpose": "collect information about table physics"},
                        "interaction_summary": "Order a cup of coffee in library",
                    },
                    "word_understanding": "1) the library is a good place to collect information. 2) the interaction_summary did not realize the purpose of previous action.",
                    "difference_level": 9,
                }
        
        '''
        pre_disc = self.get_character_wm_by_name('MostDiscrepancy')
        # find the most discrepancy
        cur_discre_level = -1
        # # TODO: temperary solution, need to be updated
        # most_dis_info = dict(
        #     aspect="AnalyseInternalPerceptions",
        #     AnalyseInternalPerceptions=[{'perception': {'attribute': 'satiety', 'value': self.character.satiety}, 'word_understanding': 'I am fine', 'difference_level': 0}]
        # )
        for aspect, disc_ls in result.items():
            for disc in disc_ls: 
                assert 'difference_level' in disc, 'difference_level is not in the dict, your dict is: ' + str(disc)
                if disc['difference_level'] > cur_discre_level:
                    cur_discre_level = disc['difference_level']
                    most_dis_info = copy.deepcopy(disc)
                    most_dis_info['aspect'] = aspect
        self.character.working_memory.store_memory('MostDiscrepancy', most_dis_info)

                  
        if pre_disc and pre_disc['perception'] == most_dis_info['perception'] and\
              pre_disc['aspect'] == most_dis_info['aspect'] and \
            self.get_character_wm_by_name('step_complete') !=False:
            return False, {'continue_plan': True} # plan.forward(), followed state: act
        else:
            self.character.working_memory.store_memory('MostDiscrepancy', most_dis_info)
            return False, {'continue_plan': False} # followed state: plan
    
    def state_router(self, result, continue_plan): 
        # if discrepancy level is low, then skip plan state
        most_dis_info = self.get_character_wm_by_name('MostDiscrepancy')
        if continue_plan or most_dis_info['difference_level'] < 3 and (not self.character.plan.is_none): 
            current_step = self.character.plan.forward()
            self.character.working_memory.store_memory('current_step', current_step)
            return self.turn_on_states(CharacterState.ACT)
        elif not continue_plan:
            return self.turn_on_states(CharacterState.PLAN)
        
    def store_memory(self, result, text=None, scale_dict=None):
        if os.getenv('Milvus') :
            for aspect, disc_ls in result.items():
                for disc in disc_ls: 
                    assert 'difference_level' in disc, 'difference_level is not in the dict, your dict is: ' + str(disc)
                    if disc['difference_level'] >= 5:
                        if aspect == "AnalyseExternalObservations":
                            # if disc["perception"]["category"] == "building":
                            act_obj = disc["perception"]["object"]
                            obj_agent = self.get_agent_by_name(act_obj)
                            if obj_agent:
                                text = disc['perception']['description']
                                scale_dict = self.build_scale_dict(obj_agent, memory=text)
                                asyncio.create_task(self.insert_memory_item(result, text=text, scale_dict=scale_dict))

        return False, dict()
    
    def push_attr_change_to_server(self, **kwargs):
        import json
        from time import sleep
        from ...utils.gameserver_utils import add_msg_to_send_to_game_server
        if "monologue_understanding" in self.character.inner_monologue.content:
            msg = {
                'content' : f'{self.character.inner_monologue.content["monologue_understanding"]}',
                'agent_guid' : self.character.guid,
                'content_type': 1,
                'display_duration': 3
            }
            
            msg = f"1002@{json.dumps(msg)}"

            add_msg_to_send_to_game_server(msg)
            sleep(3)
        return super().push_attr_change_to_server(**kwargs)
    
    def push_state_change_to_server(self, **kwargs):
        import json
        from ...utils.gameserver_utils import add_msg_to_send_to_game_server
        # super().push_state_change_to_server(**kwargs)
        msg = {
            'content': f'{self.character.name} is perspecting the world',
            'agent_guid': self.character.guid,
            'content_type': 2,
            'display_duration': 1000,
        }
        msg = f"1002@{json.dumps(msg)}"

        add_msg_to_send_to_game_server(msg)
        return False, dict()
        