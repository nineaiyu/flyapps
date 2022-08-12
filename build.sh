#!/bin/bash
#
#
# shellcheck disable=SC2006
s_path=`pwd`

#first build fir_client
docker pull node:14.17.3
\cp -a build_client.sh fir_client/
docker run --rm --privileged=true -v "${s_path}"/fir_client:/fir_client -it node:14.17.3  sh /fir_client/build_client.sh

cd "${s_path}"/fir_ser/ && docker build . -t flyapps
