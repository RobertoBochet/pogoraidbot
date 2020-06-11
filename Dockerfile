FROM python:3.7-slim

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    libsm6 \
    tesseract-ocr \
    tesseract-ocr-eng
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

VOLUME /srv

COPY ./pogoraidbot/requirements.txt /pogoraidbot/

RUN pip3 install -r /pogoraidbot/requirements.txt

COPY ./pogoraidbot/ /pogoraidbot

ENTRYPOINT python3 -m pogoraidbot -e