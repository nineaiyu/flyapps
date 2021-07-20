#!/bin/bash
#
#
w_path=`pwd`
s_path=`dirname ${w_path}`

#first build fir_client
docker pull node:14.17.3
docker run --rm -v ${s_path}/fir_client:/fir_client -it node:14.17.3  sh /fir_client/build.sh

## secode build fir_ser
cd ../
docker build . -t flyapps 
