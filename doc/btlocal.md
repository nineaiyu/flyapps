### 本地部署前准备
系统 | Centos 8 Stream [2cpu 4G内存] 宝塔面板
----|----
域名|```app.hehelucky.cn```
域名SSL证书| nginx 格式证书 [可以使用bt自带的免费证书或者阿里云和腾讯云都可以申请免费ssl证书]
数据路径| ```/data```


### 环境依赖
#### 安装宝塔面板，并且在面板中安装 mysql数据库和redis数据库和nginx服务
面板版本 | 不低于 宝塔Linux面板8.0.2
----|----
nginx|1.22
maridb| 10.3
redis| 6.2


### 开始源码本地部署

##### 从git上面下载源码
```shell
mkdir /data/
cd /data/
dnf install git gcc zip unzip mariadb-devel -y
git clone https://github.com/nineaiyu/flyapps
```

##### 搭建python env 环境
```shell
dnf install python39 python39-devel -y
python3.9 -m venv py39
```

###### 安装pip包
```shell
source /data/py39/bin/activate
cd /data/flyapps/fir_ser/
pip install -U setuptools pip -i https://pypi.tuna.tsinghua.edu.cn/simple/
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple/
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

### 宝塔面板操作
- 网站->添加站点【域名为上面准备好的域名】->无需创建数据库，并且PHP版本为纯静态
- 上面站点添加成功之后，点击右面的设置->配置文件->在```access_log  /www/wwwlogs/app.hehelucky.cn.log;```（倒数第三行）上面添加如下配置并保存
```shell
    location ~ ^/(download|api|files|udid|captcha|show_udid|flower) {
        uwsgi_send_timeout 300;        # 指定向uWSGI传送请求的超时时间，完成握手后向uWSGI传送请求的超时时间。
        uwsgi_connect_timeout 300;     # 指定连接到后端uWSGI的超时时间。
        uwsgi_read_timeout 300;        # 指定接收uWSGI应答的超时时间，完成握手后接收uWSGI应答的超时时间。
        include  uwsgi_params;
        uwsgi_pass 127.0.0.1:8898;
        uwsgi_param UWSGI_SCRIPT wsgi;
        }

    location ~ ^/(index|apps|user|login|register|supersign|home|reset) {
        try_files $uri $uri/  /index.html;
    }


    location / {
        try_files $uri $uri/  /short/short.html;
    }
```
- 软件商店->已安装->Redis->性能调整->将 requirepass 对应的值修改为 ```nineven``` 并保存重启
- 数据库->添加数据库，按照下面信息进行添加

字段 | 值
----|----
数据库名 | ```flyapps```
用户名| ```flyuser```
密码| ```KGzKjZpWBp4R4RSa```


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

##### 创建软连接，用与放置编译好的代码
- ```/www/wwwroot/app.hehelucky.cn``` 为上面网站的根目录
```shell
rm -rf /data/fir_client && ln -sv /www/wwwroot/app.hehelucky.cn /data/fir_client
```
1.创建web目录，并将打包好的web复制该目录
```shell
mkdir -pv /data/fir_client/short
\cp -a /data/flyapps/fir_client/dist_index/*  /data/fir_client/
\cp -a /data/flyapps/fir_client/dist_short/*  /data/fir_client/short/
chown www.www -R /data/fir_client
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
python manage.py start all -u www -usm 1 -d
```

##### 根据提示创建默认管理用户,用于访问管理后台
```shell
cd /data/flyapps/fir_ser/
source /data/py39/bin/activate
python manage.py createsuperuser
```
- 需要输入用户名，邮箱和密码
- 用户名和密码用与登录管理后台
- 邮箱和密码用与登录前端web


### 管理后台部署
#### 面板操作
- 网站->添加站点【域名为管理后台的域名】->无需创建数据库，并且PHP版本为纯静态
- 上面站点添加成功之后，点击右面的设置->配置文件->在```access_log  /www/wwwlogs/admin.hehelucky.cn.log;```（倒数第三行）上面添加如下配置并保存
```shell
    location ~ ^/(api|flower) {
        uwsgi_send_timeout 300;        # 指定向uWSGI传送请求的超时时间，完成握手后向uWSGI传送请求的超时时间。
        uwsgi_connect_timeout 300;     # 指定连接到后端uWSGI的超时时间。
        uwsgi_read_timeout 300;        # 指定接收uWSGI应答的超时时间，完成握手后接收uWSGI应答的超时时间。
        include  uwsgi_params;
        uwsgi_pass 127.0.0.1:8898;
        uwsgi_param UWSGI_SCRIPT wsgi;
    }

```

#### 终端操作-编译web管理后台
```shell
cd /data/flyapps/fir_admin/
yarn install
yarn build:prod  # 下载页打包，输出目录 dist
```

##### 创建软连接，用与放置编译好的代码
- ```/www/wwwroot/admin.hehelucky.cn``` 为上面管理后台网站的根目录
```shell
rm -rf /data/fir_admin && ln -sv /www/wwwroot/admin.hehelucky.cn /data/fir_admin
```
1.创建web目录，并将打包好的web复制该目录
```shell
\cp -a /data/flyapps/fir_admin/dist/* /data/fir_admin/
chown www.www -R /data/fir_admin
```

## 上述部署的域名需要开启ssl访问，否则应用会下载异常