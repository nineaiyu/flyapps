##### 从git上面下载源码
```
cd /data/
git clone https://github.com/nineaiyu/FlyApps
```

#### docker环境安装 [centos7]
```
yum install epel-release -y
yum clean all && yum makecache
yum install docker -y

```
#### 配置域名和证书，如果有cdn或者oss,也要进行配置
```shell script
nginx.conf.d/app.hehelucky.cn.key
nginx.conf.d/app.hehelucky.cn.pem
nginx.conf.d/flyapps-vhost.conf
```
### api服务需要修改api和web域名，短信，邮箱，geetest，存储等信息
```shell script
vim fir_ser/config.py

API_DOMAIN = "https://app.hehelucky.cn"
WEB_DOMAIN = "https://app.hehelucky.cn"
MOBILEPROVISION = "https://ali-static.jappstore.com/embedded.mobileprovision"

```
### web页面需要修改指定api域名
```vuejs
vim fir_client/vue.config.js

const pro_base_env = {
    baseUrl: 'https://flyapps.cn',
    index_static: 'https://static.flyapps.cn/index/',
    baseShortUrl: 'https://flyapps.top',
    short_static: 'https://static.flyapps.top/short/',
};
```

#####  构建静态资源和api服务
```
sh build.sh
```


#####  启动所有服务
```
sh start.sh
```

