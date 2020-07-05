FROM arm32v7/python:3.7
LABEL maintainer="Sebastian Arboleda <sebastian.a.arboleda@loins.enc.edu>" 
LABEL Name="publisher Version=0.1.0"

COPY requirements/ /requirements
COPY ./publisher/ /publisher
COPY ./tests /tests
COPY ./run.py /

RUN apt-get update \
    && apt-get install --no-install-recommends -y gcc build-essential gfortran libopenblas-dev libatlas-base-dev \
    && pip install --no-cache-dir -r ./requirements/prod.txt

CMD /bin/bash -c "python run.py"
