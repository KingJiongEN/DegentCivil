import os
import random

from app.repository.artwork_repo import get_artwork_from_db

from .base_state import BaseState
from .register import register
from ...communication.websocket_server import WebSocketServer
from ...constants import CharacterState
from ...models.location import BuildingList
from ...models.character import Character, CharacterList
from ...constants import PromptType
from ...models.trade import Trade


from diskcache import Cache
from ...utils.log import LogManager
import asyncio

@register(name='BARGAIN', type="state")
class BargainState(BaseState):
    
    def __init__(self, character: Character, character_list: CharacterList, building_list: BuildingList,
                 on_change_state,
                 followed_states=[CharacterState.EMOTION],
                 main_prompt = PromptType.BARGAIN,
                 state_name = CharacterState.BARGAIN,
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
        self.enter_state_chain.add(self.retrieve_impression, 0)
        self.enter_state_chain.add(self.retrieve_external_obs, 1)
        self.enter_state_chain.add(self.retrieve_knowledge, 2)
        self.enter_state_chain.add(self.retrieve_emotion, 3)
        self.enter_state_chain.add(self.retrieve_preference, 4)
        self.exit_state_chain.add(self.restore_system_prompt, 0)
    
    def enter_state(self):
        super().enter_state()
        
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
        
        return False, {"external_obs": ext_obs}

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
        return False, {"emotion": self.character.emotion.impression}
    
    def retrieve_preference(self, ):
        # TODO: design preference art form of characters
        return False, {"preference": "This painting is very beautiful and invaluable. I really like it."}
    
    def retrieve_impression(self, act_obj="Emma Smith"):
        mem_on_rec = self.character.longterm_memory.get_people_memory(act_obj)
        return False, { "impression": mem_on_rec }
        
    
    def build_prompt(self, impression, world_model, external_obs, emotion, preference):
        prompt = None
        # TODO: get real item and seller
        character = self.character_list.get_character_by_name("Emma Smith")
        resource_id = character.drawings[-1].id
        
        self.character.working_memory.store_memory("resource_id", resource_id)
        resource = character.drawings.get(resource_id)
        price = resource.price if resource.price else "Unknown"
        perception = {
            "name": self.character.name,
            "item": "painting",
            "seller": character.name,
            "price": price,
            "money": self.character.Gold,
            "world_model": world_model, 
            "external_obs": external_obs,
            "emotion": emotion,
            "preference": preference,
            "impression": impression,
            }
        prompt = self.prompt_class.create_prompt(perception)
            
        return  False, {"prompt": prompt}

    def add_chat_recv(self, ):
        img_id = self.character.working_memory.retrieve_by_name("img_id")
        character = self.character_list.get_character_by_name("Emma Smith") # FIXME
        self.character.working_memory.store_memory("act_obj", character.name)
        Trade.make_trade(self.character, character, img_id, 200, resource_type="drawings")
        return False, {}
    
    def get_owner_name(self, artwork_id):
        try:
            artwork = get_artwork_from_db(artwork_id)
            return artwork['owner_name']
        except Exception as e:
            if os.getenv('DEBUG'): __import__('ipdb').set_trace()
            LogManager.log_error(f"Error getting artwork from database: {e}")
            return self.character.name
    
    def update_sys_prompt_to_bargain(self, resource_id, owner_agent:Character):
       
        purchase_request =  {"bill":{"money": 200, "artwork_id": "a8c50360-1405-4e9f-a300-1f25d80d7e53"  }}
        
        mem_on_buyer = self.character.longterm_memory.get_people_memory(owner_agent.name)
        buyer_expected_price = self.get_character_wm_by_name('expected_price', 10000)
        buyer_bargain_instruction = f"""
        Your current status: {self.character.internal_status}. 
        You would like to buy an artwork, whose id is {resource_id}. The owner of it is {owner_agent.name}.
        Your impression on him/her is {mem_on_buyer}.
        The price you can accept is {buyer_expected_price}.
        Now trying to bargain the price with the its owner.
        Follow the following instructions to bargain:
        1. Remember, the price you can accept is ${buyer_expected_price} !
        2. You can not reply more than 30 words at a time.
        3. everytime before you respond to others, think about if you are willing to pay. If the price is acceptable, in another word, the price is lower than your expected price, write willing_to_pay as 'yes'. Otherwise, write 'no'. 
        4. return in json format, like {{ 'current_price': X, 'expected_price':Y, 'willing_to_pay': yes/no, 'content': xxx }}.
        5. Once your willing_to_pay is yes, call the tool named 'handle_purchase_request' and write the price you are willing to pay. And the artwork id, like {{ 'current_price': X, 'expected_price':Y, 'willing_to_pay': yes, 'content': {{"tool_call": "handle_purchase_request", "price":300, "artwork_id":xxxx}} }}. Then the system will transfer the money to the seller.

        """
        #        3. everytime before you respond to others, think twice about what is the best strategy to bargain, think about how to keep the price lower than ${buyer_expected_price},  then your response as the content of the response.

        seller_excepted_price = owner_agent.estimate_artwork_price(artwork_id = resource_id) 
        mem_on_buyer = owner_agent.longterm_memory.get_people_memory(self.character.name) 
        seller_bargain_instruction = f"""
        Your current status: {owner_agent.internal_status}. 
        {self.character.name} would like to buy your artwork. 
        Your impression on him/her is {mem_on_buyer}.
        Your expected price is {seller_excepted_price}.
        Follow the following instructions to bargain:
        1. Remember, the lowest price you can accept is ${seller_excepted_price} !
        2. Analyse price each time. If the price is acceptable, in another word, the price is higher than your expected price, ask the buyer to record the bill. Otherwise the trade can not sucess since the buyer does not send money to you.
        3. The seller will bargain with you, if you feel boring about the bargain process, say 'TERMINATE' to end the conversation.
        4. You can not reply more than 30 words at a time.
        5. return in json format, like {{ 'current_price': X, 'expected_price':Y,'content': xxx }}.
        """
        self.character.update_system_message( buyer_bargain_instruction)
        owner_agent.update_system_message( seller_bargain_instruction)
        
        return buyer_bargain_instruction, seller_bargain_instruction
        
    def call_llm(self, prompt, prompt_type: PromptType):
        # act_obj = self.get_character_wm_by_name('act_obj')
        # recipient = self.character_list.get_character_by_name(act_obj)
        # if recipient is None: # is building 
        #     recipient = self.building_list.get_building_by_name(act_obj)
        #     mem_on_rec = self.character.longterm_memory.get_building_memory(act_obj)
        #     mem_on_send = None # DEBUG
        # else:
        #     mem_on_rec = self.character.longterm_memory.get_people_memory(act_obj)
        #     mem_on_send = recipient.longterm_memory.get_people_memory(self.character.name)
            
        # bargain_instruction = self.build_bargain_instruction() 
        
        # self.character.update_system_message(self.character.system_message + f'Your current status: {self.character.internal_status}. You are chatting with {recipient.name}. Your impression of him/her is {mem_on_rec }. If you are purchasing something, calculate the final price carefully. You can not reply more than 30 words at a time.')
        # recipient.update_system_message(recipient.system_message + f' Your current status: {recipient.internal_status}. {bargain_instruction}  You can not reply more than 30 words at a time.') 
        resource_id = self.get_character_wm_by_name('appreciate_id') 
        self.owner_name = self.get_owner_name(artwork_id = resource_id)
        owner_agent = self.get_agent_by_name(self.owner_name)
        assert owner_agent is not None, f'Owner agent {self.owner_name} is not found.'
        self.update_sys_prompt_to_bargain(resource_id=resource_id, owner_agent=owner_agent)
        self.llm_task = asyncio.create_task(self.character.a_initiate_chat(recipient=owner_agent,
                                            message="I like this painting! It seems it belongs to you. Could you give me a price for it? I want to buy it.", #self.get_character_wm_by_name(''),
                                            clear_history=True, )
                                            )
    def restore_system_prompt(self):
        ''' 
        restore in exist func chain may cause some issues about async process. But if not, the system message will be restored to the original one when llm calls
        '''
        self.character.update_system_message(self.character.build_sys_message())
        owner_agent = self.get_agent_by_name(self.owner_name)

        owner_agent.update_system_message(owner_agent.build_sys_message())
        return False, dict()