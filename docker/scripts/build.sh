#!/bin/bash
#
#

cd ../build/

for i in buildclient buildadmin;do
	docker-compose up ${i}
done

docker-compose build


