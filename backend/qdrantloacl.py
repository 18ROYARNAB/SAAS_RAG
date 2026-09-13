import pandas as pd
import glob
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# 1. Connect to the local Docker container
client = QdrantClient(url="http://localhost:6333")
collection_name = "ms_marco_index"

# 2. Initialize the collection
# (Change 'size' to match your embedding model, e.g., 768 or 384)
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# 3. Locate all your downloaded Parquet files
# Point this to the folder where HF downloaded the 11.5 GB dataset
parquet_files = glob.glob("./ms_marco_local_shards/*.parquet")

print(f"Found {len(parquet_files)} files. Beginning ingestion...")

# 4. Process each file
for file_path in parquet_files:
    print(f"Loading {file_path}...")
    
    # Read the file into memory
    df = pd.read_parquet(file_path)
    
    # Push the data to Qdrant in batches
    client.upload_collection(
        collection_name=collection_name,
        vectors=df['vector'].tolist(), # Ensure this matches your column name
        payload=df[['docid','text']].to_dict(orient="records"), # Metadata for search context
        ids=df.index.tolist(),
        batch_size=256 # Batching prevents memory spikes
    )
    
print("All shards successfully ingested!")