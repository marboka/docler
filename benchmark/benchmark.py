import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tagmatch.vec_db import Embedder
from tagmatch.logging_config import setup_logging
from tagmatch.vec_db import VecDB
from pydantic_settings import BaseSettings
import pandas as pd
import logging
import concurrent.futures
import onnxruntime as ort

print(ort.get_available_providers())
ort.set_default_logger_severity(3)

class Settings(BaseSettings):
    model_name: str
    cache_dir: str
    qdrant_host: str
    qdrant_port: int
    qdrant_collection: str
    use_reduced_precision: bool
    n_components: int

    class Config:
        env_file = ".env"

settings = Settings()

def embed_and_store(embedder: Embedder, vec_db: VecDB, name:str):
    vector = embedder.embed(name)
    vec_db.store(vector, {"name": name})
    return vector 

def benchmark_process_csv(use_gpu: bool, csv_path: str, num_threads: int = 1):
    embedder = Embedder(model_name=settings.model_name, cache_dir=settings.cache_dir, settings=settings, use_gpu=use_gpu)

    vec_db = VecDB(host=settings.qdrant_host,
               port=settings.qdrant_port,
               collection=settings.qdrant_collection,
               vector_size=embedder.embedding_dim)
    
    df = pd.read_csv(csv_path, sep=None, header=0, engine='python')
    names_storage = df['name'].dropna().unique().tolist()

    start_time = time.time()

    if not use_gpu and num_threads > 1:
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
                results = list(executor.map(lambda name: embed_and_store(embedder, vec_db, name), names_storage))      
    else:
        for name in names_storage:
            embed_and_store(embedder, vec_db, name)
        
    end_time = time.time()
    total_time = end_time - start_time
    
    vec_db.remove_collection()

    logger.info(f"{'GPU' if use_gpu else 'CPU'} Performance:")
    logger.info(f"Total time: {total_time:.2f} seconds")


if __name__ == "__main__":
    if os.path.exists("./benchmark/benchmark_log.txt"):
        os.remove("./benchmark/benchmark_log.txt")
    setup_logging(file_path="benchmark/benchmark_log.txt")
    logger = logging.getLogger("fastapi")

    logger.info("Running CPU benchmark with 1 thread, small dataset...")
    benchmark_process_csv(use_gpu=False, csv_path='tags/dummy_tags.csv', num_threads=1)

    logger.info("Running CPU benchmark with 4 thread, small dataset...")
    benchmark_process_csv(use_gpu=False, csv_path='tags/dummy_tags.csv', num_threads=4)
    
    logger.info("Running GPU benchmark, small dataset...")
    benchmark_process_csv(use_gpu=True,csv_path='tags/dummy_tags.csv')

    logger.info("Running CPU benchmark with 1 thread, large dataset...")
    benchmark_process_csv(use_gpu=False, csv_path='tags/long_dummy_tags.csv', num_threads=1)

    logger.info("Running CPU benchmark with 4 thread, large dataset...")
    benchmark_process_csv(use_gpu=False, csv_path='tags/long_dummy_tags.csv', num_threads=4)
    
    logger.info("Running GPU benchmark, large dataset...")
    benchmark_process_csv(use_gpu=True,csv_path='tags/long_dummy_tags.csv')