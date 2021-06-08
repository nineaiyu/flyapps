<template>
    <el-main>
        <h1> 请点击打开 <a href="https://appstoreconnect.apple.com/" target="_blank">appstoreconnect</a> 登录苹果开发者账户进行操作</h1>
        <div v-for="helpic in imagelist" :key="helpic">
            <img v-lazy="helpic" alt="" style="width: 1100px;margin-top: 20px"/>
        </div>
    </el-main>
</template>

<script>
    import {getUserInfoFun} from "@/utils";

    export default {
        name: "FirSuperSignHelp",
        data() {
            return {
                imagelist: [
                    require('@/assets/sign/help/sign_help_0.png'),
                    require('@/assets/sign/help/sign_help_1.png'),
                    require('@/assets/sign/help/sign_help_2.png'),
                    require('@/assets/sign/help/sign_help_3.png'),
                    require('@/assets/sign/help/sign_help_4.png'),
                    require('@/assets/sign/help/sign_help_5.png'),
                ]
            }
        }, mounted() {
            getUserInfoFun(this);
        }
    }
</script>

<style scoped>
    .el-main {
        margin: 20px auto 100px;
        width: 1166px;
        position: relative;
        padding-bottom: 1px;
        text-align: center;
        color: #9b9b9b;
        -webkit-font-smoothing: antialiased;
        border-radius: 1%;
    }
</style>
