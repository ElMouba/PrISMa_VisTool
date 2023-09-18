#!/bin/bash
echo "buildig image models-dev"
docker build --tag models-dev .

docker stop models-dev
docker container prune

echo "connect to http://localhost:8000"
docker run --rm -p 8000:8000 -e PORT=8000 -e WORKERS=2 -e CONCURRENCY_LIMIT=2 --name=models-dev models-dev