#!/bin/bash

# Build the Docker image
docker build -t python-log-api .

# Run multiple containers
for i in {1..3}; do
    port=$((5000 + i))
    docker run -d -p $port:5000 -v $(pwd):/app --name python-log-api-container-$i python-log-api
done
