<template>
    <el-main>
        <el-dialog
                :title="domain_title"
                :close-on-click-modal="false"
                :close-on-press-escape="false"
                :visible.sync="bind_domain_sure"
                width="666px">
            <bind-domain v-if="bind_domain_sure" transitionName="bind-app-domain" :app_id="current_domain_info.app_id"
                         :domain_type="current_domain_info.domain_type" :domain_state="true"/>
        </el-dialog>
        <div>
            <el-input
                    style="width: 30%;margin-right: 30px;margin-bottom: 5px"
                    v-model="search_key"
                    clearable
                    placeholder="输入域名或者应用名称搜索"/>
            <el-button type="primary" icon="el-icon-search" @click="handleCurrentChange(1)">
                搜索
            </el-button>
            <div style="float: right">
                <el-button type="primary" plain @click="$store.dispatch('dodomainaction', 1)">
                    设置下载页域名
                </el-button>
                <el-button type="primary" plain v-if="$store.state.userinfo&&$store.state.userinfo.role >1"
                           @click="$store.dispatch('dodomainaction', 2)">
                    设置下载码域名
                </el-button>
            </div>


            <el-table
                    :data="domain_info_list"
                    v-loading="loading"
                    border
                    stripe
                    style="width: 100%">

                <el-table-column
                        fixed
                        prop="domain_name"
                        align="center"
                        label="绑定域名">
                    <template slot-scope="scope">
                        <el-tooltip content="点击复制到剪贴板">
                            <el-link v-if="scope.row.domain_name" :underline="false"
                                     v-clipboard:copy="scope.row.domain_name"
                                     v-clipboard:success="copy_success">{{ scope.row.domain_name }}
                            </el-link>
                        </el-tooltip>
                    </template>
                </el-table-column>

                <el-table-column
                        prop="is_enable"
                        label="状态"
                        align="center"
                        width="110">

                    <template slot-scope="scope">
                        <el-tooltip content="点击查看域名绑定信息" v-if="scope.row.is_enable === true" placement="left-start">
                            <el-button type="success" size="small" @click="show_bind_domain_info(scope.row)">已绑定
                            </el-button>
                        </el-tooltip>
                        <el-tooltip content="激活下载域名绑定信息" v-else placement="left-start">

                            <el-button type="warning" size="small" @click="show_bind_domain_info(scope.row)">继续绑定
                            </el-button>
                        </el-tooltip>

                    </template>

                </el-table-column>


                <el-table-column
                        prop="domain_type"
                        align="center"
                        label="域名类型"
                        width="260">
                    <template slot-scope="scope">
                        <el-tooltip content="点击查看应用信息" v-if="scope.row.domain_type===2 && scope.row.app_info"
                                    placement="right-start">
                            <el-button type="info" plain size="small" @click="appInfos(scope.row.app_info)">{{
                                format_domain_type(scope.row) }}
                            </el-button>
                        </el-tooltip>
                        <el-button v-else-if="scope.row.domain_type===1" type="success" plain size="small">{{
                            format_domain_type(scope.row) }}
                        </el-button>
                        <el-button v-else type="primary" plain size="small">{{ format_domain_type(scope.row) }}
                        </el-button>

                    </template>
                </el-table-column>

                <el-table-column
                        :formatter="format_create_time"
                        prop="created_time"
                        width="170"
                        align="center"
                        label="域名绑定时间"
                >
                </el-table-column>
            </el-table>


        </div>
        <div style="margin-top: 20px;margin-bottom: 20px">
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
    </el-main>
</template>

<script>

    import {domaininfo} from "@/restful";
    import BindDomain from "@/components/base/BindDomain";
    import {getUserInfoFun} from '@/utils'

    export default {
        name: "FirUserDomain",
        components: {BindDomain},
        data() {
            return {
                domain_title: '绑定应用专属下载页域名',
                bind_domain_sure: false,
                domain_info_list: [],
                search_key: "",
                pagination: {"currentPage": 1, "total": 0, "pagesize": 10},
                domain_type_choices: [],
                current_domain_info: {'domain_type': 1, 'app_id': null},
                loading: false,
            }
        },
        methods: {
            show_bind_domain_info(domain_info) {
                this.bind_domain_sure = true;
                let app_id = null;
                if (domain_info.app_info && domain_info.app_info.app_id) {
                    app_id = domain_info.app_info.app_id;
                }
                this.current_domain_info.app_id = app_id;
                this.current_domain_info.domain_type = domain_info.domain_type;
                this.domain_title = this.format_domain_type(domain_info) + ' 绑定详情';
            },
            appInfos(app_info) {
                if (app_info && app_info.app_id) {
                    this.$router.push({name: 'FirAppInfossecurity', params: {id: app_info.app_id}})
                }
            },
            copy_success() {
                this.$message.success('复制剪切板成功');
            },
            handleSizeChange(val) {
                this.pagination.pagesize = val;
                this.get_data_from_tabname({
                    "size": this.pagination.pagesize,
                    "page": 1
                })
            },
            handleCurrentChange(val) {
                this.pagination.currentPage = val;
                this.get_data_from_tabname({
                    "size": this.pagination.pagesize,
                    "page": this.pagination.currentPage
                })
            },

            get_data_from_tabname(data = {}) {
                data.search_key = this.search_key.replace(/^\s+|\s+$/g, "");
                this.UserDomainFun(data)
            },
            UserDomainFun(params) {
                this.loading = true;
                domaininfo(data => {
                    if (data.code === 1000) {
                        this.domain_info_list = data.data;
                        this.pagination.total = data.count;
                        this.domain_type_choices = data.domain_type_choices;

                    } else {
                        this.$message.error("域名绑定信息获取失败")
                    }
                    this.loading = false;
                }, {methods: 'GET', data: params})
            },
            format_choices(key, obj) {
                for (let i = 0; i < obj.length; i++) {
                    if (key === obj[i].id) {
                        return obj[i].name
                    }
                }
                return "未知"
            },

            format_domain_type(row) {
                if (row.domain_type === 2) {
                    return "应用" + row.app_info.name + "域名"
                }
                return this.format_choices(row.domain_type, this.domain_type_choices)
            },

            format_create_time(row) {
                return this.format_time(row.created_time)
            },

            format_time(stime) {
                if (stime) {
                    stime = stime.split(".")[0].split("T");
                    return stime[0] + " " + stime[1]
                } else
                    return '';
            },
        }, mounted() {
            getUserInfoFun(this);
            this.get_data_from_tabname();
        }, watch: {
            '$store.state.domian_show_state': function () {
                if (this.$store.state.domian_show_state) {
                    this.bind_domain_sure = false;
                    this.get_data_from_tabname();
                }
            },
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
