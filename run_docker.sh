#!/bin/bash
docker build -t prisma_vis .
echo "connect to http://localhost:5006"
docker run --rm -p 5007:5007 -e PORT=5007 -e WORKERS=2 -e CONCURRENCY_LIMIT=2 --name=prisma_vis prisma_vis