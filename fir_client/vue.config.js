module.exports = {
    pages: {
        index: {
            entry: 'src/main.js',
            template: 'public/index.html',
            chunks:['chunk-vendors','chunk-common','index']
        },

        download: {
            entry: 'src/download.js',
            template: 'public/download.html',
            chunks:['chunk-vendors','chunk-common','download']

        },
    }
};