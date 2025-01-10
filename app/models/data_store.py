import os
import re
import sys
import traceback
sys.path.append('./app')
sys.path.append('../../')

from collections import defaultdict
import copy
import json
from typing import List, Dict, Any
import uuid

# from ..utils.serialization import serialize
from ..database.milvus_datastore import MilvusDataStore
from ..global_config import MILVUS_HOST, MILVUS_PORT, MILVUS_INDEX_PARAMS
from ..database.milvus_constants import ENTITY_SCHEMA

ENTITY_COLLECTION = 'entity_memory'
LOCATION_COLLECTION = 'location_memory'
TRANSACTION_COLLECTION = 'transaction_records'

class Memory:
    def __init__(self, entity_name: str) -> None:
        self.entity_name = entity_name
        self.datastore = MilvusDataStore(
            host=MILVUS_HOST,
            port=MILVUS_PORT,
            collection_name=self.build_collection_name(),
            schema=ENTITY_SCHEMA,
            index_params=MILVUS_INDEX_PARAMS
        )
        self.numeric_memory = defaultdict(float)
        
    def build_collection_name(self):
        name = f"{ENTITY_COLLECTION}_{self.entity_name}"
        name = re.sub(' ', '', name)
        return name

    def update_numeric_memory(self, value_change:float, name, alpha=0.6):
        '''
        moving average based
        '''
        if name not in self.numeric_memory:
            self.numeric_memory[name] = value_change
        else:
            old_value = self.numeric_memory[name]
            self.numeric_memory[name] = alpha * old_value + (1-alpha) * (value_change)
        
    def store(self, memory: Dict[str, Any]) -> None:
        self.store_entity_memory(memory)
        self.store_location_memory(memory)
        self.store_transaction_memory(memory)


    async def insert_milvus_memory(self, text:str, scale_dict: Dict[str, Any],data_store:MilvusDataStore=None) -> None:
        '''
        scale_dict:
        {   
            act_id,
            act_name,
            obj_id,
            obj_name,
            in_building_id,
            in_building_name,
            money,
            emotion,
            timestamp,
            memory,
        } 
        '''
        try:
            embedding = self.embeddings.embed_query(text)
            print(len(embedding))
            dict_to_insert = copy.deepcopy(scale_dict)
            dict_to_insert.update({
                "id": str(uuid.uuid1()), 
                "emb": embedding 
            })
            #the dict should match the collection schema in milvus_constants.py
            if data_store is None: data_store = self.character_milvus_data_store
            response = data_store.insert_data( dict_to_insert )
            # "id": str(uuid.uuid1()),
            # "character_id": scale_dict['character_id'],
            # "character_name": scale_dict['character_name'],
            # "in_building_id": scale_dict['in_building_id'],
            # "in_building_name": scale_dict['in_building_name'],
            # "money": scale_dict["money"],
            # "emotion": scale_dict["emotion"],
            # "timestamp":scale_dict['timestamp'],
            # "surprise_level": scale_dict["surprise_level"],
            # "emb": embedding,
                
            print(response)
        except Exception as e:
            traceback.print_exc()
            if os.getenv('DEBUG'):
                __import__('ipdb').set_trace()
            print(e)
            

    def store_entity_memory(self, memory: Dict[str, Any]) -> None:
        if 'people' in memory:
            for name in list(memory['people'].keys()):
                new_mem = copy.deepcopy(memory["people"][name])
                self.people[name].append(new_mem)

                # if hasattr(self,'character_milvus_data_store'):
                #     self.insert_milvus_memory(
                #         memory=new_mem, #自己构建
                #         data_store=self.character_milvus_data_store
                #     )

    def store_location_memory(self, memory: Dict[str, Any]) -> None:
        if 'building' in memory:
            for name, info in memory['building'].items():

                self.building[name].append(info)

                # if hasattr(self,'character_milvus_data_store'):
                #     self.insert_milvus_memory(
                #         memory=memory,  #自己构建
                #         data_store=self.character_milvus_data_store
                #     )

    def store_transaction_memory(self, memory: Dict[str, Any]) -> None:
        if 'records' in memory:
            for name, info in memory['records'].items():
                self.trade_records[name].append(info)

                # if hasattr(self,'character_milvus_data_store'):
                #     self.insert_milvus_memory(
                #         memory=memory,  #自己构建
                #         data_store=self.character_milvus_data_store
                #     )
    
    @property
    def impression_memory(self) -> Dict[str, Any]:
        return {
            "people": self.people,
            "building": self.building,
        }


    def get_memory(self, main_category, name) -> Dict[str, Any]:
        if main_category == 'people':
            return self.get_people_memory(name)
        elif main_category == 'building':
            return self.get_building_memory(name) 
        else: 
            raise NotImplemented 
            

    def get_people_memory(self, name: str, default=[]) -> Dict[str, Any]:
        return self.people.get(name, default)
    

    def get_building_memory(self, name: str, default=[]) -> Dict[str, Any]:
        return self.building.get(name, default)
    
    def get_records_memory(self, name: str) -> Dict[str, Any]:
        return self.trade_records.get(name, [])
    

    def name_specific_memory_retrieve_from_milvus(self, obj_name: str, query:str,topk:int=4):
        milvus_expression = f"obj_name=='{obj_name}' && act_name=='{self.character_name}'"
        search_param = {
                "data": [self.embeddings.embed_query(text=query)], # 要搜索的query的emb
                "anns_field": "emb", # 要检索的向量字段
                "param": {"metric_type": "COSINE"},
                "limit": topk, # Top K 
                'output_fields': ["text",'timestamp'],   #自定义输出字段
                'expr': milvus_expression,
        }
        search_result:SearchResult = self.character_milvus_data_store.vector_search(
            search_param=search_param,
        )
        return search_result
    
    def buyer_specific_memory_retrieve_from_milvus(self, obj_name: str, query:str, topk:int=4):
        milvus_expression = f"buyer=='{obj_name}'"
        search_param = {
                "data": [self.embeddings.embed_query(text=query)], # 要搜索的query的emb
                "anns_field": "emb", # 要检索的向量字段
                "param": {"metric_type": "COSINE"},
                "limit": topk, # Top K 
                'output_fields': ['resource_id', 'seller', 'timestamp', 'market_price', 'emotion', 'like_score', 'expected_price', 'final_price'],   #自定义输出字段
                'expr': milvus_expression,
        }
        search_result:SearchResult = self.trade_records_milvus_data_store.vector_search(
            search_param=search_param,
        )
        return search_result

    def to_json(self) -> Dict[str, Any]:
        return {
            "people": self.people,
            "experience": self.experience,
            "building": self.building,
        }

    def from_json(self, obj: Dict[str, Any]):
        self.people = obj.get("people", dict())
        self.experience = obj.get("experience", dict())
        self.building = obj.get("building", dict())

    def __repr__(self) -> str:
        return json.dumps(self.impression_memory)

class WorkingMemory:
    # TODO: forget, different type of memory has different forget period, some will be forgotten one state later
    def __init__(self) -> None:
        self.wm = dict()
    
    def retrieve_by_name(self, name, default=None):
        return self.wm.get(name, default)
    
    def store_memory(self, name, memory):
        self.wm[name] = memory
    
    def forget_by_name(self, name):
        if name in self.wm:
            del self.wm[name]
     
    def serialize(self):
        return self.wm
    
    def __repr__(self) -> str:
        return f'{self.wm}'
        
        
class PeopleMemory:
    def __init__(self, name: str, relationship: str, impression: str) -> None:
        self.name = name
        self.relationship = relationship
        self.impression = impression
        self.episodicMemory = list()

    def add_episodic_memory(self, memory: str) -> None:
        self.episodicMemory.append(memory)


class ExperienceMemory:
    def __init__(self, plan: str, acts: List[str]) -> None:
        self.plan = plan
        self.acts = acts


class BuildingMemory:
    def __init__(self, name, relationship, impression) -> None:
        self.name = name
        self.relationship = relationship
        self.impression = impression
        self.episodicMemory = list()

    def add_episodic_memory(self, memory: str) -> None:
        self.episodicMemory.append(memory)



if __name__ == '__main__':
    from langchain_openai import OpenAIEmbeddings
    memory = Memory(character_id=1, character_name='1', embeddings=OpenAIEmbeddings(model="text-embedding-3-large"))
    import asyncio

    #insert
    asyncio.run(memory.insert_milvus_memory(
        scale_dict = {
            "act_id": '1',
            "act_name": '1',
            "obj_id": '00000',
            "obj_name": 'test_building',
            "in_building_id": '00000',
            "in_building_name": 'test_building',
            "money": 15.0,
            "emotion": 'HAPPY',
            "emotion_level": '0.8',
            "timestamp":1234567890,
        },
        text= "I ate shit.",
        data_store=memory.character_milvus_data_store
    ))
    asyncio.run(memory.insert_milvus_memory(
        scale_dict = {
            "act_id": '1',
            "act_name": '1',
            "obj_id": '00000',
            "obj_name": 'test_building',
            "in_building_id": '00000',
            "in_building_name": 'test_building',
            "money": 15.0,
            "emotion": 'HAPPY',
            "emotion_level": '0.8',
            "timestamp":1234567890,
        },
        text = "I drink milk.",
        data_store=memory.character_milvus_data_store
    ))
    # asyncio.run(memory.insert_milvus_memory(
    #     memory = {
    #         "character_id": '12345',
    #         "character_name": 'test_character',
    #         "in_building_id": '00000',
    #         "in_building_name": 'test_building',
    #         "money": 15.0,
    #         "emotion": 'HAPPY',
    #         "timestamp":1234567890,
    #     },
    #     data_store=memory.character_milvus_data_store
    # ))

    #query
    retrieve_res = (memory.name_specific_memory_retrieve_from_milvus(
        obj_name='test_building',
        query="The bar is open.",
        topk=4
    ))
