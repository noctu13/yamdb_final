# API YAMDB

An application that implements the API for YAMDB running in Docker containers.
YAMDB is site about cinema with the possibility of rating and review.

## Getting Started

Download [Docker Desktop](https://www.docker.com/products/docker-desktop) for Mac or Windows. [Docker Compose](https://docs.docker.com/compose) will be automatically installed. On Linux, make sure you have the latest version of [Compose](https://docs.docker.com/compose/install/).

## Enviroment settings

specify the following environment variables for .env

    NGINX_PORT=80
    NGINX_IP=0.0.0.0
    NGINX_HOST=http://web:8000

Run in this directory:

    docker-compose up

Install migrations by executing the "startup.sh" script:

    docker-compose exec web startup.sh

The app will be running at [http://localhost:80](http://localhost:80)

## Run tests

You can run the Django tests within the running web container by doing this:

    sudo docker-compose exec web pytest

## Workflow

![name_worklow Actions Status](https://github.com/noctu13/yamdb_final/workflows/yamdb-app_workflow/badge.svg)

## Other commands

Run other Django management commands, e.g.:

    docker-compose exec web ./manage.py createsuperuser

Or get a bash prompt within the web container:

    docker-compose exec web bash

Stop it all running:

    docker-compose down

If you change something in `docker-compose.yml` then you'll need to build
things again:

    docker-compose build

Or, just for the `web` container:

    docker-compose build web
