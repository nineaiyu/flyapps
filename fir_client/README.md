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


### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).
