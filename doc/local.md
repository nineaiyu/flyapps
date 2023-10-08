### 本地部署前准备
系统 | Centos 8 Stream [2cpu 4G内存]
----|----
域名|```app.hehelucky.cn```
域名SSL证书| nginx 格式证书 [阿里云和腾讯云都可以申请免费ssl证书]
数据路径| ```/data```


### 数据库环境依赖
##### 安装mariadb数据库并启动数据库 [如果存在mysql数据库服务则忽略该操作]
```shell
dnf install mariadb-devel mariadb-server -y
systemctl restart mariadb
systemctl enable mariadb
```
##### 安装redis数据库 [如果存在redis数据库服务则忽略该操作]
```shell
dnf install redis -y
systemctl restart redis
systemctl enable redis
```

### 开始部署源码

##### 从git上面下载源码
```shell
mkdir /data/
cd /data/
dnf install git gcc zip unzip mariadb-devel -y
git clone https://github.com/nineaiyu/flyapps
```


### flyapps 本地部署 [python3 环境]

##### 搭建python env 环境
```shell
dnf install python39 python39-devel -y
python3.9 -m venv py39
```

###### 安装pip包
```shell
cd /data/flyapps/fir_ser/
source /data/py39/bin/activate
pip install -U setuptools pip -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

#### 配置数据库

##### 创建mysql数据库
```shell
mysql
```
执行下面mysql命令
```mariadb
create database flyapps default character set utf8 COLLATE utf8_general_ci;
grant all on flyapps.* to flyuser@'127.0.0.1' identified by 'KGzKjZpWBp4R4RSa';
quit;
```

##### 增加redis密码并重启redis数据库
```shell
echo 'requirepass nineven' >> /etc/redis.conf  # 配置授权密码
systemctl restart redis
```

### flyapps  zsign ipa重签名工具安装
```shell
dnf install openssl-devel -y
dnf install gcc-c++ gcc -y
cd /data/flyapps/fir_ser/
tar xvf zsign-1.1.2.tar.gz
cd zsign-1.1.2/
g++ *.cpp common/*.cpp -lcrypto -O3 -std=c++11 -o /usr/bin/zsign
```

##### 添加redis和mariadb uwsgi本地解析
```shell
echo '127.0.0.1 mariadb redis flyapps' >> /etc/hosts
```

### 配置文件操作

####  配置api服务需要修改api和web域名，如果有需求，还可以配置 短信，邮箱，geetest，存储等信息
##### fir_ser配置文件 ```fir_ser/config.py```
```python
class DOMAINCONF(object):
    API_DOMAIN = "https://app.hehelucky.cn"  # 用与开启本地存储，上传应用配置
    WEB_DOMAIN = "https://app.hehelucky.cn"  # 用于超级签跳转配置，该域名一般为前端页面域名
```

##### fir_client配置文件 ```fir_client/vue.confjg.js```
```javascript
const pro_base_env = {
    baseUrl: '/',       //该选项可以填写web-api的域名，类似 https://api.xxx.com/
    index_static: '/',  //若配置cdn等加速，可以填写cdn加速域名
    baseShortUrl: '/',  //该选项可以填写short-api的域名,也可以和web-api域名一样，类似 https://api.xxx.com/
    short_static: '/short/',  //若配置cdn等加速，可以填写cdn加速域名
    version: version,
};
```

### flyapps web端搭建
###### npm编译环境
```shell
dnf install npm -y
npm install -g n
n 12.13      # 安装12版本的node或者14版本 ,最新版本会有问题
npm install -g yarn
```

###### 修改前端web编译信息【可选】
```shell
vim  /data/flyapps/fir_client/vue.config.js  #根据需求修改相关信息,并保存退出
# pro_base_env 正式环境信息
# dev_base_env 开发环境信息
```
###### 编译web端和下载页
```shell
cd /data/flyapps/fir_client/
yarn install
yarn build index  # 前端打包,输出目录 dist_index
yarn build short  # 下载页打包，输出目录 dist_short
```

###### 编译web管理后台
```shell
cd /data/flyapps/fir_admin/
yarn install
yarn build:prod  # 下载页打包，输出目录 dist
```

### nginx配置
##### 安装nginx
```shell
dnf install nginx -y
```
##### 将域名ssl证书解压到```/etc/nginx/conf.d/``` 目录中，并重命名为```域名.pem```,```域名.key```格式
##### 拷贝虚拟主机配置文件
```shell
cp /data/flyapps/nginx.conf.d/flyapps-vhost.conf /etc/nginx/conf.d/
```
1.创建web目录，并将打包好的web复制该目录
```shell
mkdir -pv /data/{fir_client/short,fir_admin}
cp -a /data/flyapps/fir_client/dist_index/*  /data/fir_client/
cp -a /data/flyapps/fir_client/dist_short/*  /data/fir_client/short/
cp -a /data/flyapps/fir_admin/dist/* /data/fir_admin/
chown nginx.nginx -R /data/{fir_client,fir_admin}
```
2.启动nginx服务
```shell
nginx -t
systemctl restart nginx
systemctl enable nginx
```

###### 迁移数据库
```shell
source /data/py39/bin/activate
cd /data/flyapps/fir_ser/
python manage.py makemigrations
python manage.py migrate
```

#### 配置内核参数【仅执行一次】
```shell
echo 'net.core.somaxconn=1024' >> /etc/sysctl.conf
sysctl -p
```
#### 启动api服务
```shell
cd /data/flyapps/fir_ser/
source /data/py39/bin/activate
python manage.py start all -u nginx -usm 1 -d
```

##### 根据提示创建默认管理用户,用与访问管理后台
```shell
python manage.py createsuperuser
```
- 需要输入用户名，邮箱和密码
- 用户名和密码用与登录管理后台
- 邮箱和密码用与登录前端web