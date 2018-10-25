# Docker file to build container image based on 
# a miniconda image from the docker cloud
FROM arm32v7/python:3.4-stretch
LABEL maintainer="Sebastian Arboleda <sebasarboleda22@gmail.com>" 
LABEL Name="mqtt-publisher Version=0.0.1"

COPY environment.yml /

RUN apt-get update \
    && md5sum Miniconda3-latest-Linux-armv7l.sh \
    && /bin/bash Miniconda3-latest-Linux-armv7l.sh \
    && conda update conda \
    && apt-get autoremove \
    && apt-get autoclean \
    && conda clean --all --yes

ENV PATH /opt/conda/bin:$PATH

# Create conda environment based on yaml file
RUN conda env create -f environment.yml

COPY ./mqtt_publisher /app
WORKDIR /app
CMD /bin/bash -c "source activate mqtt-publisher && python -u publisher.py"
