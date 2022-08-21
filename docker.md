##### 从git上面下载源码
```
cd /data/
git clone https://github.com/nineaiyu/FlyApps
```

#### docker环境安装 [centos8]
```
cd /data/FlyApps/docker/init
sh init.sh
```
#### 域名证书准备
- 域名： app.hehelucky.cn
- 证书（nginx）
  - app.hehelucky.cn.key
  - app.hehelucky.cn.pem

#### 配置域名和证书，如果有cdn或者oss,也要进行配置
```shell script
nginx.conf.d/app.hehelucky.cn.key
nginx.conf.d/app.hehelucky.cn.pem
nginx.conf.d/flyapps-vhost.conf
```

####  api服务需要修改api和web域名，短信，邮箱，geetest，存储等信息
##### fir_ser配置文件 config.py
```python
class DOMAINCONF(object):
    API_DOMAIN = "https://app.hehelucky.cn"  # 用与开启本地存储，上传应用配置
    WEB_DOMAIN = "https://app.hehelucky.cn"  # 用于超级签跳转配置，该域名一般为前端页面域名
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

#####  构建静态资源和api服务
```
cd /data/FlyApps/docker/scripts
sh build.sh
```
##### 构建镜像的同时，下载依赖镜像
```shell
docker pull 'bitnami/mariadb:10.7.3'
docker pull 'bitnami/redis:6.2.7'
docker pull 'nginx:1.21.3'
```

#####  启动所有服务
```
cd /data/FlyApps/docker/scripts
sh start_all.sh
```

#####  关闭所有服务
```
cd /data/FlyApps/docker/scripts
sh stop_all.sh
```

##### 根据提示创建默认管理用户
```shell
docker exec -it flyapps python manage.py createsuperuser
```

##### 测试访问
- 在浏览器输入自己配置的域名 https://app.hehelucky.cn/ 进行访问
- 管理后台访问 https://app.hehelucky.cn:3448/ 进行访问