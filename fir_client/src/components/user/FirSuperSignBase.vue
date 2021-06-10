<template>
    <el-main>

        <el-dialog :title="title" :visible.sync="dialogaddDeveloperVisible" :destroy-on-close="true"
                   :close-on-click-modal="false" style="text-align:center">

            <el-form ref="storageinfoform" :model="editdeveloperinfo"
                     label-width="80px" style="margin:0 auto;">


                <div v-if="editdeveloperinfo.auth_type===0">
                    <el-form-item label-width="110px" label="issuer_id">
                        <el-input :disabled='isedit' v-model="editdeveloperinfo.issuer_id"/>
                    </el-form-item>

                    <el-form-item label-width="110px" label="private_key_id">
                        <el-input v-model="editdeveloperinfo.private_key_id"/>
                    </el-form-item>

                    <el-form-item label-width="110px" label="p8key">
                        <el-input type="textarea"
                                  :rows="6" v-model="editdeveloperinfo.p8key" :placeholder="placeholder"/>
                    </el-form-item>
                </div>

                <el-form-item label-width="110px" label="设备数量" style="text-align: left">
                    <el-input-number v-model="editdeveloperinfo.usable_number" :min="0" :max="100" label="设备数量"/>
                </el-form-item>

                <el-form-item label-width="110px" label="备注">
                    <el-input v-model="editdeveloperinfo.description"/>
                </el-form-item>
                <div style="">
                    <el-button v-if="isedit && editdeveloperinfo.is_actived" size="small" @click="syncdevices">同步设备信息
                    </el-button>
                    <el-button v-if="isedit && editdeveloperinfo.is_actived && !editdeveloperinfo.certid" size="small"
                               @click="isocertcert">手动创建证书
                    </el-button>
                    <el-button v-if="isedit && editdeveloperinfo.is_actived" type="danger" size="small"
                               @click="activedeveloperFun(editdeveloperinfo,'checkauth')">开发者账户激活检测
                    </el-button>

                    <el-button @click="updateorcreate">保存</el-button>
                    <el-button @click="canceledit">取消</el-button>
                </div>


            </el-form>
        </el-dialog>

        <el-tabs v-model="activeName" type="border-card" @tab-click="handleClick" tab-position="top">
            <el-tab-pane label="开发者账户" name="iosdeveloper">
                <el-input
                        style="width: 30%;margin-right: 30px;margin-bottom: 10px"
                        v-model="appidseach"
                        clearable
                        placeholder="输入用户ID"/>
                <el-button type="primary" icon="el-icon-search" @click="handleCurrentChange(pagination.currentPage)">
                    搜索
                </el-button>
                <div style="width: 40%;margin-right: 30px;float:right">
                    <el-link :underline="false">总设备量：{{ developer_used_info.all_usable_number}} 已经使用：【平台：{{
                        developer_used_info.all_use_number}} 】【其他：{{developer_used_info.other_used_sum}} 】
                        还剩：{{developer_used_info.all_usable_number- developer_used_info.flyapp_used_sum}} 可用
                    </el-link>
                    <el-progress
                            type="line"
                            :color="developer_usedColor"
                            :text-inside="true" :stroke-width="18" :percentage="percentage"
                            status="success"/>
                </div>

                <el-table
                        :data="app_developer_lists"
                        border
                        v-loading="loading"
                        stripe
                        style="width: 100%">

                    <el-table-column
                            fixed
                            prop="issuer_id"
                            label="用户 issuer_id"
                            width="300">
                        <template slot-scope="scope">
                            <el-popover trigger="hover" placement="top">
                                <p>开发者账户已使用设备数: {{ scope.row.developer_used_number }}</p>
                                <p>开发者账户可用设备数: {{ 100-scope.row.developer_used_number }}</p>
                                <p>由于您设置可用设备数: {{ scope.row.usable_number}} ,所以现在可用设备数: {{
                                    scope.row.usable_number-scope.row.developer_used_number > 0
                                    ?scope.row.usable_number-scope.row.developer_used_number :0 }}</p>

                                <div slot="reference" class="name-wrapper">
                                    <el-tag size="medium" v-if="scope.row.issuer_id"><i class="el-icon-key"/> {{
                                        scope.row.issuer_id }}
                                    </el-tag>
                                </div>
                            </el-popover>
                        </template>

                    </el-table-column>
                    <el-table-column
                            prop="is_actived"
                            label="是否激活"
                            width="110">
                        <template slot-scope="scope">
                            <el-button v-if="scope.row.is_actived === true" type="success" size="small">已激活</el-button>
                            <el-button v-else type="danger" size="small"
                                       @click="activedeveloperFun(scope.row,'preactive')">点击激活
                            </el-button>

                        </template>
                    </el-table-column>
                    <el-table-column
                            prop="certid"
                            label="账户状态"
                            width="100">
                        <template slot-scope="scope">
                            <el-popover trigger="hover" placement="top">
                                <p v-if="!scope.row.certid && scope.row.is_actived === true">开发证书不可用，请在编辑中手动创建开发者证书</p>
                                <p v-if="!scope.row.certid && scope.row.is_actived !== true">请先激活开发者账户</p>
                                <p v-if="scope.row.certid && scope.row.is_actived === true">账户已经启用</p>
                                <div slot="reference" class="name-wrapper">
                                    <el-button v-if="scope.row.certid " type="success" size="small">可用</el-button>
                                    <el-button v-else type="danger" size="small">不可用</el-button>
                                </div>
                            </el-popover>

                        </template>
                    </el-table-column>
                    <el-table-column
                            prop="usable_number"
                            label="可用设备"
                            width="60">
                        <template slot-scope="scope">
                            <el-popover trigger="hover" placement="top">
                                <p>可用设备数: {{ scope.row.usable_number-scope.row.developer_used_number > 0
                                    ?scope.row.usable_number-scope.row.developer_used_number :0}}</p>
                                <div slot="reference" class="name-wrapper">
                                    <el-tag size="medium"> {{ scope.row.usable_number-scope.row.developer_used_number >
                                        0 ?scope.row.usable_number-scope.row.developer_used_number :0 }}
                                    </el-tag>
                                </div>
                            </el-popover>
                        </template>
                    </el-table-column>

                    <el-table-column
                            prop="use_number"
                            label="设备消耗"
                            width="60">
                        <template slot-scope="scope">
                            <el-popover trigger="hover" placement="top">
                                <p>开发者账户已使用设备数【本平台】: {{ scope.row.use_number }}</p>
                                <p>开发者账户已使用设备数【其他】: {{ scope.row.developer_used_other_number }}</p>
                                <div slot="reference" class="name-wrapper">
                                    <el-tag size="medium">{{ scope.row.use_number }}</el-tag>
                                </div>
                            </el-popover>
                        </template>
                    </el-table-column>

                    <el-table-column
                            :formatter="formatter"
                            prop="cert_expire_time"
                            label="证书到期时间"
                            width="160">
                    </el-table-column>
                    <el-table-column
                            prop="description"
                            label="备注"
                    >
                    </el-table-column>
                    <el-table-column
                            fixed="right"
                            label="操作"
                            width="150">
                        <template slot-scope="scope">

                            <el-button
                                    size="mini"
                                    @click="handleEditDeveloper(scope.row)">编辑
                            </el-button>
                            <el-button
                                    size="mini"
                                    type="danger"
                                    @click="handleDeleteDeveloper(scope.row)">删除
                            </el-button>

                        </template>
                    </el-table-column>
                </el-table>


            </el-tab-pane>
            <el-tab-pane label="添加开发者" name="adddeveloper" style="text-align:center">
                <el-form ref="storageinfoform" :model="editdeveloperinfo"
                         label-width="80px" style="margin:0 auto;">

                    <el-form-item label-width="100px" label="认证类型">
                        <el-select v-model="editdeveloperinfo.auth_type" placeholder="认证类型"
                                   style="margin-left: -100px">
                            <el-option v-for="st in apple_auth_list" :key="st.id" :label="st.name"
                                       :value="st.id"/>
                        </el-select>
                    </el-form-item>
                    <div v-if="editdeveloperinfo.auth_type===0">
                        <el-form-item label-width="110px" label="issuer_id">
                            <el-input :disabled='isedit' v-model="editdeveloperinfo.issuer_id"/>
                        </el-form-item>

                        <el-form-item label-width="110px" label="private_key_id">
                            <el-input v-model="editdeveloperinfo.private_key_id" :placeholder="placeholder"/>
                        </el-form-item>

                        <el-form-item label-width="110px" label="p8key">
                            <el-input type="textarea"
                                      :rows="6" v-model="editdeveloperinfo.p8key" :placeholder="placeholder"/>
                        </el-form-item>
                    </div>

                    <el-form-item label-width="110px" label="设备数量" style="text-align: left">
                        <el-input-number v-model="editdeveloperinfo.usable_number" :min="0" :max="100" label="设备数量"/>
                    </el-form-item>

                    <el-form-item label-width="110px" label="备注">
                        <el-input v-model="editdeveloperinfo.description"/>
                    </el-form-item>
                    <div style="">
                        <el-button @click="updateorcreate">添加</el-button>
                        <el-button @click="canceledit">取消</el-button>
                    </div>

                </el-form>
                <el-card style="margin-top: 20px;text-align: left" header="获取密钥帮助">
                    <h1>获取密钥：</h1>
                    <p>前往 AppStore Connect 。按照
                        <el-button plain type="primary" size="small" @click="$router.push({name:'FirSuperSignHelp'})">
                            此步骤
                        </el-button>
                        获取 API 密钥，将获取到的密钥添加到这里。
                    </p>

                    <h1>注意事项：</h1>
                    <p>1.添加后，请勿撤销 API 密钥，否则会导致用户安装的软件闪退或无法安装！</p>
                    <p>2.每个开发者账号最多可创建两本证书，请确保至少还可以创建一本证书！</p>
                    <p>3.添加后，系统会自动创建证书、设备和描述文件，请勿删除这些文件，否则会导致用户安装的软件闪退或无法安装！</p>

                </el-card>
            </el-tab-pane>
            <el-tab-pane label="设备消耗" name="useddevices">
                <el-input
                        style="width: 30%;margin-right: 30px;margin-bottom: 10px"
                        v-model="udidsearch"
                        clearable
                        placeholder="输入UDID"/>
                <el-input
                        style="width: 30%;margin-right: 30px;margin-bottom: 10px"
                        v-model="Bundleidsearch"
                        clearable
                        placeholder="输入BundleID"/>
                <el-input
                        style="width: 23%;margin-right: 30px;margin-bottom: 10px"
                        v-model="appidseach"
                        clearable
                        placeholder="输入用户ID"/>
                <el-button type="primary" icon="el-icon-search" @click="handleCurrentChange(pagination.currentPage)">
                    搜索
                </el-button>

                <el-table
                        :data="app_devices_lists"
                        v-loading="loading"
                        border
                        stripe
                        style="width: 100%">
                    <el-table-column
                            fixed
                            prop="device_udid"
                            label="设备ID"
                    >
                    </el-table-column>
                    <el-table-column
                            prop="device_name"
                            label="设备名称"
                            width="120">
                    </el-table-column>
                    <el-table-column
                            prop="bundle_id"
                            label="应用ID"
                            width="180">
                    </el-table-column>
                    <el-table-column
                            prop="bundle_name"
                            label="应用名称"
                            width="160">
                    </el-table-column>
                    <el-table-column
                            prop="developer_id"
                            label="开发者ID"
                            width="200">
                    </el-table-column>
                    <el-table-column
                            :formatter="deviceformatter"
                            prop="created_time"
                            label="授权时间"
                            width="160">
                    </el-table-column>
                </el-table>


            </el-tab-pane>
            <el-tab-pane label="设备管理" name="devicesudid">
                <el-input
                        style="width: 30%;margin-right: 30px;margin-bottom: 10px"
                        v-model="udidsearch"
                        clearable
                        placeholder="输入UDID"/>
                <el-input
                        style="width: 30%;margin-right: 30px;margin-bottom: 10px"
                        v-model="Bundleidsearch"
                        clearable
                        placeholder="输入BundleID"/>
                <el-button type="primary" icon="el-icon-search" @click="handleCurrentChange(pagination.currentPage)">
                    搜索
                </el-button>


                <el-table
                        :data="app_udid_lists"
                        v-loading="loading"
                        border
                        stripe
                        style="width: 100%">

                    <el-table-column
                            fixed
                            prop="udid"
                            label="设备ID"
                    >
                        <template slot-scope="scope">
                            <el-popover trigger="hover" placement="top">
                                <p>Bundle_ID: {{ scope.row.bundle_id }}</p>
                                <p>应用名称: {{ scope.row.bundle_name }}</p>
                                <p>UDID: {{ scope.row.udid }}</p>
                                <div slot="reference" class="name-wrapper">
                                    <el-tag size="medium">{{ scope.row.udid }}</el-tag>
                                </div>
                            </el-popover>
                        </template>
                    </el-table-column>
                    <el-table-column
                            prop="imei"
                            label="imei"
                            width="180">

                    </el-table-column>
                    <el-table-column
                            prop="product"
                            label="设备名称"
                            width="100">
                    </el-table-column>
                    <el-table-column
                            prop="version"
                            label="设备型号"
                            width="100">
                    </el-table-column>
                    <el-table-column
                            prop="serial"
                            label="设备序列号"
                            width="150">
                    </el-table-column>
                    <el-table-column
                            :formatter="deviceformatter"
                            prop="created_time"
                            label="添加时间"
                            width="160">
                    </el-table-column>
                    <el-table-column
                            fixed="right"
                            label="操作"
                            width="80">
                        <template slot-scope="scope">
                            <el-button
                                    size="mini"
                                    type="danger"
                                    @click="udidDeleteFun(scope)">删除
                            </el-button>
                        </template>
                    </el-table-column>
                </el-table>

            </el-tab-pane>
            <div style="margin-top: 20px" v-if="activeName!== 'adddeveloper'">
                <el-pagination
                        @size-change="handleSizeChange"
                        @current-change="handleCurrentChange"
                        :current-page.sync="pagination.currentPage"
                        :page-sizes="[10, 20, 50, 100]"
                        :page-size="pagination.pagesize"
                        layout="total,sizes, prev, pager, next"
                        :total="pagination.total">
                </el-pagination>
            </div>
        </el-tabs>

    </el-main>
</template>

<script>

    import {iosdeveloper, iosdevices, iosdevicesudid} from "@/restful";
    import {getUserInfoFun, removeAaary} from "@/utils";

    export default {
        name: "FirSuperSignBase",
        data() {
            return {
                app_developer_lists: [],
                app_devices_lists: [],
                app_udid_lists: [],
                activeName: "iosdeveloper",
                udidsearch: "",
                Bundleidsearch: "",
                appidseach: "",
                dialogaddDeveloperVisible: false,
                title: "",
                editdeveloperinfo: {auth_type: 0, usable_number: 100},
                isedit: false,
                placeholder: "",
                pagination: {"currentPage": 1, "total": 0, "pagesize": 10},
                developer_used_info: {"all_usable_number": 0, "other_used_sum": 0, "all_use_number": 0},
                percentage: 0,
                apple_auth_list: [],
                apple_auth_type: 0,
                loadingfun: {},
                loading: false
            }
        },
        methods: {
            developer_usedColor(percentage) {
                if (percentage < 20) {
                    return '#6f7ad3';
                } else if (percentage < 40) {
                    return '#1989fa';
                } else if (percentage < 60) {
                    return '#5cb87a';

                } else if (percentage < 80) {
                    return '#e6a23c';
                } else if (percentage < 90) {
                    return '#E63918';
                } else {
                    return '#F50346';
                }
            },
            udidDeleteFun(scope) {
                this.iosdevicesudidFun('DELETE', {id: scope.row.id, aid: scope.row.app_id});
                this.app_udid_lists = removeAaary(this.app_udid_lists, scope.row)
            },
            handleSizeChange(val) {
                this.pagination.pagesize = val;
                this.get_data_from_tabname(this.activeName, {
                    "size": this.pagination.pagesize,
                    "page": 1
                })
            },
            handleCurrentChange(val) {
                this.pagination.currentPage = val;
                this.get_data_from_tabname(this.activeName, {
                    "size": this.pagination.pagesize,
                    "page": this.pagination.currentPage
                })
            },
            syncdevices() {
                this.iosdeveloperFun({
                    "methods": "PUT",
                    "data": {"issuer_id": this.editdeveloperinfo.issuer_id, "act": "syncdevice"}
                });
            },
            isocertcert() {
                this.iosdeveloperFun({
                    "methods": "PUT",
                    "data": {"issuer_id": this.editdeveloperinfo.issuer_id, "act": "ioscert"}
                });
            },
            activedeveloperFun(developer, act) {
                this.iosdeveloperFun({"methods": "PUT", "data": {"issuer_id": developer.issuer_id, "act": act}});
            },
            canceledit() {
                this.dialogaddDeveloperVisible = false;
                this.editdeveloperinfo = {auth_type: 0,usable_number:100};
                this.isedit = false;
                this.placeholder = ""
            },
            handleEditDeveloper(developer_info) {
                this.editdeveloperinfo = developer_info;
                this.title = '编辑开发者账户';
                this.dialogaddDeveloperVisible = true;
                this.isedit = true;
                this.placeholder = "为空表示不修改该信息"
            },
            updateorcreate() {
                if (this.isedit) {
                    this.iosdeveloperFun({"methods": "PUT", "data": this.editdeveloperinfo})
                } else {
                    if (this.editdeveloperinfo.auth_type === 0) {
                        if (this.editdeveloperinfo.issuer_id && this.editdeveloperinfo.private_key_id && this.editdeveloperinfo.usable_number && this.editdeveloperinfo.p8key) {
                            this.iosdeveloperFun({"methods": "POST", "data": this.editdeveloperinfo});
                        } else {
                            this.$message.warning("输入格式有误")
                        }
                    } else {
                        this.$message.error("输入格式有误")
                    }

                }
            },
            handleDeleteDeveloper(developer_info) {
                this.$confirm('此操作会删除该苹果开发者账户下面的生成的证书等数据,可能会导致超级签包的闪退, 是否继续?', '警告', {
                    confirmButtonText: '确定',
                    cancelButtonText: '取消',
                    type: 'warning'
                }).then(() => {
                    this.iosdeveloperFun({"methods": "DELETE", "data": {"issuer_id": developer_info.issuer_id}});
                }).catch(() => {
                    this.$message({
                        type: 'info',
                        message: '已取消删除'
                    });
                });
            },
            get_data_from_tabname(tabname, data = {}) {
                data.udid = this.udidsearch.replace(/^\s+|\s+$/g, "");
                data.bundleid = this.Bundleidsearch.replace(/^\s+|\s+$/g, "");
                data.appid = this.appidseach.replace(/^\s+|\s+$/g, "");
                this.$router.push({"name": 'FirSuperSignBase', params: {act: tabname}});
                if (tabname === "useddevices") {
                    this.iosdevicesFun('GET', data)
                } else if (tabname === "devicesudid") {
                    this.iosdevicesudidFun('GET', data)
                } else if (tabname === "adddeveloper") {
                    this.iosdeveloperFun({"methods": "GET", "data": data})
                    // this.title='新增私有开发者账户';
                    // this.dialogaddDeveloperVisible=true;
                } else if (tabname === "iosdeveloper") {
                    this.iosdeveloperFun({"methods": "GET", "data": data})
                }
            },
            // eslint-disable-next-line no-unused-vars
            handleClick(tab, event) {
                this.pagination = {"currentPage": 1, "total": 0, "pagesize": 10};
                this.get_data_from_tabname(tab.name);
            },
            // eslint-disable-next-line no-unused-vars
            deviceformatter(row, column) {
                let stime = row.created_time;
                if (stime) {
                    stime = stime.split(".")[0].split("T");
                    return stime[0] + " " + stime[1]
                } else
                    return '';
            },
            // eslint-disable-next-line no-unused-vars
            formatter(row, column) {
                let stime = row.cert_expire_time;
                if (stime) {
                    stime = stime.split(".")[0].split("T");
                    return stime[0] + " " + stime[1]
                } else
                    return '';
            },
            iosdevicesFun(methods, data) {
                this.loading = true;
                iosdevices(data => {
                    if (data.code === 1000) {
                        this.app_devices_lists = data.data;
                        this.pagination.total = data.count;
                    }
                    this.loading = false;
                }, {
                    "methods": methods, "data": data
                })
            },
            iosdeveloperFun(params) {
                if (params.methods !== 'GET') {
                    this.loadingfun = this.$loading({
                        lock: true,
                        text: '执行中,请耐心等待...',
                        spinner: 'el-icon-loading',
                        background: 'rgba(0, 0, 0, 0.7)'
                    });
                } else {
                    this.loading = true
                }
                iosdeveloper(data => {
                    if (data.code === 1000) {
                        this.app_developer_lists = data.data;
                        this.pagination.total = data.count;
                        this.apple_auth_list = data.apple_auth_list;
                        if (data.use_num) {
                            this.developer_used_info = data.use_num;
                            if (this.developer_used_info.all_usable_number !== 0) {
                                let p = parseInt(this.developer_used_info.flyapp_used_sum * 100 / this.developer_used_info.all_usable_number);
                                if (p < 0 || p >= 100) {
                                    p = 100
                                }
                                this.percentage = p;
                            }
                        }

                        if (this.dialogaddDeveloperVisible) {
                            this.canceledit();
                            this.$message.success("操作成功");
                            this.activeName = "iosdeveloper";
                            this.editdeveloperinfo = {auth_type: 0};
                        }
                        if (!this.edit && this.editdeveloperinfo.issuer_id) {
                            this.$message.success("添加成功");
                            this.activeName = "iosdeveloper";
                            this.editdeveloperinfo = {auth_type: 0};
                        }
                    } else if (data.code === 1008) {
                        this.$message.error(data.msg);
                    } else {
                        this.$message.error("操作失败")
                    }
                    if (params.methods !== 'GET') {
                        this.loadingfun.close();
                    } else {
                        this.loading = false
                    }
                }, params)
            },
            iosdevicesudidFun(action, data) {
                if (action !== 'GET') {
                    this.loadingfun = this.$loading({
                        lock: true,
                        text: '执行中,请耐心等待...',
                        spinner: 'el-icon-loading',
                        background: 'rgba(0, 0, 0, 0.7)'
                    });
                } else {
                    this.loading = true
                }
                iosdevicesudid(data => {
                    if (data.code === 1000) {
                        if (action !== "DELETE") {
                            this.app_udid_lists = data.data;
                            this.pagination.total = data.count;
                        }
                    }
                    if (action !== 'GET') {
                        this.loadingfun.close()
                    } else {
                        this.loading = false
                    }
                }, {
                    "methods": action, "data": data
                })
            },
        }, mounted() {
            getUserInfoFun(this);
            if (this.$route.params.act) {
                let activeName = this.$route.params.act;
                let activeName_list = ["useddevices", "devicesudid", "adddeveloper", "iosdeveloper"];
                for (let index in activeName_list) {
                    if (activeName_list[index] === activeName) {
                        this.activeName = activeName;
                        let bundleid = this.$route.query.bundleid;
                        if (bundleid) {
                            this.Bundleidsearch = bundleid;
                        }
                        this.get_data_from_tabname(activeName);
                        return
                    }
                }
            }
            this.get_data_from_tabname(this.activeName);
        }
    }
</script>

<style scoped>
    .el-main {
        margin: 20px auto 100px;
        width: 1166px;
        position: relative;
        padding-bottom: 1px;
        color: #9b9b9b;
        -webkit-font-smoothing: antialiased;
        border-radius: 1%;
    }

</style>
