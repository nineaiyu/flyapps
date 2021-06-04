<template>
    <div>
        <div class="main">
            <div class="top">
                <el-carousel :interval="5000" arrow="always" height="600px">
                    <el-carousel-item v-for="item in swiperList" :key="item.title">
                        <div :style="{backgroundImage:`url(${item.img})`}" class="bpic">
                            <div class="topplayer-top">
                                <div class="word">{{ item.title }}</div>
                                <div class="content">{{ item.content }}</div>

                                <!--                                                <el-button @click="$router.push({name:'FirApps'})">开始分发 &gt;</el-button>-->
                            </div>
                        </div>
                    </el-carousel-item>
                </el-carousel>

            </div>
        </div>

        <div id="whyChooseUs">
            <div class="container">
                <div class="whyChooseUs-title text-center">
                    <p>为什么选择我们的服务</p>
                    <p>THE REASON TO CHOOSING US</p>
                </div>
                <el-row :gutter="20">
                    <el-col :span="6" v-for="(item,index) in serverList" :key="index">
                        <div class="server-block"
                             onmouseenter="this.style.color='#28f';this.style.borderColor='#28f'"
                             onmouseleave="this.style.color='#666';this.style.borderColor='#ccc'">
                            <img class="center-block" :src="item.logo" alt="logo">
                            <p class="text-center">{{item.title}}</p>
                            <div
                                    class="text-center"
                                    v-html="item.content"
                                    onmouseenter="this.style.color='#28f'"
                                    onmouseleave="this.style.color='#ccc'"
                            ></div>
                        </div>
                    </el-col>
                </el-row>
            </div>
        </div>

        <el-container id="contactUs">
            <el-main class="contactUs-container">
                <div class="content">您身边的应用托管分发</div>
                <div class="content">7x24小时提供出色的不间断服务</div>
                <el-button
                        onmouseleave="this.style.borderColor='#ffffff'; this.style.backgroundColor='#ffffff'; this.style.color='#3f3f3f';"
                        onmouseenter="this.style.backgroundColor='transparent'; this.style.borderColor='#ffffff'; this.style.color='#ffffff';"
                >联系我们
                </el-button>
                <div class="contactUs-contactWay">
                    <span/>
                    <span/>
                    <span/>
                </div>
            </el-main>
        </el-container>

    </div>
</template>

<script>
    export default {
        name: "FirIndex",
        data() {
            return {
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


    .main .top {
        margin-top: 10px;
        width: 100%;
        height: 600px;
    }

    .main .top .bpic {
        width: 100%;
        height: 600px;
    }

    .main .topplayer-top {
        width: 800px;
        height: 300px;
        position: absolute;
        top: 220px;
        margin-top: -150px;
        z-index: 2;
        right: 50%;
        margin-right: -400px;
    }

    .word {
        padding-top: 100px;
        color: #ffffff;
        font-size: 45px;
        font-weight: bolder;
        text-align: center;
        font-family: "微软雅黑";
    }

    .content {
        padding-top: 30px;
        color: #ffffff;
        font-size: 20px;
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

    #contactUs {
        margin-top: 60px;
        color: #fff;
        height: 400px;
        text-align: center;
        background: url("../../assets/imgs/contact_us_bg.jpg") 0 0 no-repeat;
        background-size: 100% 100%;
        transition: all ease 0.6s;
    }

    #contactUs .contactUs-container {
        padding-top: 50px;
    }

    #contactUs .contactUs-container button {
        width: 300px;
        height: 50px;
        margin-top: 40px;
    }

    #contactUs .contactUs-container .contactUs-contactWay span {
        display: inline-block;
        width: 48px;
        height: 48px;
        margin: 30px;
    }

    #contactUs .contactUs-container .contactUs-contactWay span:nth-of-type(1) {
        background: url("../../assets/imgs/weixin.png") 0 0 no-repeat;
        background-size: 100% 100%;
    }

    #contactUs .contactUs-container .contactUs-contactWay span:nth-of-type(2) {
        background: url("../../assets/imgs/weibo.png") 0 0 no-repeat;
        background-size: 100% 100%;
    }

    #contactUs .contactUs-container .contactUs-contactWay span:nth-of-type(3) {
        background: url("../../assets/imgs/twitter.png") 0 0 no-repeat;
        background-size: 100% 100%;
    }

    /* 为什么选择我们 */
    #whyChooseUs {
        padding: 100px;
        text-align: center;
    }

    #whyChooseUs .whyChooseUs-title {
        margin-bottom: 50px;
    }

    #whyChooseUs .whyChooseUs-title p:nth-of-type(1) {
        font-size: 25px;
        font-weight: 500;
    }

    #whyChooseUs .whyChooseUs-title p:nth-of-type(2) {
        font-size: 14px;
    }

    #whyChooseUs .server-block {
        padding: 50px 20px;
        border: 1px solid #ccc;
        border-bottom: 5px solid #ccc;
    }

    #whyChooseUs .server-block img {
        width: 48px;
        height: 48px;
    }

    #whyChooseUs .server-block > p {
        font-size: 20px;
        margin: 30px 0;
    }

    #whyChooseUs .server-block > div {
        color: #ccc;
    }

</style>
