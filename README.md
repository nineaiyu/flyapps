##### 从git上面下载源码
```shell
cd /data/
git clone https://github.com/nineaiyu/FlyApps
```


### FlyApp 服务器搭建 [python3 环境]

##### 搭建python env 环境
```shell
yum install python36 python36-devel  redis mariadb-server  mariadb-devel -y
python3 -m venv py3
source py3/bin/activate
```

###### 安装pip包
```shell
cd  fir_ser/
pip install -U setuptools pip
pip install -r requirements.txt
```

###### 配置数据库
```
在 config.py 配置redis 和 mysql 数据库
```

###### 迁移数据库
```shell
#如果是mysql,需要做一下配置，如果是sqlite,需要升级sqlite
#记得根据配置创建数据库
#create database flyapp default character set utf8 COLLATE utf8_general_ci;
#grant all on flyapp.* to flyuser@'127.0.0.1' identified by 'flypwd00oo.1';

python manage.py makemigrations
python manage.py migrate
```

### FlyApp  zsign ipa重签名工具安装
```shell
yum install openssl-devel -y
yum install gcc-c++ gcc -y
wget https://github.com/nineaiyu/zsign/archive/refs/tags/v1.1.2.tar.gz
tar xvf v1.1.2.tar.gz
cd zsign-1.1.2/
g++ *.cpp common/*.cpp -lcrypto -O3 -std=c++11 -o zsign
cp zsign /usr/bin/
```

### FlyApp web端搭建
###### npm编译环境
```shell
yum install npm
npm install -g n
n 12.13      # 安装12版本的node ,最新版本会有问题
npm install -g yarn
```

###### 编译web端和下载页
```shell
cd FlyApps/fir_client/
vim  vue.config.js  #修改api接口地址
# pro_base_env 正式环境信息
# dev_base_env 开发环境信息

yarn install
yarn build index  # web打包
yarn build short  # 下载也打包
```


###### web目录操作
```shell
# web目录： /www/wwwroot/fly.dvcloud.xin/

cd  /www/wwwroot/fly.dvcloud.xin/
cp -a /data/FlyApps/fir_client/dist/*   .
cp -a /data/FlyApps/fir_download/dist/*  .
```

##### 更新sqllite
```shell
tar xvf sqlite-autoconf-3310100.tar.gz 
cd sqlite-autoconf-3310100

./configure --prefix=/usr/local/sqlite
make -j4

make install
rm -rf /usr/bin/sqlite3

ln -s /usr/local/sqlite/bin/sqlite3   /usr/bin/sqlite3
ll /usr/bin/sqlite3


echo "/usr/local/sqlite/lib" > /etc/ld.so.conf.d/sqlite3.conf
ldconfig 

```