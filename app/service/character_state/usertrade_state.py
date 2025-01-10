import asyncio
import json
import random
from .base_state import BaseState
from ...constants import PromptType
from ...models.location import BuildingList, Building
from ...models.character import Character, CharacterList, CharacterState
from .register import register
from ...constants.msg_id import State2RecieveMsgId
from ...utils.gameserver_utils import add_msg_to_send_to_game_server

@register("USERTRADE",'state')
class USERTRADE(BaseState):
        def __init__(self, 
                     character: Character, character_list: CharacterList, building_list: BuildingList,  on_change_state, 
                    followed_states=[CharacterState.USERTRADE],
                    main_prompt = None,
                    state_name = CharacterState.USERTRADE,
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
            
        def monitor_server_msg(self, msg=None):
            if not msg: return False, dict()
            # if int(msg['msg_id']) in int(State2RecieveMsgId.get(self.state_name, 0)):
            if msg['msg_id'] == 2004:
                return self.handle_server_buy_msg(msg['msg'])
            elif msg['msg_id'] == 2005:
                return self.handle_server_sell_msg(msg['msg'])
            return False, dict()

        def handle_server_sell_msg(self, msg):
            '''
            User buy 
            this.price = price;
            this.artwork_id = artwork_id;
            this.from_agent_id = from_agent_id;
            this.to_user_name = to_user_name;
           
            User sell
            this.price = price;
            this.artwork_id = artwork_id;
            this.to_agent_id = to_agent_id;
            this.from_user_name = from_user_name;
            
            '''
            msg = json.loads(msg)
            assert all( k in msg.keys() for k in ['artwork_id','to_agent_id', 'from_user_name', ] ), 'The msg does not contain all necessary keys, your msg is: ' + str(msg)
            artwork_id = msg['artwork_id']
            agent_id = msg['to_agent_id']
            agent = self.character_list.get_character_by_id(agent_id)
            is_succ, res_message = self.agent_buy_judge(agent, ) 
            self.push_state_msg(msg, is_succ, res_message)
            return super().handle_server_msg(msg)

        def handle_server_buy_msg(self, msg):
            msg = json.loads(msg)
            assert all( k in msg.keys() for k in ['artwork_id','from_agent_id', 'to_user_name',] ), 'The msg does not contain all necessary keys, your msg is: ' + str(msg)
            agent_id = msg['from_agent_id']
            agent = self.character_list.get_character_by_id(agent_id)
            artwork_id = msg['artwork_id']
            artwork = agent.drawings.get(artwork_id)

            assert artwork is not None, 'The artwork_id should be in the character artworks, your artwork_id is: ' + str(artwork_id) 
            proposed_price = msg['price']
            is_succ, res_message = self.agent_sell_judge(artwork, proposed_price)
            self.push_state_msg(msg, is_succ, res_message)
            # message = f"Would you like to sell {artwork['name']} for {artwork['price']}?\
            #     Answer Yes or No, with a reason."
            return False, dict()
        
        def agent_sell_judge(self, artwork, proposed_price):
            if proposed_price > artwork.price:
                return True, "It is a great deal! I will sell it to you!"
            return False, "Good price, but I think I will keep it for now. Thank you for your offer!"

        def agent_buy_judge(self, agent, artwork):
            if random.random() > 0.5:
                return True, " It is a random decision, need to be implemented"
            return False, "It is a random decision, need to be implemented"

        def push_state_msg(self, server_msg, is_succ, res_message):
            server_msg['is_succ'] = is_succ
            server_msg['error_msg'] = res_message
            msg_id = 1004 if 'to_user_name' else 1005
            msg_str = f"{msg_id}@{json.dumps(server_msg)}"
            add_msg_to_send_to_game_server(msg_str)