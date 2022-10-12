FROM python:3.9.14-slim

# Fixes some weird terminal issues such as broken clear / CTRL+L
ARG PIP_MIRROR=https://mirrors.aliyun.com/pypi/simple

RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list \
    && apt update 

RUN apt-get install g++ wget -y
RUN apt-get install libssl-dev openssl libmariadb-dev  -y
RUN rm -rf /var/lib/apt/lists/* 



#COPY fir_client/dist /data/flyapps/fir_client

#RUN cd /opt/ && wget https://github.com/nineaiyu/zsign/archive/refs/tags/v1.1.2.tar.gz
COPY zsign-1.1.2.tar.gz /opt/zsign-1.1.2.tar.gz
RUN cd /opt/ && tar xvf zsign-1.1.2.tar.gz && cd zsign-1.1.2/ && g++ *.cpp common/*.cpp -lcrypto -O3 -std=c++11 -o zsign && cp zsign /usr/bin/
# install pip
COPY requirements.txt /opt/requirements.txt
RUN cd /opt/ && pip install -U setuptools pip -i ${PIP_MIRROR} --ignore-installed && pip install --no-cache-dir -r requirements.txt -i ${PIP_MIRROR}  && pip install --no-cache-dir uwsgi -i ${PIP_MIRROR} 


#COPY Docker/flyapps.conf  /etc/supervisor/conf.d/flyapps.conf
#COPY Docker/uwsgi.conf /data/flyapps/fir_ser/uwsgi.conf
#COPY Docker/flyapps-vhost.conf  /etc/nginx/conf.d/flyapps-vhost.conf
#COPY Docker/app.hehelucky.cn.pem /data/flyapps/app.hehelucky.cn.pem
#COPY Docker/app.hehelucky.cn.key /data/flyapps/app.hehelucky.cn.key

WORKDIR /data/fir_ser/
RUN addgroup --system --gid 101 nginx \
    && adduser --system --disabled-login --ingroup nginx --no-create-home --home /nonexistent --gecos "nginx user" --shell /bin/false --uid 101 nginx 

#EXPOSE 443
#ENTRYPOINT ["./entrypoint.sh"]
#ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]
#CMD ["python", "manage.py", "start", "all","-u","nginx","-usm","1"]
ENTRYPOINT ["/bin/bash", "entrypoint.sh"]

