FROM python:3.9-bullseye

RUN apt-get update
RUN apt-get install -y gdal-bin libgdal-dev g++

WORKDIR /usr/src

COPY src ./

RUN pip install --no-cache-dir -r requirements.txt

CMD ["gunicorn"  , "-b", "0.0.0.0:80", "app:server"]
