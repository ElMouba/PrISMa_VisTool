#!/bin/bash
docker build -t prisma-front .
echo "connect to http://localhost:5006"
docker run --rm -p 5006:5006 -e PORT=5006 -e WORKERS=2 -e CONCURRENCY_LIMIT=2 --name=prisma-front prisma-front