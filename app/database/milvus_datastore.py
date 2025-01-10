from typing import List, Optional, Union
from pymilvus import (
    connections,
    db,
    CollectionSchema, FieldSchema, DataType,
    Collection,
    utility,
    Partition,
)
from pymilvus.orm.collection import (
    MutationResult,
    SearchResult
)
from ..utils.log import LogManager
import os

MILVUS_ALIAS = 'default'
MILVUS_INDEX_PARAMS = {
    "metric_type":"COSINE",
    "index_type":"IVF_FLAT",
    "params":{"nlist":64}
}
MILVUS_CONSISTENCY_LEVEL = os.environ.get("MILVUS_CONSISTENCY_LEVEL") or 'Strong'

class MilvusDataStore():
    MODULE_NAME = 'MilvusDataStore'
    def __init__(
        self,
        host: str = "",
        collection_name: str = "",
        port: int = "",
        alias: str = MILVUS_ALIAS,
        field_schema: CollectionSchema = None,
        index_field: str = 'emb',
        index_params: dict = MILVUS_INDEX_PARAMS,
        scalar_index_fields: Union[str, List[str]] = None,
        create_new: Optional[bool] = False,
        consistency_level: str = "Bounded",
    ):
        """Create a Milvus DataStore.

        The Milvus Datastore allows for storing your indexes and metadata within a Milvus instance.

        Args:
            create_new (Optional[bool], optional): Whether to overwrite if collection already exists. Defaults to True.
            consistency_level(str, optional): Specify the collection consistency level.
                                                Defaults to "Bounded" for search performance.
                                                Set to "Strong" in test cases for result validation.
        """
        # Overwrite the default consistency level by MILVUS_CONSISTENCY_LEVEL
        # self._consistency_level = MILVUS_CONSISTENCY_LEVEL or consistency_level
        self.collection_name = collection_name
        self.port = port
        self.alias = alias
        self.host = host
        self.field_schema = field_schema
        self.index_field = index_field
        self.index_params = index_params
        self.scalar_index_fields = scalar_index_fields
        self._consistency_level = consistency_level
        self._create_connection()
        self._create_collection(self.collection_name, create_new)  # type: ignore
        self._create_index()
        if self.collection:
                self.collection.load()


    def _create_connection(self):
        try:
            self.connection = connections.connect(
                alias=self.alias,
                host=self.host,
                port=self.port,
                #   user='username',
                #   password='password',
                # db_name=db_name, # 指定使用的db，否则默认是'default'
            )
        except Exception as e:
            # 已脱敏，如要修改日志，请注意脱敏问题
            LogManager.log_error(
                # level='error',
                # function=self.MODULE_NAME,
                msg = "Failed to create connection to Milvus server '{}:{}', error: {}".format(self.host, self.port, e)
            )

    def _disconnect(self,):
        connections.disconnect(self.alias)
    
    def _create_collection(self, collection_name:str, create_new: bool = False) -> None:
        """Create a collection based on environment and passed in variables.

        Args:
            create_new (bool): Whether to overwrite if collection already exists.
        """
        # try:
        # If the collection exists and create_new is True, drop the existing collection
        # __import__('ipdb').set_trace()
        if utility.has_collection(collection_name, using=self.alias) and create_new:
            utility.drop_collection(collection_name, using=self.alias)

        # Check if the collection doesnt exist
        if utility.has_collection(collection_name, using=self.alias) is False:
            # If it doesnt exist use the field params from init to create a new schem
            # Use the schema to create a new collection
            self.collection = Collection(
                collection_name,
                schema=self.field_schema,
                using=self.alias,
                consistency_level=self._consistency_level,
            )
            print("Create Milvus collection '{}' with schema {} and consistency level {}"
                                .format(collection_name, self.field_schema, self._consistency_level))
            # if self.collection:
            #     self.collection.load()
        else:
            # If the collection exists, point to it
            self.collection = Collection(
                collection_name, using=self.alias
            )  # type: ignore
            # Which sechma is used
            # if self.collection:
            #     self.collection.load()
        # except Exception as e:
        #     LogManager.log_error(
        #         msg = "Failed to create collection '{}', error: {}".format(collection_name, e),
        #     )
    


    def insert_data(self, data:List[dict]) ->MutationResult:
        return self.collection.insert(data)

    
    def _create_index(self):
            
        self.collection.create_index(
            field_name=self.index_field, 
            index_params=self.index_params
        )
        #create scalar index
        if not self.scalar_index_fields:
            return
        if isinstance(self.scalar_index_fields, list):
            for scalar_index_field in  self.scalar_index_fields:
                index_name = "scalar_index_" + scalar_index_field
                self.collection.create_index(
                    field_name=scalar_index_field, 
                    index_name=index_name,
                )
        elif isinstance(self.scalar_index_fields, str):
            index_name = "scalar_index_" + self.scalar_index_fields
            self.collection.create_index(
                field_name=scalar_index_field, 
                index_name=index_name,
            )
        else:
            raise ValueError("not valid type: scalar_index_fields")

    def drop_index(self, collection_name, index_name=None):
        collection = Collection(collection_name)      # Get an existing collection.
        if index_name is None: # Drop the only index in a collection
            collection.drop_index()
        else: # If a collection contains two or more indexes, specify the name of the index to delete it
            collection.drop_index(index_name=index_name)  

    # 搜索 search & query

    def vector_search(self, search_param:dict) -> SearchResult:
        return self.collection.search(
            **search_param
        )


    def count(self) -> int:
        res = self.collection.query(
        expr="", 
        output_fields = ["count(*)"],
        )
        return int(res[0]['count(*)'])

