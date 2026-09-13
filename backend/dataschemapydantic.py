from pydantic import BaseModel


class queryrequest(BaseModel):
    query:str
    
class ScoredChunk(BaseModel):
    id:int | str
    chunk:str
    score:float

class QueryResponse(BaseModel):
    results: list[ScoredChunk]