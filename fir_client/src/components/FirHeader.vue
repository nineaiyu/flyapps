<template>
    <div>
        <el-container class="navbar-wrapper">
            <el-row :gutter="20">
                <el-col :span="14" style="padding-top: 16px;margin-left: 60px">

                    <el-breadcrumb separator=">" style="height: 80px;font-size: 20px">
                        <el-breadcrumb-item :to="{ name:'FirIndex' }"><i class="el-icon-s-home elbi"></i>
                        </el-breadcrumb-item>
                        <el-breadcrumb-item :to="{ name:'FirApps'}"><i class="el-icon-apple elbi"></i>
                        </el-breadcrumb-item>
                        <el-breadcrumb-item v-if="$store.state.currentapp.name">{{ $store.state.currentapp.name}}
                        </el-breadcrumb-item>
                    </el-breadcrumb>

                </el-col>
                <el-col :span="4" :push="5">

                    <el-dropdown style="padding-top: 12px;" @command="handleCommand">
                        <el-button type="success" plain round>
                            {{$store.state.userinfo.first_name }}<i class="el-icon-arrow-down el-icon--right"></i>
                        </el-button>
                        <el-dropdown-menu slot="dropdown">
                            <el-dropdown-item command="userinfo">个人资料</el-dropdown-item>
                            <el-dropdown-item command="chpasswd">修改密码</el-dropdown-item>
                            <el-dropdown-item command="exit">退出</el-dropdown-item>

                        </el-dropdown-menu>
                    </el-dropdown>

                </el-col>

            </el-row>


        </el-container>

    </div>
</template>

<script>

    export default {
        name: "FirHeader",
        data() {
            return {
                current_user: {},
                appName: '',
            }
        }, methods: {
            handleSelect() {

            },
            checkUrl() {

            },
            handleCommand(command) {
                if (command === 'userinfo') {
                    this.$router.push({name: 'FirUserProfileInfo'})
                } else if (command === 'chpasswd') {
                    this.$router.push({name: 'FirUserProfileChangePwd'})
                }else if(command === 'exit'){
                    this.$cookies.remove("token");
                    this.$cookies.remove("auth_token");
                    this.$cookies.remove("username");
                    this.$cookies.remove("first_name");
                    this.$store.dispatch('doucurrentapp', {});
                    this.$store.dispatch('getUser', {});
                    this.$router.push({name: 'FirLogin'});
                }
            }

        }, created() {
            // this.$bus.$on('appName',val =>{
            //     this.appName = val;
            //     alert('header')
            // })
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
