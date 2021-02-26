#!/usr/bin/env bash

export $(grep -v '^#' .env-common | xargs)
export $(grep -v '^#' .env | xargs)

# A string with random chars for Django security purposes
export SECRET_KEY='<replace with some random string>'

export REDIS_HOST=127.0.0.1
export POSTGRES_HOST=127.0.0.1
