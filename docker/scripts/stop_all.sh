#!/bin/bash
#
#


cd ../flyapps/ && docker-compose down

cd ../redis/ && docker-compose down

cd ../mariadb/ && docker-compose down
