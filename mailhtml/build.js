const spawn = require("child_process").spawn;
const path = require('path')
const fs = require('fs')
const cmdPath = path.resolve('./node_modules/.bin/mjml.cmd')


function build_html(file_full_path, buildPath) {
    let output_path = file_full_path.replace('mjml.html','html')
    output_path = path.join(buildPath,path.basename(output_path))
    return new Promise(function(resolve, reject) {
        let result = spawn(cmdPath, [file_full_path,'-o',output_path]);
        result.on('close', function(code) {
            if(code === 0){
                console.log('build success. output:'+output_path)
            }else {
                console.log('child process exited with code :' + code);
            }
        });
        result.stdout.on('data', function(data) {
            console.log('stdout: ' + data);
        });
        result.stderr.on('data', function(data) {
            console.log('stderr: ' + data);
            reject(new Error(data.toString()));
        });
        resolve();
    });
}
let filePath = path.resolve('./src')
let buildPath = path.resolve('./build')
fs.exists(buildPath,function (exists) {
    if(!exists){
        fs.mkdir(buildPath,res=>{
        })
    }else {
        fs.rmdir(buildPath,{recursive:true},res=>{
            fs.mkdir(buildPath,res=>{
            })
        })
    }
})
fs.readdir(filePath,function (err,files) {
    if (err) {
        console.warn(err, "读取文件夹错误！")
    } else {
        files.forEach(function(filename) {
            //获取当前文件的绝对路径
            let file_full_path = path.join(filePath, filename);
            fs.stat(file_full_path, function(error, stats) {
                if (error) {
                    console.warn('获取文件stats失败');
                } else {
                    if(stats.isFile() && file_full_path.endsWith('.mjml.html')){
                        build_html(file_full_path, buildPath).then()
                    }
                }
            })

        })
    }
})
