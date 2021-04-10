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

                    <el-breadcrumb separator-class="el-icon-arrow-right" style="height: 80px;font-size: 20px">
                        <el-breadcrumb-item :to="{ name:'FirIndex' }">首页</el-breadcrumb-item>
                        <el-breadcrumb-item :to="{ name:'FirApps'}">我的应用</el-breadcrumb-item>

                        <el-breadcrumb-item v-if="this.route_info.label" :to="{ name:route_info.name}">{{
                            this.route_info.label }}
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
                            <el-dropdown-item command="apitoken">API token</el-dropdown-item>
                            <el-dropdown-item command="storage" v-if="$store.state.userinfo.storage_active">存储管理
                            </el-dropdown-item>
                            <el-dropdown-item command="supersign" v-if="$store.state.userinfo.supersign_active">超级签名
                            </el-dropdown-item>
                            <el-dropdown-item command="myorder">订单信息</el-dropdown-item>
                            <el-dropdown-item command="exit">退出</el-dropdown-item>

                        </el-dropdown-menu>
                    </el-dropdown>

                </el-col>

            </el-row>


        </el-container>

    </div>
</template>

<script>
    import {apitoken, logout} from '@/restful'

    export default {
        name: "FirHeader",
        data() {
            return {
                current_user: {},
                appName: '',
                token: '',
                dialogVisible: false,
                route_info: {'name': '', 'label': ''},
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
                    } else {
                        this.$message.error("失败了 " + data.msg)
                    }
                }, {methods: 'PUT', token: this.token});
            },
            handleCommand(command) {
                if (command === 'userinfo') {
                    this.$router.push({name: 'FirUserProfileInfo'})
                } else if (command === 'storage') {
                    this.$router.push({name: 'FirUserStorage', params: {act: "change"}})
                } else if (command === 'supersign') {
                    this.$store.dispatch('doucurrentapp', {});
                    this.$router.push({"name": 'FirSuperSignBase', params: {act: "iosdeveloper"}})
                } else if (command === 'apitoken') {
                    apitoken(data => {
                        if (data.code === 1000) {
                            this.token = data.data.token;
                            this.dialogVisible = true;
                        } else {
                            this.dialogVisible = false;
                            this.$message.error("获取失败了 " + data.msg)
                        }
                    }, {methods: 'GET', token: this.token});

                } else if (command === 'myorder') {
                    this.$router.push({"name": 'FirUserOrders'})
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
            },
            init_route_name() {
                if (this.$route.meta) {
                    this.route_info.label = this.$route.meta.label;
                    this.route_info.name = this.$route.name;
                }
            },

        }, created() {
            this.appName = this.$route.params.id
        }, watch: {
            $route: function () {
                this.appName = this.$route.params.id;
                this.init_route_name();
            }
        }, mounted() {
            this.init_route_name();
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
