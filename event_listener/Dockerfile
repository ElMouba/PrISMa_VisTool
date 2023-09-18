FROM python:3.8-slim-buster


COPY main.py ./main.py
COPY . .

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "/main.py"]
