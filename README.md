##### 从git上面下载源码
```
cd /data/
git clone https://github.com/nineaiyu/FlyApps
```

#### 超级签名依赖部署
##### fastlane [相关文档](https://github.com/fastlane/fastlane/blob/master/spaceship/docs/DeveloperPortal.md)
```
# fastlane
#1 gem ruby安装
yum install gem -y
yum install ruby-devel -y 
yum install gcc gcc-c++ -y

#gem修改为国内镜像
gem sources --add https://gems.ruby-china.com/ --remove https://rubygems.org/

gem sources -l
#https://gems.ruby-china.com
#确保只有 gems.ruby-china.com

#2 更新rubby
gpg2 --keyserver hkp://pool.sks-keyservers.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 7D2BAF1CF37B13E2069D6956105BD0E739499BDB

#如果脚本执行失败，可以这样
# echo 199.232.68.133 raw.githubusercontent.com >> /etc/hosts

curl -L get.rvm.io | bash -s stable
source /etc/profile.d/rvm.sh
rvm list known
rvm install 2.7

#3 安装fastlane
gem install fastlane  
gem install pry 

# space 好像有点问题，需要把这个注释掉
vim /usr/local/rvm/gems/ruby-2.7.0/gems/fastlane-2.146.1/spaceship/lib/spaceship/base.rb +298
#v.gsub!("\n", "\n\t") # to align nested elements  #注释掉，要不然会报错

```
##### isign
```
# python2.7
yum update python -y
pip install -U setuptools pip

wget https://github.com/nineaiyu/isign/archive/v1.8.0.tar.gz
tar xvf  v1.8.0.tar.gz
cd  isign-1.8.0/

python setup.py build
python setup.py install
```

### FlyApp 服务器搭建 [python3 环境]


##### 搭建python env 环境
```
yum install python36 python36-devel  redis mariadb-server  mariadb-devel -y
python3 -m venv py3
source py3/bin/activate
```

###### 安装pip包
```
cd FlyApps/fir_ser/
pip install -r requirements.txt
```

###### 配置数据库
```
在 settings.py 配置redis 和 mysql 数据库
```

###### 迁移数据库
```
#如果是mysql,需要做一下配置，如果是sqlite,需要升级sqlite
#记得根据配置创建数据库
#create database flyapp default character set utf8 COLLATE utf8_general_ci;
#grant all on flyapp.* to flyuser@'127.0.0.1' identified by 'flypwd00oo.1';

python manage.py makemigrations
python manage.py migrate
```

### FlyApp web端搭建
###### npm编译环境
```
yum install npm
npm install -g n
n latest
npm install -g yarn
```

###### 编译web端
```
cd FlyApps/fir_client/
vim  src/restful/index.js  #修改api接口地址

yarn install
yarn build
```


###### 编译下载页面
```
cd FlyApps/fir_download/
vim  src/restful/download.js  #修改api接口地址

yarn install
yarn build
```

###### web目录操作
```
# web目录： /www/wwwroot/fly.dvcloud.xin/

cd  /www/wwwroot/fly.dvcloud.xin/
cp -a /data/FlyApps/fir_client/dist/*   .
cp -a /data/FlyApps/fir_download/dist/*  .
```

##### 更新sqllite
```
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