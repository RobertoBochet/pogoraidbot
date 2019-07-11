## Important

**The bot now is in alpha version**

## Description

A telegram bot to organize PoGo raid that it can be self hosted.

If you publish a raid screenshot in a group where this bot is present, it identifies the raid an provides you a poll to organize the raid.

## Requirements

### Python
The bot needs Python version 3.7 or newer, and the modules that are present in the `requirements.txt` file.

To install the modules use pip:
```bash
$ pip install -r requiremtns.txt
```

### Tesseract
The bot needs an installation of Tesseract OCR and a pre-trained neural network for english. Both can be found from the official Arch and Ubuntu repositories.

Refer to this [link](https://github.com/tesseract-ocr/tesseract).

### Redis
The bot requires a dedicated instance of Redis database.

Refer to this [link](https://redis.io/).

## Run

The bot needs to know, the bot api token, that you can obtain from [@BotFather](https://telegram.me/BotFather) and the address of redis instance.

To understand how to provide these informations to the bot:
```bash
$ python ./main.py -h
```
```
usage: main.py [-h] [-t TOKEN] [-r HOST] [-p PORT] [-d DEBUG_FOLDER]

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        telegram bot token
  -r HOST, --host HOST  redis host
  -p PORT, --port PORT  redis port
  -d DEBUG_FOLDER, --debug-folder DEBUG_FOLDER
                        debug folder
```

An example:
```bash
$ python ./main.py -t [BOT_TOKEN] -r 127.0.0.1 -p 6379
```

The parameters can be provided also as environment variables.

## Dockerized version \[recommended\]

If you don't want to manage the this bot as a standalone application you can use the dockerized version.

You can find it in this [repo](https://github.com/RobertoBochet/pogoraidbot-dockerized).