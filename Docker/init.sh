#!/bin/bash
cd /data/flyapps/fir_ser/ 
python manage.py makemigrations && python manage.py migrate
python manage.py loaddata dumpdata.json
exit 0
