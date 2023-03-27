#!/bin/bash
#
#

cd ../mariadb/ && docker compose up -d
cd ../redis/ && docker compose up -d

cd ../flyapps/ && docker compose up -d
docker logs -f flyapps
