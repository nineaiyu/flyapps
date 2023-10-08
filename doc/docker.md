### Docker最小化部署前准备，如果使用超级签和云存储，需要使用阿里云的服务器
系统|Centos 8 Stream 纯净系统 [2cpu 4G内存]
----|----
域名|```app.hehelucky.cn```
域名SSL证书| nginx 格式证书 [阿里云和腾讯云都可以申请免费ssl证书]
数据路径| ```/data```


### 开始部署
##### 1.从git上面下载源码
```
mkdir /data/
cd /data/
dnf install git -y
git clone https://github.com/nineaiyu/flyapps
```

## 注意，下面展示的相对路径，都是以```/data/flyapps```为相对目录

#### 2.docker环境安装
```
cd /data/flyapps/docker/init
sh init.sh
```

#### 3.配置域名和证书，如果有cdn或者oss,也要进行配置
a.将域名证书通过```sftp软件```或者```rz命令```复制到```/data/flyapps/nginx.conf.d```目录中

b.将域名证书分别重命名为 ```域名.pem``` 和 ```域名.key``` .本次使用的域名是 ```app.hehelucky.cn``` ,因此，证书名称类似如下
```shell script
nginx.conf.d/app.hehelucky.cn.key
nginx.conf.d/app.hehelucky.cn.pem
```
c.修改NGINX配置文件```nginx.conf.d/flyapps-vhost.conf```,将```server_name```字段修改为域名，将```ssl_certificate```和
```ssl_certificate_key```修改为对应证书路径，修改之后，对应字段如下
```shell
server_name     app.hehelucky.cn;
ssl_certificate        /etc/nginx/conf.d/app.hehelucky.cn.pem;
ssl_certificate_key    /etc/nginx/conf.d/app.hehelucky.cn.key;
```

####  4.配置api服务需要修改api和web域名，如果有需求，还可以配置 短信，邮箱，geetest，存储等信息
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

#####  构建静态资源
```
cd /data/flyapps/docker/scripts
sh build.sh
```

#####  启动所有服务
```
cd /data/flyapps/docker/scripts
sh start_all.sh
```

#####  关闭所有服务
```
cd /data/flyapps/docker/scripts
sh stop_all.sh
```

##### 根据提示创建默认管理用户,用与访问管理后台
```shell
docker exec -it flyapps python manage.py createsuperuser
```

##### 测试访问
- 在浏览器输入自己配置的域名 https://app.hehelucky.cn/ 进行访问
- 管理后台访问 https://app.hehelucky.cn:3448/ 进行访问


##### 如果要使用本地的数据库和redis，api服务使用容器，需要修改文件```/data/flyapps/docker/flyapps/docker-compose.yml```
```shell
    external_links:
        - mariadb:mariadb
        - redis:redis
```
修改为
```shell
    extra_hosts:
      - "mariadb:172.31.31.1"
      - "redis:172.31.31.1"
```
并将```nginx:```下面的配置注释掉

同时还需要修改mariadb和redis授权