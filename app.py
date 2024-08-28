import io
import logging
import os
import threading
from typing import List

import pandas as pd
import numpy as np
from fastapi import (BackgroundTasks, FastAPI, File, HTTPException, Request,
                     UploadFile)
from fastapi.responses import JSONResponse
from pydantic_settings import BaseSettings

from tagmatch.fuzzysearcher import FuzzyMatcher
from tagmatch.logging_config import setup_logging
from tagmatch.vec_db import Embedder, VecDB
from tagmatch.synonym_manager import SynonymManager
from tagmatch.vector_reducer import PcaReducer

if not os.path.exists("./data"):
    os.makedirs("./data")

setup_logging(file_path="./data/service.log")


#move this to utils
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

app = FastAPI()
logger = logging.getLogger("fastapi")
# In-memory storage for tags
app.names_storage: List[str] = []

# Placeholder for the semantic search components
embedder = Embedder(model_name=settings.model_name, cache_dir=settings.cache_dir, settings=settings)
vec_db = VecDB(host=settings.qdrant_host,
               port=settings.qdrant_port,
               collection=settings.qdrant_collection,
               vector_size=embedder.embedding_dim)
app.fuzzy_matcher = FuzzyMatcher([])

# Flag to track background task status
task_running = threading.Event()

synonym_manager = SynonymManager(app.names_storage)
if settings.use_reduced_precision:
    pca_reducer = PcaReducer(settings.n_components)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")

    if request.method in ["POST", "PUT", "PATCH"]:
        body = await request.body()
        logger.info(f"Request Body: {body.decode('utf-8')}")

    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


@app.post("/upload-csv/")
async def upload_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if task_running.is_set():
        raise HTTPException(status_code=400, detail="A task is already running. Please try again later.")

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400,
                            detail="Invalid file format. Please upload a CSV file (needs to env with '.csv'.")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content), sep=None, header=0)

    if 'name' not in df.columns:
        raise HTTPException(status_code=400, detail="CSV file must contain a 'name' column.")

    names_storage = df['name'].dropna().unique().tolist()

    if len(names_storage) == 0:
        raise HTTPException(status_code=400, detail="No names found in the CSV file.")

    # Return error if the collection is already existing (and it's populated)
    if vec_db.collection_exists():
        raise HTTPException(status_code=400, detail="Collection already exists. Please delete the collection first.")
    else:
        vec_db._create_collection()

    # Set the flag to indicate that a task is running
    task_running.set()

    # Add background task to process the CSV file
    background_tasks.add_task(process_csv, names_storage)

    return {"message": "File accepted for processing. Names will be extracted and stored in the background."}


@app.post("/upload-synonym-csv/")
async def upload_synonym_csv(background_tasks: BackgroundTasks, file: UploadFile = File(...)):
    if task_running.is_set():
        raise HTTPException(status_code=400, detail="A task is already running. Please try again later.")

    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400,
                            detail="Invalid file format. Please upload a CSV file (needs to env with '.csv'.")

    content = await file.read()
    df = pd.read_csv(io.BytesIO(content), sep=None, header=0)

    if 'word' not in list(df.columns) or 'synonym' not in list(df.columns):
        raise HTTPException(status_code=400, detail="CSV file must contain a 'word' and 'synonym' columns.")

    if len(df) < 1 :
        raise HTTPException(status_code=400, detail="No names found in the CSV file.")

    if synonym_manager.synonyms_exist():
        raise HTTPException(status_code=400, detail="Synonyms already exists. Please delete the synonyms first.")
    
    task_running.set()
    background_tasks.add_task(process_synonym_csv, df)

    return {"message": "File accepted for processing. Names will be extracted and stored in the background."}


def process_csv(names_storage: List[str]):
    try:
        # Store embedded vectors for semantic search
        if not settings.use_reduced_precision:
            for name in names_storage:
                vector = embedder.embed(name)
                vec_db.store(vector, {"name": name})
        else:
            embedding_matrix = np.array([embedder.embed(name) for name in names_storage])
            pca_reducer.fit(embedding_matrix)
            reduced_vectors = pca_reducer.transform(embedding_matrix)
            for name, reduced_vector in zip(names_storage, reduced_vectors):
                vec_db.store(reduced_vector, {"name": name})

        app.names_storage = names_storage
        app.fuzzy_matcher = FuzzyMatcher(app.names_storage)
        synonym_manager.set_names_storage(names_storage)

    finally:
        # Clear the flag to indicate that the task has completed
        task_running.clear()

def process_synonym_csv(dataframe: pd.DataFrame):
    try:
        synonym_manager.set_synonym_csv(dataframe)
    except Exception as e:
        logger.error(f"Error processing synonym CSV: {str(e)}")
    finally:
        task_running.clear()
        logger.info("Synonym CSV processing task finished")


@app.delete("/purge/")
async def delete_collection():
    vec_db.remove_collection()
    app.names_storage = []
    return {"message": "DB deleted successfully."}

@app.delete("/purge-synonym/")
async def delete_synonym_collection():
    synonym_manager.remove_synonym_csv()
    return {"message": "DB deleted successfully."}


@app.get("/search/")
async def search(query: str, k: int = 5):
    if not query:
        raise HTTPException(status_code=400, detail="Query parameter is required.")

    # Fuzzy search
    fuzzy_matches = app.fuzzy_matcher.get_top_k_matches(query, k)

    # Semantic search
    synonym_words = synonym_manager.get_synonym(query.lower())
    logger.info(f"Synonyms found for the word {query.lower()}: {synonym_words}")
    semantic_matches = []
    if synonym_words != None:
        for syn_word in synonym_words:
            query_vector = embedder.embed(syn_word)
            if settings.use_reduced_precision:
                query_vector = pca_reducer.transform(query_vector)
            semantic_matches += vec_db.find_closest(query_vector, k)
        if len(synonym_words) > 1:
            semantic_matches = sorted(semantic_matches, key=lambda x: x.score)
            semantic_matches = list({x.id: x for x in semantic_matches}.values())
            semantic_matches = sorted(semantic_matches, key=lambda x: x.score, reverse=True)[:k]
    else:
        query_vector = embedder.embed(query)
        if settings.use_reduced_precision:
            query_vector = pca_reducer.transform(query_vector)
        semantic_matches = vec_db.find_closest(query_vector, k)       

    # Formatting the response
    semantic_results = [{"name": match.payload["name"], "score": match.score} for match in semantic_matches]
    typo_results = [{"name": match["matched"], "score": match["score"]} for match in fuzzy_matches]

    response = {"match": {"semantic": semantic_results, "typo": typo_results}}

    return JSONResponse(content=response)


@app.get("/task-status/")
async def task_status():
    if task_running.is_set():
        return {"status": "running", "processed_items": vec_db.get_item_count()}
    else:
        return {"status": "finished", "nb_items_stored": vec_db.get_item_count()}
    
@app.get("/task-synonym-status/")
async def task_status():
    if task_running.is_set():
        return {"status": "running", "processed_items": synonym_manager.get_synonym_count()}
    else:
        return {"status": "finished", "nb_items_stored": synonym_manager.get_synonym_count()}




if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
