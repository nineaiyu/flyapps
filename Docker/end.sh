#!/bin/bash
sed -i '/^\[program:init/,$d' /etc/supervisor/conf.d/flyapps.conf
supervisorctl stop init &>/dev/null
supervisorctl stop end &>/dev/null
echo 'init end------------------------------------------'
exit 0
