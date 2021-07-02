#!/bin/bash
#

source /www/flyapps/py3/bin/activate && cd /www/flyapps/fir_ser/
chown www.www -R /www/flyapps/fir_ser/
stop(){
pgrep -f uwsgi |xargs -i kill {}
sleep 1
pgrep -f celery |xargs -i kill {}
}
start(){
uwsgi --ini uwsgi.conf
sleep 1
celery multi start 4 -A fir_ser -l INFO -c4  --pidfile=/var/run/celery/%n.pid --logfile=logs/%p.log
sleep 1
nohup celery -A fir_ser beat --uid=1000 --pidfile=logs/beat.pid --scheduler django -l INFO --logfile=logs/beat.log &

}

restart(){
stop
sleep 1
start
}
$@
