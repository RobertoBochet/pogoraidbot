FROM python:3-slim

RUN apt-get update
RUN apt-get install -y libsm6
RUN apt-get install -y tesseract-ocr tesseract-ocr-eng
RUN pip3 install python-telegram-bot \
    opencv-python \
    pytesseract \
    redis

RUN mkdir /app
WORKDIR /app
COPY app/ ./

ENTRYPOINT ./main.py
