FROM python:3.10

# Container vars
ENV PYTHONPATH /app

COPY Preset ./Preset
COPY Table ./Table
COPY Figure ./Figure
COPY Line ./Line
COPY Adsorption ./Adsorption
COPY Upload ./Upload
COPY Compare ./Compare
COPY data ./data
COPY serve-app.sh /opt/

RUN pip install bokeh==3.0.3 pandas==1.3.5 panel Flask==2.0.3 Jinja2==3.1.1
            
# start bokeh server
EXPOSE 5006
CMD ["/opt/serve-app.sh"]