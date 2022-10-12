### 用与应用分发，苹果超级签名
#### 部署前准备
- 备案域名【至少需要一个域名，以下可通过子域名部署】
  - API域名
  - 前端web域名
  - 下载页域名
    - 下载页域名可配置多个
  - 存储域名（使用阿里云oss存储）
- ssl证书
    - API域名证书
    - 存储域名证书（使用阿里云oss存储）
    - 前端web域名证书（可选）
- Centos8Stream 服务器
    - 如果使用oss存储，则带宽为1M,若使用本地存储，则带宽越大越好
    - 如果使用超级签，最低配置为2cpu 4G内存，若干不使用签名，则1cpu2G就行
- 阿里云短信或极光短信服务【可选一个，主要用与注册，重置密码】
  - 阿里云短信
  - 极光短信
- 邮箱服务【可选，用与注册，重置密码，通知信息】
- 阿里云OSS存储【可选】
    - [sts授权配置](https://help.aliyun.com/document_detail/100624.html)
- 阿里云CDN【可选，用与加速访问】
- 极验验证【可选，滑动验证服务】
- 微信公众号【可选，用与微信扫描登录】
- 阿里云支付【可选，用与购买下载次数】
- 微信支付【可选，用与购买下载次数】

#### 自用搭建建议
- 阿里云服务器需要1cpu 2G内存，无需系统盘，如果使用超级签，可以适当增加配置
- 需要阿里云OSS存储和阿里云CDN,并且OSS存储和阿里云服务器部署同一个地区
- 可以申请一个极验进行滑动验证，或者开启验证码验证
- 阿里云备案域名：api和前端可以使用一个域名，下载页单独域名

#### 部署必备资料
- 域名证书
  - web域名和证书
  - api域名和证书
  - 下载页域名（可配置证书）
  - 存储域名和证书
    - 本地存储，则该域名和证书可以和api域名证书一致
    - 阿里云oss存储
      - 开启cdn，需要新域名和证书
      - 不开启，无需域名和证书
- Centos8Stream 服务器

#### 修改配置文件
##### fir_ser配置文件 config.py
```python
class DOMAINCONF(object):
    API_DOMAIN = "https://app.hehelucky.cn"  # 用与开启本地存储，上传应用配置
    WEB_DOMAIN = "https://app.hehelucky.cn"  # 用于超级签跳转配置，该域名一般为前端页面域名
    MOBILEPROVISION = "https://static.hehejoy.cn/embedded3.mobileprovision"  # 用于苹果包企业签信任企业跳转

```

##### fir_client配置文件 vue.confjg.js
```javascript
const pro_base_env = {
    baseUrl: '/',       //该选项可以填写web-api的域名，类似 https://api.xxx.com/
    index_static: '/',  //若配置cdn等加速，可以填写cdn加速域名
    baseShortUrl: '/',  //该选项可以填写short-api的域名,也可以和web-api域名一样，类似 https://api.xxx.com/
    short_static: '/short/',  //若配置cdn等加速，可以填写cdn加速域名
    version: version,
};
```

##### 从git上面下载源码
```shell
cd /data/
git clone https://github.com/nineaiyu/FlyApps
```


### [Docker 部署](./docker.md)

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