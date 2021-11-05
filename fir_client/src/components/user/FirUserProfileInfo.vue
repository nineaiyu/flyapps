<template>
    <div>

        <el-dialog
                :visible.sync="show_wx_visible"
                width="780px"
                center
                :close-on-click-modal="false"
                :close-on-press-escape="false">
                <span slot="title" style="color: #313639;font-size: 28px; margin-bottom: 14px;">
                    微信授权登录用户信息
                </span>
            <el-tag style="margin-bottom: 10px">授权用户将可以使用微信扫码直接登录</el-tag>
            <el-table
                    :data="wx_user_list"
                    stripe
                    border
                    style="width: 100%">


                <el-table-column
                        label="昵称"
                        align="center"
                        width="180">
                    <template slot-scope="scope">
                        <el-popover trigger="hover" placement="top">
                            <p>昵称: {{ scope.row.nickname }}</p>
                            <p>性别: {{ scope.row.sex|sex_filter }}</p>
                            <p>住址: {{ scope.row.address }}</p>
                            <p>openid: {{ scope.row.openid }}</p>
                            <div slot="reference" class="name-wrapper">
                                <el-tag size="medium">{{ scope.row.nickname }}</el-tag>
                            </div>
                        </el-popover>
                    </template>
                </el-table-column>

                <el-table-column
                        label="头像"
                        align="center"
                        width="120">
                    <template slot-scope="scope">
                        <el-image :src="scope.row.head_img_url" style="width: 80px;height: 80px"/>
                    </template>
                </el-table-column>

                <el-table-column
                        label="关注公众号"
                        align="center"
                        width="100">
                    <template slot-scope="scope">
                        <div slot="reference" class="name-wrapper">
                            <el-tag size="medium" v-if="scope.row.subscribe">是</el-tag>
                            <el-tag size="medium" v-else type="danger">否</el-tag>
                        </div>
                    </template>
                </el-table-column>
                <el-table-column
                        label="授权时间"
                        align="center"
                        width="200">
                    <template slot-scope="scope">
                        <i class="el-icon-time"></i>
                        <span style="margin-left: 10px">{{ scope.row.created_time|format_time }}</span>
                    </template>
                </el-table-column>
                <el-table-column
                        label="操作"
                        align="center"
                >
                    <template slot-scope="scope">
                        <el-button
                                size="mini"
                                type="danger"
                                @click="delete_wx_u(scope.row)">移除授权
                        </el-button>
                    </template>
                </el-table-column>
            </el-table>

        </el-dialog>

        <el-form ref="form" :model="userinfo" label-width="90px">
            <el-form-item label="用户名" v-if="userinfo && userinfo.login_type && userinfo.login_type.up">
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
                                  :disabled="!captcha.change_type.sms"/>
                    </el-col>
                    <el-col :span="1">
                        <el-button icon="el-icon-edit" @click="changePhoneValue">
                        </el-button>
                    </el-col>
                    <el-col :span="5" v-if="editphone === true && captcha.change_type.sms">
                        <el-button type="success" @click="savePhone" plain
                                   class="save-button">
                            保存
                        </el-button>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="图片验证码" style="height: 40px"
                          v-if="editphone === true && captcha.captcha_image && captcha.change_type.sms">
                <el-row style="height: 40px" :gutter="36">
                    <el-col :span="14">
                        <el-input placeholder="请输入图片验证码" v-model="userinfo.authcode" maxlength="6" clearable/>
                    </el-col>
                    <el-col :span="8">
                        <el-image
                                style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px"
                                :src="captcha.captcha_image"
                                fit="contain" @click="get_auth_code">
                        </el-image>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="手机验证码" v-if="editphone === true && captcha.change_type.sms">
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
                                  :disabled="!captcha.change_type.email"/>
                    </el-col>
                    <el-col :span="1">
                        <el-button icon="el-icon-edit" @click="changeemailValue">
                        </el-button>
                    </el-col>
                    <el-col :span="5" v-if="editemail === true && captcha.change_type.email">
                        <el-button type="success" @click="saveemail" plain
                                   class="save-button">
                            保存
                        </el-button>
                    </el-col>
                </el-row>
            </el-form-item>


            <el-form-item label="图片验证码" style="height: 40px"
                          v-if="editemail === true && captcha.captcha_image && captcha.change_type.email">
                <el-row style="height: 40px" :gutter="36">
                    <el-col :span="14">
                        <el-input placeholder="请输入图片验证码" v-model="userinfo.authcode" maxlength="6" clearable/>
                    </el-col>
                    <el-col :span="8">
                        <el-image
                                style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px"
                                :src="captcha.captcha_image"
                                fit="contain" @click="get_auth_code">
                        </el-image>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="邮箱验证码" v-if="editemail === true && captcha.change_type.email">
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

            <div class="other-way"
                 v-if="userinfo && userinfo.login_type && userinfo.login_type.third && JSON.stringify(userinfo.login_type.third).indexOf('true')!==-1">
                <hr>
                <span class="info">绑定第三方账户</span>
                <el-row :gutter="20" v-if="userinfo.login_type.third && userinfo.login_type.third.wxp">
                    <el-col :span="6" :offset="6">
                        <el-popover
                                placement="top"
                                trigger="manual"
                                title="打开微信扫一扫进行绑定"
                                v-model="wx_visible">
                            <div>
                                <el-image :src="wx_login_qr_url" style="width: 176px;height: 166px"/>
                            </div>
                            <el-button slot="reference" size="small" @click="wxLogin">绑定微信</el-button>
                        </el-popover>
                    </el-col>
                    <el-col :span="6">
                        <el-button size="small" @click="get_wx_user_list">授权信息</el-button>
                    </el-col>
                </el-row>

            </div>

        </el-form>


    </div>
</template>

<script>
    import {changeInfoFun, getAuthcTokenFun, userinfos, wxLoginFun, wxutils} from '@/restful'
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
                captcha: {"captcha_image": '', "captcha_key": '', "length": 8, change_type: {email: false, sms: false}},
                form: {},
                wx_login_qr_url: '',
                wx_visible: false,
                loop_flag: false,
                show_wx_visible: false,
                wx_user_list: [],
                pagination: {"currentPage": 1, "total": 0, "pagesize": 999},
            }
        }, methods: {
            delete_wx_u(wx_user_info) {
                this.$confirm(`此操作将导致微信用户 “${wx_user_info.nickname}” 无法通过扫码登录, 是否继续删除?`, '提示', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.wxUtilsFun({
                        methods: 'DELETE',
                        data: {
                            "size": this.pagination.pagesize,
                            "page": this.pagination.currentPage,
                            "user_id": wx_user_info.user_id,
                            "openid": wx_user_info.openid,
                        }
                    })
                }).catch(() => {
                    this.$message({
                        type: 'info',
                        message: '已取消删除'
                    });
                });
            },
            wxUtilsFun(params) {
                wxutils(data => {
                    if (data.code === 1000) {
                        this.wx_user_list = data.data;
                        this.show_wx_visible = true
                    } else {
                        this.$message.error("获取授权列表失败")
                    }
                }, params)
            },
            get_wx_user_list() {
                this.wxUtilsFun({
                    methods: 'GET',
                    data: {
                        "size": this.pagination.pagesize,
                        "page": this.pagination.currentPage
                    }
                })
            },
            loop_get_wx_info(wx_login_ticket) {
                if (wx_login_ticket && wx_login_ticket.length < 3) {
                    this.$message.error("获取登陆码失败，请稍后再试");
                    return
                }
                let c_count = 1;
                // eslint-disable-next-line no-unused-vars
                const loop_t = window.setInterval(res => {
                    if (!this.loop_flag) {
                        window.clearInterval(loop_t);
                    }
                    wxLoginFun(data => {
                        c_count += 1;
                        if (c_count > 120) {
                            window.clearInterval(loop_t);
                        }
                        if (data.code === 1000) {
                            window.clearInterval(loop_t);
                            if (this.userinfo.uid === data.userinfo.uid) {
                                this.$message.success("绑定成功");
                                this.wx_visible = false;
                                this.loop_flag = false;
                            }
                        } else if (data.code === 1005) {
                            window.clearInterval(loop_t);
                            this.$message({
                                message: data.msg,
                                type: 'error',
                                duration: 30000
                            });
                        }
                    }, {
                        "methods": "POST",
                        data: {"ticket": wx_login_ticket}
                    })
                }, 3000)

            },
            wxLogin() {
                this.wx_visible = !this.wx_visible;
                this.wx_login_qr_url = '';
                if (this.wx_visible) {
                    userinfos(data => {
                        if (data.code === 1000) {
                            this.wx_login_qr_url = data.data.qr;
                            this.loop_flag = true;
                            this.loop_get_wx_info(data.data.ticket);
                        } else {
                            this.$message.error(data.msg);
                            this.wx_visible = false;
                            this.loop_flag = false;
                        }
                    }, {
                        "methods": "POST",
                    })
                } else {
                    this.loop_flag = false;
                }
            },
            get_auth_code() {
                changeInfoFun(data => {
                    if (data.code === 1000) {
                        this.captcha = data.data;
                        this.userinfo.captcha_key = this.captcha.captcha_key;
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
                    captcha_key: this.userinfo.captcha_key,
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
                    "captcha_key": this.captcha.captcha_key,
                };
                let params = {
                    'act': act, 'target': target, 'ext': picode
                };
                if (this.captcha.geetest) {
                    geetest(this, this.form.email, target, params, (n_params) => {
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
        }, filters: {
            sex_filter: function (x) {
                let ret = '未知';
                if (x === 1) {
                    ret = '男'
                } else if (x === 2) {
                    ret = '女'
                }
                return ret;
            },
            format_time: function (x) {
                if (x) {
                    x = x.split(".")[0].split("T");
                    return x[0] + " " + x[1]
                } else
                    return '';
            }
        }
    }
</script>

<style scoped>

    .other-way {
        position: relative;
        text-align: center;
    }

    .other-way hr {
        height: 1px;
        margin: 30px 0;
        border: 0;
        background-color: #e4e7ed;
    }

    .other-way span.info {
        font-size: 12px;
        line-height: 1;
        position: absolute;
        top: -6px;
        left: 50%;
        padding: 0 10px;
        transform: translate(-50%, 0);
        color: #9ba3af;
    }

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
