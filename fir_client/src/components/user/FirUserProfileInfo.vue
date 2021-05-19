<template>
    <div>

        <el-form ref="form" :model="userinfo" label-width="90px">
            <el-form-item label="用户名">
                <el-row :gutter="36">
                    <el-col :span="16">
                        <el-input v-model="userinfo.username" :readonly="edituser_name !== true"
                                  prefix-icon="el-icon-user" placeholder="用户名" ref="user_name"
                                  clearable/>
                    </el-col>

                    <el-col :span="1">
                        <el-button icon="el-icon-edit" @click="changeUsernameValue">
                        </el-button>
                    </el-col>
                    <el-col :span="5" v-if="edituser_name === true">
                        <el-button type="success" @click="saveUsername" plain
                                   class="save-button">
                            保存
                        </el-button>
                    </el-col>

                </el-row>
            </el-form-item>


            <el-form-item label="手机号码">
                <el-row :gutter="36">
                    <el-col :span="16">
                        <el-input v-model="userinfo.mobile" ref="phone" :readonly="editphone !== true"
                                  prefix-icon="el-icon-mobile" placeholder="手机" maxlength="11" clearable
                                  :disabled="!cptch.change_type.sms"/>
                    </el-col>
                    <el-col :span="1">
                        <el-button icon="el-icon-edit" @click="changePhoneValue">
                        </el-button>
                    </el-col>
                    <el-col :span="5" v-if="editphone === true && cptch.change_type.sms">
                        <el-button type="success" @click="savePhone" plain
                                   class="save-button">
                            保存
                        </el-button>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="图片验证码" style="height: 40px"
                          v-if="editphone === true && cptch.cptch_image && cptch.change_type.sms">
                <el-row style="height: 40px" :gutter="36">
                    <el-col :span="14">
                        <el-input placeholder="请输入图片验证码" v-model="userinfo.authcode" maxlength="6" clearable/>
                    </el-col>
                    <el-col :span="8">
                        <el-image
                                style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px"
                                :src="cptch.cptch_image"
                                fit="contain" @click="get_auth_code">
                        </el-image>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="手机验证码" v-if="editphone === true && cptch.change_type.sms">
                <el-row :gutter="36">
                    <el-col :span="16">
                        <el-input v-model="userinfo.auth_key" prefix-icon="el-icon-mobile" placeholder="验证码"
                                  maxlength="6" clearable/>
                    </el-col>
                    <el-col :span="7">
                        <el-button type="info" @click="getsmsemailcode('sms',userinfo.mobile)" plain
                                   class="save-button">
                            获取验证码
                        </el-button>
                    </el-col>

                </el-row>
            </el-form-item>


            <el-form-item label="邮箱地址">
                <el-row :gutter="36">
                    <el-col :span="16">
                        <el-input v-model="userinfo.email" ref="email" :readonly="editemail !== true"
                                  prefix-icon="el-icon-bank-card" placeholder="邮箱" maxlength="20" clearable
                                  :disabled="!cptch.change_type.email"/>
                    </el-col>
                    <el-col :span="1">
                        <el-button icon="el-icon-edit" @click="changeemailValue">
                        </el-button>
                    </el-col>
                    <el-col :span="5" v-if="editemail === true && cptch.change_type.email">
                        <el-button type="success" @click="saveemail" plain
                                   class="save-button">
                            保存
                        </el-button>
                    </el-col>
                </el-row>
            </el-form-item>


            <el-form-item label="图片验证码" style="height: 40px"
                          v-if="editemail === true && cptch.cptch_image && cptch.change_type.email">
                <el-row style="height: 40px" :gutter="36">
                    <el-col :span="14">
                        <el-input placeholder="请输入图片验证码" v-model="userinfo.authcode" maxlength="6" clearable/>
                    </el-col>
                    <el-col :span="8">
                        <el-image
                                style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px"
                                :src="cptch.cptch_image"
                                fit="contain" @click="get_auth_code">
                        </el-image>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="邮箱验证码" v-if="editemail === true && cptch.change_type.email">
                <el-row :gutter="36">
                    <el-col :span="16">
                        <el-input v-model="userinfo.auth_key" prefix-icon="el-icon-mobile" placeholder="验证码"
                                  maxlength="6" clearable/>
                    </el-col>
                    <el-col :span="7">
                        <el-button type="info" @click="getsmsemailcode('email',userinfo.email)" plain
                                   class="save-button">
                            获取验证码
                        </el-button>
                    </el-col>

                </el-row>
            </el-form-item>
            <el-form-item v-if="editphone === true || editemail === true">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <div id="captcha" ref="captcha"></div>
                    </el-col>
                </el-row>
            </el-form-item>

            <!--            <el-form-item label="下载域名">-->
            <!--                <el-row :gutter="36">-->
            <!--                    <el-col :span="16">-->
            <!--                        <el-input v-model="userinfo.domain_name" :readonly="editdomain_name !== true" ref="domain_name"-->
            <!--                                  prefix-icon="el-icon-download"-->
            <!--                                  placeholder="下载页域名" clearable/>-->
            <!--                    </el-col>-->
            <!--                    <el-col :span="1">-->
            <!--                        <el-button icon="el-icon-edit" @click="changeDomainValue">-->
            <!--                        </el-button>-->
            <!--                    </el-col>-->
            <!--                    <el-col :span="5" v-if="editdomain_name === true">-->
            <!--                        <el-button type="success" @click="saveDomain" plain-->
            <!--                                   class="save-button">-->
            <!--                            保存-->
            <!--                        </el-button>-->
            <!--                    </el-col>-->
            <!--                </el-row>-->
            <!--            </el-form-item>-->
            <el-form-item label="下载域名">
                <el-row :gutter="36">
                    <el-col :span="16">
                        <el-input :value="userinfo.domain_name" :readonly="true" ref="domain_name"
                                  prefix-icon="el-icon-download"
                                  placeholder="下载页域名" clearable/>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="职位">
                <el-row :gutter="36">
                    <el-col :span="16">
                        <el-input v-model="userinfo.job" ref="position" :readonly="editposition !== true"
                                  prefix-icon="el-icon-postcard" placeholder="职位" clearable/>
                    </el-col>
                    <el-col :span="1">
                        <el-button icon="el-icon-edit" @click="changePositionValue">
                        </el-button>
                    </el-col>
                    <el-col :span="5" v-if="editposition === true">
                        <el-button type="success" @click="savePositionValue" plain
                                   class="save-button">
                            保存

                        </el-button>
                    </el-col>
                </el-row>
            </el-form-item>


        </el-form>


    </div>
</template>

<script>
    import {changeInfoFun, getAuthcTokenFun, userinfos} from '@/restful'
    import {deepCopy, geetest} from "@/utils";

    export default {
        name: "FirUserProfileInfo",
        data() {
            return {
                userinfo: {
                    srccode: 'https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg',
                    authcode: ''
                },
                orguserinfo: {},
                editphone: false,
                editemail: false,
                editdomain_name: false,
                edituser_name: false,
                editposition: false,
                cptch: {"cptch_image": '', "cptch_key": '', "length": 8, change_type: {email: false, sms: false}},
                form: {},
            }
        }, methods: {
            get_auth_code() {
                changeInfoFun(data => {
                    if (data.code === 1000) {
                        this.cptch = data.data;
                        this.userinfo.cptch_key = this.cptch.cptch_key;
                        if (this.userinfo.authcode) {
                            this.userinfo.authcode = '';
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

            saveUsername() {
                if (this.userinfo.username.toString().length < 6) {
                    this.$message.error("密码至少6位");
                    return
                }
                this.updateUserInfo({"methods": 'PUT', 'data': {username: this.userinfo.username}});
                this.changeUsernameValue()
            },
            saveDomain() {
                this.updateUserInfo({"methods": 'PUT', 'data': {domain_name: this.userinfo.domain_name}});
                this.changeDomainValue()
            },
            savePositionValue() {
                this.updateUserInfo({"methods": 'PUT', 'data': {job: this.userinfo.job}});
                this.changePositionValue()
            },
            authinfo() {
                return {
                    auth_token: this.userinfo.auth_token,
                    auth_key: this.userinfo.auth_key,
                    cptch_key: this.userinfo.cptch_key,
                    authcode: this.userinfo.authcode,
                };
            },
            saveemail() {
                let data = this.authinfo();
                data.email = this.userinfo.email;
                data.act = 'email';
                this.updateUserInfo({"methods": 'PUT', 'data': data});
                this.changeemailValue()
            },
            savePhone() {
                let data = this.authinfo();
                data.mobile = this.userinfo.mobile;
                data.act = 'sms';
                this.updateUserInfo({"methods": 'PUT', 'data': data});
                this.changePhoneValue()
            },

            updateUserInfo(datainfo) {
                userinfos(data => {
                    if (data.code === 1000) {
                        this.userinfo = data.data;
                        this.$store.dispatch("doUserinfo", data.data);
                        this.orguserinfo = deepCopy(data.data);
                        if (datainfo.data) {
                            this.$message.success("更新成功")
                        }

                    } else {
                        this.$message.error("更新失败 " + data.msg);
                        this.$store.dispatch('doUserinfo', this.orguserinfo);

                    }
                }, datainfo)
            },
            changeemailValue() {
                if (this.editphone) {
                    this.editphone = !this.editphone;
                }
                this.get_auth_code();
                this.editemail = !this.editemail;
                if (this.$refs.email.$el.children[0].style.backgroundColor) {
                    this.$refs.email.$el.children[0].style.backgroundColor = ''
                } else {
                    this.$refs.email.$el.children[0].style.backgroundColor = '#f6ffdc';
                }

            },
            changePhoneValue() {
                if (this.editemail) {
                    this.editemail = !this.editemail;
                }
                this.get_auth_code();
                this.editphone = !this.editphone;
                if (this.$refs.phone.$el.children[0].style.backgroundColor) {
                    this.$refs.phone.$el.children[0].style.backgroundColor = ''
                } else {
                    this.$refs.phone.$el.children[0].style.backgroundColor = '#f6ffdc';
                }

            },
            changePositionValue() {
                this.editposition = !this.editposition;
                if (this.$refs.position.$el.children[0].style.backgroundColor) {
                    this.$refs.position.$el.children[0].style.backgroundColor = ''
                } else {
                    this.$refs.position.$el.children[0].style.backgroundColor = '#f6ffdc';
                }

            },
            changeUsernameValue() {
                this.edituser_name = !this.edituser_name;
                if (this.$refs.user_name.$el.children[0].style.backgroundColor) {
                    this.$refs.user_name.$el.children[0].style.backgroundColor = ''
                } else {
                    this.$refs.user_name.$el.children[0].style.backgroundColor = '#f6ffdc';
                }
            },
            changeDomainValue() {
                this.editdomain_name = !this.editdomain_name;
                if (this.$refs.domain_name.$el.children[0].style.backgroundColor) {
                    this.$refs.domain_name.$el.children[0].style.backgroundColor = ''
                } else {
                    this.$refs.domain_name.$el.children[0].style.backgroundColor = '#f6ffdc';
                }
            }, do_get_auth_token(params) {
                getAuthcTokenFun(data => {
                    if (data.code === 1000) {
                        this.userinfo.act = params.act;
                        let msg = '您正在修改手机号码，验证码已经发送您手机';
                        if (params.act === "email") {
                            msg = '您正在修改邮箱，验证码已经发送您邮箱';
                        }
                        this.$notify({
                            title: '验证码',
                            message: msg,
                            type: 'success'
                        });
                        this.userinfo.auth_token = data.data.auth_token;
                    } else {
                        this.$message.error(data.msg)
                    }

                }, {"methods": 'POST', 'data': params})
            },
            getsmsemailcode(act, target) {
                let picode = {
                    "authcode": this.userinfo.authcode,
                    "cptch_key": this.cptch.cptch_key,
                };
                let params = {
                    'act': act, 'target': target, 'ext': picode
                };
                if (this.cptch.geetest) {
                    this.form.email = target;
                    geetest(this, params, (n_params) => {
                        this.do_get_auth_token(n_params);
                    })
                } else {
                    this.do_get_auth_token(params);
                }
            }
        }, mounted() {
            this.$store.dispatch('douserInfoIndex', 0);
            // this.updateUserInfo({"methods":false});
            this.userinfo = this.$store.state.userinfo;
            this.orguserinfo = deepCopy(this.$store.state.userinfo);


        }, watch: {
            '$store.state.userinfo': function () {
                this.userinfo = this.$store.state.userinfo;
                this.orguserinfo = deepCopy(this.$store.state.userinfo);
            }
        }
    }
</script>

<style scoped>
    .el-form {
        max-width: 500px;
        margin: 0 auto;
    }


    .el-button {
        padding: 0;
        border: none;
        background-color: transparent;
        color: #7e5ef8;
    }

    .save-button {
        margin: 0 4px;
        border-radius: 4px;
        cursor: pointer;
        height: 36px;
        background-color: #409eff;
        color: #f9f9f9;
        max-width: 360px;
        width: 100%;
        position: relative;
    }

    .save-button:focus {
        background-color: #bfe7f9;
    }

</style>
