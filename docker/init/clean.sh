#!/bin/bash
#
#

for i in nginx flyapps mariadb redis buildclient buildshort buildadmin;do echo $i;docker rm -f $i;done


docker network rm flyapps

