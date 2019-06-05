FROM python:3-slim

RUN mkdir /app
WORKDIR /app
COPY app/ ./

RUN apt-get update
RUN apt-get install -y tesseract-ocr tesseract-ocr-eng
RUN pip3 install -r ./requirements.txt

ENTRYPOINT ./main.py
