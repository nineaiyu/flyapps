#!/bin/bash
#
#

# shellcheck disable=SC2006
s_path=`pwd`

docker network create flyapps
docker run --net flyapps --name redis -d  redis:6.2.5 redis-server --requirepass nineven --bind '0.0.0.0'

docker run --net flyapps --name mariadb -e MARIADB_ROOT_PASSWORD=root  -v "${s_path}"/data/mysql:/var/lib/mysql  -d  mariadb:10.5
sleep 3

code=1
count=1
while [ ${code} -ne 0 ];do
        docker exec -it mariadb mysql -proot -e 'show databases;'
        code=$?
        ((count+=1))
        if [ "$count" -gt 30 ];then
                echo "30s away, but mysql service is not available"
                exit 1
        fi
        sleep 2
        echo "check whether mysql service is ready..."
done

docker exec -it mariadb mysql -proot -e 'create database flyapp default character set utf8 COLLATE utf8_general_ci;'
docker exec -it mariadb mysql -proot -e "grant all on flyapp.* to flyuser@'%' identified by 'KGzKjZpWBp4R4RSa';"


docker run --sysctl net.core.somaxconn=4096 --net flyapps \
	-v "${s_path}"/fir_ser:/data/fir_ser \
	-v "${s_path}"/data/files:/data/fir_ser/files \
	-v "${s_path}"/data/supersign:/data/fir_ser/supersign \
	--name flyapps -d flyapps

docker run --net flyapps --name nginx -d -p 80:80  -p 443:443 \
  -v "${s_path}"/fir_client/dist:/data/fir_client  \
  -v "${s_path}"/nginx.conf.d:/etc/nginx/conf.d nginx:1.21.3

