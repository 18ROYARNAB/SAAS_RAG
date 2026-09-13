from langfuse import observe
from sentence_transformers import CrossEncoder, SentenceTransformer

from backend.dataschemapydantic import queryrequest

model_name="BAAI/bge-reranker-base"
encoder=CrossEncoder(model_name)

@observe
def crossencoderfunction(query,retrievedchunks:list[str],top_n:int=3):
    if not retrievedchunks:
        return[]
    
    pair=[[query,chunk['text']] for chunk in retrievedchunks]
    scores = encoder.predict(pair)
    scored_chunk = [
        {"id":chunk['id'],"text": chunk['text'], "score": score.item()} 
        for chunk, score in zip(retrievedchunks, scores)
    ]
    scored_chunk.sort(key=lambda x: x["score"], reverse=True)
    return scored_chunk[:top_n]