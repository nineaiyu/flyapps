const IS_PROD = ['production', 'prod'].includes(process.env.NODE_ENV);
const path = require('path');

function resolve(dir) {
    return path.join(__dirname, dir);
}

const argv = process.argv;


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
    chunks: ['chunk-vendors', 'chunk-common', 'index']
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
        chunks: ['chunk-vendors', 'chunk-common', 'mshort']
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
        chunks: ['chunk-vendors', 'chunk-common', 'short']
};
let pages = {index,short,mshort};
const page = argv[3];
if(page){
    for(const key of Object.keys(pages)){
        if(key === page){
            pages = {key:pages[key]}
        }
    }
}
module.exports = {
    pages: pages,
    productionSourceMap: false,
    configureWebpack: {
        // provide the app's title in webpack's name field, so that
        // it can be accessed in index.html to inject the correct title.
        name: '应用分发',
        resolve: {
            alias: {
                '@': resolve('src')
            }
        }
    },
    chainWebpack: config => {

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


        config.optimization.splitChunks({
            cacheGroups: {
                vendors: {
                    name: 'chunk-vendors',
                    minChunks: 4,
                    test: /node_modules/,
                    priority: -10,
                    chunks: 'initial'
                },
                common: {}
            }
        });

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

        config.when(!IS_PROD,
                config => {
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
                        chunks: 'all',
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
                            commons: {
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
            );


    }

};

