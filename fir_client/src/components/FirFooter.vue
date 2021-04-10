<template>
    <div>
        <el-container class="navbar-wrapper">
            <el-main align="center">

                <div style="width: 300px; margin: 0 auto; padding: 5px 0;">
                    <el-link :underline="false"> {{ footer.copyright }}</el-link>

                </div>

                <div style="width: 300px; margin: 0 auto; padding: 5px 0;">
                    <a style="display: inline-block; text-decoration: none; height: 20px; line-height: 20px;"
                       :href="footer.gongAnBeiAn.url"
                       target="_blank" rel="noopener">
                        <img style="float: left;" src="@/assets/beianlogo.png"/>
                        <el-link :underline="false"
                                 style="float: left; height: 20px; line-height: 20px; margin: 0px 0px 0px 5px; color: #939393;">
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

            </el-main>
        </el-container>

    </div>
</template>

<script>

    export default {
        name: "FirFooter",
        data() {
            return {
                footer: {
                    copyright: '',
                    ipcBeiAn: {
                        url: '',
                        text: '',
                    },
                    gongAnBeiAn: {
                        url: '',
                        text: '',
                    },
                }
            }
        }, methods: {}, created() {
        }, mounted() {
            this.footer = window.g.footer;
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
