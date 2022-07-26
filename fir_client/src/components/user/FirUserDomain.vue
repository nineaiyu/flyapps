<template>
  <el-main>
    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :title="domain_title"
        :visible.sync="bind_domain_sure"
        width="666px">
      <bind-domain v-if="bind_domain_sure" :app_id="current_domain_info.app_id"
                   :c_domain_name="current_domain_info.domain_name"
                   :domain_state="true" :domain_type="current_domain_info.domain_type"
                   transitionName="bind-app-domain"/>
    </el-dialog>
    <div>
      <el-input
          v-model="search_key"
          clearable
          placeholder="输入域名或者应用名称搜索"
          style="width: 30%;margin-right: 30px;margin-bottom: 5px"/>
      <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
        搜索
      </el-button>
      <div style="float: right">
        <el-tooltip content="应用安装下载页，多个下载页域名可以避免域名被封导致其他应用也无法访问">
          <el-button plain type="primary" @click="$store.dispatch('dodomainaction', 1)">
            添加下载页域名
          </el-button>
        </el-tooltip>
        <el-tooltip content="用与生成预览和下载码的域名">
          <el-button plain type="primary" @click="$store.dispatch('dodomainaction', 2)">
            设置下载码域名
          </el-button>
        </el-tooltip>

      </div>


      <el-table
          v-loading="loading"
          :data="domain_info_list"
          border
          stripe
          style="width: 100%">

        <el-table-column
            align="center"
            fixed
            label="绑定域名"
            prop="domain_name">
          <template slot-scope="scope">
            <el-tooltip content="该域名解析到了私有下载服务器上面">
              <el-tag v-if="scope.row.is_private" style="margin-right: 5px" type="small">Private</el-tag>
            </el-tooltip>
            <el-tooltip content="点击复制到剪贴板">
              <el-link v-if="scope.row.domain_name" v-clipboard:copy="scope.row.domain_name"
                       v-clipboard:success="copy_success"
                       :underline="false">{{ scope.row.domain_name }}
              </el-link>
            </el-tooltip>
          </template>
        </el-table-column>

        <el-table-column
            align="center"
            label="状态"
            prop="is_enable"
            width="110">

          <template slot-scope="scope">
            <el-tooltip v-if="scope.row.is_enable === true" content="点击查看域名绑定信息" placement="left-start">
              <el-button size="small" type="success" @click="show_bind_domain_info(scope.row)">已绑定
              </el-button>
            </el-tooltip>
            <el-tooltip v-else content="激活下载域名绑定信息" placement="left-start">

              <el-button size="small" type="warning" @click="show_bind_domain_info(scope.row)">继续绑定
              </el-button>
            </el-tooltip>

          </template>

        </el-table-column>
        <el-table-column
            align="center"
            label="开启https"
            prop="is_https"
            width="110">
          <template slot-scope="scope">
            <el-tooltip content="点击关闭" placement="top">
              <div slot="content">
                <span v-if="scope.row.is_https">
                  点击关闭 HTTPS 访问
                </span>
                <span v-else>
                  点击开启支持 HTTPS 访问
                </span>
              </div>
              <el-button v-if="scope.row.is_https" size="small" type="success"
                         @click="changeHttpsFun(scope.row, false)">已开启
              </el-button>
              <el-button v-else size="small" type="info" @click="changeHttpsFun(scope.row, true)">未开启</el-button>
            </el-tooltip>
          </template>
        </el-table-column>


        <el-table-column
            align="center"
            label="域名类型"
            prop="domain_type"
            width="260">
          <template slot-scope="scope">
            <el-tooltip v-if="scope.row.domain_type===2 && scope.row.app_info" content="点击查看应用信息"
                        placement="right-start">
              <el-button plain size="small" type="info" @click="appInfos(scope.row.app_info)">{{
                  format_domain_type(scope.row)
                }}
              </el-button>
            </el-tooltip>
            <el-button v-else-if="scope.row.domain_type===1" plain size="small" type="success">{{
                format_domain_type(scope.row)
              }}
            </el-button>
            <el-button v-else plain size="small" type="primary">{{ format_domain_type(scope.row) }}
            </el-button>

          </template>
        </el-table-column>
        <el-table-column
            align="center"
            label="跳转权重"
            prop="weight"
            width="110">
          <template slot-scope="scope">
            <el-popover v-if="scope.row.domain_type === 1" placement="top" trigger="hover">
              <p>绑定域名：{{ scope.row.domain_name }}</p>
              <p>域名类型：{{ format_domain_type(scope.row) }}</p>
              <p>权重越大，下载域名使用频率越高</p>
              <p>
                跳转权重:
                <el-input-number v-model="scope.row.weight" :max="100" :min="1"
                                 label="跳转权重" size="small"/>
                <el-button size="small" style="margin-left: 10px" @click="saveWeight(scope.row)">保存修改</el-button>
              </p>
              <div slot="reference" class="name-wrapper">
                <el-link :underline="false" plain size="small">{{ scope.row.weight }}
                </el-link>
              </div>

            </el-popover>
          </template>
        </el-table-column>
        <el-table-column
            :formatter="format_create_time"
            align="center"
            label="域名绑定时间"
            prop="created_time"
            width="170"
        >
        </el-table-column>
      </el-table>


    </div>
    <div style="margin-top: 20px;margin-bottom: 20px">
      <el-pagination
          :current-page.sync="pagination.currentPage"
          :page-size="pagination.pagesize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total,sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange">
      </el-pagination>
    </div>
  </el-main>
</template>

<script>

import {domaininfo, personalConfigInfo} from "@/restful";
import BindDomain from "@/components/base/BindDomain";
import {format_choices, getUserInfoFun} from '@/utils'
import {format_time} from "@/utils/base/utils";

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
      configVisible: false,
      config_lists: [],
      short_download_uri: ''
    }
  },
  methods: {
    changeHttpsFun(domain_info, is_https) {
      domain_info['is_https'] = is_https
      domaininfo(data => {
        if (data.code === 1000) {
          this.$message.success("https支持修改成功")
        } else {
          this.$message.error("修改失败 " + data.msg)
        }
      }, {methods: 'PUT', data: domain_info})
    },
    configFun() {
      personalConfigInfo(data => {
        if (data.code === 1000) {
          if (data.data.length === 1) {
            this.short_download_uri = data.data[0].value
          }
        } else {
          this.$message.error("获取数据失败了 " + data.msg)
        }
      }, {
        methods: 'GET'
      }, 'short_download_uri')


      personalConfigInfo(data => {
        if (data.code === 1000) {
          this.config_lists = data.data
          this.configVisible = true
        } else {
          this.$message.error("获取数据失败了 " + data.msg)
        }
      }, {
        methods: 'GET'
      }, 'preview_route')
    },
    changeConfig(info) {
      personalConfigInfo(data => {
        if (data.code === 1000) {
          this.$message.success("操作成功")
          this.configFun()
        } else {
          this.$message.error("操作失败了 " + data.msg)
        }
      }, {
        methods: 'PUT', data: {config_key: info.key, config_value: info.value}
      }, 'preview_route')
    },
    updateConfig() {
      personalConfigInfo(data => {
        if (data.code === 1000) {
          this.$message.success("操作成功")
          this.configFun()
        } else {
          this.$message.error("操作失败了 " + data.msg)
        }
      }, {
        methods: 'DELETE'
      }, 'preview_route')
    },
    saveWeight(domain_info) {
      domaininfo(data => {
        if (data.code === 1000) {
          this.$message.success("权重修改成功")

        } else {
          this.$message.error("权重修改失败 " + data.msg)
        }
      }, {methods: 'PUT', data: domain_info})
    },
    show_bind_domain_info(domain_info) {
      this.bind_domain_sure = true;
      let app_id = null;
      if (domain_info.app_info && domain_info.app_info.app_id) {
        app_id = domain_info.app_info.app_id;
      }
      this.current_domain_info.app_id = app_id;
      this.current_domain_info.domain_type = domain_info.domain_type;
      this.current_domain_info.domain_name = domain_info.domain_name;
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

    format_domain_type(row) {
      if (row.domain_type === 2) {
        return "应用" + row.app_info.name + "域名"
      }
      return format_choices(row.domain_type, this.domain_type_choices)
    },

    format_create_time(row) {
      return format_time(row.created_time)
    },


  }, mounted() {
    getUserInfoFun(this);
    this.get_data_from_tabname();
  }, watch: {
    '$store.state.domain_show_state': function () {
      if (this.$store.state.domain_show_state) {
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
