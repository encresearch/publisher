#!/bin/bash

printf "\n~~~ Running tests...this can take a few minutes ~~~\n"

# Get project root
PROJECT_ROOT=`pwd`

# Run tests with pytest
python3 -m pytest $PROJECT_ROOT -s