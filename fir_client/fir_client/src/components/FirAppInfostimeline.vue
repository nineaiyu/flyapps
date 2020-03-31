<template>
    <el-timeline>


        <el-timeline-item v-for="(app) in release_apps" :key="app.release_id"
                          :timestamp="app.created_time|formatdatatimeline"
                          :color="app.master_color"
                          placement="top">
            <el-card>
                <div class="directive-view-release">

                    <i class="el-icon-cloudy" v-if="! app.is_master"></i>
                    <i class="el-icon-cloudy" style="background-color: #409eff" v-else></i>

                    <b class="ng-binding">{{app.app_version}} (Build {{app.build_version}})</b>
                    <div class="release-metainfo ng-hide"
                         v-if="app.release_type === 0">
                        <small>
                            <i class="icon-calendar"></i>
                            <span class="el-icon-date">&nbsp;{{app.created_time|formattimeline}}</span>
                        </small>
                    </div>

                    <div class="release-metainfo" v-else>
                        <small>
                            <i class="icon-calendar"></i>
                            <span class="el-icon-date">&nbsp;{{app.created_time|formattimeline}}</span>
                        </small> &nbsp;&nbsp;·&nbsp;&nbsp;

                        <small>{{app.release_type|getiOStype}}</small>

                        <!--                                        <i-->
                        <!--                                                v-if="app.changelog" class="ng-hide">&nbsp;&nbsp;·&nbsp;&nbsp;</i>-->
                        <!--                                        <small v-if="app.changelog"-->
                        <!--                                               ng-bind="activity.distribution_name"-->
                        <!--                                               class="ng-binding ng-hide"> {{app.changelog}}</small>-->
                    </div>

                    <p>{{app.changelog}}</p>
                    <textarea v-if="app.editing.changelog"
                              v-model="app.changelog"
                              placeholder="更新日志" >
                    </textarea>
                    <div class="release-actions editing " v-if="app.editing.changelog">

                        <button class="btn-cancel" @click="endEdit(app,'changelog')"><span
                        >取消</span></button>
                        <button class="btn-save" @click="updateChangelog(app,'changelog')"><span
                        >保存</span></button>
                    </div>


                    <el-input v-if="app.editing.binary_url"
                              v-model="app.binary_url"
                              placeholder="下载地址,默认本服务器，填写第三方可以 自动跳转到第三方平台" >
                    </el-input>
                    <div class="release-actions editing " v-if="app.editing.binary_url">

                        <button class="btn-cancel" @click="endEdit(app,'binary_url')"><span
                        >取消</span></button>
                        <button class="btn-save" @click="updateChangelog(app,'binary_url')"><span
                        >保存</span></button>
                    </div>


                    <div class="release-actions" v-show="!app.editing.changelog && !app.editing.binary_url ">

                        <el-tooltip class="tooltip-top" content="编辑更新日志" placement="top">

                            <el-button @click="startEdit(app,'changelog')"
                                       tooltip="编辑更新日志"
                                       class="tooltip-top ">
                                <i class="el-icon-edit"></i>
                            </el-button>

                        </el-tooltip>


                        <el-tooltip class="tooltip-top" content="下载原文件" placement="top">

                            <el-button class="tooltip-top" tooltip="下载原文件"
                                       @click="downloadPackage(app)">
                                <i class="el-icon-download"></i>
                                <span >{{app.binary_size}}</span>
                            </el-button>

                        </el-tooltip>

                        <el-tooltip class="tooltip-top" :content="app.binary_url|downcontent" placement="top">

                            <el-button class="tooltip-top" tooltip="修改下载地址"
                                       @click="startEdit(app,'binary_url')"><i
                                    class="el-icon-link"></i> <span >下载地址</span>
                            </el-button>

                        </el-tooltip>

                        <el-button class="tooltip-top" @click="previewRelase(app)"><i
                                class="el-icon-view"></i> <span class="ng-binding">预览</span>
                        </el-button>

                        <el-button v-if="! app.is_master" class="tooltip-top" @click="make_master_release(app)">
                            <i class="el-icon-view"></i>
                            <span class="ng-binding ng-scope">标记上线</span>
                        </el-button>

                        <el-button v-if="(! app.is_master )|| (app.is_master && release_apps.length === 1)"
                                   class="tooltip-top" @click="del_release_app(app)">
                            <i class="el-icon-delete"></i>
                            <span class="ng-binding ng-scope">删除</span>
                        </el-button>

                    </div>
                </div>


            </el-card>
        </el-timeline-item>

    </el-timeline>
</template>

<script>
    import {deletereleaseapp, getapptimeline, getdownloadurl, updatereleaseapp} from "../restful"

    export default {
        name: "FirAppInfostimeline",
        data() {
            return {
                release_apps: [],
                currentapp: {},
                activity: {
                    editing: {'changelog':false,'binary_url':false}
                },
                updatas:{},

            }
        },
        methods: {
            downloadPackage(app){
                getdownloadurl(res=>{
                    if(res.code === 1000){
                        window.location.href=res.data.download_url;
                    }
                }, {
                    'data': {
                        'token': app.download_token,
                        'short': this.currentapp.short,
                        'release_id': app.release_id,
                        "isdownload":true
                    },
                    'app_id': this.currentapp.app_id
                })
            },
            previewRelase(app){
                this.$router.push({name: 'FirDownload', params: { short: this.currentapp.short },query:{release_id:app.release_id}})

            },
            getapptimelineFun() {
                const loading = this.$loading({
                    lock: true,
                    text: '加载中',
                    spinner: 'el-icon-loading',
                    // background: 'rgba(0, 0, 0, 0.7)'
                });
                getapptimeline(data => {
                    if (data.code === 1000) {
                        this.release_apps = data.data.release_apps;
                        this.currentapp = data.data.currentapp;
                    } else if (data.code === 1003) {
                        this.$router.push({name: 'FirApps'});
                    }
                    loading.close();
                }, {
                    "app_id": this.$route.params.id,
                    "action": "timeline",
                    "methods": false
                })
            },
            del_release_app(app) {
                //发送删除APP的操作
                this.$confirm('确认删除 ' + this.currentapp.name + '下 当前 release 版本吗?')
                    // eslint-disable-next-line no-unused-vars
                    .then(res => {
                        deletereleaseapp(data => {
                            if (data.code === 1000) {
                                this.$message({
                                    message: '删除成功',
                                    type: 'success'
                                });
                                this.getapptimelineFun();

                            } else {
                                this.$message({
                                    message: '删除失败，请联系管理员',
                                    type: 'error'
                                });
                            }
                        }, {
                            "app_id": this.currentapp.app_id,
                            "release_id": app.release_id,
                        });
                    });

            },
            updatereleaseappFun(params) {
                updatereleaseapp(data => {
                        if (data.code === 1000) {
                            this.$message({
                                message: '更新成功',
                                type: 'success'
                            });
                            this.release_apps = data.data.release_apps;
                            this.currentapp = data.data.currentapp;
                            // this.getapptimelineFun();
                            // this.currentapp["icon_url"] = this.currentapp.master_release.icon_url;
                            // this.$store.dispatch('doucurrentapp', this.currentapp);

                        } else {
                            this.$message({
                                message: '更新失败，请联系管理员',
                                type: 'error'
                            });
                        }
                    }, params
                );
            },
            make_master_release(app) {
                this.updatereleaseappFun({
                    "app_id": this.currentapp.app_id,
                    "release_id": app.release_id,
                    "data": {
                        "make_master": app.release_id
                    }
                });

            },
            endEdit(app,type) {
                if(type==='changelog'){
                    app.editing.changelog = false;

                }else if(type === 'binary_url'){
                    app.editing.binary_url = false;
                }
            },
            updateChangelog(app,type) {
                if(type==='changelog'){
                    this.activity.editing.changelog = false;
                    this.updatas = {"changelog": app.changelog}
                }else if(type === 'binary_url') {
                    this.activity.editing.binary_url = false;
                    this.updatas = {"binary_url": app.binary_url}
                }
                this.updatereleaseappFun({
                    "app_id": this.currentapp.app_id,
                    "release_id": app.release_id,
                    "data": this.updatas
                });
                this.updatas={}
            },
            startEdit(app,type) {
                if (type === 'changelog') {

                    app.editing.changelog = true;
                } else if (type === 'binary_url') {
                    app.editing.binary_url = true;
                }
            }

        }, created() {

        }, watch: {},
        computed: {}, mounted() {
            this.$store.dispatch('doappInfoIndex', [[5, 5], [5, 5]]);
            this.getapptimelineFun();
        }, filters: {
            downcontent(content){
                if(content){
                    return content
                }else{
                    return "修改下载地址"
                }
            },
            formatdatatimeline: function (timestr) {
                return timestr.split("T")[0];
            },
            formattimeline: function (timestr) {
                return timestr.split(".")[0].split("T")[1];
            },
            getiOStype: function (type) {
                let ftype = '';
                if (type === "Adhoc") {
                    ftype = '内测版'
                } else {
                    ftype = '企业版'
                }
                return ftype
            },
        }
    }
</script>

<style scoped>


    .directive-view-release {
        position: relative;
        padding-left: 80px;
        color: #9b9b9b;

    }

    .directive-view-release > i {
        display: -webkit-box;
        display: -ms-flexbox;
        display: flex;
        height: 50px;
        -webkit-box-align: center;
        -ms-flex-align: center;
        align-items: center;
        -webkit-box-pack: center;
        -ms-flex-pack: center;
        justify-content: center;
        position: absolute;
        left: 0;
        z-index: 2;
        width: 50px;
        border: 1px solid rgba(151, 151, 151, .2);
        border-radius: 50%;
        background-color: #f6f6f6;
        text-align: center;
        font-size: 22px
    }

    .directive-view-release > i:before {
        display: inline-block;
        margin-top: 2px;
        margin-left: 2px
    }

    .directive-view-release .release-metainfo {
        margin-top: 2px
    }

    .directive-view-release .release-metainfo small {
        display: inline-block;
        vertical-align: middle;
        margin: 8px 0;
        line-height: 14px
    }

    .directive-view-release .release-metainfo small i, .directive-view-release .release-metainfo small span {
        display: inline-block;
        vertical-align: middle
    }

    .directive-view-release .release-metainfo small i {
        margin-right: 2px;
        line-height: 14px
    }

    .directive-view-release > b {
        display: inline-block;
        vertical-align: middle;
        margin-right: 30px;
        color: #4a4a4a;
        font-weight: 400;
        font-size: 20px
    }

    .directive-view-release pre, .directive-view-release textarea {
        margin: 14px 0;
        padding: 0;
        border: 0;
        background-color: transparent;
        color: #4a4a4a;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif
    }

    .directive-view-release textarea {
        padding: 12px 16px;
        width: 500px;
        height: 120px;
        border-radius: 5px;
        resize: none;
        border: 1px solid #bdc6c7;
        color: #555;
        font-size: 16px
    }

    .directive-view-release .tooltip-top {
        position: relative;
        overflow: visible;
        color: #9b9b9b;
    }

    .directive-view-release .edit-pen {
        cursor: pointer
    }

    .directive-view-release .release-type {
        position: relative;
        display: inline-block;
        margin-left: 8px;
        padding: 2px 6px;
        border: 1px solid;
        border-radius: 5px
    }

    .directive-view-release .release-info {
        margin-top: 6px
    }

    .directive-view-release .release-info i, .directive-view-release .release-info span {
        display: inline-block;
        vertical-align: middle
    }

    .directive-view-release .release-info span {
        margin-right: 12px;
        margin-left: 4px
    }

    .directive-view-release .release-actions {
        margin-top: 10px;
        position: relative
    }

    .directive-view-release .release-actions .is-history {
        display: inline-block
    }

    .directive-view-release .release-actions toggle {
        margin-right: 8px
    }

    .directive-view-release .release-actions .comp-toggle.toggle-off {
        background-color: #9b9b9b
    }

    .directive-view-release .release-actions a, .directive-view-release .release-actions button {
        display: inline-block;
        vertical-align: middle;
        margin-right: 8px;
        background-color: transparent;
        border: 1px solid;
        overflow: hidden;
        border-radius: 17px;
        padding: 4px 10px
    }

    .directive-view-release .release-actions .release-actions-group .mqc-wait-btn, .directive-view-release .release-actions .tooltip-top {
        overflow: visible;
        position: relative
    }

    .directive-view-release .release-actions a i, .directive-view-release .release-actions button i {
        display: inline-block;
        vertical-align: middle
    }

    .directive-view-release .release-actions a.btn-save, .directive-view-release .release-actions button.btn-save {
        border-color: #3d6df8;
        background-color: #92c1f8;

        color: #fff
    }

    .directive-view-release .release-actions a.btn-cancel, .directive-view-release .release-actions button.btn-cancel {
        border: 0;

    }

    .directive-view-release .release-actions a.btn-cancel:hover, .directive-view-release .release-actions button.btn-cancel:hover {
        color: #686868
    }

    .directive-view-release .release-actions a {
        color: #9b9b9b
    }

    .directive-view-release .release-actions a:focus, .directive-view-release .release-actions a:hover {
        text-decoration: none
    }


    .directive-view-release .release-actions .has-text i {
        border-right: 1px solid
    }

    .directive-view-release .release-actions.editing {
        margin-top: 0;
        text-align: right;
        width: 500px
    }


    .time-line {
        position: relative
    }

    .time-line:before {
        position: absolute;
        left: 25px;
        z-index: 1;
        height: 100%;
        border-left: 1px solid rgba(151, 151, 151, .2);
        content: ' '
    }

    .time-line li {
        margin-top: 80px
    }

    .time-line li:first-child {
        padding-left: 80px;
        margin-top: 0
    }

    .time-line li:first-child .dot {
        position: absolute;
        left: 20px;
        z-index: 2;
        display: inline-block;
        width: 10px;
        height: 10px;
        border: 1px solid rgba(151, 151, 151, .2);
        border-radius: 50%;
        background-color: #9b9b9b;
        text-align: center
    }

    .time-line li:nth-child(2) {
        margin-top: 20px
    }

    .time-line li:nth-child(3) {
        margin-top: 40px
    }

    .time-line .filter {
        position: relative;
        top: -6px;
        display: inline-block;
        margin-right: 32px;
        font-weight: 700;
        cursor: pointer
    }

    .time-line .filter.active {
        color: #4a4a4a
    }

    .time-line .filter.version-rollback .button {
        display: inline-block;
        vertical-align: middle;
        background-color: transparent;
        border: 1px solid;
        padding: 4px 20px;
        border-radius: 17px
    }

    .time-line .more button {
        background: #f6f6f6;
        border: 1px solid;
        position: relative;
        z-index: 99;
        width: 160px;
        padding: 10px 0;
        border-radius: 40px
    }

</style>
