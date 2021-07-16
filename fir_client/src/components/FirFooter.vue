<template>
    <div class="ifooter">

        <div style="width: 300px; margin: 0 auto; padding: 5px 0;">
            <el-link :underline="false"> {{ footer.copyright }}</el-link>
        </div>
        <div style="width: 300px; margin: 0 auto; padding: 5px 0;">
            <a style="display: inline-block; text-decoration: none; height: 20px; line-height: 20px;"
               :href="footer.gongAnBeiAn.url"
               target="_blank" rel="noopener">
                <img style="float: left;" src="@/assets/beianlogo.png" alt=""/>
                <el-link :underline="false"
                         style="float: left; height: 20px; line-height: 20px; margin: 0 0 0 5px; color: #939393;">
                    {{ footer.gongAnBeiAn.text }}
                </el-link>
            </a>

        </div>

        <div>
            <div :underline="false" style="width: 200px; margin: 0 auto; padding: 5px 0;">
                <el-link :underline="false" :href="footer.ipcBeiAn.url" target="_blank"
                         rel="nofollow noopener">{{ footer.ipcBeiAn.text }}
                </el-link>
            </div>
        </div>
    </div>
</template>

<script>

    export default {
        name: "FirFooter",
        data() {
            return {
                footer: {
                    copyright: 'Copyright © 2017-2021 东城飞阳 版权所有.',
                    ipcBeiAn: {
                        url: 'https://beian.miit.gov.cn',
                        text: '粤ICP备2021097895号',
                    },
                    gongAnBeiAn: {
                        url: 'http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=41142202000049',
                        text: '粤公网安备 41142202000049号',
                    },
                }
            }
        }
    }
</script>

<style scoped>
    .ifooter {
        margin: 20px auto 100px;
        width: 1166px;
        text-align: center;
        font-size: 0;
        border-radius: 10px;
    }

</style>
