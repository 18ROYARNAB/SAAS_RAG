from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

client=QdrantClient(url="http://localhost:6333")
model_name="BAAI/bge-small-en-v1.5"
model=SentenceTransformer(model_name)

def query_search(query):
    
    query_vector = model.encode(query).tolist()
    results = client.query_points(
        collection_name="ms_marco_index",
        query=query_vector,
        limit=40 # Return the closest matches
    )
    # Display the retrieved documents
    extracted_chunks=[]
    for rank, point in enumerate(results.points, 1):
        text_data = point.payload.get('text', '')
        docid=point.payload.get("docid",point.id)
        extracted_chunks.append({
            "id":docid,
            "text":text_data
            })
        
        # Optional: Print to your terminal
        print(f"--- Rank {rank} | Match Score: {point.score:.4f} ---")
        print(f"{point.payload.get('docid')}")
        
    # 4. Return the list of 40 strings to feed into the Cross-Encoder
    return extracted_chunks