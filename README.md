## Description

This is a dockerized version of my telegram bot for organization of PoGo raid.

You can find the vanilla bot in [this](https://github.com/RobertoBochet/pogoraidbot) repo.

## Requirements

The dockerized version of the bot requires `docker` and `docker-compose` to work.

Refer to this [link](https://docs.docker.com/compose/install/).

## Installation

You can choose two kinds of setup:

### Use the image on Docker Hub

1. Download **.env** and **docker-compose.yaml** files and put them in a folder.

2. Edit them to adapt the setup to your requirements(see below).

3. Run the containers.

    ```bash
    docker-compose up
    ```

### Compile your own Docker image 

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

## Configuration

### Required

In **.env** replace:

- `[BOT_TOKEN]` with your bot's token
- `[SUPERADMIN_ID]` with the Telegram id of the main admin
- `[TIME_ZONE]` with your time zone (refer to [this](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones#List) table on column *TZ database name*)

### Optional

- Add support to gym identification
    
    In **.env** set the env `PGRB_BOT_GYMS_FILE` with the position of your gyms file.

- Add support to boss identification
    
    In **.env** set the env `PGRB_BOT_BOSSES_FILE` with the position of your bosses file.
     
- Make **redis** data persistent

    Uncomment the line `command: ["redis-server", "--appendonly", "yes"] ` in **docker-compose.yaml**.
    
    If you want make the redis data persistent also to container destruction uncomment also the **volumes** section of the **redis** service and set the env `PGRB_REDIS_PATH`.
    
- Assign static IP for the virtual network

    Uncomment all the three **networks** sections in **docker-compose.yaml** and set the three env `PGRB_NETWORK_*` with *IP* and *subnet* in **.env**.