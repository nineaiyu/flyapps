<template>
    <div>
        <el-container >

            <el-header style="height: 100px">

                <el-dialog
                        :title="getDelappTitle"
                        :visible.sync="willDeleteApp"
                        width="50%"
                >
                    <span>删除后不可恢复，请谨慎操作</span>
                    <span slot="footer" class="dialog-footer">
            <el-button @click="willDeleteApp = false">取 消</el-button>
            <el-button type="danger" @click="delApp">确 定</el-button>
          </span>
                </el-dialog>

                <el-row>
                    <el-col :span="4">
                        <el-radio-group v-model="searchfromtype">
                            <el-radio-button label="android" icon="el-icon-mobile-phone"><i class="iconfont icon-android2"/>
                            </el-radio-button>
                            <el-radio-button label="ios" ><i class="iconfont icon-ios"/>
                            </el-radio-button>
                        </el-radio-group>

                    </el-col>
                    <el-col :span="5">
                        <el-input
                                placeholder="请输入名称搜索"
                                v-model="keysearch"
                                @click="searchapps"
                                clearable prefix-icon="el-icon-search">
                        </el-input>

                    </el-col>

                    <el-col :span="7" class="surplus-card">
                        <el-row>
                            <el-col :span="8">
                                <div>
                                    <span class="name">iOS应用</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                                <div>
                                    <span class="value">{{ hdata.ios_count }}</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                            </el-col>

                            <el-col :span="8">
                                <div>
                                    <span class="name">Android应用</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                                <div>
                                    <span class="value">{{ hdata.android_count }}</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                            </el-col>

                            <el-col :span="8">
                                <div>
                                    <span class="name">总应用</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                                <div>
                                    <span class="value">{{ hdata.ios_count + hdata.android_count}}</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                            </el-col>
                        </el-row>
                    </el-col>

                    <el-col :span="8" class="surplus-card">
                        <el-row>
                            <el-col :span="8">
                                <div>
                                    <span class="name">今日苹果下载次数</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                                <div>
                                    <span class="value">{{ hdata.ios_today_hits_count }}</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                            </el-col>

                            <el-col :span="8">
                                <div>
                                    <span class="name">今日安卓下载次数</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                                <div>
                                    <span class="value">{{ hdata.android_today_hits_count }}</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                            </el-col>

                            <el-col :span="8">
                                <div>
                                    <span class="name">总共下载次数</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                                <div>
                                    <span class="value">{{ hdata.all_hits_count}}</span>
                                    <el-divider direction="vertical"></el-divider>
                                </div>
                            </el-col>
                        </el-row>
                    </el-col>

                </el-row>


            </el-header>


            <div
                 ref="appmain" style="margin: 40px 20px">

                <el-row style="max-height: 460px; margin: 0 auto;" :gutter="10" class="page-apps">

                    <el-col style="width: 33%;height: 460px ">
                        <div class=" app-animator appdownload">
                            <div class=" card app card-ios" style="padding: 0">
                                <el-upload
                                        :on-success="handleAvataruploadsuccess"
                                        drag
                                        accept=".ipa , .apk"
                                        :headers="uploadconf.AuthHeaders"
                                        :action="uploadconf.UploadUrl"
                                        multiple>
                                    <i class="el-icon-upload" style="color: #fff"></i>
                                    <div class="el-upload__text" style="color: #fff;margin-top: 20px">拖拽到这里上传</div>
                                </el-upload>

                            </div>
                        </div>

                    </el-col>
                    <el-col  style="width: 33%;height: 460px"
                 v-for="(r,index) in applists" :key="r.id" @click="appInfos(index)">

            <div class=" app-animator">
                <div class="card app card-ios">

                    <i class=" type-icon iconfont icon-ios" v-if="r.type === 1" src=""></i>
                    <i class="type-icon iconfont icon-android2"  v-if="r.type === 0"></i>

                    <div class="type-mark" v-if="r.type === 1"></div>
                    <div class="type-mark" style="border-top: 48px solid #A4C639" v-if="r.type === 0"></div>
                    <a class="appicon" @click="appInfos(r)">
                        <img class="icon ng-isolate-scope" width="100" height="100"
                             :src="r.master_release.icon_url|make_icon_url"></a>

                    <div class="combo-info ng-scope" v-if="r.has_combo !== null ">
                        <i class="el-icon-copy-document" style="transform:rotateX(180deg);"></i>
                        <a @click="appInfos(r.has_combo)">
                            <img class="icon ng-isolate-scope" width="45" height="45"
                                 :src="r.has_combo.master_release.icon_url|make_icon_url">
                        </a>
                    </div>


                    <br>
                    <p class="appname"><i class="el-icon-user-solid"></i><span class="ng-binding">{{ r.name }}</span>
                    </p>
                    <table>
                        <tbody>


                        <tr>
                            <td class="ng-binding">应用大小：</td>
                            <td><span
                                    class="ng-binding">{{ r.master_release.binary_size  }}</span>
                            </td>
                        </tr>
                        <tr>
                            <td class="ng-binding">应用平台：</td>
                            <td><span class="ng-binding">{{ r.type |getapptype }}</span></td>
                        </tr>
                        <tr>
                            <td class="ng-binding">应用标识：</td>
                            <td><span class="ng-binding">{{ r.bundle_id | autoformat }}</span></td>
                        </tr>
                        <tr>
                            <td class="ng-binding">最新版本：</td>
                            <td><span class="ng-binding">{{ r.master_release.app_version }}（Build {{ r.master_release.build_version }}）</span>
                            </td>
                        </tr>
                        <tr v-if="r.type === 1">
                            <td class="ng-binding">打包类型：</td>
                            <td><span class="ng-binding">
                                        {{ r.master_release.release_type|getiOStype }}
                                    </span></td>
                        </tr>

                        </tbody>
                    </table>
                    <div class="action">
                        <el-button @click="appInfos(r)">
                            <i class="icon-pen el-icon-edit"></i> 管理
                        </el-button>

                        <el-button @click="appDownload(r)" target="_blank" class="ng-binding">
                            <i class="icon-eye el-icon-view"></i> 预览
                        </el-button>


                        <el-button @click="DeleteApp(r)" class="btn btn-remove" icon="el-icon-delete"
                                   circle></el-button>

                    </div>
                </div>
            </div>

        </el-col>

                </el-row>

            </div>

        </el-container>

    </div>
</template>

<script>
    import {getapps, deleteapp} from "../restful";
    import {getScrollHeight,getScrollTop,getWindowHeight} from "../utils";

    export default {
        name: "FirApps",
        data() {
            return {
                uploadconf: {"UploadUrl": ""},
                keysearch: '',
                searchfromtype: '',
                applists: [],
                orgapplists: [],
                hdata: {},
                willDeleteApp: false,
                delapp: {},
                has_next:true,
                query:{'page':1,size:20},
                searchflag:false,
                uploadflag:false,
                autoloadflag:true
            }
        }, methods: {
            searchFun(){
                let keysearch = this.keysearch.replace(/^\s+|\s+$/g, "");
                if(keysearch === ''){
                    this.searchflag=false;
                    this.applists=[];
                    this.orgapplists=[];
                    this.query.page=1;
                    if(this.searchfromtype){
                        this.getappsFun({"type": this.searchfromtype});
                    }else {
                        this.getappsFun({});
                    }
                }else {
                    this.searchflag=true
                }
                if(this.searchflag){
                    this.applists=[];
                    this.orgapplists=[];
                    if(this.searchfromtype){
                        this.getappsFun({"type": this.searchfromtype,'page':1,size:999});
                    }else {
                        this.getappsFun({'page':1,size:999});
                    }
                }
            },
            auto_load(){
                // eslint-disable-next-line no-console
                // console.log(getScrollTop() , getWindowHeight(),getScrollTop() + getWindowHeight(), getScrollHeight());
                if(getScrollTop() + getWindowHeight() >= getScrollHeight()){

                        if(this.has_next){      //先判断下一页是否有数据
                            if(this.autoloadflag) {
                                this.autoloadflag = false;
                                if (this.applists.length === 0) {
                                    this.query.page = 1;
                                } else {
                                    this.query.page += 1;
                                }
                                if (this.searchfromtype !== '') {
                                    this.query.type = this.searchfromtype;
                                }
                                this.getappsFun(this.query);
                            }

                        }else{
                            if(! this.has_next){
                                this.$message.success("已经到底啦")
                            }
                        }
                }
            },
            searchapps() {
                let keysearch = this.keysearch.replace(/^\s+|\s+$/g, "");
                let newapplists = [];
                for (let i = 0; i < this.orgapplists.length; i++) {
                    if (this.orgapplists[i].name.search(keysearch) === 0) {
                        newapplists.push(this.orgapplists[i]);
                    }
                }
                if (keysearch === "") {
                    this.applists = this.orgapplists.slice();
                } else {
                    this.applists = newapplists.slice();
                }

            },
            getappsFun(parms) {

                getapps(data => {
                    if (data.code === 1000) {
                        this.autoloadflag = true;

                        if(this.uploadflag){
                            this.applists = data.data ;
                            this.uploadflag = false;
                        }else {
                            this.applists = this.applists.concat(data.data) ;
                        }
                        this.has_next = data.has_next;
                        this.orgapplists = this.applists.slice(); //深拷贝
                        this.hdata = data.hdata;
                        this.$store.dispatch("getUser",data.userinfo);

                        this.searchapps();
                        let upload_domain=data.hdata.upload_domain;
                        if(!upload_domain){
                            upload_domain=location.origin;
                        }
                        this.uploadconf = {
                            "UploadUrl": upload_domain+"/api/v1/fir/server/upload",
                            "AuthHeaders": {"Authorization": this.$cookies.get("auth_token")}
                        };
                        // this.$store.dispatch('doucurrentapp', {'firapps':1});

                    } else {
                        this.$router.push({name: 'FirLogin'});
                    }
                }, parms);

            },

            // eslint-disable-next-line no-unused-vars
            handleAvataruploadsuccess(response, file, fileList) {
                if(response.code === 1000){
                    this.$message.success(file.name + '上传成功');
                }else {
                    this.$message.error(file.name + '上传失败,'+response.msg);
                }

                for (let x = 0; x < fileList.length; x++) {
                    if (file.name === fileList[x].name) {
                        fileList.splice(x, 1)
                    }
                }

                this.uploadflag = true;
                this.getappsFun({});
            },

            delApp() {
                        this.willDeleteApp = false;

                // eslint-disable-next-line no-console

                        deleteapp(data => {
                            if (data.code === 1000) {
                                for(let i=0;i< this.applists.length;i++){
                                    if(this.delapp.app_id === this.applists[i].app_id){
                                        this.applists.splice(i,1);
                                        this.orgapplists.splice(i,1);
                                    }
                                }
                                this.$message.success(this.delapp.name+'删除成功');
                                this.delapp={};
                            } else {
                                this.$message.error('删除失败，请联系管理员');

                            }
                        }, {
                            "app_id": this.delapp.app_id
                        });
            },
            DeleteApp(delapp) {
                //页面删除按钮触发
                this.willDeleteApp = true;
                this.delapp = delapp;
            },
            appInfos(app) {
                this.$router.push({name: 'FirAppInfostimeline', params: {id: app.app_id}})
            },
            appDownload(app) {
                this.$router.push({name: 'FirDownload', params: { short: app.short }})
            }
        }, computed: {


            getDelappTitle() {
                return `删除应用 ${this.delapp.name}`
            },
            getBH: function () {
                let sch = this.$refs.appmain.scrollHeight;

                if (sch === 0 || sch < window.innerHeight) {
                    sch = window.innerHeight;

                } else {
                    sch += 280;
                }
                return sch;
            }

        },
        filters: {

            getiOStype: function (type) {
                let ftype = '';
                if (type === 1) {
                    ftype = '内测版'
                } else if(type === 2)  {
                    ftype = '企业版'
                }
                return ftype
            },
            formatsize: function (size) {
                return size / 1000;
            },
            autoformat: function (packname) {
                if ((packname.length) > 20) {
                    return packname.split('').slice(0, 20).join('') + '...';
                }
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
            make_icon_url(icon_url){
                if(!icon_url.startsWith("http")){
                    return location.origin+icon_url
                }else {
                    return icon_url
                }
            }

        }, mounted() {
            // this.$store.dispatch('dosetAh',this.getBH);
            window.addEventListener('scroll',this.auto_load);
            this.$store.dispatch('doucurrentapp', {});

            this.getappsFun({});

        },
        destroyed(){
            window.removeEventListener('scroll', this.auto_load, false);
        },
        watch: {

            // eslint-disable-next-line no-unused-vars
            keysearch: function (val, oldVal) {
                // this.searchapps()
                this.searchFun()

            },
            // eslint-disable-next-line no-unused-vars
            searchfromtype: function (val, oldVal) {
                this.applists=[];
                this.query.page=1;
                // this.keysearch='';
                this.searchFun();

                // this.getappsFun({"type": this.searchfromtype});
            },
        }
    }
</script>

<style scoped>


    .el-container {
        margin: 10px auto 100px;
        width: 1166px;
        position: relative;
        padding-bottom: 1px;
        background-color: #bfe7f9;
        color: #9b9b9b;
        -webkit-font-smoothing: antialiased;
        border-radius: 1%;
    }

    .el-header {
        margin-top: 20px;
        padding-top: 30px;
        border-bottom: 1px solid rgba(208, 208, 208, .5);
        background-color: #d5f9f9;
        border-radius: 10px;
    }

    .surplus-card {
        height: 40px;
        text-align: right;
        display: inline-block;
        vertical-align: middle;
        /*border-right: 1px solid #9b9b9b;*/
    }


    .surplus-card .name {
        font-size: 12px;
        color: #9b9b9b;
    }

    .surplus-card .value {
        font-size: 16px;
        color: #434343;
    }

    .appdownload {
        width: 96%;
        height: 96%;
        margin: 2px auto; /*水平居中*/
        /*background: #f8ba0b;*/
        border-radius: 5px;

    }

    .appdownload /deep/ .el-upload-dragger {
        width: 349.22px;
        height: 430px;
        background: #9cb8f8;
        border: 0;
    }

    .appdownload /deep/ .el-icon-upload {
        margin-top: 50%;
    }

    .appdownload /deep/ .el-upload-list__item-name {
        margin-top: -43px;
    }


    .page-apps .card.app .action a, .page-apps .card.app .appname, .page-apps .card.app table tr td, .upload-modal .state-form .release-body .input-addon {
        font-family: 'Open Sans', sans-serif
    }

    .page-apps .row-apps-top > div {
        height: 100%
    }


    .page-apps .card.app .appicon img, .page-apps .card.app .combo-info img {
        border-radius: 17.54%
    }

    .page-apps .card.app {
        position: relative;
        padding: 45px;
        height: 340px;
        background-color: #fff;
        -webkit-transition: all .25s;
        transition: all .25s
    }

    .page-apps .card.app:hover {
        -webkit-transform: translateY(-4px);
        transform: translateY(-4px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, .1)
    }

    .page-apps .card.app .type-icon {
        position: absolute;
        top: 9px;
        right: 7px;
        z-index: 2;
        color: #fff;

    }

    .page-apps .card.app .type-mark {
        position: absolute;
        top: 0;
        right: 0;
        z-index: 1
    }

    .page-apps .card.app .type-mark i {
        position: absolute;
        top: 9px;
        right: 7px
    }

    .page-apps .card.app .appicon {
        display: inline-block;
        width: 100px;
        height: 100px;
        cursor: pointer
    }

    .page-apps .card.app .appname {
        margin-top: 36px;
        font-size: 18px;
        cursor: pointer;
        display: inline-block
    }

    .page-apps .card.app .appname i {
        color: #f8ba0b;
        font-size: 16px;
        margin-right: 6px
    }

    .page-apps .card.app:hover .appname {
        color: #4a4a4a
    }

    .page-apps .card.app .combo-info {
        display: inline-block;
        margin-left: 26px;
        vertical-align: bottom
    }

    .page-apps .card.app .combo-info i {
        margin-right: 14px;
        font-size: 20px
    }

    .page-apps .card.app table {
        width: 100%;
        table-layout: fixed
    }

    .page-apps .card.app table tr td {
        padding: 2px 0;
        font-size: 12px;
        color: #9b9b9b;
    }

    .page-apps .card.app table tr td > span {
        display: inline-block
    }

    .page-apps .card.app table tr td:last-child {
        color: #1a1a1a;
        width: 58%
    }


    .page-apps .card.app .action {
        position: absolute;
        padding: 40px 0 40px 40px;
        left: 0;
        bottom: 0;
        width: 100%
    }

    .page-apps .card.app .action .el-button {
        text-decoration: none;
        border: 1px solid;
        text-align: center;
        padding: 8px 20px;
        margin-right: 4px;
        border-radius: 40px;
        color: #9b9b9b;
        -webkit-transition: all .25s;
        transition: all .25s;
        display: inline-block
    }

    .page-apps .card.app .action .el-button:hover {
        color: #7e9bf8
    }

    .page-apps .card.app .action .el-button i {
        font-size: 18px;
        margin-right: 4px;
        display: inline-block;
        vertical-align: middle
    }


    .page-apps .card.app .action .btn-remove {
        font-size: 0;
        border: 1px solid;
        background: 0;
        padding: 10px;
        border-radius: 50%;
        vertical-align: top;
        color: #9b9b9b;
    }

    .page-apps .card.app .action .btn-remove {
        font-size: 16px
    }

    .page-apps .card.app .action .btn-remove:hover {
        background-color: #ec4242;
        color: #fff
    }

    .page-apps .card-android .type-mark {
        height: 0;
        width: 0;
        border-top: 48px solid #a4c639;
        border-left: 48px solid transparent
    }

    .page-apps .card-ios .type-mark {
        height: 0;
        width: 0;
        border-top: 48px solid #c6c7c9;
        /*border-top-right-radius: 10px;*/
        border-left: 48px solid transparent;
    }


    .page-apps .card-ios {
        border-radius: 10px;
    }

    .page-apps .card.card-invite .appname {
        color: #4a4a4a;
        margin-top: 0
    }


    .page-apps .card.card-invite .actions button {
        display: block;
        padding: 8px;
        width: 120px;
        border: 1px solid #4a4a4a;
        border-radius: 20px;
        background-color: transparent
    }

    .page-apps .card.card-invite .actions button:first-child {
        position: absolute;
        bottom: 44px;
        margin: 0;
        background-color: #4a4a4a;
        color: #fff
    }

    .page-apps .card.card-invite .actions button:last-child {
        position: absolute;
        bottom: 44px;
        left: 170px;
        border-color: transparent
    }

    .page-apps .card.card-invite .actions button:last-child:hover {
        color: #4a4a4a
    }


</style>
