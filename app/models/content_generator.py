
import copy
import traceback

from langchain_openai import OpenAIEmbeddings
from ..llm.llm_expends.dalle3 import DALLE3Caller
import asyncio
import uuid
from PIL import Image
from autogen.agentchat.contrib.img_utils import _to_pil, get_image_data
from typing import List, Union
from diskcache import Cache
import os
from typing import Dict, Any

# from .db_modules.milvus_collections import artwork_milvus_data_store
from ..repository.artwork_repo import add_artwork_to_db
from ..global_config import MILVUS_HOST, MILVUS_PORT, MILVUS_INDEX_PARAMS
from ..database.milvus_datastore import MilvusDataStore
from ..database.milvus_constants import ARTWORK_MILVUS_FILED_SCHEMA

class Drawing:
    def __init__(self, id: str, owner: 'Character', image_url: str, description: str) -> None:
        self.id: str = id
        self.owner: 'Character' = owner
        self.image_url: str = image_url
        self.description: str = description
        self.price = None
        self.timestamp = owner.date_num
        self.sanity_check()
        self.owner.add_artwork('Drawing', self)
        self.store_locally('./drawing')
     
    @classmethod
    async def a_draw(cls, prompt: str, owner: 'Character', api_key:str=None) -> 'Drawing':
        '''
        Deprecated, use DALLEAgent.a_draw instead
        '''
        caller = DALLE3Caller(api_key=api_key)
        llm_task = asyncio.create_task(caller.ask(prompt))
        image_url = await llm_task
        _id = str(uuid.uuid4())
        print(f"Drawing id: {_id}")
        try:
            return cls(_id, owner, image_url, prompt)
        except Exception as e:
            print(f"Error creating Drawing: {e}")
            return await Drawing.a_draw(prompt, owner, api_key) 
    
    def sanity_check(self) -> bool:
        assert type(self.id) == str,f' the type of id should be str, your type of {self.id} is {type(self.id)}  '
        assert type(self.image_url) == str and self.image_url.startswith('http'),f' the type of image_url should be str and the url should start with http, your type of url is {type(self.image_url)}, and url is {self.image_url[:10]}  ' 
        assert type(self.description) == str,f' the type of description should be str, your type of {self.description} is {type(self.description)}  '
    
    def set_price(self, price: int) -> None:
        self.price = price
    
    @property
    def image(self) -> Image:
        image_data = get_image_data(self.image_url)
        return _to_pil(image_data)
    
    def store_locally(self, dir):
        os.makedirs(dir, exist_ok=True)
        self.image.save(f'{dir}/{self.id}.png')
    
    def __eq__(self, __value: Union['Drawing', str]) -> bool:
        if isinstance(__value, Drawing):
            return self.id == __value.id
        elif isinstance(__value, str):
            return self.id == __value
        else:
            raise ValueError(f"Invalid comparison between Drawing and {type(__value)}")
        
    def __getstate__(self) -> object:
        state = self.__dict__.copy()
        state['owner'] = self.owner.name
        return state

    def __setstate__(self, state: object) -> None:
        self.__dict__.update(state)
        

class DrawingList:
    ARTWORK_COLLECTION_NAME = 'artwork_collection'
    def __init__(self, owner: 'Character') -> None:
        self.cache = Cache(os.path.join('.drawings', owner.name))
        self.drawings: List[Drawing] = []
        self.owner = owner
        for d in self.cache:
            drawing = self.cache[d]
            drawing.owner = owner
            self.drawings.append(drawing)
            
        if os.getenv('Milvus'):
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
            # self.artwork_milvus_data_store = artwork_milvus_data_store
            self.artwork_milvus_data_store = MilvusDataStore(
                host=MILVUS_HOST,
                port=MILVUS_PORT,
                collection_name=self.ARTWORK_COLLECTION_NAME,
                field_schema=ARTWORK_MILVUS_FILED_SCHEMA,
                index_field='prompt_emb',
                index_params= MILVUS_INDEX_PARAMS,
            )
    
    def __len__(self) -> int:
        return len(self.drawings)
    
    def __iter__(self):
        return iter(self.drawings)
    
    def __str__(self) -> str:
        return str([d.id for d in self.drawings])
    
    def __getitem__(self, index: int) -> Drawing:
        return self.drawings[index]
    
    def __contains__(self, __value: object) -> bool:
        if isinstance(__value, Drawing):
            return __value in self.drawings
        elif isinstance(__value, str):
            return __value in [d.id for d in self.drawings]
        else:
            raise ValueError(f"Invalid comparison between Drawing and {type(__value)}")
    
    def add(self, drawing: Drawing):
        self.cache.set(drawing.id, drawing)
        self.drawings.append(drawing)
        info_dict = {
                "id": drawing.id,
                "resource_id": drawing.id,
                "resource":  drawing.id,
                "artwork_type": "Drawing",
                "prompt": drawing.description,
                "create_place_id": self.owner.in_building_id,
                "create_place_name": self.owner.in_building_name,
                "timestamp": drawing.timestamp,
                "creator_money": self.owner.money,
                "emotion": self.owner.emotion.extreme_emotion_name,
                "emotion_level": self.owner.emotion.extreme_emotion_value,
                "owner_id": self.owner.guid,
                "owner_name": self.owner.name,
                "price": drawing.price if drawing.price is not None else 0,
            }
        add_artwork_to_db(info_dict=info_dict)
        if os.getenv('Milvus'):
            scale_dict = copy.deepcopy(info_dict)
            
            for k in scale_dict.keys():
                assert scale_dict[k] is not None, f"key {k} is None"
                if k == 'timestamp': continue
                scale_dict[k] = str(scale_dict[k])
                
            self.insert_milvus_memory(prompt_text=drawing.description, scale_dict=scale_dict, data_store=self.artwork_milvus_data_store)
        
    def get(self, id: str):
        for drawing in self.drawings:
            if drawing.id == id:
                return drawing
        return None
    
    def remove(self, drawing: Union[Drawing, str]):
        if drawing in self.drawings:
            self.drawings.remove(drawing)
            self.cache.pop(drawing.id)
            return True
        else:
            return False
        
    def insert_milvus_memory(self, prompt_text:str, scale_dict: Dict[str, Any],data_store:MilvusDataStore=None) -> None:
        try:
            embedding = self.embeddings.embed_query(prompt_text)
            if os.getenv('DEBUG'): print(f"len of embedding {len(embedding)}")
            dict_to_insert = copy.deepcopy(scale_dict)
            dict_to_insert.update({
                # "id": str(uuid.uuid1()), 
                "prompt_emb": embedding 
            })
            if data_store is None: data_store = self.artwork_milvus_data_store
            response = data_store.insert_data( dict_to_insert )
            
            print(response)
        except Exception as e:
            traceback.print_exc()
            if os.getenv('DEBUG'):
                __import__('ipdb').set_trace()
            print(e)
            