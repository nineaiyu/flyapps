<template>
    <div>
        <el-container class="navbar-wrapper">
            <el-main align="center">

                <div style="width: 300px; margin: 0 auto; padding: 20px 0;">
                    <el-link :underline="false">Copyright &copy;&nbsp;2017-2020&nbsp;第九系艾文&nbsp;&nbsp;版权所有.</el-link>

                </div>

                <div style="width: 300px; margin: 0 auto; padding: 20px 0;">
                    <a style="display: inline-block; text-decoration: none; height: 20px; line-height: 20px;" href="http://www.beian.gov.cn/portal/registerSystemInfo?recordcode=41142202000049" target="_blank" rel="noopener">
                    <img style="float: left;" src="https://blog.dvcloud.xin/beianlogo/beianlogo.png" />
                        <el-link  :underline="false" style="float: left; height: 20px; line-height: 20px; margin: 0px 0px 0px 5px; color: #939393;">豫公网安备 41142202000049号</el-link>
                    </a>

                </div>

                <div>
                    <div  :underline="false" style="width: 200px; margin: 0 auto; padding: 10px 0;">
                        <el-link :underline="false" href="https://beian.miit.gov.cn" target="_blank" rel="nofollow noopener">豫ICP备15004336号</el-link>
                    </div>
                </div>

            </el-main>
        </el-container>

    </div>
</template>

<script>

    export default {
        name: "FirFooter",
        data() {
            return {

            }
        }, methods: {

        }, created() {
        }, watch: {

        }
    }
</script>

<style scoped>


    .el-container {
        margin: 10px auto 100px;
        width: 1166px;
    }

    .navbar-wrapper {
        font-size: 0;
        border-radius: 10px;
    }



</style>
