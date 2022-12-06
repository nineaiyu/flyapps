### 本地部署前准备
系统|Centos 8 Stream [1cpu 4G内存]
----|----
域名|```app.hehelucky.cn```
域名SSL证书| nginx 格式证书 [阿里云和腾讯云都可以申请免费ssl证书]
数据路径| ```/data```


##### 从git上面下载源码
```shell
cd /data/
git clone https://github.com/nineaiyu/FlyApps
```


### FlyApp 本地部署 [python3 环境]

##### 搭建python env 环境
```shell
yum install python39 python39-devel  redis mariadb-server  mariadb-devel -y
python3.9 -m venv py39
source py39/bin/activate
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
n 12.13      # 安装12版本的node或者14版本 ,最新版本会有问题
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

###### 编译web管理后台
```shell
cd FlyApps/fir_admin/

yarn install
yarn build
```
