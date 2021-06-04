<template>
    <el-container>
        <div style="background-color:rgba(162, 193, 230, 0.18);">
            <el-header class="header">
                <el-row :gutter="12">
                    <el-col :span="12">
                        <el-image class="logo img" :src="require('@/assets/logo.png')" alt="logo"/>
                    </el-col>
                    <el-col :span="12" :offset="12">
                        <el-row :gutter="12" class="nav">
                            <el-col :span="8">
                                <el-link @click="$router.push({name:'FirIndex'})">首页</el-link>
                            </el-col>
                            <el-col :span="8">
                                <el-link @click="$router.push({name:'FirService'})">服务</el-link>
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
        </div>

        <div>
            <router-view/>
        </div>
        <el-tooltip placement="top" content="回到顶部">
            <back-to-top :custom-style="myBackToTopStyle" :visibility-height="300" :back-position="50"
                         transition-name="fade"/>
        </el-tooltip>
        <el-footer>
            <el-divider/>
            <FirFooter/>
        </el-footer>
    </el-container>
</template>

<script>
    import FirFooter from "@/components/FirFooter";
    import BackToTop from "@/components/base/BackToTop";

    export default {
        name: "FirIndex",
        components: {FirFooter, BackToTop},
        data() {
            return {
                myBackToTopStyle: {
                    right: '80px',
                    bottom: '100px',
                    width: '40px',
                    height: '40px',
                    'border-radius': '4px',
                    'line-height': '45px',
                    background: '#e7eaf1'
                },
                swiperList: [
                    {
                        img: require("@/assets/imgs/banner2.jpg"),
                        path: "",
                        title: '超级签名',
                        content: '自定义超级签签名，不再为频繁填写udid打包而烦恼',
                    },
                    {
                        img: require("@/assets/imgs/banner1.png"),
                        path: "",
                        title: '内测托管',
                        content: '一键上传应用，扫描二维码下载',
                    },
                    {
                        img: require("@/assets/imgs/banner_2.jpg"),
                        path: "",
                        title: '应用合并',
                        content: '扫描同一个二维码，根据设备类型自动下载对应的 iOS 或 Android 应用',
                    },
                    {
                        img: require("@/assets/imgs/banner_1.jpg"),
                        path: "",
                        title: '权限控制',
                        content: '灵活的访问权限控制，密码授权，下载页展示，管理应用',
                    },

                ],
                serverList: [
                    {
                        logo: require("@/assets/imgs/tel.png"),
                        title: "核心优势1",
                        content: "<p>由专业客服提供人工服务</p>负责疑难问题和故障受理"
                    },
                    {
                        logo: require("@/assets/imgs/computer.png"),
                        title: "核心优势2",
                        content: "<p>可定制私有化部署</p>帮助客户进行私有操作"
                    },
                    {
                        logo: require("@/assets/imgs/qq.png"),
                        title: "核心优势3",
                        content: "<p>利用QQ微信等提供在线解答</p>帮助用户快速准确解决问题和故障"
                    },
                    {
                        logo: require("@/assets/imgs/skill.png"),
                        title: "核心优势4",
                        content: "<p>由技术支持工程师，负责问题解答</p>需求受理及故障受理"
                    }
                ]
            }
        }
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

</style>
