import json

import redis
from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from langfuse import observe

from backend.trialserach import query_search

from .crossencoder import crossencoderfunction
from .dataschemapydantic import queryrequest
from .llmclient import llm_answer, reqwritequery

load_dotenv() 

app=FastAPI()
router=APIRouter()
redis_client=redis.Redis(host="localhost",port=6379,db=0,decode_responses=True)
CACHE_TTL=60


@app.get('/')

async def read_root():
    return {"hello":"welcome"}



@app.post('/query')
@observe
async def results(request: queryrequest):
    uquery = request.query.strip().lower()
    cache_key = f"rag_cache:{uquery}"
    # redis cache check
    cached_response = redis_client.get(cache_key)
    if cached_response:
        print("CACHE HIT! Returning result instantly from Redis.")
        return json.loads(cached_response)
    
    print("CACHE MISS. Running full RAG pipeline...")
    
    rewritten_query = await reqwritequery(uquery)
    chunks = query_search(rewritten_query)
    sorted_chunk = crossencoderfunction(rewritten_query, chunks)
    final_result = await llm_answer(rewritten_query, sorted_chunk)
    
    # unified response payload
    response_data = {
        "source": "retrieval",
        "optimized_query": rewritten_query,
        "results": final_result
    }
    
    # Guard cache against error/fallback states
    is_error_response = "unable to generate" in final_result.lower() or "error" in final_result.lower()
    
    if not is_error_response:
        redis_client.setex(cache_key, CACHE_TTL, json.dumps(response_data))
    else:
        print("Skipping Redis cache write due to fallback/error state.")
        
    return response_data    
