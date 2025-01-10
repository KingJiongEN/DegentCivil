from datetime import datetime
import inspect
import json
import os
from pathlib import Path
import random
import dill
from typing import Optional, Union
from autogen import filter_config, ConversableAgent, AssistantAgent, UserProxyAgent, config_list_from_json, Agent

from app.models.base_agent import SimsAgent
from app.utils.load_oai_config import plug_api_to_cfg, register_callback
from app.utils.save_object import find_instance_specific_data_attrs
from ..service.character_state.register import FuncName2Registered
from ..utils.serialization import serialize
from ..utils.globals import RESOURCE_SPLITER
from config import cfg_tmplt

class Building(SimsAgent):
    '''
    description: texts describing building , sys prompt for building
    building instruction: text as part of sys prompt, to guide the tougue of the building
    equipment instruction: texts to guide the usage, to start conversation with character. It is the first message for init_chat
    equipments: {nameA: { 'instruction': xx }, nameB:{ 'instruction': xx }}
    jobs: {jobA: { 'description': xx, 'salary': xx, 'num_positions': xx }, jobB: { 'description': xx, 'salary': xx, 'num_positions': xx }
    '''
    DEFAULT_SYS_PROMPT = """
    You are an operational equipment in a building.
    * If the customer tries to purchase something, ask for their current money and relvant information and estimate the result after purchase.
    * If the customer tries to haggle ask for the price they want and estimate the result after haggling
    * If the customer tries to use a equipment, guid them how to use it and estimate the equipment status after use.
    * Do not provide any information beyond the status of the building and equipments. If the customer is asking about the information you do not know, reject the request.
    * Try your best to temptate the customer to spend more money.
    * When you are in a dialogue, you can stop it at any time by saying 'TERMINATE'.
    """
       
    def __init__(self, id:int, name, llm_cfg, xMin, yMin, xMax, yMax, 
                 description, instruction,
                 equipments: dict[str, str]=None, 
                 jobs:dict[str, dict] = None, 
                 max_consecutive_auto_reply=10, 
                 money= 0, 
                 save_dir=None,
                 map = None,
                 **kwargs) -> None:
        self.guid = id
        self.xMin = xMin
        self.yMax = yMax
        self.xMax = xMax
        self.yMin = yMin
        self.money = money
        self.instruction = instruction
        self.save_dir = Path(save_dir) / name
        self.map = map
        assert RESOURCE_SPLITER not in name, f'building name should not contain {RESOURCE_SPLITER}, your building name: {name}'
                
        register_callback(llm_cfg, guid=self.guid, prefix=f'building_{name}')
        config_list = plug_api_to_cfg(cfg_tmplt, **llm_cfg) 
        cfg_ls = filter_config(
                config_list=config_list, 
                filter_dict={
                    "model": [  "gpt-4-0125-preview", "gpt-3.5-turbo-0125","deepseek-chat"],
                    # "tag": ["gpt-3.5-turbo-0125-official", "gpt-4-0125-preview-official"]
                }
            )
        llm_cfg = \
                {
                    "config_list": cfg_ls,
                    "seed": 35,
                    "temperature": 0.5
                }
            
        super().__init__(
            name = name,
            llm_config = llm_cfg,
            human_input_mode= 'NEVER',
            max_consecutive_auto_reply = max_consecutive_auto_reply,
            description=description,
        )
        self.job_positions: dict[str, Job] = self.add_jobs(jobs) if jobs else dict()
        self.equipments:dict[str, InBuildingEquip] = self.add_equipments(equipments) if equipments else dict()
        self.update_system_message(self.build_sys_message())
    
    @classmethod
    def decode_from_json(self, **kwargs):
        return Building(**kwargs)   
    
    @property
    def position(self):
        return (self.xMin, self.yMin, self.xMax, self.yMax) 
    
    @property
    def random_pos_inside(self):
        while True:
            x, y = random.randint(self.xMin, self.xMax), random.randint(self.yMin, self.yMax)
            if self.map[x][y] == 1:
                break                
        return (x, y)
   
    @property
    def internal_status(self):
        return f'balance: {self.balance}'

    @property
    def modifiable_status(self):
        return ['description']
    
    def modify_internal_properties(self, prop):
        for key, val in prop.items():
            if key in self.modifiable_status:
                setattr(prop, key, val)
    
    def cordinate_in_building(self, x:int, y:int):
        return (self.xMin <= x) and (x <= self.xMax) and (self.yMin <= y) and (y <= self.yMax  )
    
    def add_equipments(self, equipments):
        return dict( ( f'{self.name}{RESOURCE_SPLITER}{eqp["name"]}', InBuildingEquip.build(inbuilding=self, **eqp)) for eqp in equipments.values())
    
    def update_equipments(self, equipments):
        for eqp in equipments.values():
            name = f'{self.name}{RESOURCE_SPLITER}{eqp["name"]}'
            if self.equipments.get(name) is None:
                self.equipments.update({name:  InBuildingEquip.build(inbuilding=self, **eqp)}) 
            
            self.equipments[name].same_itmes_guid_inbuilding.append(eqp['guid']) 
            
    def add_jobs(self, jobs):
        return dict(( f'{self.name}{RESOURCE_SPLITER}{job_name}', Job.build(inbuilding=self.name, **job_des)) for job_name, job_des in  jobs.items())
    
    def update_jobs(self, jobs):
        self.job_positions.update(self.add_jobs(jobs))
    
    @property
    def occupied_jobs(self):
        if self.job_positions is None:
            return []
        return [job for job in self.job_positions.values() if len(job.applicants) ]
    
    @property
    def available_jobs(self):
        if self.job_positions is None:
            return None
        ava_jobs = [job for job in self.job_positions.values() if not job.occupied]
        return ava_jobs
        
    @property
    def available_equipments(self):
        return [ eqp for eqp in self.equipments.values() ]
        
    def build_sys_message(self):
        return f''' {self.DEFAULT_SYS_PROMPT} the description of the building: {self.description}. 
            Open jobs in this building: {self.available_jobs} 
            The equipments in the building: {self.available_equipments}'''
    
    def equipment_instr(self, equip_name):
        return f"{self.equipments[equip_name].instruction} Current status: {self.equipments[equip_name].organize_status()} in the building {self.name}"
    
    def register_equip_functions(self, equipment:'InBuildingEquip'):
        if equipment.functions:
            for func in equipment.functions:
                self.register_callable_tools(func)
    
    def clean_equipment_functions(self, equipment:'InBuildingEquip'):
        if equipment.functions:
            for func in equipment.functions:
                self.callable_tools.remove(func)
    
    def encode_to_json(self) -> json:
        return json.dumps(serialize(self))
    
    def save_self_locally(self):
        save_path = None
        if self.save_dir:
            os.makedirs(f'{self.save_dir}', exist_ok=True)
            
            attr_to_save = find_instance_specific_data_attrs(self)
            attr_to_save = attr_to_save + ['name']
            dict2save = dict( ((attr, getattr(self, attr)) for attr in attr_to_save))
            
            # Keep the number of files less than K
            files = os.listdir(self.save_dir)
            files.sort(key=lambda x: os.path.getctime(os.path.join(self.save_dir, x)))  # Sort files by creation time
            while len(files) >= 10: 
                os.remove(os.path.join(self.save_dir, files[0]))
                files.pop(0)
            
            save_path = f'{self.save_dir}/building_{self.name}_{datetime.now().strftime("%m%d%H%M%S")}.dill'
            with open(save_path, 'wb') as f:
                dill.dump(dict2save, f)
        
        return save_path
    
    def load_from_local(self, file_path):
        print(f'load Building from {file_path}')
        with open(file_path, 'rb') as f:
            attr_dict = dill.load(f)
        for key, value in attr_dict.items():
            if key in ['name','save_dir']: continue
            setattr(self, key, value)
            
    def __repr__(self):
        return self.name
            
class BuildingList:
    def __init__(self):
        self.buildings: list[Building] = []

    def add_building(self, building):
        self.buildings.append(building)

    def get_building_name(self):
        return [building.name for building in self.buildings]

    def encode_to_json(self) -> json:
        dicts = [serialize(building) for building in self.buildings]
        return dicts

    def get_building_by_id(self, building_id):
        for building in self.buildings:
            if building.name == building_id:
                return building
        return None

    def get_building_by_name(self, building_name):
        for building in self.buildings:
            if building.name == building_name:
                return building
        return None
    
    def get_building_by_pos(self, x, y):
        for building in self.buildings:
            if building.cordinate_in_building(x, y):
                return building
        return None

    def get_building_descriptions(self):
        return { building.name:building.description for building in self.buildings}
    
    def save_locally(self):
        for building in self.buildings:
            building.save_self_locally()
    
class InBuildingEquip:
    def __init__(self, name:str, instruction:str, inbuilding=None, x:int=None, y:int=None, interactable = False, status: str = None, functions: Union[str, callable, None]= None, other_status: dict[str,str] = None, **kwargs) -> None:
        assert RESOURCE_SPLITER not in name, f'equipment name should not contain {RESOURCE_SPLITER}, your building name: {name}'
        self.name = name #f'{inbuilding}{EQUIPSPLITER}{name}'
        self.guid_on_name = hash(name) % 100000
        self.x = x
        self.y = y
        self.inbuilding = inbuilding
        if inbuilding is None:
            assert self.x is not None and self.y is not None, 'If inbuilding is not provided, the x and y should be provided'
        if any( pos is None for pos in [self.x, self.y] ):
            assert inbuilding, 'If x or y is not provided, the inbuilding should be provided'
            
        self.instruction = instruction
        self.same_itmes_guid_inbuilding = []
        self.interactable = interactable
        
        self.status = status
        self.modifiable_status = ['status']
        if self.interactable: assert self.status
        if other_status:
            self.__dict__.update(other_status)
            self.modifiable_status += list(other_status.keys())
        if functions:
            if type(functions) is list:
                self.functions = [ fc if callable(fc) else FuncName2Registered[fc] for fc in functions ]
            elif type(functions) is str:
                self.functions = [functions] if callable(functions) else [FuncName2Registered[functions]]
        else:
            self.functions = None
            
        self.add_functions_to_instruction()
        
    def add_functions_to_instruction(self):
        if self.functions:
            meta_inst ='You can use the following tools by return corresponding structured response:\n'
            for func in self.functions:
                sig = inspect.signature(func)
                name = func.__name__
                struct_response = {
                    "content":{
                        "tool_call": name,
                    }
                }
                for para in sig.parameters:
                    if para not in  ['self', 'sender']:
                        struct_response['content'][para] = 'your value'
                    
                meta_inst += f'{name}: {struct_response}\n'
            
            self.instruction += meta_inst
        
    @classmethod
    def build(cls, name, instruction, **kwargs):
        return cls(name, instruction, **kwargs)

    def set_building(self, building:Building):
        if building.cordinate_in_building(self.x, self.y):
            self.inbuilding = building
            return True
        return False

    def random_choose(self):
        '''
        choose an item from the same items in the building
        '''
        assert len(self.same_itmes_guid_inbuilding) > 0, f'No same items in the building {self.inbuilding.name} for {self.name}'
        rd_idx = random.randint(0, len(self.same_itmes_guid_inbuilding)-1)
        return self.same_itmes_guid_inbuilding[rd_idx]
    

    def organize_status(self):
        return {key: getattr(self, key) for key in self.modifiable_status} 
    
    def modify_internal_properties(self, prop):
        for key, val in prop.items():
            if key in self.modifiable_status:
                setattr(self, key, val)
    
    def __repr__(self) -> str:
        return f'''
        name: {self.name},
        in_building: {self.inbuilding},
        instruction: {self.instruction}
    '''
    
class Job:
    def __init__(self, name, description, salary, inbuilding, num_positions) -> None:
        self.name = name
        self.description = description
        self.salary = salary
        self.inbuilding = inbuilding
        self.applicants = []
        self.num_positions = 1 # default 1 position
    
    @classmethod
    def build(cls, name, description, salary, inbuilding, num_positions, **kwargs):
        return cls(name, description, salary, inbuilding, num_positions)
    
    @property
    def occupied(self):
        return len(self.applicants) >= self.num_positions
    
    @property
    def open_positions(self):
        return -len(self.applicants) + self.num_positions 
    
    def add_job_des_to_agent_messge(self, agent: ConversableAgent):
        '''
        add job description into the system message of the character
        '''
        message = f'Your Job: {self.name}, Description: {self.description}, Salary: {self.salary}'
        agent.update_system_message( agent.system_message + message)
    
    def __repr__(self) -> str:
        return f'''
        name: {self.name},
        description: {self.description},
        in_building: {self.inbuilding},
        salary: {self.salary},
        open_positions: {self.open_positions}
    '''
    
    def add_applicant(self, applicant):
        self.applicants.append(applicant)
        
    def remove_applicant(self, applicant):
        self.applicants.remove(applicant)
        
    def to_json(self):
        return json.dumps(serialize(self))
    
    @classmethod
    def decode_from_json(cls, **kwargs):
        return cls(**kwargs)