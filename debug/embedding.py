from langchain_openai import OpenAIEmbeddings
import os
import numpy as np
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
embed = embeddings.embed_query('Pediatric nurse, loves children. BAD BAD BAD')
print(np.array(embed).min())