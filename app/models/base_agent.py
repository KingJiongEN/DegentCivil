import asyncio
import copy
import inspect
import json
from typing import Callable, Dict, List, Literal, Union, Optional, Any
from autogen import ConversableAgent, Agent, OpenAIWrapper, AssistantAgent

from app.repository.artwork_repo import check_artwork_belonging
from app.repository.utils import check_balance_and_trade
from app.utils.gameserver_utils import add_msg_to_send_to_game_server
# from app.models.trader_agent import Trader

class SimsAgent(AssistantAgent):
    def __init__(self,
            name: str,
            system_message: Optional[str] = None,
            llm_config: Optional[Union[Dict, Literal[False]]] = None,
            is_termination_msg: Optional[Callable[[Dict], bool]] = None,
            max_consecutive_auto_reply: Optional[int] = None,
            human_input_mode: Optional[str] = "NEVER",
            description: Optional[str] = None,
            **kwargs,
        ):
        super().__init__(name, system_message, llm_config, is_termination_msg, max_consecutive_auto_reply, human_input_mode, description, **kwargs)
        
        self.clients = {} # for multi client case, each client is for one model config
        for cfg_idx in range(len(self.llm_config.get('config_list', []))):
            seperate_llm_cfg = copy.deepcopy(self.llm_config)
            model_cfg = self.llm_config['config_list'][cfg_idx]
            if 'tag' in model_cfg:
                model_name = model_cfg.pop('tag')
            else: 
                model_name = model_cfg['model']
            
            seperate_llm_cfg.update({"config_list": [model_cfg]})
            # __import__('ipdb').set_trace()
            self.clients[model_name] = OpenAIWrapper(**seperate_llm_cfg)
        self.client =OpenAIWrapper(**self.llm_config) # without the tag arg 
        
        
        self.register_hook('process_message_before_send', self.push_reply_to_game_server)
        self.register_reply([Agent, None], SimsAgent.func_router)
        self.subsitute_reply(SimsAgent.generate_oai_reply) 
        self.callable_tools = [self.handle_purchase_request]
    
    def subsitute_reply(self, new_func):
        '''
        replace the old registered reply by the new func with the same name
        '''
        for reply_func_tuple in self._reply_func_list:
            reply_func = reply_func_tuple["reply_func"]
            if reply_func.__name__ == new_func.__name__:
                reply_func_tuple.update({"reply_func": new_func})
                
    def update_system_message(self, system_message: str) -> None:
        return super().update_system_message(system_message)
     
    def push_reply_to_game_server(self, message: Union[Dict, str], recipient: Agent, silent: bool
    ) -> Union[Dict, str]:
        '''
        push the message to the game server
        '''
        if recipient != self:
            try:
                message_dict = self._message_to_dict(message)
                content = message_dict.get('content') or message_dict[0].get('content') or message_dict['messages'][0]['content']
            except (KeyError, IndexError):
                content = None
                msg = {
                    'agent_guid': self.guid,
                    'content': content,
                    'song': "agent_song_on_walk3"
                }

                msg_str = f"1008@{json.dumps(msg)}"
                add_msg_to_send_to_game_server(msg_str)
            except Exception as e:
                print('#'*10, '\n', e, '\n', '#'*10)
                print('#'*10, f'\n Error in push_reply_to_game_server, the content is {self._message_to_dict(message)} \n', '#'*10)
        return message 
    
    def vigor_cost(self, message: Union[Dict, str], recipient: Agent, silent: bool
    ):
        if hasattr(self, 'vigor'):
            self.vigor -= len(self._message_to_dict(message)['content']) * 0.01 * self.vigor_decay_rate
    
    @staticmethod
    def _message_to_dict(message: Union[Dict, str]) -> Dict:
        """
        For the case that we must return a json style text for agent reply, we set the reply format in chat as {'content': xxx}
        So try to transform it to disct first
        """
        if message is None: __import__('ipdb').set_trace()
        # print("!!! message is ", message)
        if isinstance(message, str):
            try:
                message = json.loads(message)
                if type(message) is dict:
                    if 'messages' in message:
                        message = message['messages'][-1]
                    if 'content' in message:
                        message['content'] = str(message['content']) # ensure the content is str
                        return message
            except:
                return {"content": message}
        elif isinstance(message, dict):
            return message
        else:
            raise ValueError(f"message is not in the proper format {message}")
            
    # async def a_process_then_reply(self, message, sender: Agent, restart=True, silent=True, check_exempt_layers=[1,2,3,4,5,6,7,8,9,10] ):
    #     # modified from ConversableAgent.a_receive()
    #     self._prepare_chat(self,clear_history=restart)
    #     self._process_received_message(message, sender, silent)
    #     reply = await self.a_generate_reply(sender=sender)
    #     error = self.prompt_and_response.response_vanity_check(reply, check_exempt_layers)
    #     if error:
    #         print(f'Error in response: {error}.')
    #         return await self.a_process_then_reply(message + error +' Please strictly follow the example in the prompt', sender, restart=False, silent=silent, check_exempt_layers=check_exempt_layers)  
    #     else:
    #         return json.loads(reply)
        
    # def process_then_reply(self, message, sender: Agent, restart=True, silent=True, check_exempt_layers=[1,2,3,4,5,6,7,8,9,10] ):
    #     # modified from ConversableAgent.receive(), for debug purpose
    #     self._prepare_chat(self,clear_history=restart)
    #     self._process_received_message(message, sender, silent)
    #     reply = self.generate_reply(sender=sender)
    #     error = self.prompt_and_response.response_vanity_check(reply, check_exempt_layers)
    #     if error:
    #         print(f'Error in response: {error}.')
    #         return self.process_then_reply(message + error +' Please strictly follow the example in the prompt', sender, restart=False, silent=silent, check_exempt_layers=check_exempt_layers)  
    #     else:
    #         return json.loads(reply)
        
    # async def a_generate_reply(
    #     self,
    #     messages:Optional[List[Dict[str, Any]]] = None,
    #     sender: Optional["Agent"] = None,
    #     **kwargs: Any,
    # ) -> Union[str, Dict[str, Any], None]:
    #     reply = await super().a_generate_reply(messages, sender, **kwargs)
    #     if sender!=self:
    #         self.push_reply_to_game_server(reply)
    #     return reply

    def func_router(self, messages: Union[Dict, str], sender: Agent, config:  Optional['OpenAIWrapper'] = None):
        '''
        route the function request from the messages to the corresponding function
        '''
        if messages is None:
            messages = self._oai_messages[sender]
        message = messages[-1]['content']
        
        try:
            message_dict = eval(message)
        except:
            return False, None
        if 'tool_call' not in message_dict: return False, None
        
        func_name = message_dict.pop('tool_call')
        arg_dict = message_dict
        arg_dict.update({'sender': sender})
        for func in self.callable_tools:
            if func.__name__ == func_name:
                sig = inspect.signature(func)
                missed_args = set(sig.parameters) - set(list(arg_dict.keys()))
                redundant_args = set(list(arg_dict.keys())) - set(sig.parameters) 
                if len(missed_args)==0 and len(redundant_args)==0 :
                    res = func(**arg_dict)
                    
                else:
                    part1 = f'You missed some important argumemnts {missed_args} .'
                    part2 = f'You add some redundant arguments {redundant_args} .'
                    part3 = f'The proper argument list is {sig.parameters}. Do not add extra args or mis any of them.'
                    res = 'Sorry. '
                    if missed_args:
                        res = res + part1
                    if redundant_args:
                        res = res + part2
                    res = res + part3
                break
            
        return True, res
    
    def generate_oai_reply(self,
        messages: Optional[List[Dict]] = None,
        sender: Optional[Agent] = None,
        config: Optional['OpenAIWrapper'] = None,
    ) -> tuple[bool, Union[str, Dict, None]]:
        """
        use the client set by the current state
        Generate a reply using autogen.oai.
        
        """
        try:
            client = self.clients[self.state.default_client]
        except:                          
            client = self.client
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]
        extracted_response = self._generate_oai_reply_from_client(
            client, self._oai_system_message + messages, self.client_cache
        )
        if extracted_response.startswith(' ```json') and extracted_response.endswith('```'):
            extracted_response = extracted_response[8:-3]
        return (False, None) if extracted_response is None else (True, extracted_response)
    
   
     
    def register_callable_tools(self, func):
        '''
        callable tools are designed to modify the attributes of the character, 
        it substitutes for the previous func: modify_internal_properties
        since it is checked every time when the character responses, it is more flexible and do not need an extral CharacterState to modify the character
        '''
        self.callable_tools.append(func)
        return func
        
    def handle_purchase_request(self, artwork_id, price:int, sender: Agent):
        '''
        handle the purchase request, check the price and money of the sender and the belonging of the artwork
        '''

        if not check_artwork_belonging(artwork_id, self.guid):
            return True, "Sorry, I just checked my artwork storage, this artwork is not mine. There may be some misunderstanding."
        
        if sender.money < price:
            return True, f"Sorry, there is only {sender.Gold} gold coins in your account. It is not enought to finish the purchase."
        
        result=check_balance_and_trade(balance_decrease_agent_id=sender.guid,
                                balance_increase_agent_id=self.guid,
                                trade_type='AGENT_TRADE_ARTWORK',
                                balance_change=price,
                                commodity_id=artwork_id,
                                from_user_name= sender.name,
                                to_user_name= self.name,
                                )
        if result['success']:
            sender.money = result['from_account_balance']
            self.money = result['to_account_balance']
            return " Thanks! The purchase is successful. The artwork is in your storage now. "
        else: 
            return f'Error when recording the transction: {result["response"]}' 

if __name__ == '__main__':
    agent = SimsAgent('test')
    # asyncio.run(agent.a_process_then_reply('{"tool_call": "handle_purchase_request", "artwork_id": "123", "price": 100}', agent)
