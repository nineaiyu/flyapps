<template>
    <el-container>
        <el-header style="height: 100px">
            <el-dialog
                    :visible.sync="show_buy_download_times"
                    width="780px"
                    :close-on-click-modal="false"
                    :close-on-press-escape="false"
                    center>

                    <span slot="title" style="color: #313639;font-size: 28px; margin-bottom: 14px;">
                        购买下载次数包
                    </span>

                <div class="packages" style="max-width: 768px;">
                    <div class="package-item" v-for="(packages,index) in data_package_prices" :key="packages.name">
                        <div class="arraw-badge" v-if="index===1"><span>荐</span> <span class="arraw"/></div>
                        <div class="package-content">
                            <div class="money ">￥{{ packages.price / 100 }}</div>
                            <div class="times ">{{ packages.package_size |formatMoney }}</div>
                            <div class="unit" style="font-size: 14px;color: #869096">累计下载次数</div>
                            <div class="text-gift" v-if="packages.download_count_gift">{ 赠 <span>{{ packages.download_count_gift }}</span>
                                次 }
                            </div>
                        </div>
                        <div class="package-actions">
                            <el-radio v-model="default_price_radio" :label="packages.name" border>
                                <span>此套餐</span>
                                <span class="pay-current" v-if="default_price_radio === packages.name"
                                      :style="{background:`url(${pay_image.selected}) right bottom/100% no-repeat`}"/>

                            </el-radio>
                        </div>
                    </div>

                </div>
                <div>
                    <div style="margin-top: 30px;text-align: center">
                        <el-radio v-model="default_pay_radio" :label="pay.name" border v-for="pay in pay_choices"
                                  :key="pay.name">
                            <span style="color: white">xxxxxxxxxxxxxx</span>
                            <span style="width: 160px; height: 45px">
                                    <span class="pay-icon alipay" :style="{backgroundImage:`url(${pay_image.ali})`}"
                                          v-if="pay.type === 'ALI'"/>
                                    <span class="pay-icon" :style="{backgroundImage:`url(${pay_image.wx})`}"
                                          v-if="pay.type === 'WX'"/>
                                    <span class="pay-current" v-if="default_pay_radio === pay.name"
                                          :style="{background:`url(${pay_image.selected}) right bottom/100% no-repeat` }"/>
                                </span>
                        </el-radio>
                    </div>

                    <div style="text-align: center">
                        <el-button type="primary" :disabled="buy_button_disable" @click="buy"
                                   style="margin-top:30px;width: 166px"> 立即支付
                        </el-button>
                    </div>

                </div>

                <span slot="footer">
                        {{ PaymentQuestionMsg }}
                    </span>
            </el-dialog>

            <el-dialog
                    :title="getDelappTitle"
                    :visible.sync="willDeleteApp"
                    width="666px">

                <span v-if="delapp.issupersign">该应用开启了超级签名，执行删除操作，将会删除相关开发者账户下的证书等数据，可能会导致已经下载的APP闪退，并且删除后不可恢复，请谨慎操作</span>
                <span v-else>删除后不可恢复，请谨慎操作</span>

                <span slot="footer" class="dialog-footer">
                        <el-button @click="willDeleteApp = false">取 消</el-button>
                        <el-button type="danger" @click="delApp">确 定</el-button>
                    </span>
            </el-dialog>

            <el-dialog
                    :title="`应用批量上传，`+multiFileList.filter(function(val){return val}).length +` 个应用待上传`"
                    :visible.sync="multiupload"
                    @closed="closeUpload"
                    :destroy-on-close="true"
                    :close-on-click-modal="false"
                    :close-on-press-escape="false"
                    :center="true"
                    width="766px">
                <el-table
                        :data="multiFileList"
                        stripe
                        border
                        height="366px"
                        style="width: 100%">
                    <el-table-column
                            prop="name"
                            align="center"
                            label="文件名称">
                    </el-table-column>
                    <el-table-column
                            prop="size"
                            label="文件大小"
                            align="center"
                            width="80">
                        <template slot-scope="scope">
                            {{ scope.row.size|diskSize }}
                        </template>
                    </el-table-column>
                    <el-table-column
                            label="短连接"
                            align="center"
                            width="70">
                        <template slot-scope="scope">
                            {{ uploadprocess[uploadprocessList[multiFileList.indexOf(scope.row)]].short }}
                        </template>
                    </el-table-column>
                    <el-table-column
                            align="center"
                            label="应用名称">
                        <template slot-scope="scope">
                            {{ uploadprocess[uploadprocessList[multiFileList.indexOf(scope.row)]].appname }}
                        </template>
                    </el-table-column>
                    <el-table-column
                            width="80"
                            align="center"
                            label="上传进度">
                        <template slot-scope="scope">
                            {{ uploadprocess[uploadprocessList[multiFileList.indexOf(scope.row)]].process }} %
                        </template>
                    </el-table-column>
                    <el-table-column
                            width="100"
                            align="center"
                            label="上传速度">
                        <template slot-scope="scope">
                            {{ uploadprocess[uploadprocessList[multiFileList.indexOf(scope.row)]].speed }}/s
                        </template>
                    </el-table-column>
                </el-table>

                <span slot="footer" class="dialog-footer">
                        <el-button plain @click="closeUpload">取 消</el-button>
                        <el-button type="primary" plain @click="multiuploadFun"
                                   :disabled="multiuploaddisable">开始上传</el-button>
                    </span>
            </el-dialog>

            <el-dialog class="upload-app"
                       style="position: fixed"
                       :visible.sync="willuploadApp"
                       :destroy-on-close="true"
                       :show-close="!uploading"
                       width="666px"
                       :close-on-click-modal="false"
                       @closed="closeUpload">
                <div v-if="!uploading">
                    <el-row :gutter="20">
                        <el-col :span="6">
                            <div class="grid-content bg-purple">
                                <div style="width: 100px;height: 100px">
                                    <el-avatar shape="square" :size="100" :src="analyseappinfo.icon"/>
                                </div>
                            </div>
                        </el-col>
                        <el-col :span="18">
                            <div class="grid-content bg-purple">
                                <el-row :gutter="20" style=" margin-top: 8px;">
                                    <el-col :span="18">
                                        {{ analyseappinfo.version}} (Build {{ analyseappinfo.buildversion}}) {{
                                        analyseappinfo.release_type_id|getiOStype}}
                                        <el-link :underline="false"
                                                 v-if="analyseappinfo.udid && analyseappinfo.udid.length > 0"
                                                 @click="showUDID(analyseappinfo)">- {{ analyseappinfo.udid.length
                                            }} UDID
                                        </el-link>
                                    </el-col>
                                </el-row>
                                <el-row :gutter="20" style="margin-top: 18px;">
                                    <el-col :span="18">
                                        <el-input v-model="analyseappinfo.appname"/>
                                    </el-col>

                                </el-row>
                            </div>
                        </el-col>
                    </el-row>
                    <el-divider/>

                    <el-row :gutter="20">

                        <el-col :span="6">
                            <div class="grid-content bg-purple">
                                <el-row :gutter="20" style="margin-top: 18px;">
                                    <el-col :span="18" :offset="8">
                                        <span>短连接</span>
                                    </el-col>
                                </el-row>
                            </div>
                        </el-col>
                        <el-col :span="18">
                            <div class="grid-content bg-purple">
                                <el-row :gutter="20" style="margin-top: 10px;">
                                    <el-col :span="18">
                                        <el-input v-model="short">
                                            <template slot="prepend">{{analyseappinfo.short_domain_name}}/</template>
                                        </el-input>
                                    </el-col>
                                </el-row>
                            </div>
                        </el-col>
                    </el-row>

                    <el-row :gutter="20">

                        <el-col :span="6">
                            <div class="grid-content bg-purple">
                                <el-row :gutter="20" style="margin-top: 18px;">
                                    <el-col :span="18" :offset="8">
                                        <span>更新日志</span>
                                    </el-col>
                                </el-row>
                            </div>
                        </el-col>
                        <el-col :span="18">
                            <div class="grid-content bg-purple">
                                <el-row :gutter="20" style="margin-top: 10px;">
                                    <el-col :span="18">
                                        <el-input type="textarea"
                                                  v-model="analyseappinfo.changelog"
                                                  placeholder="请输入内容"
                                                  rows="5"
                                                  show-word-limit/>
                                    </el-col>
                                </el-row>
                            </div>
                        </el-col>
                    </el-row>

                </div>
                <div v-if="uploading">
                    <!--                        <canvas ref="canvas" class="canvas"/>-->
                    <div class="wrap">
                        <!--包裹所有元素的容器-->
                        <div class="cube">
                            <!--前面图片 -->
                            <div class="out_front">
                                <img src="@/assets/imgs/1.png" class="pic" alt="">
                            </div>
                            <!--后面图片 -->
                            <div class="out_back">
                                <img src="@/assets/imgs/5.png" class="pic" alt="">
                            </div>
                            <!--左面图片 -->
                            <div class="out_left">
                                <img src="@/assets/imgs/6.png" class="pic" alt="">
                            </div>
                            <!--右面图片 -->
                            <div class="out_right">
                                <img src="@/assets/imgs/7.png" class="pic" alt="">
                            </div>
                            <!--上面图片 -->
                            <div class="out_top">
                                <img src="@/assets/imgs/8.png" class="pic" alt="">
                            </div>
                            <!--下面图片 -->
                            <div class="out_bottom">
                                <img src="@/assets/imgs/9.png" class="pic" alt="">
                            </div>

                            <!--小正方体 -->
                            <span class="in_front">
                                    <img :src="this.analyseappinfo.icon" class="in_pic" alt="">
                                </span>
                            <span class="in_back">
                                     <img :src="this.analyseappinfo.icon" class="in_pic" alt="">
                                </span>
                            <span class="in_left">
                                    <img :src="this.analyseappinfo.icon" class="in_pic" alt="">
                                </span>
                            <span class="in_right">
                                    <img :src="this.analyseappinfo.icon" class="in_pic" alt="">
                                </span>
                            <span class="in_top">
                                    <img :src="this.analyseappinfo.icon" class="in_pic" alt="">
                                </span>
                            <span class="in_bottom">
                                    <img :src="this.analyseappinfo.icon" class="in_pic" alt="">
                                </span>
                        </div>

                    </div>
                </div>
                <span slot="footer" class="dialog-footer" v-if="currentfile&& currentfile.uid">
                    <span v-if="uploadflag === true">
                         {{ uploadprocess[uploadprocessList[multiFileList.indexOf(currentfile)]].speed }}/s
                            <el-progress :text-inside="true" :stroke-width="26"
                                         :percentage="uploadprocess[uploadprocessList[multiFileList.indexOf(currentfile)]].process"/>
                    </span>
                        <el-button type="primary" plain
                                   @click="uploadcloud(analyseappinfo,currentfile,false,getappsFun)" v-else>{{ analyseappinfo.is_new|get_upload_text}}</el-button>
                  </span>
            </el-dialog>

            <el-row>
                <el-col :span="3">
                    <el-radio-group v-model="searchfromtype">
                        <el-radio-button label="android" icon="el-icon-mobile-phone"><i
                                class="iconfont icon-android2"/>
                        </el-radio-button>
                        <el-radio-button label="ios"><i class="iconfont icon-ios"/>
                        </el-radio-button>
                    </el-radio-group>

                </el-col>
                <el-col :span="5">
                    <el-row>
                        <el-col :span="20">
                            <el-input
                                    placeholder="请输入名称搜索"
                                    v-model="keysearch"
                                    @click="searchapps"
                                    @keyup.enter.native="searchapps"
                                    clearable>
                            </el-input>
                        </el-col>
                        <el-col :span="2">

                            <el-button icon="el-icon-search" @click="searchFun">
                            </el-button>
                        </el-col>
                    </el-row>
                </el-col>
                <el-col :span="4" class="surplus-card">
                    <el-row>
                        <el-col :span="12">
                            <div>
                                <span class="name">iOS应用</span>
                                <el-divider direction="vertical"/>
                            </div>
                            <div>
                                <span class="value">{{ hdata.ios_count }}</span>
                                <el-divider direction="vertical"/>
                            </div>
                        </el-col>

                        <el-col :span="12">
                            <div>
                                <span class="name">Android应用</span>
                                <el-divider direction="vertical"/>
                            </div>
                            <div>
                                <span class="value">{{ hdata.android_count }}</span>
                                <el-divider direction="vertical"/>
                            </div>
                        </el-col>
                    </el-row>
                </el-col>

                <el-col :span="5" class="surplus-card">
                    <el-row>
                        <el-col :span="12">
                            <div>
                                <span class="name">今日苹果下载次数</span>
                                <el-divider direction="vertical"/>
                            </div>
                            <div>
                                <span class="value">{{ hdata.ios_today_hits_count }}</span>
                                <el-divider direction="vertical"/>
                            </div>
                        </el-col>

                        <el-col :span="12">
                            <div>
                                <span class="name">今日安卓下载次数</span>
                                <el-divider direction="vertical"/>
                            </div>
                            <div>
                                <span class="value">{{ hdata.android_today_hits_count }}</span>
                                <el-divider direction="vertical"/>
                            </div>
                        </el-col>
                    </el-row>
                </el-col>


                <el-col :span="7" class="surplus-card">
                    <el-row>
                        <el-col :span="9">
                            <div>
                                <el-tooltip placement="top">
                                    <div slot="content">
                                        1.账号下所有应用共用此剩余下载次数<br/>
                                        2.每日凌晨 0 点自动重置下载次数<br/>
                                    </div>
                                    <span class="name">今日剩余免费次数</span>
                                </el-tooltip>
                                <el-divider direction="vertical"/>
                            </div>
                            <div>
                                <span class="value">{{$store.state.userinfo.free_download_times }}</span>
                                <el-divider direction="vertical"/>
                            </div>
                        </el-col>

                        <el-col :span="8">
                            <div>
                                <el-tooltip placement="top">
                                    <div slot="content">1.下载次数包没有时间限制，用完为止<br/>2.购买的下载次数包为总下载量，不会每日重置</div>
                                    <span class="name">剩余付费次数</span>
                                </el-tooltip>
                                <el-divider direction="vertical"/>
                            </div>
                            <div>
                                <span class="value">{{$store.state.userinfo.download_times }}</span>
                                <el-divider direction="vertical"/>
                            </div>
                        </el-col>

                        <el-col :span="6">
                            <div>
                                <el-tooltip placement="top">
                                    <div slot="content">
                                        1.下载应用，每100M消耗一次下载次数<br>
                                        2.超级签下载，下载消耗次数翻倍<br>
                                    </div>
                                    <span class="name">购买次数</span>
                                </el-tooltip>
                            </div>
                            <div>
                                <el-button class="action" size="small" icon="el-icon-shopping-cart-1"
                                           @click="show_package_prices"/>
                            </div>
                        </el-col>

                    </el-row>
                </el-col>
            </el-row>

        </el-header>
        <div ref="appmain" style="margin: 40px 10px;height: 100%;width:1166px">
            <el-row style="max-height: 460px; margin: 0 auto;" :gutter="10" class="page-apps">

                <el-col style="width: 30%;height: 460px ;margin-left: 2%">
                    <div class=" app-animator appdownload">
                        <div class=" card app card-ios" style="padding: 0">
                            <el-upload
                                    drag
                                    ref="upload"
                                    :on-change="onUploadChange"
                                    :show-file-list="false"
                                    accept=".ipa , .apk"
                                    action="#"
                                    :auto-upload="false"
                                    :limit="50"
                                    multiple>
                                <i class="el-icon-upload" style="color: #fff"/>
                                <div class="el-upload__text" style="color: #fff;margin-top: 20px">拖拽到这里上传</div>
                            </el-upload>

                        </div>
                    </div>

                </el-col>
                <el-col style="width: 30%;height: 460px;margin-left: 2%"
                        v-for="(r,index) in applists" :key="r.id" @click="appInfos(index)">

                    <div class=" app-animator">
                        <div class="card app card-ios">

                            <i class=" type-icon iconfont icon-ios" v-if="r.type === 1"/>
                            <i class="type-icon iconfont icon-android2" v-if="r.type === 0"/>

                            <div class="type-mark" v-if="r.type === 1"></div>
                            <div class="type-mark" style="border-top: 48px solid #A4C639" v-if="r.type === 0"></div>
                            <a class="appicon" @click="appInfos(r)">
                                <img class="icon ng-isolate-scope" width="100" height="100"
                                     :src="r.master_release.icon_url|make_icon_url" alt=""></a>

                            <div class="combo-info ng-scope" v-if="r.has_combo !== null ">
                                <i class="el-icon-copy-document" style="transform:rotateX(180deg);"/>
                                <a @click="appInfos(r.has_combo)">
                                    <img class="icon ng-isolate-scope" width="45" height="45"
                                         :src="r.has_combo.master_release.icon_url|make_icon_url" alt="">
                                </a>
                            </div>
                            <br>
                            <p class="appname"><i class="el-icon-user-solid"/><span
                                    class="ng-binding">{{ r.name }}</span>
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
                                <tr v-if="r.type === 1 && r.master_release.binary_url === ''">
                                    <td class="ng-binding">打包类型：</td>
                                    <td>
                                            <span class="ng-binding">
                                                {{ r.master_release.release_type|getiOStype }}
                                                <span v-if="r.issupersign">超级签名</span>
                                            </span>
                                    </td>
                                </tr>
                                <tr v-if=" r.master_release.binary_url !== ''">
                                    <td>第三方平台下载：</td>
                                    <td>
                                           <span>
                                            <el-tooltip :content="r.master_release.binary_url" placement="top">
                                                <a target="_blank" :href="r.master_release.binary_url">{{ r.master_release.binary_url| autoformat}}</a>
                                            </el-tooltip>
                                            </span>
                                    </td>
                                </tr>

                                </tbody>
                            </table>

                            <div class="action">
                                <el-button @click="appInfos(r)">
                                    <i class="icon-pen el-icon-edit"/> 管理
                                </el-button>

                                <el-button @click="appDownload(r)" class="ng-binding">
                                    <i class="icon-eye el-icon-view"/> 预览
                                </el-button>

                                <el-button v-if="r.issupersign" @click="DeleteApp(r)" class="btn btn-remove"
                                           icon="el-icon-loading"
                                           circle/>

                                <el-button v-else @click="DeleteApp(r)" class="btn btn-remove" icon="el-icon-delete"
                                           circle/>

                            </div>
                        </div>
                    </div>

                </el-col>

            </el-row>

        </div>
    </el-container>
</template>
<script>
    import {analyseApps, apputils, get_package_prices, getapps, getuploadurl, my_order} from "@/restful";
    import {
        dataURLtoFile,
        format_money,
        getappinfo,
        getScrollHeight,
        getScrollTop,
        getWindowHeight,
        uploadaliyunoss,
        uploadlocalstorage,
        uploadqiniuoss,
        getUserInfoFun,
        makeFiveC,
        deepCopy,
        diskSize,
        upspeed
    } from "@/utils";

    let fiveProcess = {};
    let fiveProcessList = [];
    for (const c of makeFiveC()) {
        fiveProcess[c] = {process: 0, short: '', appname: '', percent: [], speed: '0 MB'};
        fiveProcessList.push(c)
    }
    export default {
        name: "FirApps",
        data() {
            return {
                timer: '',
                multiupload: false,
                multiuploaddisable: false,
                multiFileList: [],
                default_pay_radio: '',
                default_price_radio: '',
                pay_choices: [],
                analyseappinfo: {icon: ''},
                short: '',
                keysearch: '',
                searchfromtype: '',
                applists: [],
                orgapplists: [],
                hdata: {},
                willDeleteApp: false,
                willuploadApp: false,
                uploading: false,
                delapp: {},
                has_next: false,
                query: {'page': 1, size: 20},
                searchflag: false,
                uploadflag: false,
                autoloadflag: true,
                firstloadflag: true,
                currentfile: null,
                uploadprocess: deepCopy(fiveProcess),
                uploadprocessList: fiveProcessList,
                loadingobj: null,
                show_buy_download_times: false,
                data_package_prices: [],
                buy_button_disable: true,
                pay_image: {
                    'wx': require('@/assets/pay/pay_weixin.png'),
                    'ali': require('@/assets/pay/pay_alipay.png'),
                    'selected': require('@/assets/pay/pay_selected.png'),
                },
                PaymentQuestionMsg: '',
            }
        }, methods: {
            multirun(process, keylist, func) {
                let thr = [];
                for (let i = 0; i < process; i++) {
                    thr.push(Promise.resolve())
                }
                for (let j = 0; j < keylist.length; j += process) {
                    for (let i = 0; i < process; i++) {
                        if (i + j < keylist.length) {
                            // eslint-disable-next-line no-unused-vars
                            thr[(j + i) % process] = thr[(j + i) % process].then(_ => func(keylist[i + j]))
                        }
                    }

                }

            },
            uploadasync(file) {
                return new Promise((resolve, reject) => {
                    try {
                        const loading = this.$loading({
                            lock: true,
                            text: `文件 ${file.name} 解析中`,
                            spinner: 'el-icon-loading',
                        });
                        getappinfo(file.raw, appinfo => {
                            if (appinfo && appinfo.bundleid) {
                                let analyseappinfo = appinfo;
                                if (this.currentfile) {
                                    this.analyseappinfo = appinfo;
                                }
                                analyseApps(data => {
                                    if (data.code === 1000) {
                                        this.short = data.data.short;
                                        for (let name of Object.keys(data.data)) {
                                            analyseappinfo[name] = data.data[name]
                                        }
                                        if (this.currentfile) {
                                            this.willuploadApp = true;
                                            resolve()
                                        } else {
                                            this.uploadcloud(analyseappinfo, file, true, resolve)
                                        }

                                    } else {
                                        this.$message.error("应用 " + analyseappinfo.appname + " 上传token获取失败，请刷新重试")
                                    }
                                    loading.close();
                                }, {
                                    'methods': 'POST',
                                    'data': {"bundleid": analyseappinfo.bundleid, "type": analyseappinfo.type}
                                });

                            } else {
                                this.$message.error("文件 " + file.raw.name + " 解析失败,请检查是否为APP应用")
                            }
                        }, err => {
                            loading.close();
                            this.$message.error("应用解析失败,请检查是否为APP应用");
                            // eslint-disable-next-line no-console
                            console.log('Error ', err);
                        });

                    } catch (e) {
                        reject(e);
                    }
                });
            },
            multiuploadFun() {
                this.multiuploaddisable = true;
                if (this.multiFileList && this.multiFileList.length > 0) {
                    this.multirun(3, this.multiFileList, this.uploadasync)
                }
            },
            show_package_prices() {
                get_package_prices(res => {
                    if (res.code === 1000) {
                        this.show_buy_download_times = true;
                        this.data_package_prices = res.data;
                        this.pay_choices = res.pay_choices;
                        if (this.pay_choices && this.pay_choices.length > 0) {
                            this.default_pay_radio = this.pay_choices[0].name;
                        }
                        if (this.data_package_prices && this.data_package_prices.length > 0) {
                            this.default_price_radio = this.data_package_prices[parseInt(this.data_package_prices.length / 2)].name;
                        }
                        if (this.pay_choices.length === 0) {
                            this.$message.warning("暂不支持下载次数购买，请联系管理员");
                            this.show_buy_download_times = false;
                        }
                    } else {
                        this.$message.error("获取价格异常");
                        this.show_buy_download_times = false;
                    }
                }, {})

            },
            buy() {
                this.buy_button_disable = true;
                my_order(res => {
                    if (res.code === 1000) {
                        if (res.data && res.data.url) {
                            this.$message.success("下订单成功，正在跳转支付页");
                            this.$router.push({name: 'FirUserOrders', params: {out_trade_no: res.data.out_trade_no}})
                        } else {
                            this.$message.error("下订单异常，请联系管理员");
                        }
                    } else {
                        this.$message.error("异常" + res.msg);
                        this.buy_button_disable = false;

                    }
                }, {
                    methods: 'POST', data: {
                        price_id: this.default_price_radio,
                        pay_id: this.default_pay_radio,
                    }
                })
            },
            showUDID(appinfo) {
                let udidstr = '';
                for (let i = 0; i < appinfo.udid.length; i++) {
                    udidstr = udidstr + "<p>" + appinfo.udid[i] + "</p>"
                }
                this.$alert(udidstr, appinfo.appname + ' UDID', {
                    confirmButtonText: '确定',
                    dangerouslyUseHTMLString: true,
                });
            },
            updateappinfo(file, analyseappinfo, multiFlag, binaryFlag, resolve) {
                if (binaryFlag) {
                    delete analyseappinfo.icon;
                    this.$message.success(file.raw.name + '上传成功');
                    if (!multiFlag) {
                        analyseappinfo.short = this.short;
                    }
                    const loading = this.$loading({
                        lock: true,
                        text: `应用 ${analyseappinfo.appname} 入库中，请耐心等待`,
                        spinner: 'el-icon-loading',
                    });
                    analyseApps(data => {
                        if (data.code === 1000) {
                            if (!multiFlag) {
                                this.closeUpload();
                                this.$router.push({name: 'FirAppInfostimeline', params: {id: analyseappinfo.app_uuid}});
                            } else {
                                this.$message.success(analyseappinfo.appname + ' 入库成功');
                            }
                        }
                        loading.close();
                        const start = this.multiFileList.indexOf(file);
                        if (start > -1) {
                            delete this.multiFileList[start]
                        }
                        if (this.multiFileList && this.multiFileList.filter(function (val) {
                            return val
                        }).length === 0) {
                            this.closeUpload();
                            this.searchFun();
                        }
                        resolve()
                    }, {'methods': 'PUT', 'data': analyseappinfo});
                }
            },
            updateprocess(binaryFlag, process_key, process, analyseappinfo, rawfile) {
                if (binaryFlag && process_key) {
                    this.uploadprocess[process_key].percent.push({time: Date.now(), process});
                    const pnumber = 20;
                    this.uploadprocess[process_key].process = process;
                    this.uploadprocess[process_key].short = analyseappinfo.short;
                    this.uploadprocess[process_key].appname = analyseappinfo.appname;
                    if (process > 0) {
                        let percent = this.uploadprocess[process_key].percent;
                        if (percent.length > pnumber) {
                            this.uploadprocess[process_key].speed = upspeed(percent[percent.length - pnumber].time, rawfile.size, process - percent[percent.length - pnumber].process)
                        } else {
                            if (percent.length > 1) {
                                this.uploadprocess[process_key].speed = upspeed(percent[0].time, rawfile.size, process)
                            }
                        }
                    }
                }
            },
            uploadtostorage(file, analyseappinfo, multiFlag, binaryFlag, resolve) {
                let upload_key = analyseappinfo.png_key;
                let upload_token = analyseappinfo.png_token;
                let rawfile = file;
                let process_key = '';
                if (binaryFlag) {
                    upload_key = analyseappinfo.upload_key;
                    upload_token = analyseappinfo.upload_token;
                    process_key = this.uploadprocessList[this.multiFileList.indexOf(file)];
                    rawfile = file.raw
                }
                let certinfo = {
                    'upload_key': upload_key,
                    'upload_token': upload_token,
                    'app_info': analyseappinfo
                };
                if (analyseappinfo.storage === 1) {
                    // eslint-disable-next-line no-unused-vars,no-unreachable
                    uploadqiniuoss(rawfile, certinfo, this, res => {
                        this.updateappinfo(file, analyseappinfo, multiFlag, binaryFlag, resolve)
                    }, process => {
                        this.updateprocess(binaryFlag, process_key, process, analyseappinfo, rawfile);
                    })
                } else if (analyseappinfo.storage === 2) {
                    // eslint-disable-next-line no-unused-vars
                    uploadaliyunoss(rawfile, certinfo, this, res => {
                        this.updateappinfo(file, analyseappinfo, multiFlag, binaryFlag, resolve)
                    }, process => {
                        this.updateprocess(binaryFlag, process_key, process, analyseappinfo, rawfile);
                    });
                } else {
                    //本地
                    if (analyseappinfo.domain_name) {
                        certinfo.upload_url = getuploadurl(analyseappinfo.domain_name)
                    } else {
                        certinfo.upload_url = getuploadurl();
                    }
                    certinfo.ftype = 'app';
                    certinfo.app_id = analyseappinfo.app_uuid;
                    // eslint-disable-next-line no-unused-vars,no-unreachable
                    uploadlocalstorage(rawfile, certinfo, this, res => {
                        this.updateappinfo(file, analyseappinfo, multiFlag, binaryFlag, resolve)
                    }, process => {
                        this.updateprocess(binaryFlag, process_key, process, analyseappinfo, rawfile);
                    })
                }
            },
            uploadcloud(analyseappinfo, binary_file, multiFlag, resolve) {
                if (analyseappinfo.binary_url !== '') {
                    this.$confirm(`该应用 ${analyseappinfo.appname} 存在第三方下载链接 <a target="_blank" href="${analyseappinfo.binary_url}"> ${analyseappinfo.binary_url}  </a>更新之后，将不会自动跳转第三方下载；若您还需要第三方跳转，请在第三方平台更新该应用。`, '确定更新应用？', {
                        confirmButtonText: '确定',
                        cancelButtonText: '取消',
                        dangerouslyUseHTMLString: true,
                        type: 'warning'
                    }).then(() => {
                        this.$message({
                            type: 'success',
                            message: '确定更新'
                        });
                        this.uploadstorage(analyseappinfo, binary_file, multiFlag, resolve)
                    }).catch(() => {
                        this.$message({
                            type: 'info',
                            message: `应用 ${analyseappinfo.appname} 已取消更新`
                        });
                        if (!multiFlag) {
                            this.closeUpload();
                        } else {
                            const start = this.multiFileList.indexOf(binary_file);
                            if (start > -1) {
                                delete this.multiFileList[start]
                            }
                            resolve()
                        }
                    });
                } else {
                    this.uploadstorage(analyseappinfo, binary_file, multiFlag, resolve)
                }
            },
            uploadstorage(analyseappinfo, binary_file, multiFlag, resolve) {
                if (!multiFlag) {
                    this.uploadflag = true;
                    this.uploading = true;
                }
                let file = dataURLtoFile(analyseappinfo.icon, analyseappinfo.png_key);
                this.uploadtostorage(file, analyseappinfo, multiFlag, false, resolve);
                this.uploadtostorage(binary_file, analyseappinfo, multiFlag, true, resolve);

            },
            closeUpload() {
                this.uploadflag = false;
                this.uploading = false;
                this.willuploadApp = false;
                this.uploadflag = false;
                this.analyseappinfo = {};

                this.multiupload = false;
                this.multiuploaddisable = false;
                this.multiFileList = [];
                this.$refs.upload.clearFiles();
                this.$refs.upload.abort();
                this.uploadprocess = deepCopy(fiveProcess);
                this.uploadprocessList = fiveProcessList;
            },

            searchFun() {
                let keysearch = this.keysearch.replace(/^\s+|\s+$/g, "");
                if (keysearch === '') {
                    this.searchflag = false;
                    this.applists = [];
                    this.orgapplists = [];
                    this.query.page = 1;
                    if (this.searchfromtype) {
                        this.getappsFun({"type": this.searchfromtype});
                    } else {
                        this.getappsFun({});
                    }
                } else {
                    this.searchflag = true
                }
                if (this.searchflag) {
                    this.applists = [];
                    this.orgapplists = [];
                    if (this.searchfromtype) {
                        this.getappsFun({"type": this.searchfromtype, 'page': 1, size: 999});
                    } else {
                        this.getappsFun({'page': 1, size: 999});
                    }
                }
            },
            auto_load() {
                if (getScrollTop() + getWindowHeight() >= getScrollHeight()) {
                    if (this.has_next) {      //先判断下一页是否有数据
                        if (this.autoloadflag) {
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

                    }
                }
            },
            searchapps() {
                let keysearch = this.keysearch.replace(/^\s+|\s+$/g, "");
                let newapplists = [];
                for (let i = 0; i < this.orgapplists.length; i++) {
                    if (this.orgapplists[i].name.search(keysearch) >= 0) {
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
                this.loadingobj = this.$loading({
                    lock: true,
                    text: '加载中',
                    spinner: 'el-icon-loading',
                    // background: 'rgba(0, 0, 0, 0.7)'
                });
                getapps(data => {
                    if (data.code === 1000) {
                        this.loadingobj.close();
                        if (this.firstloadflag) {
                            window.addEventListener('scroll', this.auto_load);
                            this.firstloadflag = false
                        }
                        this.autoloadflag = true;

                        if (this.uploadflag) {
                            this.applists = data.data;
                            this.uploadflag = false;
                        } else {
                            this.applists = this.applists.concat(data.data);
                        }
                        this.has_next = data.has_next;
                        this.orgapplists = this.applists.slice(); //深拷贝
                        this.hdata = data.hdata;
                        this.searchapps();

                    } else {
                        this.loadingobj.close();
                        this.$router.push({name: 'FirLogin'});
                    }
                }, parms);

            },
            onUploadChange(file, fileList) {
                if (fileList && fileList.length > 1) {
                    this.multiupload = true;
                }
                this.multiFileList = fileList;
                // eslint-disable-next-line no-unused-vars
                this.timer = setTimeout(data => {
                    if (fileList && fileList.length === 1) {
                        this.currentfile = this.multiFileList[0];
                        this.multiuploadFun();
                    }
                    clearTimeout(this.timer);
                }, 300);
            },
            delApp() {
                let loadingobj = this.$loading({
                    lock: true,
                    text: '操作中，请耐心等待',
                    spinner: 'el-icon-loading',
                    // background: 'rgba(0, 0, 0, 0.7)'
                });
                this.willDeleteApp = false;
                apputils(data => {
                    loadingobj.close();
                    if (data.code === 1000) {
                        for (let i = 0; i < this.applists.length; i++) {
                            if (this.delapp.app_id === this.applists[i].app_id) {
                                this.applists.splice(i, 1);
                                this.orgapplists.splice(i, 1);
                            }
                        }
                        this.$message.success(this.delapp.name + '删除成功');
                        this.delapp = {};
                    } else {
                        this.$message.error('删除失败，请联系管理员');
                    }
                }, {
                    "methods": "DELETE",
                    "app_id": this.delapp.app_id
                });
            },
            DeleteApp(delapp) {
                this.willDeleteApp = true;
                this.delapp = delapp;
            },
            appInfos(app) {
                this.$router.push({name: 'FirAppInfostimeline', params: {id: app.app_id}})
            },
            appDownload(app) {
                // this.$router.push({name: 'FirDownload', params: {short: app.short}});
                let routeData = this.$router.resolve({name: 'FirDownload', params: {short: app.short}});
                let p_url = routeData.href;
                if (app.preview_url && app.preview_url.length > 6) {
                    p_url = app.preview_url + p_url
                }
                window.open(p_url, '_blank', '');
            }
        }, computed: {
            getDelappTitle() {
                return `删除应用 ${this.delapp.name}`
            },
        },
        filters: {
            diskSize,
            formatMoney: function (money) {
                return format_money(money, 19);
            },
            getiOStype: function (release_type_id) {
                let ftype = '';
                if (release_type_id === 1) {
                    ftype = '内测版'
                } else if (release_type_id === 2) {
                    ftype = '企业版'
                }
                return ftype
            },
            formatsize: function (size) {
                return size / 1000;
            },
            autoformat: function (packname) {

                if (packname && (packname.length) > 20) {
                    return packname.split('').slice(0, 20).join('') + '...';
                } else {
                    return packname
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
            make_icon_url(icon_url) {
                if (icon_url) {
                    if (!icon_url.startsWith("http")) {
                        return location.origin + icon_url
                    } else {
                        return icon_url
                    }
                }
                return icon_url

            },
            get_upload_text(is_new) {
                if (is_new) {
                    return '新应用上传'
                } else {
                    return '应用更新'
                }
            }

        }, mounted() {
            getUserInfoFun(this);
            this.$store.dispatch('doucurrentapp', {});
            this.getappsFun({});
        },
        destroyed() {
            window.removeEventListener('scroll', this.auto_load, false);
            this.loadingobj.close();
        },
        watch: {
            // eslint-disable-next-line no-unused-vars
            default_pay_radio: function (val, oldVal) {
                this.buy_button_disable = !(this.default_pay_radio.length > 2 && this.default_price_radio.length > 2);
            },
            // eslint-disable-next-line no-unused-vars
            default_price_radio: function (val, oldVal) {
                this.buy_button_disable = !(this.default_pay_radio.length > 2 && this.default_price_radio.length > 2);
            },
            // eslint-disable-next-line no-unused-vars
            keysearch: function (val, oldVal) {
                // this.searchapps()
                let keysearch = this.keysearch.replace(/^\s+|\s+$/g, "");
                if (keysearch === "") {
                    this.searchFun()
                }
            },
            // eslint-disable-next-line no-unused-vars
            searchfromtype: function (val, oldVal) {
                this.applists = [];
                this.query.page = 1;
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
        color: #9b9b9b;
        -webkit-font-smoothing: antialiased;
        border-radius: 1%;
    }

    .el-header {
        margin-top: 20px;
        padding-top: 30px;
        border-bottom: 1px solid rgba(208, 208, 208, .5);
        border-radius: 10px;
    }

    .surplus-card {
        height: 40px;
        text-align: right;
        display: inline-block;
        vertical-align: middle;
    }


    .surplus-card .name {
        font-size: 12px;
        color: #9b9b9b;
    }

    .surplus-card .value {
        font-size: 16px;
        color: #434343;
    }

    .surplus-card .action {
        width: 50px;
        height: 24px;
        line-height: 24px;
        padding: 0;
        border-radius: 30px;
        background-color: #fff;
        border: 1px solid #B6BDC1;
    }

    .appdownload {
        width: 96%;
        height: 96%;
        margin: 2px auto; /*水平居中*/
        border-radius: 5px;

    }

    .appdownload /deep/ .el-upload-dragger {
        width: 339.8px;
        height: 430px;
        background: #8bc3f8;
        border: 0;
    }

    .appdownload /deep/ .el-icon-upload {
        margin-top: 50%;
    }

    .appdownload /deep/ .el-upload-list__item-name {
        margin-top: -43px;
    }

    .appdownload /deep/ .el-upload-list__item {
        font-size: 17px;
        line-height: 1;
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
        padding: 20px 0 40px 40px;
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

    /*最外层容器样式*/
    .wrap {
        width: 100px;
        height: 100px;
        /*margin: 119px;*/
        margin: 120px auto 119px auto;
        position: relative;
        z-index: 9999;
    }

    /*包裹所有容器样式*/
    .cube {
        width: 50px;
        height: 50px;
        margin: 0 auto;
        transform-style: preserve-3d;
        transform: rotateX(-30deg) rotateY(-80deg);
        animation: rotate linear 20s infinite;
    }

    @-webkit-keyframes rotate {
        from {
            transform: rotateX(0deg) rotateY(0deg);
        }
        to {
            transform: rotateX(360deg) rotateY(360deg);
        }
    }

    .cube div {
        position: absolute;
        width: 200px;
        height: 200px;
        opacity: 0.8;
        transition: all .4s;
    }

    /*定义所有图片样式*/
    .pic {
        width: 200px;
        height: 200px;
    }

    .cube .out_front {
        transform: rotateY(0deg) translateZ(100px);
    }

    .cube .out_back {
        transform: translateZ(-100px) rotateY(180deg);
    }

    .cube .out_left {
        transform: rotateY(-90deg) translateZ(100px);
    }

    .cube .out_right {
        transform: rotateY(90deg) translateZ(100px);
    }

    .cube .out_top {
        transform: rotateX(90deg) translateZ(100px);
    }

    .cube .out_bottom {
        transform: rotateX(-90deg) translateZ(100px);
    }

    /*定义小正方体样式*/
    .cube span {
        display: block;
        width: 100px;
        height: 100px;
        position: absolute;
        top: 50px;
        left: 50px;
    }

    .cube .in_pic {
        width: 100px;
        height: 100px;
    }

    .cube .in_front {
        transform: rotateY(0deg) translateZ(50px);
    }

    .cube .in_back {
        transform: translateZ(-50px) rotateY(180deg);
    }

    .cube .in_left {
        transform: rotateY(-90deg) translateZ(50px);
    }

    .cube .in_right {
        transform: rotateY(90deg) translateZ(50px);
    }

    .cube .in_top {
        transform: rotateX(90deg) translateZ(50px);
    }

    .cube .in_bottom {
        transform: rotateX(-90deg) translateZ(50px);
    }

    /*鼠标移入后样式*/
    .cube:hover .out_front {
        transform: rotateY(0deg) translateZ(200px);
    }

    .cube:hover .out_back {
        transform: translateZ(-200px) rotateY(180deg);
    }

    .cube:hover .out_left {
        transform: rotateY(-90deg) translateZ(200px);
    }

    .cube:hover .out_right {
        transform: rotateY(90deg) translateZ(200px);
    }

    .cube:hover .out_top {
        transform: rotateX(90deg) translateZ(200px);
    }

    .cube:hover .out_bottom {
        transform: rotateX(-90deg) translateZ(200px);
    }

    .text-gift {
        color: #8E7BF8;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 20px;
        text-align: center;
    }

    .package-item .unit {
        font-size: 14px;
        color: #869096;
    }

    .package-item .times {
        font-size: 24px;
        line-height: 28px;
        color: #4F5156;
    }

    .package-item .money {
        font-size: 30px;
        color: #7e5ef8;
        line-height: 42px;
    }

    .package-item .package-content {
        margin-bottom: 0;
    }

    .package-item {
        -ms-flex: 1;
        flex: 1;
        border-right: 1px solid transparent;
        padding: 8px 48px;
        text-align: center;
        position: relative;
    }

    .package-item:not(:last-child) {
        border-right-color: #DBE0E3;
    }

    .packages {
        display: -ms-flexbox;
        display: flex;
        -ms-flex-align: center;
        align-items: center;
        margin-bottom: 22px;
    }

    .package-actions .btn:hover {
        color: #fff;
        background-color: #7CB1F8;
        border-color: #7CB1F8;
        cursor: pointer;
        touch-action: manipulation;
    }

    .package-actions .btn {
        background-color: #fff;
        border: 1px solid #B6BDC1;
        border-radius: 30px;
        min-width: 120px;
        height: 40px;
    }

    .arraw-badge {
        position: absolute;
        background-color: #1dcaf8;
        color: #fff;
        left: -1px;
        top: 0;
        width: 30px;
        height: 40px;
        text-align: center;
        padding-top: 5px;
    }

    .arraw-badge .arraw {
        width: 0;
        height: 0;
        overflow: hidden;
        border: 15px solid transparent;
        border-bottom: 10px solid #fff;
        border-top: none;
        position: absolute;
        bottom: 0;
        left: 0;
    }

    .canvas {
        position: absolute;
        margin-top: -58px;
        z-index: 999;
    }

    .pay-current {
        width: 18px;
        height: 19px;
        position: absolute;
        bottom: -1px;
        right: -1px;
    }

    .pay-icon {
        width: 120px;
        height: 30px;
        background-size: 100%;
        position: absolute;
        top: 6px;
        left: 15px;
    }

</style>
