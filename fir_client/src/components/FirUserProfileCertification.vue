<template>
    <div>

        <el-form ref="form" :model="form">
            <el-form-item>
                <el-row>
                    <el-col :span="22">
                        <el-input v-model="form.oldpassword" autofocus="true" prefix-icon="el-icon-user"
                                  placeholder="真实姓名" clearable></el-input>
                    </el-col>
                </el-row>
            </el-form-item>
            <el-form-item>
                <el-row>
                    <el-col :span="22">
                        <el-input v-model="form.newpassword" clearable prefix-icon="el-icon-s-order"
                                  placeholder="身份证号"></el-input>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item>
                <el-row>
                    <el-col :span="22">
                        <el-input v-model="form.surepassword" clearable prefix-icon="el-icon-house"
                                  placeholder="居住地"></el-input>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="身份证" style="width: 100%">

                <div class="appdownload">
                    <el-image
                            style="width: 155px;height: 188px;margin-right: 20px;background-color: #d1eef9;float: left"
                            fit="scale-down"
                            @click="delscreen(screen.id)"
                            v-for="(screen) in user_certification" :key="screen.id" :src="screen.url" alt=""/>
                    <div style="width: 155px;height: 188px;background-color: #d1eef9;float: left"
                         v-if="user_certification && user_certification.length < 2">
                        <el-upload
                                drag
                                action="#"
                                accept=".png , .jpg , .jpeg"
                                :before-upload="beforeAvatarUpload">
                            <i class="el-icon-upload"></i>
                        </el-upload>
                    </div>

                </div>

            </el-form-item>


            <el-form-item>
                <el-row>
                    <el-col :span="22">
                        <el-input v-model="form.mobile" ref="phone" clearable
                                  prefix-icon="el-icon-mobile" placeholder="请输入手机号码" maxlength="11"></el-input>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item style="height: 40px" v-if="cptch.cptch_image">
                <el-row style="height: 40px" :gutter="10">
                    <el-col :span="11">
                        <el-input placeholder="请输入图片验证码" v-model="userinfo.authcode" maxlength="6"></el-input>
                    </el-col>
                    <el-col :span="8">
                        <el-image
                                style="margin:0px 4px;border-radius:4px;cursor:pointer;height: 40px"
                                :src="cptch.cptch_image"
                                fit="contain" @click="get_auth_code">
                        </el-image>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item>
                <el-row :gutter="10">
                    <el-col :span="16">
                        <el-input v-model="userinfo.auth_key" prefix-icon="el-icon-mobile" placeholder="请输入您收到的验证码"
                                  maxlength="6"></el-input>
                    </el-col>
                    <el-col :span="6">
                        <el-button type="info" @click="getsmsemailcode('sms',userinfo.mobile)" plain
                                   style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px;background-color: #ecf5ff;color: #dd6161">
                            获取验证码
                        </el-button>
                    </el-col>

                </el-row>
            </el-form-item>


            <el-form-item>
                <el-row>
                    <el-col :span="22">
                        <el-button type="danger" @click="updatepasswd">提交</el-button>
                    </el-col>
                </el-row>
            </el-form-item>

        </el-form>


    </div>
</template>

<script>
    import {userinfos} from "../restful";
    import {AvatarUploadUtils} from "../utils";

    export default {
        name: "FirUserProfileCertification",
        data() {
            return {
                form: {
                    oldpassword: '',
                    newpassword: '',
                    surepassword: ''
                },
                cptch: {},
                userinfo: {},
                user_certification: [],
            }
        }, methods: {
            beforeAvatarUpload(file) {
                // eslint-disable-next-line no-unused-vars
                return AvatarUploadUtils(this, file, {
                    'app_id': this.$store.state.userinfo.uid,
                    'upload_key': file.name,
                    'ftype': 'certification',
                    'ext': {'type': 1}
                }, res => {
                });

            },
            updatepasswd() {
                if (this.form.newpassword === this.form.surepassword) {

                    userinfos(data => {
                        if (data.code === 1000) {
                            this.userinfo = data.data;
                            this.$message.success('密码修改成功');
                        } else {
                            this.$message.error('密码修改失败,' + data.msg);
                        }
                    }, {
                        "methods": 'PUT', 'data': {
                            "oldpassword": this.form.oldpassword,
                            "surepassword": this.form.surepassword
                        }
                    });
                } else {
                    this.$message.error('密码不一致');
                }
            }
        }, mounted() {
            this.$store.dispatch('douserInfoIndex', 2);
        }
    }
</script>

<style scoped>
    .el-form {
        max-width: 360px;
        margin: 0 auto;
    }

    .el-form-item .el-button {
        max-width: 360px;
        width: 100%;
        height: 50px;
    }

    .appdownload /deep/ .el-upload-dragger {
        background: #d1eef9;
        width: 155px;
        height: 188px;
    }

    .appdownload /deep/ .el-icon-upload {
        margin-top: 45%;
    }

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
        width: 178px;
        height: 178px;
        display: block;
    }
</style>
