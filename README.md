[![Codacy Badge](https://app.codacy.com/project/badge/Grade/dcfaeb382e18477491720692ea2f818f)](https://www.codacy.com/manual/RobertoBochet/pogoraidbot?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=RobertoBochet/pogoraidbot&amp;utm_campaign=Badge_Grade)
[![GitHub](https://img.shields.io/github/license/robertobochet/pogoraidbot?color=blue)](https://github.com/RobertoBochet/pogoraidbot/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/pogoraidbot?color=yellow)](https://pypi.org/project/pogoraidbot/)
[![GitHub Workflow Status](https://img.shields.io/github/workflow/status/robertobochet/pogoraidbot/Upload%20Python%20Package?label=pypi%20build)](https://pypi.org/project/pogoraidbot/)
[![Docker Image Version (latest semver)](https://img.shields.io/docker/v/robertobochet/pogoraidbot?color=blue&label=docker%20version&sort=semver)](https://hub.docker.com/r/robertobochet/pogoraidbot)
[![Docker Cloud Build Status](https://img.shields.io/docker/cloud/build/robertobochet/pogoraidbot)](https://hub.docker.com/r/robertobochet/pogoraidbot)

## Important

**The bot is now in beta version**

## Description

A telegram bot to organize PoGo raid that it can be self hosted.

If you publish a raid screenshot in a group where this bot is present, it identifies the raid an provides you a poll to organize the raid.

## Requirements

### Python

The bot needs Python version 3.7 or newer.

You can install `pogoraidbot` from `pypi`:

```bash
$ pip install pogoraidbot
```

### Tesseract

The bot needs an installation of Tesseract OCR and a pre-trained neural network for english. Both can be found from the official Arch and Ubuntu repositories.

Refer to this [link](https://github.com/tesseract-ocr/tesseract).

### Redis

The bot requires a dedicated instance of Redis database.

Refer to this [link](https://redis.io/).

## Run

The bot needs to know, the bot api token, that you can obtain from [@BotFather](https://telegram.me/BotFather) and the address of redis instance.

To understand how to provide these information to the bot:

```bash
$ python3 -m pogoraidbot
```

```bash
usage: pogoraidbot [-h] [-t TOKEN] [-r REDIS] [-a SUPERADMIN] [-b BOSSES_FILE] [-o BOSSES_EXPIRATION]
                   [-g GYMS_FILE] [-y GYMS_EXPIRATION] [-e] [-d DEBUG_FOLDER] [-v] [--info] [--debug]

optional arguments:
  -h, --help            show this help message and exit
  -t TOKEN, --token TOKEN
                        telegram bot token
  -r REDIS, --redis REDIS
                        redis url in "redis://{host}[:port]/{db}" format
  -a SUPERADMIN, --superadmin SUPERADMIN
                        superadmin's id
  -b BOSSES_FILE, --bosses-file BOSSES_FILE
                        JSON or CSV file contains possible pokémons in the raids. It can be also
                        provided over http(s)
  -o BOSSES_EXPIRATION, --bosses-expiration BOSSES_EXPIRATION
                        Validity of the bosses list in hours
  -g GYMS_FILE, --gyms-file GYMS_FILE
                        JSON file contains gyms and their coordinates. It can be also provided over
                        http(s)
  -y GYMS_EXPIRATION, --gyms-expiration GYMS_EXPIRATION
                        Validity of the gyms list in hours
  -e, --env             Use environment variables for the configuration
  -d DEBUG_FOLDER, --debug-folder DEBUG_FOLDER
                        debug folder
  -v                    number of -v specifics level of verbosity
  --info                equal to -vv
  --debug               equal to -vvv
```

An example:

```bash
$ python3 -m pogoraidbot -t [BOT_TOKEN] -r redis://192.168.15.2:4044/3
```

## Dockerized version \[recommended]

### Requirements

The dockerized version of the bot requires `docker` and `docker-compose` to work.

Refer to this [link](https://docs.docker.com/compose/install/).

### Installation

You can choose two kinds of setup:

#### Use the image on Docker Hub

1. Download **.env** and **docker-compose.yaml** files and put them in a folder.

2. Edit them to adapt the setup to your requirements(see below).

3. Run the containers.

    ```bash
    docker-compose up
    ```

#### Compile your own Docker image 

1. Clone the whole repo and init the submodule.

    ```bash
    git clone https://github.com/RobertoBochet/pogoraidbot-dockerized.git ./pogoraidbot
    cd pogoraidbot
    git submodule update --init
    ```

2. Edit the **.env** and **docker-compose.yaml** to adapt the setup to your requirements(see below).

3. Build and start the containers.

    ```bash
    docker-compose build
    docker-compose up
    ```

### Configuration

#### Required

In **.env** replace:

- `[BOT_TOKEN]` with your bot's token
- `[SUPERADMIN_ID]` with the Telegram id of the main admin
- `[TIME_ZONE]` with your time zone (refer to [this](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List) table on column *TZ database name*)

#### Optional

- Add support to gym identification
    
    In **.env** set the env `PGRB_BOT_GYMS_FILE` with the position of your gyms file.

- Add support to boss identification
    
    In **.env** set the env `PGRB_BOT_BOSSES_FILE` with the position of your bosses file.
     
- Make **redis** data persistent

    Uncomment the line `command: ["redis-server", "--appendonly", "yes"] ` in **docker-compose.yaml**.
    
    If you want make the redis data persistent also to container destruction uncomment also the **volumes** section of the **redis** service and set the env `PGRB_REDIS_PATH`.
    
- Assign static IP for the virtual network

    Uncomment all the three **networks** sections in **docker-compose.yaml** and set the three env `PGRB_NETWORK_*` with *IP* and *subnet* in **.env**.
    
## Credits

In this project are used the following Python libraries:

-   [python-telegram-bot](https://python-telegram-bot.org/) (LGPLv3 License)
-   [opencv-python](https://pypi.org/project/opencv-python/) (MIT License)
-   [pytesseract](https://pypi.org/project/pytesseract/) (GPLv3 License)
-   [redis](https://pypi.org/project/redis/) (MIT License)
-   [requests](https://pypi.org/project/requests/) (Apache 2.0 License)
