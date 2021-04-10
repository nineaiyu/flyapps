<template>
    <el-container>
        <el-header class="header">
            <el-row :gutter="12">
                <el-col :span="12">
                    <el-image class="logo img" :src="require('@/assets/logo.png')" alt="logo"/>
                </el-col>
                <el-col :span="12" :offset="12">
                    <el-row :gutter="12" class="nav">
                        <el-col :span="8">
                            <el-link>工具</el-link>
                        </el-col>
                        <el-col :span="8">
                            <el-link @click="$router.push({name:'FirApps'})">登录</el-link>
                        </el-col>
                        <el-col :span="8">
                            <el-link @click="$router.push({name:'FirRegist'})">注册</el-link>
                        </el-col>
                    </el-row>
                </el-col>
            </el-row>

        </el-header>
        <div>
            <div class="main">
                <div class="top">
                    <img :src="require('@/assets/bg.jpeg')" alt="topimg">
                </div>
                <div class="topplayer-top">
                    <div class="word">FLY 应用 分发平台</div>
                    <el-button @click="$router.push({name:'FirApps'})">开始分发 &gt;</el-button>
                </div>
            </div>
        </div>

        <el-footer>
            <el-divider/>
            <FirFooter></FirFooter>
        </el-footer>
    </el-container>
</template>

<script>
    import FirFooter from "@/components/FirFooter";

    export default {
        name: "FirIndex",
        components: {FirFooter},
    }
</script>

<style scoped>
    * {
        margin: 0;
        padding: 0;
    }

    .header {
        width: 100%;
        height: 120px;
    }

    .header .img {
        width: 300px;
        height: 85px;
        padding-left: 100px;
        padding-top: 8px;
    }

    .header .logo {
        float: left;
    }

    .header .nav {
        float: right;
        padding-right: 80px;

    }

    .header .nav .el-col {
        margin-right: 20px;
        float: left;
        list-style: none;
        width: 80px;
        height: 60px;
        line-height: 100px;
        color: #7d7d7d;
        font-size: 15px;
        font-weight: bolder;
    }

    .header .nav .el-link:hover {
        color: #47477d;
        font-size: 16px;
        cursor: pointer;
        touch-action: manipulation;

    }

    .main .top {
        margin-top: 60px;
        width: 100%;
        height: 700px;
    }

    .main .top img {
        width: 100%;
        height: 700px;
    }

    .main .topplayer-top {
        width: 500px;
        height: 300px;
        position: absolute;
        top: 400px;
        margin-top: -150px;
        z-index: 2;
        right: 50%;
        margin-right: -250px;
    }

    .main .topplayer-top .word {
        padding-top: 100px;
        color: #ffffff;
        font-size: 45px;
        font-weight: bolder;
        text-align: center;
        font-family: "微软雅黑";
    }

    .main .topplayer-top button {
        width: 200px;
        height: 60px;
        margin-top: 50px;
        color: #ffffff;
        background: #f5704f;
        font-family: 微软雅黑;
        text-align: center;
        font-weight: bolder;
        font-size: 14px;
        border-radius: 8px; /*圆角*/
        margin-left: 150px;
    }

</style>