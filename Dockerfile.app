FROM python:3.9-slim

RUN apt-get update && apt-get install -y gcc

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .


# FROM nvidia/cuda:12.6.0-cudnn-devel-ubuntu22.04
# #FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04
# #FROM nvidia/cuda:11.8.0-cudnn8-devel-ubuntu22.04

# ENV CUDA_VISIBLE_DEVICES=0
# ENV TORCH_CUDA_ARCH_LIST="5.0"

# ENV CUDA_HOME=/usr/local/cuda
# ENV PATH=${CUDA_HOME}/bin:${PATH}
# ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}

# RUN echo 'if [ -d "/usr/local/cuda" ]; then' >> /root/.bashrc && \
#     echo '    PATH=/usr/local/cuda/bin${PATH:+:${PATH}}' >> /root/.bashrc && \
#     echo '    LD_LIBRARY_PATH=/usr/local/cuda/targets/x86_64-linux/lib/${LD_LIBRARY_PATH:+:${LD_LIBRARY_PATH}}' >> /root/.bashrc && \
#     echo 'fi' >> /root/.bashrc


# RUN echo "/usr/local/cuda/lib64" >> /etc/ld.so.conf.d/cuda.conf && \
#     ldconfig
# RUN ln -s /usr/local/cuda/lib64/libcudnn.so.8 /usr/local/cuda/lib64/libcudnn.so && \
#     ln -s /usr/local/cuda/lib64/libcudnn.so.8 /usr/lib/x86_64-linux-gnu/libcudnn.so.8 && \
#     ln -s /usr/local/cuda/lib64/libcublasLt.so.12 /usr/local/cuda/lib64/libcublasLt.so.11 && \
#     ln -s /usr/local/cuda/lib64/libcublas.so.12 /usr/local/cuda/lib64/libcublas.so.11
# RUN apt update && apt install libcudnn8
# RUN apt install libcudnn8
# RUN apt install libcudnn8-dev
# RUN apt install libcudnn8-samples
# WORKDIR /app
# RUN apt-get update && apt-get install -y gcc
# RUN apt-get install python3-pip -y
# WORKDIR /app
# COPY requirements.txt .
# RUN pip3 install --no-cache-dir --upgrade pip setuptools wheel
# RUN pip3 install --no-cache-dir -r requirements.txt
# COPY . .
# CMD ["/bin/bash", "-c", "source /root/.bashrc && bash"]


#FROM python:3.9-slim
# FROM nvidia/cuda:12.2.2-cudnn8-devel-ubuntu22.04
# RUN apt-get update && apt-get install -y gcc
# ENV CUDA_VISIBLE_DEVICES=0
# ENV TORCH_CUDA_ARCH_LIST="5.0"

# ENV CUDA_HOME=/usr/local/cuda
# ENV PATH=${CUDA_HOME}/bin:${PATH}
# ENV LD_LIBRARY_PATH=${CUDA_HOME}/lib64:${LD_LIBRARY_PATH}
# RUN apt install wget -y
# RUN wget https://developer.download.nvidia.com/compute/cuda/repos/debian12/x86_64/cuda-keyring_1.1-1_all.deb
# RUN dpkg -i cuda-keyring_1.1-1_all.deb
# RUN apt-get install software-properties-common -y
# #RUN add-apt-repository contrib
# RUN apt-get update
# RUN apt-get -y install cuda-toolkit-12-6

# RUN apt install libcudnn8 -y --allow-change-held-packages
# RUN apt install libcudnn8-dev -y --allow-change-held-packages
# RUN apt install libcudnn8-samples -y --allow-change-held-packages
# RUN echo "/usr/local/cuda/lib64" >> /etc/ld.so.conf.d/cuda.conf && \
#     ldconfig
# RUN ln -s /usr/local/cuda/lib64/libcufft.so.11 /usr/local/cuda/lib64/libcufft.so.10
# RUN ln -s /usr/local/cuda/lib64/libcudart.so.12 /usr/local/cuda/lib64/libcudart.so.11
# RUN ln -s /usr/local/cuda/lib64/libcudart.so.12 /usr/local/cuda/lib64/libcudart.so.11.0
# RUN ln -s /usr/local/cuda/lib64/libcublasLt.so.12 /usr/local/cuda/lib64/libcublasLt.so.11 
# RUN ln -s /usr/local/cuda/lib64/libcublas.so.12 /usr/local/cuda/lib64/libcublas.so.11
# WORKDIR /app
# COPY requirements.txt .
# RUN apt-get install python3-pip -y
# RUN pip install -r requirements.txt
# COPY . .