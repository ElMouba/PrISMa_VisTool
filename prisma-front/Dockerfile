FROM python:3.10

# Container vars
ENV PYTHONPATH /app

WORKDIR /app

COPY Preset ./Preset
COPY Table ./Table
COPY Figure ./Figure
COPY Line ./Line
COPY Adsorption ./Adsorption
COPY Upload ./Upload
COPY Compare ./Compare
COPY data ./data
COPY serve-app.sh /opt/

ENV XDG_RUNTIME_DIR=/tmp/runtime-user

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# start bokeh server
CMD ["/opt/serve-app.sh"]