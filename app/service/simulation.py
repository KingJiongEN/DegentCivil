import asyncio
import copy
import os
from pathlib import Path
import queue
import shutil
import numpy as np
import random
from multiprocessing import Pool
import yaml
from autogen import config_list_from_json, filter_config
from app.constants.msg_id import State2RecieveMsgId, AllStateMsg

from app.utils.load_oai_config import build_runtime_apis_file
from config import building_data_table, character_data_table, city_status, boss_data_table, interactable_equipments_data_table, cheap_apis, official_apis, cfg_tmplt
from config.config_common import CommonConfig
from .character_state.state_manager import StateManager
from .database import SessionLocal
from ..communication.websocket_server import WebSocketServer
from ..constants.character_state import CharacterState
from ..models.building import Building, BuildingList, InBuildingEquip
from ..models.character import Character, CharacterList
from ..models.boss_agent import Boss
# from ..models.trader_agent import Trader
from ..utils.log import LogManager
from ..utils.gameserver_utils import server_msg_queue
from ..utils import globals
from ..models.agent_creation import AgentCreation
# from ..models.market_adjust import MarketAdjust
# from ..models.market_adjust import MarketAdjust
# from ipdb import set_trace
import json
from tqdm import tqdm

class Simulation:
    character_list: CharacterList
    building_list: BuildingList
    character_state_managers: dict[str: StateManager]
    total_update_count: int
    # market_simulation: MarketAdjust
    # market_simulation: MarketAdjust

    def __init__(self, state_config_file: str, oai_config_file: str):
        self.db_session = SessionLocal()
        # self.market_simulation = MarketAdjust()
        # self.market_simulation = MarketAdjust()
        
        self.total_update_count = 0
        self.newday_countdown = 100 if os.getenv("DEBUG") else 0
        self.started = False
        self.state_config_file = os.path.join(os.path.dirname(__file__), '..', '..', state_config_file)
        self.oai_config_file = os.path.join(os.path.dirname(__file__), '..', '..', oai_config_file)
        
        self.configs = dict()
        if self.state_config_file.endswith('yaml'):
            with open(self.state_config_file) as f:
                self.configs = yaml.safe_load(f)
        assert 'States' in self.configs

        self.configs.update(self.load_llm_config())
        
        LogManager.setup_logger()

    @staticmethod
    def load_llm_config():
        assert len(cheap_apis) > 0
        assert len(official_apis) > 0
        build_runtime_apis_file(cheap_apis, 'runtime/cheap_apis.json')
        build_runtime_apis_file(official_apis, 'runtime/official_apis.json')
        
        char_llm_cfgs, bldg_llm_cfgs = [], []
        assert len(cheap_apis) >= len(official_apis)
        for api_id in range(len(cheap_apis)):
            cheap_api = cheap_apis[api_id]
            official_api = official_apis[api_id%len(official_apis)]
            char_llm_cfgs.append({
                'cheap_api': cheap_api,
                'official_api': official_api,
            })
            bldg_llm_cfgs.append({
                'cheap_api': cheap_api,
                'official_api': official_api,
            })
        
        return {
            'char_llm_cfg': char_llm_cfgs,
            'bldg_llm_cfg': bldg_llm_cfgs,
        }   
        

    @staticmethod
    def load_config():
        config_lists = []
        for config_list in all_config_lists:
            cfg_ls = filter_config(
                config_list=config_list,
                filter_dict={
                    "model": ["gpt-4-0125-preview", "gpt-3.5-turbo-0125"],
                    "tag": ["gpt-3.5-turbo-0125-official", "gpt-4-1106-preview-official"]
                }
            )
            for cfg in cfg_ls:
                cfg.pop('tag')
            config_lists.append(
                {
                    "config_list": cfg_ls,
                    "seed": 35,
                    "temperature": 0.5
                }
            )

        return {
            'primary_config': config_lists,
            'secondary_config': config_lists,
        }

    def start_service(self, msg):
        # self.create_test_data()
        city_status = json.loads(msg)['city_state']
        os.makedirs('tmp', exist_ok=True)
        with open('tmp/city_status.json', 'w') as f:
            json.dump(city_status, f, indent=4)
        data = self.merge_frontend_backend_json(frontend_data=city_status, backend_data={
                                                'buildings': building_data_table, 
                                                'characters': character_data_table,
                                                'equipments': interactable_equipments_data_table,
                                                })
        
        self.load_frontend_data_from_json(data)
        # self.load_npc_characters()
        self.create_character_state_managers()
        print("Simulation started")

    def debug_service(self):
        # without the need of city_status msg, load it locally
        from config import city_status
        data = self.merge_frontend_backend_json(frontend_data=city_status, backend_data={
                                                'buildings': building_data_table, 
                                                'characters': character_data_table,
                                                'equipments': interactable_equipments_data_table,
                                                })
        self.load_frontend_data_from_json(data)
        # self.load_npc_characters()
        self.create_character_state_managers()

    def create_character_state_managers(self):
        self.character_state_managers = {}
        for character in self.character_list.characters:
            # TODO: character-level config
            LogManager.log_character_with_time(
                character.name, "--------START NEW SIMULATION--------\n\n")
            state_config = self.configs['States'][character.name] if character.name in self.configs[
                'States'] else self.configs['States']['BASE']
            self.character_state_managers[character.name] = StateManager(character, self.character_list,
                                                                         self.building_list,
                                                                         state_config=state_config)

    def load_frontend_data_from_json(self, json_data):
        map_info = json.load(open('config/city_status.json', 'r'))
        terrain = np.array(map_info['terrain_data']['data'])
        self.building_list = BuildingList()
        self.character_list = CharacterList()
        self.total_update_count = 0
        for i, building in enumerate(json_data['buildings']):
            index = i % len(self.configs['bldg_llm_cfg'])
            blg = Building.decode_from_json(llm_cfg=self.configs['bldg_llm_cfg'][index], map=terrain, **building)
            if CommonConfig.load_from is not None and os.path.exists(CommonConfig.load_from):
                ckpt_path = Path(CommonConfig.load_from) / 'buildings' / blg.name
                if ckpt_path.exists():
                    files = os.listdir(ckpt_path)
                    files.sort(key=lambda x: os.path.getctime(os.path.join(ckpt_path, x)))  
                    ckpt_path = Path(ckpt_path) / files[-1]
                    blg.load_from_local(ckpt_path)
            
            self.building_list.add_building(blg)
            
        for equip_dic in json_data['equipments']:
            added2building = False
            for blg in self.building_list.buildings:
                if blg.cordinate_in_building(equip_dic['pos']['x'], equip_dic['pos']['y']):
                    # print(f'Equipment {equip_dic["name"]} added to building {blg.name}')
                    blg.update_equipments({equip_dic['name']: equip_dic})
                    added2building = True
                    break
            assert added2building, f'Equipment {equip_dic["name"]} not added to any building'
        
        for i, character in tqdm(enumerate(json_data['characters'][:5])):
            index = i % len(self.configs['char_llm_cfg'])
            agent = Character.decode_from_json(llm_cfg=self.configs['char_llm_cfg'][index], **character)
            if CommonConfig.load_from is not None and os.path.exists(CommonConfig.load_from):
                ckpt_path = Path(CommonConfig.load_from) / 'characters' / agent.name
                if ckpt_path.exists():
                    files = os.listdir(ckpt_path)
                    files.sort(key=lambda x: os.path.getctime(os.path.join(ckpt_path, x)))  
                    ckpt_path = Path(ckpt_path) / files[-1]
                    agent.load_from_local(ckpt_path)
            self.character_list.add_character(agent)

    def merge_frontend_backend_json(self, frontend_data, backend_data):
        building_ls, equip_ls, char_ls = [], [], []
        for equip_name, equip_items in frontend_data['map_obj_list_dic_of_interactive'].items():
            if equip_name in backend_data['equipments']:
                for eqp_itm in equip_items: 
                    eqp_itm.update(backend_data['equipments'][equip_name])
                    eqp_itm['x'] = eqp_itm['pos']['x']
                    eqp_itm['y'] = eqp_itm['pos']['y']
                    equip_ls.append(copy.deepcopy(eqp_itm))                

        for build, prop in frontend_data['area_dic'].items():
            for bld in backend_data['buildings'].values():
                if bld['name'].lower() == build.lower():
                    bld.update(prop)
                    bld['save_dir'] = CommonConfig.local_blg_storage_path
                    building_ls.append(bld)
        
         
        for char, prop in frontend_data['intelligent_agent_dic'].items():
            for ch in backend_data['characters'].values():
                if int(ch['id']) == int(prop['id']):
                    ch['x'] = prop['postion']['x']
                    ch['y'] = prop['postion']['y']
                    ch['guid'] =  int(ch['id'])
                    ch['save_dir'] = CommonConfig.local_char_storage_path
                    char_ls.append(ch)            

        return {'buildings': building_ls, 'characters': char_ls, 'equipments': equip_ls}

    def load_npc_characters(self):
        self.load_boss_character(boss_data_table)

    def load_boss_character(self, boss_data):
        for i, boss in enumerate(boss_data.values()):
            index = i % len(self.configs['char_llm_cfg'])
            building_obj = self.building_list.get_building_by_name(boss.pop('in_building'))
            self.character_list.add_character(\
                Boss.decode_from_json(llm_cfg=self.configs['char_llm_cfg'][index], in_building=building_obj,  **boss))
        
    def load_trader(self):
        self.character_list.add_character(Trader(llm_cfg=self.configs['char_llm_cfg'][0]))

    def create_test_data(self):
        self.building_list = BuildingList()
        building_index = 0
        for building in building_data_table.values():
            self.building_list.add_building(Building(
                name=building["name"],
                description=building["description"],
                equipments=building["equipments"],
                xMin=building["xMin"],
                xMax=building["xMax"],
                yMax=building["yMax"],
                yMin=building["yMin"],
                llm_cfg={"config_list": self.config_list,
                         "seed": 39,
                         "temperature": 0.5
                         },
            ))
            building_index += 1
        WebSocketServer.broadcast_message(
            "all_buildings", self.building_list.encode_to_json())

        self.character_list = CharacterList()
        character_index = 0
        max_character = 2
        for character in character_data_table.values():
            if character_index >= max_character:
                break
            self.character_list.add_character(Character(
                name=character["name"],
                age=character["age"],
                bio=character["bio"],
                goal=character["goal"],
                llm_cfg=self.configs['oai_cfg'],
                town_id=1,
                health=100,
                money=100,
                staiety=2,
                x=30,
                y=30,
            ))
            character_index += 1
        WebSocketServer.broadcast_message(
            "all_characters", self.character_list.encode_to_json())

    def transform_date(self,):
        ttl_real_second = self.total_update_count * CommonConfig.update_interval
        real_simulation_ratio =  1 # in the unit of hour, indicating how many hours has passed in the simulation world within one real world second
        return ttl_real_second * real_simulation_ratio

    def handle_server_msg(self):
        global server_msg_queue
        msgs = []
        while not server_msg_queue.empty():
            try:
                msg = server_msg_queue.get()
                if msg['msg_id'] == 2000:
                    print("Simulation received city_state msg")
                    if not self.started:
                        print("Simulation starting")
                        self.newday_countdown = 10
                        self.start_service(msg['msg'])
                        self.started = True
                elif msg['msg_id'] == 2002: # new day, heart beats of game server
                    if self.started:
                        self.newday_countdown = 10
                else:
                    assert self.started, 'Simulation not started yet, received msg: %s' % msg
                    msgs.append(msg)
            except queue.Empty:
                break

        return msgs
    
    def filter_out_msg(self, server_msgs, state_manager):
        state_name = state_manager.current_state.state_name
        character_guid = state_manager.character.guid
        server_msg = None
        for msg in server_msgs:
            content = json.loads(msg['msg'])
            try:
                if int(msg['msg_id']) == int(State2RecieveMsgId.get(state_name, 0)):
                    if 'agent_guid' in content :
                        if int(content.get('agent_guid', 0)) == int(character_guid):
                            server_msg = msg 
                    else:
                        server_msg = msg
                    break # only handle the first msg for now, TODO: handle all msgs
                elif int(msg['msg_id']) in AllStateMsg :
                    server_msg = msg
                    break
            except Exception as e:
                import traceback
                traceback.print_exc()
                __import__('ipdb').set_trace()
        return server_msg        
    
    def update_state(self):
        if not self.started:
            server_msgs = self.handle_server_msg() # load the city
        if self.newday_countdown > 0:
            server_msgs = self.handle_server_msg()
            
            for state_manager in self.character_state_managers.values():
                
                server_msg = self.filter_out_msg(server_msgs, state_manager)
                date = self.transform_date()
                globals.update_date_num(date)
                if server_msg and int(server_msg.get('msg_id', 0)) == 2008:
                    AgentCreation.build_new_agent()
                state_manager.update_state(msg=server_msg, date=date)

            self.total_update_count += 1
            self.newday_countdown -= 0 if os.getenv("DEBUG") else 1
            print(f"Simulation update: {self.total_update_count}")
            
            if self.total_update_count % 100  == 0:
                self.save_state()
            # if self.total_update_count % 25 == 0:
            #     self.market_update()
            
    def save_state(self):
        return
        self.character_list.save_locally()
        self.building_list.save_locally() 
    
    def market_update(self):
        # asyncio.create_task(self.market_simulation.update())
        return
        # self.market_simulation.update()
        