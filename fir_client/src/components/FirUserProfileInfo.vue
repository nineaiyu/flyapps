<template>
    <div>

        <el-form ref="form" :model="userinfo">
            <el-form-item>
                <el-row>
                    <el-col :span="22">
                        <el-input v-model="userinfo.username" prefix-icon="el-icon-user" placeholder="用户名"
                                  disabled></el-input>
                    </el-col>
                </el-row>
            </el-form-item>
            <el-form-item>
                <el-row>
                    <el-col :span="18">
                        <el-input v-model="userinfo.domain_name" :readonly="editdomain_name !== true" ref="domain_name"
                                  prefix-icon="el-icon-download"
                                  placeholder="下载页域名"></el-input>
                    </el-col>
                    <el-col :span="2">
                        <el-button icon="el-icon-edit" @click="changeQQValue">
                        </el-button>
                    </el-col>
                    <el-col :span="4" v-if="editdomain_name === true">
                        <el-button type="success" @click="saveQQ" plain
                                   style="margin:0 4px;border-radius:4px;cursor:pointer;height: 36px">保存
                        </el-button>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item>
                <el-row>
                    <el-col :span="18">
                        <el-input v-model="userinfo.job" ref="position" :readonly="editposition !== true"
                                  prefix-icon="el-icon-postcard" placeholder="职位"></el-input>
                    </el-col>
                    <el-col :span="2">
                        <el-button icon="el-icon-edit" @click="changePositionValue">
                        </el-button>
                    </el-col>
                    <el-col :span="4" v-if="editposition === true">
                        <el-button type="success" @click="savePositionValue" plain
                                   style="margin:0 4px;border-radius:4px;cursor:pointer;height: 36px">保存
                        </el-button>
                    </el-col>
                </el-row>
            </el-form-item>


            <el-form-item>
                <el-row>
                    <el-col :span="18">
                        <el-input v-model="userinfo.mobile" ref="phone" :readonly="editphone !== true"
                                  prefix-icon="el-icon-mobile" placeholder="手机" maxlength="11"></el-input>
                    </el-col>
                    <el-col :span="2">
                        <el-button icon="el-icon-edit" @click="changePhoneValue">
                        </el-button>
                    </el-col>
                    <el-col :span="4" v-if="editphone === true">
                        <el-button type="success" @click="savePhone" plain
                                   style="margin:0 4px;border-radius:4px;cursor:pointer;height: 36px">保存
                        </el-button>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item v-if="editphone === true">
                <el-row :gutter="10">
                    <el-col :span="12">
                        <el-input v-model="userinfo.sms_code" prefix-icon="el-icon-mobile" placeholder="验证码"
                                  maxlength="6"></el-input>
                    </el-col>
                    <el-col :span="6">
                        <el-button type="info" @click="getphonecode" plain
                                   style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px">获取验证码
                        </el-button>
                    </el-col>

                </el-row>
            </el-form-item>

        </el-form>


    </div>
</template>

<script>
    import {userinfos} from '../restful'

    export default {
        name: "FirUserProfileInfo",
        data() {
            return {
                userinfo: {
                    srccode: 'https://fuss10.elemecdn.com/e/5d/4a731a90594a4af544c0c25941171jpeg.jpeg',
                },
                editphone: false,
                editdomain_name: false,
                editposition: false
            }
        }, methods: {
            saveQQ() {
                this.updateUserInfo({"methods": 'PUT', 'data': this.userinfo});
                this.changeQQValue()
            },
            savePositionValue() {
                this.updateUserInfo({"methods": 'PUT', 'data': this.userinfo});
                this.changePositionValue()
            },
            savePhone() {
                this.updateUserInfo({"methods": 'PUT', 'data': this.userinfo});
                this.changePhoneValue()
            },
            updateUserInfo(datainfo) {
                userinfos(data => {
                    if (data.code === 1000) {
                        this.userinfo = data.data;
                        this.$store.dispatch("doUserinfo", data.data);
                        if (data.data.sms_code) {
                            this.$notify({
                                title: '验证码',
                                message: '您正在修改手机号码，验证码为:' + data.data.sms_code,
                                type: 'success'
                            });
                        }
                        if (datainfo.data) {
                            this.$message.success("更新成功")
                        }
                    } else {
                        this.$message.error("更新失败")

                    }
                }, datainfo)
            },
            changePhoneValue() {
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
            changeQQValue() {
                this.editdomain_name = !this.editdomain_name;
                if (this.$refs.domain_name.$el.children[0].style.backgroundColor) {
                    this.$refs.domain_name.$el.children[0].style.backgroundColor = ''
                } else {
                    this.$refs.domain_name.$el.children[0].style.backgroundColor = '#f6ffdc';
                }
            },
            getphonecode() {
                this.updateUserInfo({"methods": 'GET', 'data': {'act': 'sms'}});

            }
        }, mounted() {
            this.$store.dispatch('douserInfoIndex', 0);
            // this.updateUserInfo({"methods":false});
            this.userinfo = this.$store.state.userinfo;

        }, watch: {
            '$store.state.userinfo': function () {
                this.userinfo = this.$store.state.userinfo;
            }
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
        position: relative;
        height: 50px;

    }

    .el-button {
        padding: 0;
        border: none;
        background-color: transparent;
        color: #e2644c;

    }

    .el-button:hover {
        background-color: #bfe7f9;
    }

    .el-button:focus {
        background-color: #bfe7f9;
    }

</style>
