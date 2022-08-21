#!/bin/bash
#
#

which dockerd
if [ $? -ne 0 ];then
	dnf config-manager --add-repo=https://download.docker.com/linux/centos/docker-ce.repo
	dnf install docker-ce -y
fi
which docker-compose
if [ $? -ne 0 ];then
	curl -L https://get.daocloud.io/docker/compose/releases/download/v2.5.0/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose
	chmod +x /usr/local/bin/docker-compose
fi

data_path="$(dirname $(dirname `pwd`))/data"
mkdir -pv ${data_path}/{flyapps,web,mariadb,redis,logs/{mariadb,nginx,flyapps}}
chown 1001.1001 -R ${data_path}/{flyapps,web,mariadb,redis,logs/{mariadb,nginx,flyapps}}
systemctl start docker && docker network create flyapps --driver bridge --subnet=172.31.31.0/24
systemctl enable docker
systemctl status docker


#docker pull 'bitnami/mariadb:10.7.3'
#docker pull 'bitnami/redis:6.2.7'
#docker pull 'nginx:1.21.3'
#docker pull 'node:14.17.3'
