import time
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tagmatch.vec_db import Embedder
from tagmatch.logging_config import setup_logging
from pydantic_settings import BaseSettings
import pandas as pd
import logging

class Settings(BaseSettings):
    model_name: str
    cache_dir: str
    qdrant_host: str
    qdrant_port: int
    qdrant_collection: str

    class Config:
        env_file = ".env"

settings = Settings()


def benchmark_process_csv(use_gpu: bool, csv_path: str):
    embedder = Embedder(model_name=settings.model_name, cache_dir=settings.cache_dir, use_gpu=use_gpu)
    
    df = pd.read_csv(csv_path, sep=None, header=0, engine='python')
    names_storage = df['name'].dropna().unique().tolist()

    start_time = time.time()

    for name in names_storage:
        vector = embedder.embed(name)
        
    end_time = time.time()
    total_time = end_time - start_time

    logger.info(f"{'GPU' if use_gpu else 'CPU'} Performance:")
    logger.info(f"Total time: {total_time:.2f} seconds")


if __name__ == "__main__":
    if os.path.exists("./benchmark/benchmark_log.txt"):
        os.remove("./benchmark/benchmark_log.txt")
    setup_logging(file_path="benchmark/benchmark_log.txt")
    logger = logging.getLogger("fastapi")

    logger.info("Running GPU benchmark...")
    benchmark_process_csv(use_gpu=False, csv_path='tags/dummy_tags.csv')
    
    logger.info("Running GPU benchmark...")
    benchmark_process_csv(use_gpu=True,csv_path='tags/dummy_tags.csv')