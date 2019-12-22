FROM python:3.7-slim

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    libsm6 \
    tesseract-ocr \
    tesseract-ocr-eng
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

VOLUME /srv

COPY ./pogoraidbot/requirements.txt /opt/

RUN pip3 install -r /opt/requirements.txt

COPY ./pogoraidbot/ /opt

WORKDIR /opt

ENTRYPOINT python3 /opt/main_docker.py