docker stop prisma-front
docker container prune

docker build -t prisma-front . --no-cache

