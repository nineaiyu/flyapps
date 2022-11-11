FROM python:3.9.14-slim

# Fixes some weird terminal issues such as broken clear / CTRL+L

RUN sed -i 's/deb.debian.org/mirrors.163.com/g' /etc/apt/sources.list \
    && sed -i 's/security.debian.org/mirrors.163.com/g' /etc/apt/sources.list \
    && apt update  \
    && apt-get install g++ wget zip unzip -y \
    && apt-get install libssl-dev openssl libmariadb-dev  -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


#RUN cd /opt/ && wget https://github.com/nineaiyu/zsign/archive/refs/tags/v1.1.2.tar.gz
ADD zsign-1.1.2.tar.gz /opt/
RUN cd /opt/zsign-1.1.2/ && g++ *.cpp common/*.cpp -lcrypto -O3 -std=c++11 -o zsign && cp zsign /usr/bin/ && rm -rf /opt/zsign-1.1.2/
# install pip
COPY requirements.txt /opt/requirements.txt
RUN cd /opt/ && pip install -U setuptools pip --ignore-installed && pip install --no-cache-dir -r requirements.txt && pip install --no-cache-dir uwsgi


WORKDIR /data/fir_ser/
COPY entrypoint.sh entrypoint.sh
RUN addgroup --system --gid 101 nginx \
    && adduser --system --disabled-login --ingroup nginx --no-create-home --home /nonexistent --gecos "nginx user" --shell /bin/false --uid 101 nginx 

#EXPOSE 443
#ENTRYPOINT ["./entrypoint.sh"]
#ENTRYPOINT ["/usr/bin/supervisord", "-c", "/etc/supervisor/supervisord.conf", "-n"]
#CMD ["python", "manage.py", "start", "all","-u","nginx","-usm","1"]
ENTRYPOINT ["/bin/bash", "entrypoint.sh"]

