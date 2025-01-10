import asyncio
import os
import sys
import time
from queue import *

sys.path.append('./')
from app.service.simulation import Simulation
from app.utils.gameserver_utils import LLM_msg_queue, server_msg_queue, add_msg_to_send_to_game_server
from config import config

import redis

if os.getenv('Milvus'):
    # 无密码连接
    r = redis.Redis(host='localhost', port=6379, db=0)

    # 有密码连接
    r = redis.Redis(host='localhost', port=6379, db=0, password='redis-pwd')
    r.set('mykey', 'myvalue')
    print('redis value',r.get('mykey'))

STAT_CFG = sys.argv[1] if len(sys.argv) > 1 else 'config/states.yaml'
OAI_CFG = sys.argv[2] if len(sys.argv) > 2 else 'OAI_CONFIG_LIST'


running_simulation = False

def setup_proxy():
    os.environ['http_proxy'] = "http://localhost:10080"
    os.environ['https_proxy'] = "http://localhost:10080"


async def periodic_update(service):
    while True:
        start_time = time.monotonic()
        service.update_state()
        elapsed = time.monotonic() - start_time
        wait_time = max(config.update_interval - elapsed, 0)
        if os.getenv("FAST"):
            wait_time = 0.5
        await asyncio.sleep(wait_time)


async def main():
    global running_simulation

    if running_simulation:
        return
    running_simulation = True

    # setup_proxy()
    simulation = Simulation(state_config_file=STAT_CFG, oai_config_file=OAI_CFG)
    simulation.start_service()
    await periodic_update(simulation)

#待通过C#发送的消息队列
# LLM_msg_queue = Queue()
# server_msg_queue = Queue()

# def add_msg_to_send_to_game_server(msg):
#     global LLM_msg_queue
#     LLM_msg_queue.put(msg)


def StartRun():
    print("PYTHON========>: Begin")
    asyncio.run(main())
    print("PYTHON========>: End")

def GetMsgToSend():
    global LLM_msg_queue
    if not LLM_msg_queue.empty():
        return LLM_msg_queue.get()
    else:
        return None

def DealMessage(_from, _msg_id, _msg):
    global server_msg_queue
    server_msg_queue.put({
        "from": _from,
        "msg_id": _msg_id,
        "msg": _msg
    })
    if _msg_id != 2000:
        print("PYTHON========>: _from=" + _from + " _msg_id=" + str(_msg_id) + " _msg=" + _msg)

if __name__ == "__main__":
    asyncio.run(main())
