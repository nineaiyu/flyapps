<template>
    <el-main>
        <div class="user-info">

            <el-upload
                    class="avatar-uploader"
                    action="#"
                    :show-file-list="false"
                    accept=".png , .jpg , .jpeg"
                    :before-upload="beforeAvatarUpload">
                <img v-if="imageUrl" :src="imageUrl" class="avatar">
                <i v-else class="el-icon-plus avatar-uploader-icon"></i>
            </el-upload>

            <div class="name">
                <input v-model="userinfo.first_name" @focusout="update_name">
            </div>

            <div class="user_pro_tabs">

                <el-row :gutter="12" class="row">
                    <el-col :span="6" :offset="3">
                        <div class="col-4">
                            <a @click="$router.push({name:'FirUserProfileInfo'})" ref="userinfo" class="">
                        <span>
                            <i class="el-icon-user"></i>
                        </span>
                                个人资料
                            </a>
                        </div>
                    </el-col>
                    <el-col :span="6">
                        <div class="col-4">
                            <a ref="changepwd" class="" @click="$router.push({name:'FirUserProfileChangePwd'})">
                                <span><i class="el-icon-lock"></i></span>
                                修改密码
                            </a>
                        </div>

                    </el-col>

                    <el-col :span="6">
                        <div class="col-4">
                            <a ref="storage" class="" @click="$router.push({name:'FirUserProfileStorage'})">
                                <span><i class="el-icon-coin"></i></span>
                                存储配置
                            </a>
                        </div>

                    </el-col>

                </el-row>

            </div>
            <div style="margin-top: 50px">
                <router-view></router-view>
            </div>

        </div>

    </el-main>
</template>

<script>
    import {userinfos, getuserpicurl, uploadimgs, getuploadurl} from '../restful';
    import {uploadaliyunoss, uploadlocalstorage, uploadqiniuoss} from "../utils";

    export default {
        name: "FirUserProfileBase",
        data() {
            return {
                imageUrl: '',
                userinfo: {},
                uploadconf: {},
            }
        },
        methods: {
            updateimgs(certinfo) {
                uploadimgs(data => {
                    if (data.code === 1000) {
                        // eslint-disable-next-line no-console
                        console.log(data.data);
                        this.$message.success('上传成功');
                        this.updateUserInfo({"methods": 'GET'});

                    } else {
                        this.$message.error('更新失败');
                    }
                }, {'methods': 'PUT', 'data': {'certinfo': certinfo}});
            },
            uploadtostorage(file, certinfo) {

                if (certinfo.storage === 1) {
                    // eslint-disable-next-line no-unused-vars,no-unreachable
                    uploadqiniuoss(file, certinfo, this, res => {
                        this.updateimgs(certinfo);

                    }, process => {
                        this.uploadprocess = process;
                    })
                } else if (certinfo.storage === 2) {
                    // eslint-disable-next-line no-unused-vars
                    uploadaliyunoss(file, certinfo, this, res => {
                        this.updateimgs(certinfo);
                    }, process => {
                        this.uploadprocess = process;
                    });

                } else {
                    //本地
                    certinfo.upload_url = getuploadurl();
                    // eslint-disable-next-line no-unused-vars,no-unreachable
                    uploadlocalstorage(file, certinfo, this, res => {
                        this.updateimgs(certinfo);
                    }, process => {
                        this.uploadprocess = process;
                    })
                }

            },
            updateUserInfo(datainfo) {
                userinfos(data => {
                    if (data.code === 1000) {
                        this.userinfo = data.data;
                        this.$store.dispatch("getUser", data.data);
                        this.$store.dispatch('doucurrentapp', {});
                        this.imageUrl = data.data.head_img;

                        if (datainfo.data) {
                            this.$message.success("更新成功")
                        }
                    } else {
                        this.$message.error("更新失败")
                    }
                }, datainfo)
            },
            update_name() {
                this.updateUserInfo({"methods": 'PUT', 'data': {"first_name": this.userinfo.first_name}});
            },
            beforeAvatarUpload(file) {
                const isLt2M = file.size / 1024 / 1024 < 2;
                if (file.type === 'image/jpeg' || file.type === 'image/png' || file.type === 'image/jpg') {
                    if (isLt2M) {
                        uploadimgs(data => {
                            if (data.code === 1000) {
                                // eslint-disable-next-line no-console
                                console.log(data.data);
                                let certinfo = data.data;
                                this.uploadtostorage(file, certinfo);
                            }
                        }, {
                            'methods': 'GET',
                            'data': {'app_id': this.userinfo.uid, 'upload_key': file.name, 'ftype': 'head'}
                        });

                        return false;
                    } else {
                        this.$message.error('上传头像图片大小不能超过 2MB!');

                    }
                } else {
                    this.$message.error('上传头像图片只能是 JPG/PNG/JPEG 格式!');

                }
                return false;

            },
            setfunactive(item) {
                for (let key in this.$refs) {
                    if (key === item) {
                        this.$refs[key].classList.add('active');
                    } else {
                        this.$refs[key].classList.remove('active');
                    }
                }
            },
            autoSetInfoIndex() {
                if (this.$store.state.userInfoIndex === 0) {
                    this.setfunactive('userinfo');
                } else if (this.$store.state.userInfoIndex === 1) {
                    this.setfunactive('changepwd');
                } else if (this.$store.state.userInfoIndex === 2) {
                    this.setfunactive('storage');
                }
            }
        }, mounted() {
            this.autoSetInfoIndex();
            this.updateUserInfo({"methods": 'GET'});
        }, watch: {
            '$store.state.userInfoIndex': function () {
                this.autoSetInfoIndex();
            },
        }, filters: {}, computed: {
            getuppicurl() {
                return getuserpicurl()
            }
        }
    }
</script>

<style scoped>
    .el-main {
        margin: 10px auto 100px;
        width: 1166px;
        position: relative;
        padding-bottom: 1px;
        background-color: #bfe7f9;
        color: #9b9b9b;
        -webkit-font-smoothing: antialiased;
        border-radius: 1%;
    }

    .user-info {
        position: relative;
        text-align: center;
        margin-bottom: 60px;
        margin-top: 46px;
    }

    .avatar {
        height: 100px;
        width: 100px;
        border-radius: 50%;
        display: block;
    }

    .name {
        text-align: center;
        padding-bottom: 20px;

    }

    .name input {
        text-align: center;
        color: #889eff;
        margin: 36px auto 0;
        width: 280px;
        padding: 0;
        border: none;
        background-color: transparent;
        font-size: 30px;
    }

    .user_pro_tabs a {
        width: 100%;
        font-size: 16px;
        text-align: center;
        display: inline-block;
        line-height: 48px;
        height: 48px;
        border-bottom: 1px solid #BABFC3;
        text-decoration: none;
        color: #BABFC3;

    }

    .user_pro_tabs a > span {
        margin-right: 16px;
        vertical-align: middle
    }

    .user_pro_tabs a.active {
        color: #e2644c;
        border-bottom-color: #e2644c
    }


</style>
