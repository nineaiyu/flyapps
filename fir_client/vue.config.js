const IS_PROD = ['production', 'prod'].includes(process.env.NODE_ENV);
const path = require('path');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

function resolve(dir) {
    return path.join(__dirname, dir);
}

const argv = process.argv;

const CompressionWebpackPlugin = require('compression-webpack-plugin');

const compress = new CompressionWebpackPlugin(
    {
        filename: info => {
            return `${info.path}.gz${info.query}`
        },
        algorithm: 'gzip',
        threshold: 10240,
        test: new RegExp(
            '\\.(' +
            ['js'].join('|') +
            ')$'
        ),
        minRatio: 0.8,
        deleteOriginalAssets: false
    }
);

const index={
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
    chunks: ['chunk-vendors', 'chunk-common', 'index','chunk-libs','chunk-elementUI','chunk-commons','runtime','chunk-aliOss','chunk-qiniuJs','chunk-qrcodejs2']
};
const mshort={
        // page 的入口
        entry: 'src/main.short.js',
        // 模板来源
        template: 'public/short.html',
        // 在 dist/short.html 的输出
        filename: 'mshort.html',
        // 当使用 title 选项时，
        // template 中的 title 标签需要是 <title><%= htmlWebpackPlugin.options.title %></title>
        title: '应用下载',
        // 在这个页面中包含的块，默认情况下会包含
        // 提取出来的通用 chunk 和 vendor chunk。
        chunks: ['chunk-vendors', 'chunk-common', 'mshort','chunk-libs','chunk-elementUI','chunk-commons','runtime']
};
const short={
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
        chunks: ['chunk-vendors', 'chunk-common', 'short','chunk-libs','chunk-commons','runtime']
};
let pages = {index,short};
const page = argv[3];
if(page){
    for(const key of Object.keys(pages)){
        if(key === page){
            const tmp = pages[key];
            pages = {};
            pages[key] = tmp;
        }
    }
}
module.exports = {
    pages: pages,
    productionSourceMap: false, //去除生产环境的productionSourceMap
    assetsDir: "static", //静态文件存储位置
    lintOnSave: true,
    runtimeCompiler:true,
    // publicPath: './',
    configureWebpack: {
        // provide the app's title in webpack's name field, so that
        // it can be accessed in index.html to inject the correct title.
        name: '应用分发',
        resolve: {
            alias: {
                '@': resolve('src')
            }
        },
        plugins:[compress],
    },
    chainWebpack: config => {
        if(IS_PROD){
           config.optimization.minimizer=[
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

        if (page==='analyz') {
            config
                .plugin('webpack-bundle-analyzer')
                .use(require('webpack-bundle-analyzer').BundleAnalyzerPlugin)
        }

        if (!IS_PROD) {
            config.output
                .filename(bundle => {
                    return bundle.chunk.name === 'index' ? 'js/[name].js' : '[name]/[name].js'
                })
        }

        if (IS_PROD) {
            config.output
                .filename(bundle => {
                    return bundle.chunk.name === 'index' ? 'js/[name].[contenthash:8].js' : '[name]/[name].[contenthash:8].js'
                })

        }
        // 移除prefetch插件，避免加载多余的资源
        config.plugins.delete('prefetch');


        // config.plugins.delete('preload');

        // config.optimization.splitChunks({
        //     cacheGroups: {
        //         vendors: {
        //             name: 'chunk-vendors',
        //             minChunks: 4,
        //             test: /node_modules/,
        //             priority: -10,
        //             chunks: 'initial'
        //         },
        //         common: {}
        //     }
        // });

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

        if(IS_PROD) {
                    config
                        .plugin('ScriptExtHtmlWebpackPlugin')
                        .after('html')
                        .use('script-ext-html-webpack-plugin', [{
                            // `runtime` must same as runtimeChunk name. default is `runtime`
                            inline: /runtime\..*\.js$/
                        }])
                        .end();
                    config
                        .optimization.splitChunks({
                        chunks: 'async',
                        minSize: 30000,  //表示在压缩前的最小模块大小,默认值是30kb
                        minChunks: 2,  // 表示被引用次数，默认为1；
                        maxAsyncRequests: 8,  //所有异步请求不得超过5个
                        maxInitialRequests: 3,  //初始话并行请求不得超过3个
                        automaticNameDelimiter:'~',//名称分隔符，默认是~
                        name: true,  //打包后的名称，默认是chunk的名字通过分隔符（默认是～）分隔
                        cacheGroups: {
                            libs: {
                                name: 'chunk-libs',
                                test: /[\\/]node_modules[\\/]/,
                                priority: 10,
                                chunks: 'initial' // only package third parties that are initially dependent
                            },
                            elementUI: {
                                name: 'chunk-elementUI', // split elementUI into a single package
                                priority: 20, // the weight needs to be larger than libs and app or it will be packaged into libs or app
                                test: /[\\/]node_modules[\\/]_?element-ui(.*)/ // in order to adapt to cnpm
                            },
                            aliOss: {
                                name: 'chunk-aliOss', // split elementUI into a single package
                                priority: 21, // the weight needs to be larger than libs and app or it will be packaged into libs or app
                                test: /[\\/]node_modules[\\/]_?ali-oss(.*)/ // in order to adapt to cnpm
                            },
                            qiniuJs: {
                                name: 'chunk-qiniuJs', // split elementUI into a single package
                                priority: 22, // the weight needs to be larger than libs and app or it will be packaged into libs or app
                                test: /[\\/]node_modules[\\/]_?qiniu-js(.*)/ // in order to adapt to cnpm
                            },
                            qrcodejs2: {
                                name: 'chunk-qrcodejs2', // split elementUI into a single package
                                priority: 23, // the weight needs to be larger than libs and app or it will be packaged into libs or app
                                test: /[\\/]node_modules[\\/]_?qrcodejs2(.*)/ // in order to adapt to cnpm
                            },
                            commons: {
                                name: 'chunk-commons',
                                test: resolve(resolve('src/components')), // can customize your rules
                                minChunks: 2, //  minimum common number
                                priority: 5,
                                reuseExistingChunk: true
                            }
                        }
                    });
                    config.optimization.runtimeChunk('single');
                }
    }
};

