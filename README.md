Branches: 
- main: starter code, no modification
- feature/benchmark - task1 solution
- feature/manual_synonym - task2 solution
- feature/size_optimization - task2 + task3 solution
- feature/final-soltuion - taks1 + task2 + task3 solutions


### Task 1. Benchmarking:

1. Created a benchmark folder with a benchmark.py script in it, which measure the Embedding time of tags with CPU with/without multithreading and GPU setups
    The logs are saved to benchmark_log.txt
2. Modified tagmatch/vec_db.py to handle CudaExecutionProdiver in the Embedder
3. I could not setup a correct Cuda/CuDNN version with Docker to utilize my GPU, therefore I could actually measure the time differences between CPU and GPU

Important metrics to consider:
1. Processing time: the total time it takes to process all the tags.
    Here we have 4 option, single thread CPU, multi thread CPU, single GPU and multiple GPUs. 
    Single thread CPU will be slower then multi thead CPU
    Single GPU will be slower then multiple GPUs
    But whether CPU is faster or the GPU setup, that depends on the size of our dataset. If we have one thread and one GPU, for smaller dataset, it is faster to process them with CPU, if the model is not yet loaded to the GPU. For larger datasets it is faster to use a single GPU over single CPU threading.

2. Memory and CPU usage can be important and is different for CPU/GPU processing

3. Latency: The time to process a single tag. Very important for real time applications. For example if we always have to load our embedding model to the GPU before processing a tag, that significantly adds to latency. While the word embedding calculation can be faster on GPU than on CPU, not just the processing time matters but everything that can add to latency: moving the model to the GPU, moving the data to the GPU, moving the data from the GPU and uploading to the vector db.

4. Cost: energy cost of running GPU vs CPU can be important and the cost of buying/renting a GPU/CPU is also important and there can be large differences

### Task 2 - Manual Tag Overrides
I reused previous components and implemented a similar setup for uploading and handling synonyms as for uploading and handling words.
#### New Gradio Page for Synonym Upload
I created a new page in Gradio where you can upload a synonym CSV. The CSV should have the following structure: <br />
<pre>word,synonym
Moon,Apollo 11
Moon,Moon Mission</pre>
**Note:** Words should not have leading or trailing spaces in the CSV. The CSV is case-insensitive. 

#### Upload Process
1. First, upload your CSV of words.
2. Then, upload your synonym CSV.

**Important:** Synonyms are checked against the words in the first CSV. We ignore any words from the synonym CSV that are not present in the words CSV. Users are informed of this design choice in the information section on the "Upload Synonym CSV" tab.

#### New endpoints:
I created the following endpoints:
- /upload-synonym-csv/
- /purge-synonym/
- /task-synonym-status/

#### Synonym management
A new class handling all synonym-related logic was created: tagmatch/synonym_manager.py
Unit tests were added in test/synonym_manager_test.py
In this solution, synonyms are symmetric and transitive

#### Quaery process in `app.py`
When querying a word:
1. Check if synonyms are defined for it
2. If synonyms exist:
    - Query the synonyms from vector db
    - Combine search results
    - Filter out duplicates, keep one with higher score
    - Sort by semantic similarity
    - Show only top k results
3. If no synonyms, query the original word

<br />

### Task 3 - Size Optimization
Implemented PCA for dimensionality reduction of embedding vectors.  
**Rationale:**
- Unsupervised method, easier to fit and doesn't require human evaluation
- Scalable through incremental fitting (not implemented in this version)
- Alternatives: SVD (similar advantages) or autoencoders (potentially better reduction but requires retraining for updates), vector quantization (storage efficiency and increased search speed, potentially reduced efficiency in fine grained semantic distinction)

**Implementation:**
- Logic in `tagmatch/vector_reducer.py`
- New .env variables: USE_REDUCED_PRECISION and N_COMPONENTS (for pca components)

**How to measure reduced vector performance?**  
App performance:  
We can first of all measure the performance of the application (how fast it is to use reduced vs normal vectors). If we use PCA, the uploading and querying from the database is faster, to fit and transform the data with PCA, adds extra time. It also adds extra compute power and RAM usage. But it has benefits: we now have vectors with a smaller size.

Semantic search accuracy:  
It is important to measure how different query results we get, if we use reduced vectors. As a query returns two things: an ordered list of words and a score for each words, we should measure these two things. I was unable to find a metric which incorporates the ranked words plus their scores, but we can measure these seperately.  
To measure what words are recommended we can use Jacard index, for example. This treats the query results as sets only. This metric should only be used when it is more important which words we return, rather their score. Here the ground thruth should be the original qury results.  
If we are interested in the score as well but not the order, we can calculate RMSE for the scores. We also have to incormporate that the returned words can have mismathces between the ground truth query results and the pca query results. To accomodate our metric, we should only calculate RMSE for the words which are in both sets, and add a penalty term for missing query results. I impemented this metric in `test/modified_rmse.py`. I also added some test cases to show different results and to show that this metric is between 0 and 1. The penalty I gave is 1, if we have a mismatch between the sets, but this value can be reduced.

