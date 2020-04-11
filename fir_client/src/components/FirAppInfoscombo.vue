<template>
    <div class="apps-app-combo page-tabcontent ">
        <div class="middle-wrapper">
            <div class="request-wrapper" v-if="has_combo ">
                <p class="lead text-center ng-scope">已经与 <b>{{ has_combo.name }}</b> 合并</p>
                <table>
                    <tr>
                        <td><span class="type">{{ currentapp.type|getapptype}}</span></td>
                        <td></td>
                        <td><span class="type">{{ has_combo.type|getapptype}}</span></td>
                    </tr>
                    <tr>
                        <td>
                            <div class="icon"><img :src="cmaster_release.icon_url" class="ng-isolate-scope">
                            </div>
                        </td>
                        <td><i class="icon-combo"></i></td>
                        <td>
                            <div class="icon"><img :src="hmaster_release.icon_url" class="ng-isolate-scope">
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <td class="actions" colspan="3">
                            <!--                            <a class="btn btn-link " @click="each_confirm"><b>解除合并</b></a>-->
                            <el-button @click="each_confirm" round>解除合并</el-button>
                        </td>
                    </tr>
                </table>
            </div>
            <div v-else>
                <div class="icon-container text-center">
                    <img :src="cmaster_release.icon_url" height="128" width="128">
                </div>
                <div class="apps-list">
                    <div class="known-apps">
                        <p class="lead ng-binding">
                            <b>选择已有的应用进行合并</b>
                        </p>
                        <div class="apps">
                            <b v-if="comboapplists.length ===0 ">暂无可以合并的应用</b>
                            <div :key="comboapp.app_id" @click="each_add(comboapp.app_id)" class="app ng-scope"
                                 v-for="comboapp in comboapplists">
                                <div class="icon">
                                    <img :src="comboapp.master_release|geticon_url" class="ng-isolate-scope">
                                </div>
                                <p class="ng-binding">{{ comboapp.name }}</p></div>
                        </div>
                    </div>


                    <span class="hr-vertical"></span>
                    <div class="find-apps">
                        <p class="lead ">
                            <b>输入需要合并的应用的短链接或者名字</b>
                        </p>

                        <div class="form-group">
                            <el-input
                                    @click="searchapps"
                                    clearables
                                    placeholder="输入短链接或者名字"
                                    prefix-icon="el-icon-search"
                                    v-model="searchKey"
                            />
                        </div>


                    </div>
                </div>


            </div>

        </div>


    </div>

</template>

<script>
    import {getappinfos, getapps, updateapp} from "../restful";

    export default {
        name: "FirAppInfoscombo"
        , data() {
            return {
                searchKey: '',
                currentapp: {},
                has_combo: {},
                cmaster_release: {},
                hmaster_release: {},
                comboapplists: [],
                orgapplists: [],
                comboapp:{"master_release":""}
            }
        }, methods: {
            searchapps() {
                let keysearch = this.searchKey.replace(/^\s+|\s+$/g, "");
                let newapplists = [];
                for (let i = 0; i < this.orgapplists.length; i++) {
                    if (this.orgapplists[i].short.search(keysearch) === 0 || this.orgapplists[i].name.search(keysearch) === 0) {
                        newapplists.push(this.orgapplists[i]);
                    }
                }
                if (keysearch === "") {
                    this.comboapplists = this.orgapplists.slice();
                } else {
                    this.comboapplists = newapplists.slice();
                }
            },
            each_add(hcombo_id) {
                updateapp(data => {
                    if (data.code === 1000) {
                        this.$message.success('操作成功');

                        this.comboapplists = [];

                        getappinfos(data => {
                            let appinfos = {};
                            appinfos = data.data;
                            appinfos["icon_url"] = appinfos.master_release.icon_url;
                            this.$store.dispatch('doucurrentapp', appinfos);

                            if (data.code === 1000) {
                                this.$store.dispatch('doucurrentapp', data.data);
                            } else if (data.code === 1003) {
                                this.$router.push({name: 'FirApps'});
                            } else {

                                // eslint-disable-next-line no-console
                                console.log("失败了");

                            }
                        }, {
                            "app_id": this.currentapp.app_id
                        });

                        this.setData();


                    }
                }, {
                    "app_id": this.currentapp.app_id,
                    "data": {
                        "has_combo": {
                            "hcombo_id": hcombo_id,
                            "action": "COMBO",
                        }
                    }
                });
            },
            each_confirm() {
                updateapp(data => {
                    if (data.code === 1000) {
                        this.$message.success('操作成功');

                        let currentapp = this.$store.state.currentapp;
                        this.has_combo = this.$store.state.currentapp.has_combo;
                        this.has_combo = null;
                        currentapp.has_combo = null;
                        this.hmaster_release = null;
                        this.$store.dispatch('doucurrentapp', currentapp);
                        this.getappiconFun();

                    }
                }, {
                    "app_id": this.currentapp.app_id,
                    "data": {
                        "has_combo": {
                            "hcombo_id": this.has_combo.app_id,
                            "action": "UNCOMBO",
                        }
                    }
                });
            },
            setData() {

                this.currentapp = this.$store.state.currentapp;
                this.cmaster_release = this.$store.state.currentapp.master_release;

                if (this.$store.state.currentapp.has_combo) {
                    this.has_combo = this.$store.state.currentapp.has_combo;
                    this.hmaster_release = this.$store.state.currentapp.has_combo.master_release;
                } else {
                    this.has_combo = null;
                    this.hmaster_release = null;
                    this.getappiconFun();
                }
            },
            getappiconFun() {
                let type = "android";
                if (this.currentapp.type === 0) {
                    type = "ios"
                }
                getapps(data => {
                    if (data.code === 1000) {
                        this.comboapplists = data.data;
                        this.orgapplists = this.comboapplists.slice(); //深拷贝

                    } else {
                        this.$router.push({name: 'FirLogin'});
                    }
                }, {"type": type,"page":1,"size":999,"act":'combo'});
            }
        }, filters: {
            geticon_url(app){
                return  app.icon_url
            },
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
     mounted() {
        this.$store.dispatch('doappInfoIndex', [[44, 44], [44, 44]]);

        // this.getappiconFun();
        this.setData();
    },
        watch: {
            '$store.state.currentapp': function () {
                this.setData();
            },
            // eslint-disable-next-line no-unused-vars
            searchKey: function (val, oldVal) {
                this.searchapps()
            },
        }
    }
</script>

<style scoped>


    .text-center {
        text-align: center
    }

    .middle-wrapper {
        margin: 0 auto;
        width: 1100px
    }

    .apps-app-combo {
        position: relative;
        padding-top: 45px
    }

    .apps-app-combo .icon-container {
        margin-bottom: 60px
    }

    .apps-app-combo .icon-container img {
        border-radius: 17.544%
    }

    .apps-app-combo .apps-list {
        position: relative;
        overflow: hidden
    }

    .apps-app-combo .lead {
        margin-bottom: 30px;
        font-size: 16px
    }

    .apps-app-combo .lead b {
        max-width: 300px;
        display: inline-block;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        vertical-align: top
    }

    .known-apps {
        text-align: center;
        float: left;
        width: 45%;
        margin: 10px 30px;
    }

    .apps-app-combo .known-apps .icon img {
        width: 80px;
        height: 80px;
        border-radius: 22.7%
    }

    .apps-app-combo .known-apps .apps .app {
        display: inline-block;
        margin: 0 0 20px 28px;
        text-align: center;
        cursor: pointer;
        vertical-align: top;

    }

    .apps-app-combo .known-apps .apps .app > p {
        margin-top: 8px;
        font-size: 12px;
        text-align: center;
        display: inline-block;
        max-width: 100px;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
        word-wrap: normal
    }

    .apps-app-combo .find-apps {
        /*padding-left: 50px;*/
        text-align: center;
        margin: 10px 30px;
        float: right;
        width: 40%;
    }

    .apps-app-combo .find-apps .lead {
        text-align: left;
    }

    .apps-app-combo .find-apps .form-group {
        position: relative;
        margin-bottom: 36px;
        width: 260px;
    }

    .apps-app-combo .hr-vertical {
        position: absolute;
        z-index: 12;
        width: 1px;
        height: 100%;
        background-color: #d5f9f9
    }

    .apps-app-combo .request-wrapper .lead {
        margin-bottom: 80px;
        font-size: 18px
    }

    .apps-app-combo .request-wrapper table {
        margin: 0 auto;
        width: 400px
    }

    .apps-app-combo .request-wrapper table tr:first-child td span {
        display: inline-block;
        margin-bottom: 12px;
        font-size: 16px
    }

    .apps-app-combo .request-wrapper table td {
        padding: 0 15px;
        text-align: center
    }

    .apps-app-combo .request-wrapper table td img {
        width: 120px;
        height: 120px;
        border-radius: 17.54%
    }

    .apps-app-combo .request-wrapper table .actions {
        padding-top: 40px
    }

    .apps-app-combo .request-wrapper table .actions .btn {
        margin-bottom: 20px;
        min-width: 100px;
        border-radius: 30px
    }

    .apps-app-combo .request-wrapper table .actions .btn-link {
        color: #a9b1b3;
        text-decoration: none;
        border: 1px solid transparent;
        -webkit-transition: border-color .25s;
        transition: border-color .25s
    }

    .apps-app-combo .request-wrapper table .actions .btn-link:hover {
        border-color: #a9b1b3
    }

    .apps-app-combo .request-wrapper table i.icon-combo {
        font-size: 30px
    }

    .apps-app-combo .combo-loading-wrap {
        margin-bottom: 8px
    }

    .apps-app-combo .combo-loading-wrap > .icon {
        display: inline-block;
        -webkit-animation: rotating 1s linear infinite;
        animation: rotating 1s linear infinite
    }


</style>
