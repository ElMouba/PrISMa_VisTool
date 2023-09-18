docker stop clean-cif
docker container prune

docker build -t cleaning-cif . --no-cache