#!/bin/bash

printf "\n~~~ Running tests...this can take a few minutes ~~~\n"

# Get project root
PROJECT_ROOT=`pwd`

# Activate conda environment
printf "\nActivating the Conda virtual environment... \n"
source activate publisher

# Run tests with pytest
python3 -m pytest $PROJECT_ROOT -s