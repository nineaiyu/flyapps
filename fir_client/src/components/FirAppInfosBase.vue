<template>
    <el-main>
        <div class="page-app app-info">
            <div class="banner">
                <div class="middle-wrapper" ref="mwp">
                    <div @click="defaulttimeline">
                        <img :src="icon_url" class="appicon" style="width:100px; height:100px">
                    </div>
                    <div class="badges">
                        <span class="bundleid">SHORT<b class="short">&nbsp;&nbsp;{{ appinfos.short }}</b></span>
                        <span>{{ master_release.release_type |getapptype }}</span>
                        <span><i class="el-icon-cloudy"></i><b class="ng-binding">{{ appinfos.count_hits }}</b></span>
                        <span class="bundleid ng-binding">BundleID<b class="ng-binding">&nbsp;&nbsp;{{ appinfos.bundle_id }}</b></span>
                        <span class="version ng-scope">{{ master_release.minimum_os_version }}&nbsp; 或者高版本</span>
                    </div>

                    <div class="actions">

                        <!--                                        <el-button class="upload" icon="el-icon-cloudy">-->
                        <!--                                            上传新版本-->
                        <!--                                        </el-button>-->

                        <el-button @click="appDownload" class="download" icon="el-icon-view">
                            预览
                        </el-button>

                    </div>

                    <div class="tabs-container">
                        <el-row :gutter="1">
                            <el-col :span="3">
                                <a class="" ref="baseinfo" @click="baseinfo"><i class="el-icon-document"></i>基本信息</a>
                            </el-col>

                            <el-col :span="3">

                                <a class="" ref="combo" @click="combo"><i class="el-icon-copy-document"
                                                                          style="transform:rotateX(180deg);"></i>应用合并</a>
                            </el-col>
                        </el-row>
                    </div>
                </div>
            </div>

            <div>
                <div class="block" style="margin-top: -46px;color: #d5f9f9">
                    <el-slider
                            v-model="$store.state.appInfoIndex[0]"
                            range
                            :show-tooltip="false"
                            :change="slidevents()"
                            :max="100">
                    </el-slider>
                </div>


                <el-container style="padding-top: 20px;max-width: 96%">
                    <router-view></router-view>
                </el-container>

            </div>


        </div>
    </el-main>

</template>

<script>
    import {getappinfos} from "../restful";

    export default {
        name: "FirAppInfosBase",
        data() {
            return {
                icon_url:"",
                appinfos: {},
                master_release: {},
                allapp: [],
                activity: {
                    editing: false
                },
                slidvalue: [[5, 5], [5, 5]]

            }
        },
        methods: {
            appDownload() {
                this.$router.push({name: 'FirDownload', params: { short: this.appinfos.short }})
            },
            combo() {
                this.$router.push({name: 'FirAppInfoscombo'});
                this.$store.dispatch('doappInfoIndex', [[31, 31], [31, 31]]);

                this.$refs.combo.classList.add('active');
                this.$refs.baseinfo.classList.remove('active');


            },
            baseinfo() {
                this.$refs.baseinfo.classList.add('active');
                this.$refs.combo.classList.remove('active');

                this.$router.push({name: 'FirAppInfosbaseinfo'});
                this.$store.dispatch('doappInfoIndex', [[18, 18], [18, 18]]);

            },
            slidevents() {
                // let index = this.$store.state.appInfoIndex[1];
                // this.$store.dispatch('doappInfoIndex',[index,index]);
                // eslint-disable-next-line no-console
                // console.log(index);
            },
            defaulttimeline() {
                this.$refs.baseinfo.classList.remove('active');
                this.$refs.combo.classList.remove('active');
                this.$router.push({name: 'FirAppInfostimeline'});
                this.$store.dispatch('doappInfoIndex', [[5, 5], [5, 5]]);
            },

        }, created() {

        }, filters: {
            getapptype: function (type) {
                let ftype = '';
                if (type === 0) {
                    ftype = 'Android'
                } else {
                    ftype = 'iOS'
                }
                return ftype
            },
        },
        computed: {
            getBH: function () {
                let sch = this.$refs.appinfomain.scrollHeight;

                if (sch === 0 || sch < window.innerHeight) {
                    sch = window.innerHeight;


                } else {
                    sch += 130;
                }
                return sch;
            }

        }, mounted() {

            getappinfos(data => {

                if (data.code === 1000) {
                    this.appinfos = data.data;
                    this.master_release = data.data.master_release;
                    this.$store.dispatch("getUser",data.userinfo);
                    this.appinfos["icon_url"] = this.master_release.icon_url;
                    this.$store.dispatch('doucurrentapp', this.appinfos);
                } else if (data.code === 1003) {
                    this.$router.push({name: 'FirApps'});
                } else {
                    // eslint-disable-next-line no-console
                    console.log("失败了");
                }

            }, {
                "app_id": this.$route.params.id
            });
            if(this.$store.state.currentapp.master_release){
                this.icon_url = this.$store.state.currentapp.master_release.icon_url
            }
            // this.$store.dispatch('dosetAh',this.getBH);
        },watch:{
            '$store.state.currentapp.master_release.icon_url':function () {
                    this.icon_url = this.$store.state.currentapp.master_release.icon_url
            }
        }

    }
</script>

<style scoped>
    .el-main {
        margin: 10px auto 100px;
        width: 1166px;
        position: relative;
        padding-bottom: 1px;
        background-color: #bfe7f9;
        color: #9b9b9b;
        -webkit-font-smoothing: antialiased;
        border-radius: 1%;
    }

    .appicon {
        overflow: hidden;
        margin-left: 10px;
        border-radius: 17.544%;
    }

    .page-app {
        padding-bottom: 0
    }

    .page-app .banner {
        padding-top: 60px;
        padding-bottom: 40px;
        border-bottom: 1px solid rgba(208, 208, 208, .5);
        background-color: #d5f9f9;
        border-radius: 10px;
    }

    .page-app .banner .actions {
        position: absolute;
        right: 0;
        top: 0;
    }

    .page-app .banner .actions .download, .page-app .banner .actions .upload {
        display: block;
        min-width: 150px;
        padding: 10px 20px;
        border-radius: 5px;
        font-size: 14px;
        margin: 0 12px 12px 12px
    }


    .page-app .banner .actions .upload {
        background-color: #3ab2a7;
        border: 1px solid transparent;
        color: #fff;
        cursor: pointer
    }

    .page-app .banner .actions .download {
        text-align: center;
        text-decoration: none;
        color: #3ab2a7;
        border: 1px solid;
        background-color: transparent
    }


    .page-app .banner .middle-wrapper {
        position: relative
    }


    .page-app .badges {
        margin-left: 160px;
        font-size: 12px;
        line-height: initial;
        position: relative;
        margin-top: -100px;
    }

    .page-app .badges > span {
        position: relative;
        display: inline-block;
        margin-right: 8px;
        padding: 4px 8px;
        border: 1px solid;
        border-radius: 5px
    }


    .page-app .badges .short {
        color: #6f6ef8
    }

    .page-app .badges b {
        display: inline-block;
        padding-left: 12px;
        height: 100%;
        font-weight: 400
    }

    .page-app .badges b:before {
        position: absolute;
        top: 0;
        width: 0;
        height: 100%;
        border-left: 1px solid;
        content: ' ';
        margin-left: -6px
    }

    .page-app .tabs-container {
        margin-top: 40px;
        margin-left: 160px
    }

    .page-app .tabs-container .el-row {
        margin: 10px auto;
    }

    .page-app .tabs-container .el-row .el-col {
        margin-right: 30px;
        border-left: 1px solid;
    }

    .page-app .tabs-container .el-row .el-col a {
        display: block;
        padding-left: 15px;
        color: #599b1a;
        text-decoration: none;
        -webkit-transition: all .5s;
        transition: all .5s
    }

    .page-app .tabs-container .el-row .el-col a > i {
        display: block;
        margin-bottom: 14px;
        height: 22px;
        font-size: 22px
    }

    .page-app .tabs-container .el-row .el-col a.active {
        color: #4a4a4a
    }

    .page-app .tabs-container .el-row .el-col:nth-child(5) {
        display: none
    }

    .page-app .has-devices .tabs-container .el-row .el-col:nth-child(5) {
        display: inline-block
    }


</style>
