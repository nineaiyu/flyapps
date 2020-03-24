<template>


    <div style="margin-top: 20px;width: 56%;margin-left: 8%">
        <el-form ref="form" label-width="80px">
            <el-form-item label="应用ID">

                <el-row>
                    <el-col :span="19">
                        <el-input v-model="currentapp.app_id" :disabled="true"></el-input>

                    </el-col>
                    <el-col :span="4">
                        <el-button type="danger" plain @click="delApp"
                                   style="margin:0 8px;border-radius:4px;cursor:pointer;height: 40px">删除应用
                        </el-button>
                    </el-col>
                </el-row>

            </el-form-item>

            <el-form-item label="应用名称">
                <el-input v-model="currentapp.name"></el-input>
            </el-form-item>

            <el-form-item label="短链接">
                <el-input v-model="currentapp.short" maxlength="16" show-word-limit type="text">
                    <template slot="prepend">Http://</template>
                </el-input>
            </el-form-item>

            <el-form-item label="应用图标">
                <el-upload
                        class="avatar-uploader"
                        :action="getuppicurl"
                        :show-file-list="false"
                        accept=".png , .jpg , .jpeg"
                        :headers="uploadconf.AuthHeaders"
                        :on-success="handleAvatarSuccess"
                        :before-upload="beforeAvatarUpload">
                    <img v-if="currentapp.icon_url" :src="currentapp.icon_url"
                         class="avatar">
                    <i v-else class="el-icon-plus avatar-uploader-icon"></i>
                </el-upload>

            </el-form-item>

            <el-form-item label="应用描述">
                <el-input type="textarea" v-model="currentapp.description"
                          :autosize="{ minRows: 6, maxRows: 18}"></el-input>
            </el-form-item>
            <el-form-item>
                <el-button type="primary" @click="saveappinfo">保存</el-button>
            </el-form-item>
        </el-form>

    </div>


</template>

<script>
    import {deleteapp, getappinfos, getapppicurl, getuploadToken, updateapp} from "../restful"

    export default {
        name: "FirAppInfosbaseinfo",
        data() {
            return {
                currentapp: {},
                imageUrl: "",
                uploadconf:{},
            }
        },
        methods: {
            delApp() {
                //发送删除APP的操作
                this.$confirm('确认删除 ' + this.currentapp.name + ' ?')
                    // eslint-disable-next-line no-unused-vars
                    .then(res => {
                        this.willDeleteApp = false;
                        deleteapp(data => {
                            if (data.code === 1000) {
                                this.$message({
                                    message: '删除成功',
                                    type: 'success'
                                });
                                this.$router.push({name: 'FirApps'});
                            } else {
                                this.$message({
                                    message: '删除失败，请联系管理员',
                                    type: 'error'
                                });
                            }
                        }, {
                            "app_id": this.currentapp.app_id
                        });

                    })
                    // eslint-disable-next-line no-unused-vars
                    .catch(err => {
                        this.willDeleteApp = false;
                    });
                // alert('发送删除APP',this.delapp.name)
            },
            updateinfo(){
                getappinfos(data => {

                    if (data.code === 1000) {
                        this.appinfos = data.data;
                        this.master_release = data.data.master_release;
                        this.$store.dispatch("getUser",data.userinfo);
                        this.appinfos["icon_url"] = this.master_release.icon_url;
                        this.$store.dispatch('doucurrentapp', this.appinfos);

                    } else if (data.code === 1003) {
                        this.$router.push({name: 'FirApps'});
                    } else {
                        // eslint-disable-next-line no-console
                        console.log("失败了");
                    }
                }, {
                    "app_id": this.currentapp.app_id
                });
            },
            saveappinfo() {
                updateapp(data => {
                    if (data.code === 1000) {
                        this.$message.success('数据更新成功');
                    }else {
                        this.$message.error('操作失败,'+data.msg);
                    }
                }, {
                    "app_id": this.currentapp.app_id,
                    "data": {
                        "description": this.currentapp.description,
                        "short": this.currentapp.short,
                        "name": this.currentapp.name,
                    }
                });
            },
            handleAvatarSuccess(res, file) {
                this.imageUrl = URL.createObjectURL(file.raw);
                this.$message({
                    message: '应用图标上传成功',
                    type: 'success'
                });
                this.updateinfo();
            },
            beforeAvatarUpload(file) {
                const isLt2M = file.size / 1024 / 1024 < 2;
                if(file.type === 'image/jpeg' || file.type === 'image/png'|| file.type === 'image/jpg'){
                    if (isLt2M) {
                        // return true;

                        getuploadToken(data => {
                            if (data.code === 1000) {
                                // eslint-disable-next-line no-console
                                console.log(data.data)
                            }
                        },{'methods':false,'data':{'app_id':this.currentapp.app_id,'upload_key':file.name}});

                    }
                    else{
                        this.$message.error('上传头像图片大小不能超过 2MB!');
                    }
                }else {
                    this.$message.error('上传头像图片只能是 JPG/PNG/JPEG 格式!');

                }
                return false;
            }
        },
        mounted() {
            this.$store.dispatch('doappInfoIndex', [[18, 18], [18, 18]]);
            if(!this.currentapp.app_id){
                this.currentapp = this.$store.state.currentapp;
            }
            this.uploadconf = {
                "AuthHeaders": {"Authorization": this.$cookies.get("auth_token")}
            };
        },
        watch: {
            '$store.state.currentapp': function () {
                this.currentapp = this.$store.state.currentapp;
            }
        },computed:{
        getuppicurl(){
            return getapppicurl(this.currentapp.app_id)
        }
    }
    }
</script>

<style scoped>


    .avatar-uploader .el-upload {
        border: 1px dashed #d9d9d9;
        border-radius: 6px;
        cursor: pointer;
        position: relative;
        overflow: hidden;

    }

    .avatar-uploader .el-upload:hover {
        border-color: #409EFF;
    }

    .avatar-uploader-icon {
        font-size: 28px;
        color: #8c939d;
        width: 178px;
        height: 178px;
        line-height: 178px;
        text-align: center;
    }

    .avatar {
        height: 100px;
        width: 100px;
        border-radius: 10px;
        display: block;
    }
</style>
