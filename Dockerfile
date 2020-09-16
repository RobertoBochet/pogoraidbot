FROM python:3.8-alpine as compiler

WORKDIR /srv

COPY setup.py ./
COPY README.md ./
COPY pogoraidbot ./pogoraidbot

RUN python3 setup.py sdist bdist_wheel

FROM python:3.8-slim

RUN apt-get update
RUN apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    tesseract-ocr \
    tesseract-ocr-eng
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

VOLUME /srv

COPY --from=compiler /srv/dist/*.whl /

RUN pip3 install *.whl

ENTRYPOINT python3 -m pogoraidbot -e