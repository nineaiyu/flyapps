<template>
    <div class="NewsInformation">
        <div>
            <div class="text-center">
                <h3>新闻动态</h3>
                <p style="color:#b2b2b2">Company News</p>
            </div>
            <div class="nav text-center">
                <a href="#" class="active">公司新闻</a>
                <a href="#">行业动态</a>
            </div>
            <ul class="news-container">
                <li v-for="(item,index) in newsList" :key="index">
                    <div class="content">
                        <p>{{item.title}}</p>
                        <p>{{item.introduce}}</p>
                    </div>
                    <div class="time">
                        <p>{{item.date}}</p>
                        <span>{{item.year}}</span>
                    </div>
                    <div class="circle">
                        <img :src="require('@/assets/imgs/circle.png')">
                        <i class="center-block"></i>
                    </div>
                </li>
            </ul>

        </div>
    </div>


</template>

<script>
    export default {
        name: "FirNews",
        data() {
            return {
                show: false,
                newsList: [
                    {
                        id: '001',
                        title: '现有版本',
                        introduce: '经过好长时间的编写，平台已经支持超级签名，权限管理，自定义域名，自定义存储',
                        date: '03-26',
                        year: '2021'
                    }, {
                        id: '002',
                        title: '发布第一个版本',
                        introduce: '只是简单的一个应用分发，然后再测试服进行分发测试',
                        date: '11-24',
                        year: '2019'
                    }, {
                        id: '003',
                        title: '撸代码',
                        introduce: '资源，签名方式，想法都已经准备好，正式写代码',
                        date: '10-10',
                        year: '2019'
                    }, {
                        id: '004',
                        title: '开始行动',
                        introduce: '网上找了些资源，然后进行设计，也找了些linux平台签名方式',
                        date: '08-20',
                        year: '2019'
                    }, {
                        id: '005',
                        title: '行动前准备',
                        introduce: '通过互联网查询，发现了fir平台，但是fir平台只支持应用分发，还不可以iOS签名',
                        date: '06-03',
                        year: '2019'
                    }, {
                        id: '006',
                        title: '萌发新想法',
                        introduce: 'iOS测试打包，应用分发复杂繁琐，怎么可以一站式分发安卓和苹果应用？',
                        date: '05-24',
                        year: '2019'
                    }
                ]
            }
        },
        mounted() {
            this.show = true;
        }
    }
</script>

<style scoped>
    .NewsInformation {
        text-align: center;
    }

    .nav {
        margin: 20px 0;
    }

    .nav > a {
        display: inline-block;
        text-decoration: none;
        width: 120px;
        height: 45px;
        line-height: 45px;
        color: #333;
        border: 1px solid #333;
    }

    .nav > a.active {
        color: #1e73be;
        border-color: #1e73be;
    }

    .nav > a:hover {
        color: #1e73be;
        border-color: #1e73be;
    }

    .news-container {
        overflow: hidden;
        margin-bottom: 0;
        width: 1140px;
        margin-right: auto;
        margin-left: auto;
        list-style: none;
    }

    .news-container > li {
        width: 55.45%;
        height: 120px;
        float: left;
        color: #333;
        text-align: right;
        border-left: 1px solid transparent;
        border-right: 1px solid transparent;
    }

    .news-container > li:hover {
        color: #1e73be;
        /*border: 1px solid #1e73be;*/
        cursor: pointer;
    }

    .news-container > li:nth-of-type(2n) {
        float: right;
        text-align: left;
    }

    .news-container > li > .content {
        width: 60%;
        float: left;
        padding: 20px 0;
    }

    .news-container > li > .time {
        width: 20%;
        float: left;
        padding: 10px 0;
    }

    .news-container > li > .time > p {
        font-size: 30px;
        margin: 5px 0;
    }

    .news-container > li > .circle {
        width: 20%;
        height: 100%;
        float: left;
        position: relative;
    }

    .news-container > li > .circle > img {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        margin: auto;
        width: 20px;
        height: 20px;
    }

    .news-container > li > .circle > i {
        display: block;
        width: 1px;
        height: 100%;
        background: #707070;
    }

    .news-container > li:nth-of-type(2n) > .content {
        float: right;
    }

    .news-container > li:nth-of-type(2n) > .time {
        float: right;
    }

    .news-container > li:nth-of-type(2n) > .circle {
        float: right;
    }

    .news-container > li:nth-of-type(1) > .circle > i {
        height: 50%;
        position: absolute;
        top: 50%;
        left: 50%;
    }

    .center-block {
        display: block;
        margin-right: auto;
        margin-left: auto
    }
</style>
