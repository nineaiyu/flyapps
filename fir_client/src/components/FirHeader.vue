<template>
    <div>
        <el-container class="navbar-wrapper">

            <el-dialog
                    title="API  Token"
                    :visible.sync="dialogVisible"
                    width="30%"
                    center
            >
                <span>可用于调用公开 API，可用于登录 fly-cli，请勿泄露您的 token</span>
                <el-main>
                    <el-link type="primary" v-if="token" :underline="false">{{ token }}</el-link>
                </el-main>
                <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="maketoken">重新生成</el-button>
             </span>
            </el-dialog>


            <el-row :gutter="20">
                <el-col :span="14" style="padding-top: 16px;margin-left: 60px">

                    <el-breadcrumb separator=">" style="height: 80px;font-size: 20px">
                        <el-breadcrumb-item :to="{ name:'FirIndex' }"><i class="el-icon-s-home elbi"></i>
                        </el-breadcrumb-item>
                        <el-breadcrumb-item :to="{ name:'FirApps'}"><i class="el-icon-apple elbi"></i>
                        </el-breadcrumb-item>
                        <el-breadcrumb-item v-if="$store.state.currentapp.name"
                                            :to="{name: 'FirAppInfostimeline', params: {id: $store.state.currentapp.app_id}}">
                            {{ $store.state.currentapp.name}}
                        </el-breadcrumb-item>
                    </el-breadcrumb>

                </el-col>
                <el-col :span="2" :push="3">
                    <div class="block">
                        <el-avatar :size="66" :src="$store.state.userinfo.head_img"></el-avatar>
                    </div>
                </el-col>
                <el-col :span="4" :push="3">
                    <el-dropdown style="padding-top: 12px;" @command="handleCommand">
                        <el-button type="success" plain round>
                            {{$store.state.userinfo.first_name }}<i class="el-icon-arrow-down el-icon--right"></i>
                        </el-button>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item command="userinfo">个人资料</el-dropdown-item>
                            <el-dropdown-item command="chpasswd">修改密码</el-dropdown-item>
                            <el-dropdown-item command="apitoken">API token</el-dropdown-item>
                            <el-dropdown-item command="storage" v-if="$store.state.userinfo.storage_active">存储管理
                            </el-dropdown-item>
                            <el-dropdown-item command="supersign" v-if="$store.state.userinfo.supersign_active">超级签名
                            </el-dropdown-item>

                            <el-dropdown-item command="exit">退出</el-dropdown-item>

                        </el-dropdown-menu>
                    </el-dropdown>

                </el-col>

            </el-row>


        </el-container>

    </div>
</template>

<script>
    // eslint-disable-next-line no-unused-vars
    import {logout, apitoken} from '../restful'

    export default {
        name: "FirHeader",
        data() {
            return {
                current_user: {},
                appName: '',
                token: '',
                dialogVisible: false
            }
        }, methods: {
            maketoken() {
                apitoken(data => {
                    if (data.code === 1000) {
                        this.token = data.data.token;
                        this.$message({
                            type: 'success',
                            message: '重新生成成功!'
                        });
                    }
                }, {methods: 'PUT', token: this.token});
            },
            handleCommand(command) {
                if (command === 'userinfo') {
                    this.$router.push({name: 'FirUserProfileInfo'})
                } else if (command === 'chpasswd') {
                    this.$router.push({name: 'FirUserProfileChangePwd'})
                } else if (command === 'storage') {
                    this.$router.push({name: 'FirUserProfileStorage'})
                } else if (command === 'supersign') {
                    this.$store.dispatch('doucurrentapp', {});
                    this.$router.push({"name": 'FirSuperSignBase', params: {act: "iosdeveloper"}})
                } else if (command === 'apitoken') {

                    this.dialogVisible = true;

                    apitoken(data => {
                        if (data.code === 1000) {
                            this.token = data.data.token;
                        }
                    }, {methods: 'GET', token: this.token});

                } else if (command === 'exit') {
                    logout(data => {
                        if (data.code === 1000) {
                            this.$message.success("退出成功");
                            this.$cookies.remove("token");
                            this.$cookies.remove("auth_token");
                            this.$cookies.remove("username");
                            this.$cookies.remove("first_name");
                            this.$store.dispatch('doucurrentapp', {});
                            this.$store.dispatch('doUserinfo', {});
                            this.$router.push({name: 'FirLogin'});
                        } else {
                            this.$message.error("退出失败")
                        }
                    }, {})
                }
            }

        }, created() {
            this.appName = this.$route.params.id
        }, watch: {
            $route: function () {
                this.appName = this.$route.params.id
            }
        }
    }
</script>

<style scoped>

    .el-container, .el-row {
        margin: 10px auto;
        width: 1166px;
    }

    .el-container {
        margin: 10px auto 100px;
        width: 1166px;
    }

    .navbar-wrapper {
        background-color: #dbffeb;
        font-size: 0;
        border-radius: 10px;
    }

    .el-dropdown {
        vertical-align: top;
    }

    .el-dropdown + .el-dropdown {
        margin-left: 15px;
    }

    .el-icon-arrow-down {
        font-size: 12px;
    }

    .elbi {
        color: #67c23a;
    }

</style>
