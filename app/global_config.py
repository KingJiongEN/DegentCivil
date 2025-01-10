import os

MILVUS_HOST = os.environ.get('MILVUS_HOST', 'localhost')
MILVUS_PORT = os.environ.get('MIVUS_PORT', 19530)

MILVUS_INDEX_PARAMS = {
    "metric_type":"COSINE",
    "index_type":"IVF_FLAT",
    "params":{"nlist":64}
}