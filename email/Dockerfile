FROM python:3.8-slim-buster

COPY . .

RUN apt-get update && \
    apt-get -y install --no-install-recommends git build-essential wkhtmltopdf && \
    rm -rf /var/lib/apt/lists/* \
    which wkhtmltopdf


COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD uvicorn main:app --host=0.0.0.0 --port=$PORT --workers=2 --loop="uvloop" --http="httptools" --log-config=logging.ini --limit-concurrency=6