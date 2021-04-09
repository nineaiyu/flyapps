<template>
    <div>

        <el-form ref="form" :model="form">
            <el-form-item label="当前密码">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-input v-model="form.oldpassword" show-password autofocus prefix-icon="el-icon-unlock"
                                  placeholder="当前密码" clearable/>
                    </el-col>
                </el-row>
            </el-form-item>
            <el-form-item label="新密码">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-input v-model="form.newpassword" show-password prefix-icon="el-icon-lock"
                                  placeholder="新密码" clearable/>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item label="确认密码">
                <el-row :gutter="36">
                    <el-col :span="18">
                        <el-input v-model="form.surepassword" show-password prefix-icon="el-icon-lock"
                                  placeholder="确认密码" clearable/>
                    </el-col>
                </el-row>
            </el-form-item>

            <el-form-item>
                <el-row :gutter="36">
                    <el-col :span="24">
                        <el-button type="primary" @click="updatepasswd">更新密码</el-button>
                    </el-col>
                </el-row>
            </el-form-item>

        </el-form>


    </div>
</template>

<script>
    import {userinfos} from "../restful";

    export default {
        name: "FirUserProfileChangePwd",
        data() {
            return {
                form: {
                    oldpassword: '',
                    newpassword: '',
                    surepassword: ''
                },
            }
        }, methods: {
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
            this.$store.dispatch('douserInfoIndex', 1);
        }
    }
</script>

<style scoped>
    .el-form {
        max-width: 500px;
        margin: 0 auto;
    }

    .el-form-item .el-button {
        margin-top: 20px;
        max-width: 260px;
        width: 100%;
        height: 50px;
        /*margin-left: 40px;*/
    }

    /deep/ .el-form-item__label {
        width: 90px;
    }


</style>
