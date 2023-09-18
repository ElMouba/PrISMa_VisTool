docker stop email-dev
docker build -t email-dev .
docker run --rm -p 8030:8030 -e PORT=8030 -e WORKERS=2 -e CONCURRENCY_LIMIT=2 --name=email-dev email-dev