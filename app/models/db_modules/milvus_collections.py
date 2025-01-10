from langchain_openai import OpenAIEmbeddings
from app.database.milvus_constants import ARTWORK_MILVUS_FILED_SCHEMA
from app.database.milvus_datastore import MilvusDataStore
from app.global_config import MILVUS_HOST, MILVUS_INDEX_PARAMS, MILVUS_PORT
from pymilvus.orm.collection import (
    SearchResult
)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")

ARTWORK_COLLECTION_NAME = 'artwork_collection'
artwork_milvus_data_store = MilvusDataStore(
                host=MILVUS_HOST,
                port=MILVUS_PORT,
                collection_name=ARTWORK_COLLECTION_NAME,
                field_schema=ARTWORK_MILVUS_FILED_SCHEMA,
                index_field='prompt_emb',
                index_params= MILVUS_INDEX_PARAMS,
            )


def retrieve_artwork_by_prompt_emb(query:str, topk=100, other_param=None):
        search_param = {
                "data": [embeddings.embed_query(text=query)], # 要搜索的query的emb
                "anns_field": "prompt_emb", # 要检索的向量字段
                "param": {"metric_type": "COSINE"},
                "limit": topk, # Top K 
                'output_fields': ['timestamp', 'resource_id'],   #自定义输出字段
                # 'expr': milvus_expression,
        }
        if other_param is not None: search_param.update(other_param)
        search_result:SearchResult = artwork_milvus_data_store.vector_search(
            search_param=search_param,
        )
        return search_result