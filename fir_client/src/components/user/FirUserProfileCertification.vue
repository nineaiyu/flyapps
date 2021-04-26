<template>
    <div v-if="(certification || certification === 0) && !cert_edit_flag">
        <el-form style="max-width: 400px">
            <el-form-item>
                <el-row>
                    <el-col :span="24">
                        <el-link :underline="false" type="success" style="font-size: x-large"
                                 v-if="certification.status === 1">已经认证
                        </el-link>
                        <el-link :underline="false" type="primary" style="font-size: x-large"
                                 v-else-if="certification.status === 0">审核中
                        </el-link>
                        <el-link v-else-if="certification.status === 2" :underline="false" type="danger"
                                 style="font-size: x-large"
                        >审核失败
                        </el-link>
                        <el-link :underline="false" type="info" style="font-size: x-large" v-else>待认证</el-link>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="真实姓名">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-link :underline="false">{{ certification.name }}</el-link>
                    </el-col>
                </el-row>
            </el-form-item>
            <el-form-item label="身份证号">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-link :underline="false">{{ certification.card }}</el-link>
                    </el-col>
                </el-row>
            </el-form-item>
            <el-form-item label="手机号码" v-if="certification.mobile">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-link :underline="false">{{ certification.mobile }}</el-link>
                    </el-col>
                </el-row>
            </el-form-item>
            <el-form-item label="联系地址">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-link :underline="false">{{ certification.addr }}</el-link>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item v-if="certification.status === 2" label="审核信息" style="width: 700px">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-link :underline="false" type="danger">{{ certification.msg }}</el-link>
                    </el-col>
                </el-row>
            </el-form-item>
            <el-form-item v-if="certification.status === 2">
                <el-row>
                    <el-col :span="24">
                        <el-button type="primary" @click="recommit">重新提交审核</el-button>
                    </el-col>
                </el-row>
            </el-form-item>
            <el-form-item v-if="certification_status === -1">
                <el-row>
                    <el-col :span="24">
                        <el-button type="primary" @click="goauth">开始认证</el-button>
                    </el-col>
                </el-row>
            </el-form-item>
        </el-form>
    </div>
    <div v-else>
        <el-form ref="form" :model="form">
            <el-form-item label="真实姓名">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-input v-model="form.name" :autofocus="true" prefix-icon="el-icon-user"
                                  placeholder="请输入真实姓名" clearable/>
                    </el-col>
                </el-row>
            </el-form-item>
            <el-form-item label="身份证号">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-input v-model="form.card" clearable prefix-icon="el-icon-s-order"
                                  placeholder="请输入身份证号"/>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="居住地址">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-input v-model="form.addr" clearable prefix-icon="el-icon-house"
                                  placeholder="请输入现居住地址"/>
                    </el-col>
                </el-row>
            </el-form-item>


            <el-form-item label="手机号码" v-if="cptch.change_type.sms">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-input v-model="form.mobile" ref="phone" clearable
                                  prefix-icon="el-icon-mobile" placeholder="请输入手机号码" maxlength="11"/>
                    </el-col>
                </el-row>
            </el-form-item>
            <el-form-item label="图片验证码" v-if="cptch.cptch_image">
                <el-row :gutter="11">
                    <el-col :span="12">
                        <el-input placeholder="请输入图片验证码" v-model="form.authcode" maxlength="6" clearable/>
                    </el-col>
                    <el-col :span="6">
                        <el-image
                                style="border-radius:4px;cursor:pointer;height: 40px"
                                :src="cptch.cptch_image"
                                fit="contain" @click="get_auth_code">
                        </el-image>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="手机验证码" v-if="cptch.change_type.sms">
                <el-row :gutter="11">
                    <el-col :span="12">
                        <el-input v-model="form.auth_key" prefix-icon="el-icon-mobile" placeholder="请输入您收到的验证码"
                                  maxlength="6" clearable/>
                    </el-col>
                    <el-col :span="6">
                        <el-button type="info" @click="getsmsemailcode('sms',form.mobile)" plain
                                   style="border-radius:4px;cursor:pointer;height: 40px;background-color: #ecf5ff;color: #dd6161">
                            获取验证码
                        </el-button>
                    </el-col>

                </el-row>
            </el-form-item>

            <el-form-item>
                <el-row style="margin-left: 88px">
                    <el-col :span="13">
                        <div id="captcha" ref="captcha"></div>
                    </el-col>
                </el-row>
            </el-form-item>
            <el-form-item label="身份证号">
                <el-row style="height: 40px" :gutter="36">
                    <el-col :span="19">
                        <div class="appdownload">
                            <el-upload
                                    drag
                                    action="#"
                                    accept=".png , .jpg , .jpeg"
                                    :before-upload="upload_one">

                                <el-tooltip v-if="user_certification.one" placement="top">
                                    <div slot="content">上传身份证<i style="color: #2abb9d!important;">国徽面</i>照片</div>
                                    <img :src="user_certification.one"
                                         class="avatar" alt="国徽面照片">
                                </el-tooltip>
                                <i v-else class="avatar-uploader-icon" style="text-align: center">
                                    上传身份证<i style="color: #2abb9d!important;">国徽面</i>照片
                                </i>
                            </el-upload>
                        </div>

                        <div class="appdownload">
                            <el-upload
                                    drag
                                    action="#"
                                    accept=".png , .jpg , .jpeg"
                                    :before-upload="upload_two">

                                <el-tooltip v-if="user_certification.two" placement="top">
                                    <div slot="content">上传身份证<i style="color: #2abb9d!important;">人像面</i>照片</div>
                                    <img :src="user_certification.two"
                                         class="avatar" alt="人像面照片">
                                </el-tooltip>
                                <i v-else class="avatar-uploader-icon" style="text-align: center">
                                    上传身份证<i style="color: #2abb9d!important;">人像面</i>照片
                                </i>
                            </el-upload>
                        </div>

                        <div class="appdownload">
                            <el-upload
                                    drag
                                    action="#"
                                    accept=".png , .jpg , .jpeg"
                                    :before-upload="upload_three">
                                <el-tooltip v-if="user_certification.three" placement="top">
                                    <div slot="content">上传<i style="color: #2abb9d!important;">手持身份证</i>照片</div>
                                    <img :src="user_certification.three"
                                         class="avatar" alt="手持身份证照片">
                                </el-tooltip>
                                <i v-else class="avatar-uploader-icon" style="text-align: center">
                                    上传<i style="color: #2abb9d!important;">手持身份证</i>照片
                                </i>
                            </el-upload>
                        </div>
                    </el-col>
                </el-row>
            </el-form-item>


            <el-form-item>
                <el-row>
                    <el-col :span="24" style="margin-top: 20px">
                        <el-button type="primary" @click="commit">提交</el-button>
                    </el-col>
                </el-row>
            </el-form-item>

        </el-form>
    </div>
</template>

<script>
    import {changeInfoFun, getAuthcTokenFun, user_certification} from "@/restful";
    import {AvatarUploadUtils, checkphone, geetest} from "@/utils";

    export default {
        name: "FirUserProfileCertification",
        data() {
            return {
                form: {},
                cptch: {
                    cptch_image: '',
                    cptch_key: '',
                    authcode: '',
                    length: 8,
                    change_type: {email: false, sms: false}
                },
                user_certification: {'one': '', 'two': '', 'three': ''},
                certification: {},
                certification_status: 0,
                cert_edit_flag: false
            }
        }, methods: {
            goauth() {
                this.cert_edit_flag = true;
                this.get_user_certification({methods: 'GET', data: {act: 'certpiccertinfo'}});
                this.get_auth_code();
            },
            recommit() {
                this.cert_edit_flag = true;
                this.get_user_certification({methods: 'GET', data: {act: 'certpiccertinfo'}});
                this.get_auth_code();
            },
            commit() {
                for (let v of Object.keys(this.form)) {
                    if (this.form[v].length < 2) {
                        this.$message.error("填写错误，请检查");
                        return false
                    }
                }
                let reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;
                if (reg.test(this.form.card) === false) {
                    this.$message.error("身份证输入不合法");
                    return false;
                }
                if (this.cptch.change_type.sms) {
                    let checkp = checkphone(this.form.mobile);
                    if (!checkp) {
                        this.$message.error("手机号输入不合法");
                        return false;
                    }
                }
                this.get_user_certification({methods: 'POST', data: this.form})
            },
            get_user_certification(params) {
                user_certification(res => {
                    if (res.code === 1000) {
                        if (params.methods === 'POST') {
                            this.$message.success("信息提交成功，正在审核中")
                        }
                        if (res.data.usercert) {
                            this.certification = res.data.usercert;
                        } else {
                            const ft = ['one', 'two', 'three'];
                            if (res.data.certification && res.data.certification.length > 0) {
                                for (let v of res.data.certification) {
                                    this.user_certification[ft[v.type - 1]] = v.certification_url;
                                }
                            }
                            if (res.data.user_certification) {
                                this.form = res.data.user_certification;
                            }
                        }

                    } else {
                        this.$message.error(res.msg)
                    }
                }, params)
            },

            getsmsemailcode(act, target) {
                let picode = {
                    "authcode": this.form.authcode,
                    "cptch_key": this.cptch.cptch_key,
                };
                if (!this.form.authcode) {
                    this.$message.error("图片验证码输入有误");
                    return;
                }
                let cptch_flag = this.form.authcode.length === this.cptch.length;
                if (this.cptch.cptch_key === '' || !this.cptch.cptch_key) {
                    cptch_flag = true
                }
                if (cptch_flag) {
                    let checkp = checkphone(this.form.mobile);
                    if (!checkp) {
                        this.$message.error("手机号输入有误");
                        return
                    }

                } else {
                    this.$message.error("图片验证码输入有误");
                    return
                }
                let params = {'act': act, 'target': target, 'ext': picode, 'user_id': target, 'ftype': 'certification'};
                this.form.email = this.form.mobile;
                if (this.cptch.geetest) {
                    geetest(this, params, (n_params) => {
                        this.get_phone_code(n_params);
                    })
                } else {
                    this.get_phone_code(params)
                }

            },

            get_phone_code(params) {
                getAuthcTokenFun(data => {
                    if (data.code === 1000) {
                        let msg = '您正在进行身份认证，验证码已经发送您手机';
                        this.$notify({
                            title: '验证码',
                            message: msg,
                            type: 'success'
                        });
                        this.form.auth_token = data.data.auth_token;
                    } else {
                        this.$message.error(data.msg)
                    }

                }, {"methods": 'POST', 'data': params})
            },

            get_auth_code() {
                if (this.form.authcode) {
                    this.form.authcode = '';
                }
                changeInfoFun(data => {
                    if (data.code === 1000) {
                        this.cptch = data.data;
                        if (this.cptch.cptch_key) {
                            this.form.cptch_key = this.cptch.cptch_key;
                        }
                    } else {
                        this.$message({
                            message: data.msg,
                            type: 'error'
                        });
                    }
                }, {
                    "methods": "GET",
                    "data": {}
                });
            },
            upload_one(file) {
                return this.beforeAvatarUpload(file, 1)
            },
            upload_two(file) {
                return this.beforeAvatarUpload(file, 2)
            },
            upload_three(file) {
                return this.beforeAvatarUpload(file, 3)
            },
            beforeAvatarUpload(file, ptype) {
                return AvatarUploadUtils(this, file, {
                    'app_id': this.$store.state.userinfo.uid,
                    'upload_key': file.name,
                    'ftype': 'certification',
                    'ext': {'ptype': ptype}
                    // eslint-disable-next-line no-unused-vars
                }, res => {
                    this.get_user_certification({methods: 'GET', data: {act: 'certpic'}});
                });

            },
            init() {
                if (this.$store.state.userinfo.certification || this.$store.state.userinfo.certification === 0) {
                    this.certification_status = this.$store.state.userinfo.certification;
                    if (this.certification_status !== -1) {
                        this.get_user_certification({methods: 'GET', data: {act: 'usercert'}});
                    }
                }

            },
        }, mounted() {
            this.$store.dispatch('douserInfoIndex', 2);
            this.init();
        }, watch: {
            '$store.state.userinfo': function () {
                this.init();
            }
        }
    }
</script>

<style scoped>
    .el-form {
        max-width: 800px;
        margin: 0 auto;
    }

    .el-form-item .el-button {
        max-width: 260px;
        width: 100%;
        height: 50px;
    }

    .appdownload /deep/ .el-upload-dragger {
        background: #d1eef9;
        width: 200px;
        height: 166px;
    }

    .appdownload /deep/ .el-icon-upload {
        margin-top: 45%;
    }

    .appdownload {
        float: left;
        width: 200px;
        height: 166px;
        background-color: #c2dcf1;
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
        color: #8c939d;
        width: 158px;
        height: 158px;
        line-height: 158px;
        text-align: center;
    }

    .avatar {
        width: 178px;
        height: 178px;
        display: block;
    }
</style>
