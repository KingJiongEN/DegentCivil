import asyncio
from queue import *

LLM_msg_queue = Queue()
server_msg_queue = Queue()
    

def add_msg_to_send_to_game_server(msg):
    global LLM_msg_queue
    LLM_msg_queue.put(msg)

