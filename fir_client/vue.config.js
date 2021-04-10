const IS_PROD = ['production', 'prod'].includes(process.env.NODE_ENV);
const path = require('path');

function resolve(dir) {
    return path.join(__dirname, dir);
}
module.exports = {

    pages: {
        index: {
            // page 的入口
            entry: 'src/main.js',
            // 模板来源
            template: 'public/index.html',
            // 在 dist/index.html 的输出
            filename: 'index.html',
            // 当使用 title 选项时，
            // template 中的 title 标签需要是 <title><%= htmlWebpackPlugin.options.title %></title>
            title: 'FlyApp',
            // 在这个页面中包含的块，默认情况下会包含
            // 提取出来的通用 chunk 和 vendor chunk。
            chunks: ['chunk-vendors', 'chunk-common', 'index']
        },
        short: {
            // page 的入口
            entry: 'src/short.js',
            // entry: 'src/main.short.js',
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
        },
        mshort: {
            // page 的入口
            // entry: 'src/short.js',
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
        }

    },
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


    }

};

