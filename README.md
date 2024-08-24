Task 1. Benchmarking:

1. Created a benchmark folder with a benchmark.py script in it, which measure the Embedding time of tags with CPU with/without multithreading and GPU setups
    The logs are saved to benchmark_log.txt
2. Modified tagmatch/vec_db.py to handle CudaExecutionProdiver in the Embedder
3. I could not setup a correct Cuda/CuDNN version with Docker to utilize my GPU, therefore I could actually measure the time differences between CPU and GPU

TODO: load onnxruntime-gpu and other packages to handle gpu

Important metrics to consider:
1. Processing time: the total time it takes to process all the tags.
    Here we have 4 option, single thread CPU, multi thread CPU, single GPU and multiple GPUs. 
    Single thread CPU will be slower then multi thead CPU
    Single GPU will be slower then multiple GPUs
    But whether CPU is faster or the GPU setup, that depends on the size of our dataset. If we have one thread and one GPU, for smaller dataset, it is faster to process them with CPU, if the model is not yet loaded to the GPU. For larger datasets it is faster to use a single GPU over single CPU threading.

2. Memory and CPU usage can be important and is different for CPU/GPU processing

3. Latency: The time to process a single tag. Very important for real time applications. For example if we always have to load our embedding model to the GPU before processing a tag, that significantly adds to latency. While the word embedding calculation can be faster on GPU than on CPU, not just the processing time matters but everything that can add to latency: moving the model to the GPU, moving the data to the GPU, moving the data from the GPU and uploading to the vector db.

4. Cost: energy cost of running GPU vs CPU can be important and the cost of buying/renting a GPU/CPU is also important and there can be large differences