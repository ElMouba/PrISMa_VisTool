#!/bin/bash

echo "connect to http://localhost:8099"
docker run --rm -p 8099:8099 -e PORT=8099 -e WORKERS=2 -e CONCURRENCY_LIMIT=2 --name=clean-cif cleaning-cif