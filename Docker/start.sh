#!/bin/bash
#
#
docker network create flyapps
docker run --net flyapps --name mariadb -e MARIADB_ROOT_PASSWORD=root -d  mariadb:10.5
docker exec -it mariadb mysql -proot -e 'create database flyapp default character set utf8 COLLATE utf8_general_ci;'
docker exec -it mariadb mysql -proot -e "grant all on flyapp.* to flyuser@'%' identified by 'KGzKjZpWBp4R4RSa';"


docker run --net flyapps --link mariadb:mariadb -p 443:443 --name flyapps -d flyapps
