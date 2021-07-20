FROM python:3.6.14-slim

# Fixes some weird terminal issues such as broken clear / CTRL+L
ARG PIP_MIRROR=https://mirrors.aliyun.com/pypi/simple

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && apt update 

RUN apt-get install g++ wget  nginx redis supervisor -y
RUN apt-get install libssl-dev openssl libmariadb-dev sqlite  -y
RUN rm -rf /var/lib/apt/lists/* 


RUN mkdir -pv /data/flyapps 
RUN mkdir -pv /data/logs/

COPY fir_client/dist /data/flyapps/fir_client

RUN cd /opt/ && wget https://github.com/nineaiyu/zsign/archive/refs/tags/v1.1.1.tar.gz
RUN cd /opt/ && tar xvf v1.1.1.tar.gz && cd zsign-1.1.1/ && g++ *.cpp common/*.cpp -lcrypto -O3 -std=c++11 -o zsign && cp zsign /usr/bin/
# install pip
COPY fir_ser /data/flyapps/fir_ser
RUN cd /data/flyapps/fir_ser/ && pip install -U setuptools pip -i ${PIP_MIRROR} --ignore-installed && pip install --no-cache-dir -r requirements.txt -i ${PIP_MIRROR}  && pip install --no-cache-dir uwsgi -i ${PIP_MIRROR} 

RUN rm -rf /var/cache/yum/

COPY Docker/flyapps.conf  /etc/supervisor/conf.d/flyapps.conf
COPY Docker/uwsgi.conf /data/flyapps/fir_ser/uwsgi.conf
COPY Docker/flyapps-vhost.conf  /etc/nginx/conf.d/flyapps-vhost.conf
COPY Docker/app.hehelucky.cn.pem /data/flyapps/app.hehelucky.cn.pem
COPY Docker/app.hehelucky.cn.key /data/flyapps/app.hehelucky.cn.key
RUN chown -R www-data:www-data /data/flyapps/fir_ser/


RUN sed -i "/^daemonize/s@yes@no@" /etc/redis/redis.conf


#RUN cd /data/flyapps/&& source py3/bin/activate && cd fir_ser/ && python manage.py makemigrations && python manage.py migrate
COPY Docker/init.sh /data/flyapps/init.sh
COPY Docker/end.sh /data/flyapps/end.sh
EXPOSE 443
#ENTRYPOINT ["/data/flyapps/init.sh"]
#ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]

