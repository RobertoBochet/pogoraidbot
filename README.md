[![Codacy Badge](https://api.codacy.com/project/badge/Grade/ffb75961a5854f7d9d429921ea71084b)](https://www.codacy.com/app/RobertoBochet/pogoraidbot?utm_source=github.com&utm_medium=referral&utm_content=RobertoBochet/pogoraidbot&utm_campaign=Badge_Grade)

## Important

**The bot is now in beta version**

## Description

This is a telegram bot to organize PoGo raids, thought for be easy to self-hosted.

If you send a raid screenshot to a group where there is this bot, it identifies the raid an provides you a poll to easily organize the raid.

## Requirements

### Python

The bot needs Python version 3.7 or newer, and the modules that are present in the `requirements.txt` file.

To install the modules use pip:

```bash
$ pip install -r ./pogoraidbot/requirements.txt
```

### Tesseract

The bot needs an installation of Tesseract OCR and a pre-trained neural network for english. Both can be found from the official Arch and Ubuntu repositories.

Refer to this [link](https://github.com/tesseract-ocr/tesseract).

### Redis

The bot requires a Redis database.

Refer to this [link](https://redis.io/).

## Run

The bot needs to know, the bot api token, that you can obtain from [@BotFather](https://telegram.me/BotFather) and the address of redis instance.

To understand how to provide these information to the bot:

```bash
$ python ./pogoraidbot -h
```

```bash
usage: pogoraidbot [-h] [-t TOKEN] [-r REDIS] [-a SUPERADMIN] [-b BOSSES_FILE] [-o BOSSES_EXPIRATION] [-g GYMS_FILE]
                   [-y GYMS_EXPIRATION] [-d DEBUG_FOLDER] [-v] [--info] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        telegram bot token
  -r REDIS, --redis REDIS
                        redis url in "redis://{host}[:port]/{db}" format
  -a SUPERADMIN, --superadmin SUPERADMIN
                        superadmin's id
  -b BOSSES_FILE, --bosses-file BOSSES_FILE
                        JSON or CSV file contains possible pokémons in the raids. It can be also provided over http(s)
  -o BOSSES_EXPIRATION, --bosses-expiration BOSSES_EXPIRATION
                        Validity of the bosses list in hours
  -g GYMS_FILE, --gyms-file GYMS_FILE
                        JSON file contains gyms and their coordinates. It can be also provided over http(s)
  -y GYMS_EXPIRATION, --gyms-expiration GYMS_EXPIRATION
                        Validity of the gyms list in hours
  -d DEBUG_FOLDER, --debug-folder DEBUG_FOLDER
                        debug folder
  -v                    number of -v specifics level of verbosity
  --info                equal to -vv
  --debug               equal to -vvv

```

An example:

```bash
$ python ./pogoraidbot -t [BOT_TOKEN] -r redis://127.0.0.1:6379/0
```

## Dockerized version \[recommended]

If you don't want to manage this bot as a standalone application you can use the dockerized version.

You can find it in the **docker** branch.

## Credits

In this project are used the following Python libraries:

-   [python-telegram-bot](https://python-telegram-bot.org/) (LGPLv3 License)
-   [opencv-python](https://pypi.org/project/opencv-python/) (MIT License)
-   [pytesseract](https://pypi.org/project/pytesseract/) (GPLv3 License)
-   [redis](https://pypi.org/project/redis/) (MIT License)
-   [jinja2](https://pypi.org/project/Jinja2/) (BSD License)
-   [requests](https://pypi.org/project/requests/) (Apache 2.0 License)
-   [schema](https://pypi.org/project/schema/) (MIT License)
-   [APScheduler](https://pypi.org/project/APScheduler/) (MIT License)
-   [mpu](https://pypi.org/project/mpu/) (MIT License)
