# Docker file to build container image based on 
# a miniconda image from the docker cloud
FROM arm32v7/python:3.4-stretch
LABEL maintainer="Sebastian Arboleda <sebasarboleda22@gmail.com>" 
LABEL Name="publisher Version=0.0.1"

COPY environment.yml /

ENV PATH /opt/conda/bin:$PATH

RUN apt-get update \
    && wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-armv7l.sh -O ~/miniconda.sh \
    && md5sum ~/miniconda.sh \
    && /bin/bash ~/miniconda.sh -b -p /opt/conda \
    && rm ~/miniconda.sh \
    && conda update conda \
    && apt-get autoremove \
    && apt-get autoclean \
    && conda clean -y --source --tarballs --packages

# Create conda environment based on yaml file
RUN conda env create -f environment.yml

COPY ./publisher /app
WORKDIR /app
CMD /bin/bash -c "source activate publisher && python -u publisher.py"
