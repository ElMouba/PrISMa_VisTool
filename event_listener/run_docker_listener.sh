docker stop listener
docker build -t listener .
docker run -d --name=listener listener
