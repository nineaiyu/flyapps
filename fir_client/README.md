# fir_test

## Project setup
```
yarn install
```

### Compiles and hot-reloads for development
```
yarn serve
```

### Compiles and minifies for production
```
yarn build
```

### Lints and fixes files
```
yarn lint
```
### mshort 和 short 区别
区别就是引用的下载不同，mshort 下面也引用了elemet , short 没有引用，mshort最终包400kb 左右，short 130kb ，体积相差3倍左右

### deploy nginx
```
    location ~ ^/(index|apps|user|login|register|supersign) {
        try_files $uri $uri/  /index.html;
    }

    # location / {
    #     try_files $uri $uri/  /mshort.html;
    # }

    location / {
        try_files $uri $uri/  /short.html;
    }

```


## deploy nginx

#### short deploy nginx
```shell
    location / {
        try_files $uri $uri/  /short.html;
    }
```
#### index.html
```html
<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <meta http-equiv="refresh" content="3;URL=https://flyapps.cn">
    <title>FLY分发平台</title>
    <style>
        .container {
            width: 60%;
            margin: 10% auto 0;
            background-color: #f0f0f0;
            padding: 2% 5%;
            border-radius: 10px
        }

        ul {
            padding-left: 20px;
        }

            ul li {
                line-height: 2.3
            }

        a {
            color: #20a53a
        }
    </style>
</head>
<body>
    <div class="container">
        <h3>这是分发平台下载默认页，正在跳转 <a href="https://flyapps.cn">首页</a></h3>
    </div>
</body>
</html>
```
