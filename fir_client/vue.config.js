const IS_PROD = ['production', 'prod'].includes(process.env.NODE_ENV);
const path = require('path');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');
const dateFormat = require("./src/utils/format.js");
const CompressionWebpackPlugin = require('compression-webpack-plugin');
const argv = process.argv;

function resolve(dir) {
    return path.join(__dirname, dir);
}

const compress = new CompressionWebpackPlugin(
    {
        filename: info => {
            return `${info.path}.gz${info.query}`
        },
        algorithm: 'gzip',
        threshold: 10240,
        test: new RegExp(
            '\\.(' +
            ['js', 'css'].join('|') +
            ')$'
        ),
        minRatio: 0.8,
        deleteOriginalAssets: false
    }
);

const index = {
    outputDir: 'dist_index',
    // page 的入口
    entry: 'src/main.js',
    // 模板来源
    template: 'public/index.html',
    // 在 dist/index.html 的输出
    filename: 'index.html',
    // 当使用 title 选项时，
    // template 中的 title 标签需要是 <title><%= htmlWebpackPlugin.options.title %></title>
    title: 'Fly分发平台',
    // 在这个页面中包含的块，默认情况下会包含
    // 提取出来的通用 chunk 和 vendor chunk。
    chunks: ['chunk-vendors', 'chunk-common', 'index', 'elementui', 'runtime', 'alioss', 'qiniujs', 'qrcodejs2']
};
// eslint-disable-next-line no-unused-vars
const mshort = {
    outputDir: 'dist_mshort',
    // page 的入口
    entry: 'src/main.short.js',
    // 模板来源
    template: 'public/short.html',
    // 在 dist/short.html 的输出
    filename: 'short.html',
    // 当使用 title 选项时，
    // template 中的 title 标签需要是 <title><%= htmlWebpackPlugin.options.title %></title>
    title: '应用下载',
    // 在这个页面中包含的块，默认情况下会包含
    // 提取出来的通用 chunk 和 vendor chunk。
    chunks: ['chunk-vendors', 'chunk-common', 'mshort', 'chunk-elementUI', 'runtime']
};
const short = {
    outputDir: 'dist_short',
    // page 的入口
    entry: 'src/short.js',
    // 模板来源
    template: 'public/short.html',
    // 在 dist/short.html 的输出
    filename: 'short.html',
    // 当使用 title 选项时，
    // template 中的 title 标签需要是 <title><%= htmlWebpackPlugin.options.title %></title>
    title: '应用下载',
    // 在这个页面中包含的块，默认情况下会包含
    // 提取出来的通用 chunk 和 vendor chunk。
    chunks: ['chunk-vendors', 'chunk-common', 'short', 'chunk-commons', 'runtime']
};
let pages = {index, short, mshort};
let outputDir = 'dist'
let page = argv[3];
if (!page) {
    page = 'index'
}

for (const key of Object.keys(pages)) {
    if (key === page) {
        const tmp = pages[key];
        pages = {};
        pages[key] = tmp;
        outputDir = tmp.outputDir
    }
}

const version='2.3.8';
const github = 'https://github.com/nineaiyu/FlyApps';

const pro_base_env = {
    baseUrl: '/',       //该选项可以填写web-api的域名，类似 https://api.xxx.com/
    index_static: '/',  //若配置cdn等加速，可以填写cdn加速域名
    baseShortUrl: '/',  //该选项可以填写short-api的域名,也可以和web-api域名一样，类似 https://api.xxx.com/
    short_static: '/short/',  //若配置cdn等加速，可以填写cdn加速域名
    version: version,
};

const dev_base_env = {
    baseUrl: 'https://app.hehelucky.cn/',
    index_static: '/',
    baseShortUrl: 'https://app.hehelucky.cn/',
    short_static: 'https://app.hehelucky.cn/short/',
    version: version,
};
let base_evn = dev_base_env;

const footer_info = {
    copyright: 'Copyright © 2022-2099 isummer 版权所有.',
    ipcBeiAn: {
        url: 'https://beian.miit.gov.cn',
        text: '京ICP备681262896号',
    },
    gongAnBeiAn: {
        url: 'https://www.beian.gov.cn/portal/registerSystemInfo?recordcode=681262896',
        text: '京公网安备681262896号',
    },
}

if (IS_PROD) {
    base_evn = pro_base_env
} else {
    base_evn = dev_base_env
}
base_evn.footer_info = footer_info

function get_public_path(pages) {
    if (!IS_PROD) {
        return '/'
    } else if (pages.index) {
        return base_evn.index_static
    } else {
        return base_evn.short_static   //正式服，需要打包下载页静态资源
    }
}

let publicPath = get_public_path(pages);
module.exports = {
    pages: pages,
    outputDir: outputDir,
    productionSourceMap: false, //去除生产环境的productionSourceMap
    assetsDir: "static", //静态文件存储位置
    lintOnSave: true,
    runtimeCompiler: true,
    publicPath: publicPath,
    configureWebpack: {
        // provide the app's title in webpack's name field, so that
        // it can be accessed in index.html to inject the correct title.
        name: '应用分发',
        resolve: {
            alias: {
                '@': resolve('src')
            }
        },
        plugins: [compress],
    },
    chainWebpack: config => {
        config
            .plugin('define')
            .tap(args => {
                args[0]['process.env']['base_env'] = JSON.stringify({
                    baseUrl: base_evn.baseUrl,
                    baseShortUrl: base_evn.baseShortUrl,
                    version: dateFormat("yyyyMMdd.hhmmss") + '.' + base_evn.version,
                    footer: base_evn.footer_info,
                    github
                });
                return args
            });

        if (IS_PROD) {
            config.optimization.minimizer = [
                new UglifyJsPlugin({
                    uglifyOptions: {
                        output: {
                            comments: false, // 去掉注释
                        },
                        warnings: false,
                        compress: {
                            drop_console: true,
                            drop_debugger: true,
                            pure_funcs: ['console.log']//移除console
                        }
                    }
                })
            ]
        }

        if (page === 'analyz') {
            config
                .plugin('webpack-bundle-analyzer')
                .use(require('webpack-bundle-analyzer').BundleAnalyzerPlugin)
        }

        // 移除prefetch插件，避免加载多余的资源
        config.plugins.delete('prefetch');


        config.plugins.delete('preload');


        // config.module
        //     .rule('images')
        //     .use('image-webpack-loader')
        //     .loader('image-webpack-loader')
        //     .options({
        //         bypassOnDebug: true
        //     }).end();

        // set preserveWhitespace
        config.module
            .rule('vue')
            .use('vue-loader')
            .loader('vue-loader')
            .tap(options => {
                options.compilerOptions.preserveWhitespace = true;
                return options
            })
            .end();
        if (IS_PROD) {
            config
                .plugin('ScriptExtHtmlWebpackPlugin')
                .after('html')
                .use('script-ext-html-webpack-plugin', [{
                    // `runtime` must same as runtimeChunk name. default is `runtime`
                    inline: /runtime\..*\.js$/
                }])
                .end();
            config.optimization.minimize(true);
            config
                .optimization.splitChunks({
                chunks: 'all',
                minSize: 30000,  //表示在压缩前的最小模块大小,默认值是30kb
                minChunks: 2,  // 表示被引用次数，默认为1；
                maxAsyncRequests: 8,  //所有异步请求不得超过5个
                maxInitialRequests: 3,  //初始话并行请求不得超过3个
                automaticNameDelimiter: '~',//名称分隔符，默认是~
                name: true,  //打包后的名称，默认是chunk的名字通过分隔符（默认是～）分隔
                cacheGroups: {
                    vendors: {
                        name: 'chunk-vendors',
                        test: /node_modules/,
                        priority: -10,
                        chunks: 'initial' // only package third parties that are initially dependent
                    },
                    elementui: {
                        name: 'elementui', // split elementUI into a single package
                        priority: 20, // the weight needs to be larger than libs and app or it will be packaged into libs or app
                        test: /[\\/]node_modules[\\/]_?element-ui(.*)/ // in order to adapt to cnpm
                    },
                    alioss: {
                        name: 'alioss', // split elementUI into a single package
                        priority: 23, // the weight needs to be larger than libs and app or it will be packaged into libs or app
                        test: /[\\/]node_modules[\\/]_?ali-oss(.*)/ // in order to adapt to cnpm
                    },
                    appinfo: {
                        name: 'appinfo', // split elementUI into a single package
                        priority: 23, // the weight needs to be larger than libs and app or it will be packaged into libs or app
                        test: /[\\/]node_modules[\\/]_?app-info-parser(.*)/ // in order to adapt to cnpm
                    },
                    qrcodejs2: {
                        name: 'qrcodejs2', // split elementUI into a single package
                        priority: 23, // the weight needs to be larger than libs and app or it will be packaged into libs or app
                        test: /[\\/]node_modules[\\/]_?qrcodejs2(.*)/ // in order to adapt to cnpm
                    },
                    qiniujs: {
                        name: 'qiniujs', // split elementUI into a single package
                        priority: 24, // the weight needs to be larger than libs and app or it will be packaged into libs or app
                        test: /[\\/]node_modules[\\/]_?qiniu-js(.*)/ // in order to adapt to cnpm
                    },
                    common: {
                        name: 'chunk-commons',
                        test: resolve('src/components'), // can customize your rules
                        minChunks: 3, //  minimum common number
                        priority: 5,
                        reuseExistingChunk: true
                    }
                }
            });
            config.optimization.runtimeChunk('single');
        }
    }
};

