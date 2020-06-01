<template>
    <el-container>
        <div style="margin: 10px 0 10px 0 ;position:absolute;right:20px;top:auto;">
            <el-button round icon="el-icon-arrow-left" @click="$router.go(-1)"></el-button>
            <el-button round icon="el-icon-s-home" @click="$router.push({name:'FirIndex'})"></el-button>

        </div>
        <el-header>

            <div>
                <span>登录</span>
            </div>

        </el-header>
        <el-main>

            <el-form ref="form" :model="form">

                <el-form-item>
                    <el-input v-model="form.email" prefix-icon="el-icon-user" placeholder="邮箱" autofocus></el-input>
                </el-form-item>

                <el-form-item>
                    <el-input v-model="form.password" prefix-icon="el-icon-lock" placeholder="密码"
                              show-password></el-input>
                </el-form-item>
                <el-form-item style="height: 40px">
                    <el-row style="height: 40px">
                        <el-col :span="16">
                            <el-input placeholder="请输入验证码" v-model="form.authcode" maxlength="6"></el-input>
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
                    <el-button type="danger" @click="onSubmit">登录</el-button>
                </el-form-item>

                <!--                <el-form-item>-->
                <!--                    <el-button type="primary" @click="onRegister" plain>注册</el-button>-->
                <!--                </el-form-item>-->
            </el-form>


        </el-main>


    </el-container>

</template>

<script>
    import {loginFun, set_auth_token} from "../restful";

    export default {
        name: "FirLogin",
        data() {
            return {
                form: {
                    email: '',
                    password: '',
                    authcode: ''
                },
                cptch: {"cptch_image": '', "cptch_key": '', "length": 8},
            }
        },
        methods: {
            onSubmit() {
                let email = this.form.email;
                let password = this.form.password;
                let authcode = this.form.authcode;
                if (authcode.length === this.cptch.length) {
                    if (this.isEmail(email) && password.length > 6) {
                        loginFun(data => {
                            if (data.code == 1000) {
                                this.$message({
                                    message: '登录成功',
                                    type: 'success'
                                });
                                this.$cookies.remove("auth_token");
                                this.$cookies.set("token", data['token'], 3600 * 24 * 30);
                                this.$cookies.set("username", data.userinfo.username, 3600 * 24 * 30);
                                this.$cookies.set("first_name", data.userinfo.first_name, 3600 * 24 * 30);
                                this.$store.dispatch("doUserinfo", data.userinfo);
                                set_auth_token();
                                this.$router.push({name: 'FirApps'})
                            } else {
                                this.$message({
                                    message: data.msg,
                                    type: 'error'
                                });
                                this.get_auth_code();
                            }
                        }, {
                            "methods": "POST",
                            "data": {
                                "username": email,
                                "password": password,
                                "authcode": authcode,
                                "cptch_key": this.cptch.cptch_key
                            }
                        });


                    } else {
                        this.$message({
                            message: '请输入正确的邮箱地址',
                            type: 'warning'
                        });
                    }
                } else {
                    this.$message({
                        message: '验证码有误',
                        type: 'warning'
                    });
                }
            },
            onRegister() {
                this.$router.push({name: 'FirRegist'})
            },
            isEmail(input) {
                if (input.match(/^([a-zA-Z0-9_.-])+@(([a-zA-Z0-9-])+.)+([a-zA-Z0-9]{2,4})+$/)) {
                    return true;
                }
                return false;
            },
            get_auth_code() {
                loginFun(data => {
                    if (data.code == 1000) {
                        this.cptch = data.data;
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
        },
        mounted() {
            this.get_auth_code();
        }, created() {
        }
    }
</script>

<style scoped>

    .el-container {
        margin: 10px auto;
        width: 1166px;
    }

    .el-header {
        margin-top: 16%;
    }

    .el-form {
        max-width: 360px;
        margin: 0 auto;
    }

    .el-form-item .el-button {
        max-width: 360px;
        /*padding: 16px 20px;*/
        width: 100%;
        position: relative;
        height: 50px;

    }

    .el-header {
        text-align: center;
        overflow: hidden;
        margin-bottom: 50px
    }


    .el-header div span {
        font-size: 24px;
        display: inline-block;
        vertical-align: middle;
        padding: 8px 40px
    }

    .el-header div:before, .el-header div:after {
        content: ' ';
        display: inline-block;
        vertical-align: middle;
        width: 50%;
        height: 1px;
        background-color: #babfc3;
        margin: 0 0 0 -50%
    }

    .el-header div {
        text-align: center
    }

    .el-header div:after {
        margin: 0 -50% 0 0
    }

</style>
