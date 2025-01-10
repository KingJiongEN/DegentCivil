import json
from typing import Coroutine, Dict

from autogen import ConversableAgent
from autogen.agentchat.agent import Agent
from autogen.agentchat.chat import ChatResult
from app.models.character import Character
from ..utils.gameserver_utils import add_msg_to_send_to_game_server
'''
An invisible NPC created to inherit trade proposals from the user.
Only one reply
No user interaction
'''

class Trader(Character):
    '''
    Under Construction
    '''
    def __init__(self, llm_cfg, name='Trader', id='-1', age='0', 
                 bio='You are a trader come from a remote town',
                 in_building=None,
                  health=10, money=1000, 
                  satiety=10, vigor=100, 
                  max_consecutive_auto_reply=1, 
                  init_emos=None, 
                  is_multi_modal_agent=True, 
                  **kwargs):
        super().__init__(name, id, age, bio, llm_cfg, 0, 0, health, money, satiety, vigor, max_consecutive_auto_reply, init_emos, is_multi_modal_agent, in_building=in_building, **kwargs)
        self.register_hook('process_last_received_message', self.push_trade_response)
        

    def push_trade_response(self, message):
        message = self.parse_final_message(message)
        add_msg_to_send_to_game_server(message)

    def pre_send(self, recipient:ConversableAgent, message):
        '''
        before send the message
        message is from the game server
        '''
        message
        if recipient._oai_messages[self.name] == 0:
            return True
        

    def send(self, message: Dict | str, recipient: Agent, request_reply: bool | None = None, silent: bool | None = False) -> ChatResult:
        # self.clear_history(, nr_messages_to_preserve=10)
        message = self._process_message_before_send(message, recipient, silent)
        # When the agent composes and sends the message, the role of the message is "assistant"
        # unless it's "function".
        valid = self._append_oai_message(message, "assistant", recipient)
        if valid:
            recipient.receive(message, self, request_reply, silent)
        else:
            raise ValueError(
                "Message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
            )
    
    async def a_send(self, message: Dict | str, recipient: Agent, request_reply: bool | None = None, silent: bool | None = False) -> Coroutine[Any, Any, ChatResult]:
        # self.clear_history(, nr_messages_to_preserve=10)
        message = self._process_message_before_send(message, recipient, silent)
        # When the agent composes and sends the message, the role of the message is "assistant"
        # unless it's "function".
        valid = self._append_oai_message(message, "assistant", recipient)
        if valid:
            await recipient.a_receive(message, self, request_reply, silent)
        else:
            raise ValueError(
                "Message can't be converted into a valid ChatCompletion message. Either content or function_call must be provided."
            )
    
              
    def parse_final_message(self, message, **kwargs):
        if message == 'Yes':
            is_succ = True
            msg = {
                'content': 'Yes',
                'action': 'trade',
                'artwork_id': self.character.drawings[0]['id'],
                'price': self.character.drawings[0]['price'],
                'trader_id': self.character.guid
            }
        elif message == 'No':
            is_succ = False

        msg = {
            'is_succ': is_succ,
            'artwork_id': self.character.drawings[0]['id'],
            'price': self.character.drawings[0]['price'],
            'to_user_name': 'user' # FIXME: should be the user's name
        }
        msg_str = f"1004@{json.dumps(msg)}"
        
        add_msg_to_send_to_game_server(msg_str)
