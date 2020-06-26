# Docker file to build container image based on 
# a miniconda image from the docker cloud
FROM arm32v7/python:3.7-slim
LABEL maintainer="Sebastian Arboleda <sebasarboleda22@gmail.com>" 
LABEL Name="publisher Version=0.0.1"

COPY requirements/prod.txt /
COPY ./publisher/publisher.py /

RUN apt-get update \
    && apt-get install -y gcc gfortran libopenblas-dev libatlas-base-dev \
    && pip install --no-cache-dir -r prod.txt

CMD /bin/bash -c "python -u publisher.py"
