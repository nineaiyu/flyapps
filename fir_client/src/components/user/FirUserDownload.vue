<template>
  <el-main>

    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :visible.sync="configVisible"
        center
        title="下载页部署配置"
        width="666px">


      <el-card v-for="info in config_lists" :key="info.key" class="box-card" shadow="hover"
               style="margin-bottom: 20px">
        <div slot="header" class="clearfix">
          <span><el-tag size="medium" type="info">配置KEY</el-tag> <el-tag size="medium">{{ info.key }}</el-tag></span>
          <div style="float: right">
            <el-switch
                v-model="info.value"
                active-color="#13ce66"
                active-text="启用"
                active-value="true"
                inactive-color="#ff4949"
                inactive-text="关闭"
                inactive-value="false"
                @change="changeConfig(info)">
            </el-switch>
          </div>
        </div>
        <el-tag size="medium" type="info">描述信息</el-tag>
        {{ info.title }}
      </el-card>
      <el-divider></el-divider>
      <el-card style="margin-top: 20px">
        <div slot="header" class="clearfix">
          <el-tag size="medium" type="success">下载页源码及操作文档</el-tag>
        </div>
        <div v-if="short_download_list.length>0">
          <div style="margin: 10px" v-for="short_download_uri in short_download_list" :key="short_download_uri.key">
            <el-tag size="medium" type="info">{{short_download_uri.title}}</el-tag>
            <el-link style="margin-left: 10px" :href="short_download_uri.value" target="_blank">点击下载</el-link>
        </div>
        </div>
      </el-card>

      <div slot="footer" class="dialog-footer">
        <el-button @click="updateConfig">恢复默认值</el-button>
        <el-button @click="configVisible=false">取消</el-button>
      </div>

    </el-dialog>

    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :visible.sync="addCnameVisible"
        center
        title="添加下载页服务器域名"
        width="800px">

      <el-steps :active="p_active" finish-status="success" :align-center="true">
        <el-step title="添加服务器域名"></el-step>
        <el-step title="验证服务器域名所有权"></el-step>
        <el-step title="添加成功"></el-step>
      </el-steps>

      <el-container>

        <div v-if="p_active===0" style="margin-top: 20px">
          <el-tag style="margin: 10px 5px">1.如果是cdn等含有CNAME，直接添加cdn的 CNAME 值</el-tag>
          <el-tag style="margin: 10px 5px">2.如果是服务器，需要将域名解析到服务器，然后添加该解析的域名</el-tag>
          <div style="width: 600px;text-align: center;margin: auto">

            <el-form ref="form" :model="addSerInfo" label-width="120px">

              <el-form-item label="下载服务器域名">
                <el-input v-model="addSerInfo.domain_record" placeholder="cdn的cname或者服务器的域名，必填"></el-input>
              </el-form-item>

              <el-form-item label="下载服务器地址">
                <el-input v-model="addSerInfo.ip_address" placeholder="如果有服务器地址，添加服务器ip，否则填写服务器域名"></el-input>
              </el-form-item>
              <el-form-item label="备注">
                <el-input type="textarea" v-model="addSerInfo.description"></el-input>
              </el-form-item>
            </el-form>
            <div style="margin-top: 20px;">
              <el-button type="primary" @click="addCnameSer">下一步</el-button>
            </div>
          </div>

        </div>

        <div v-else-if="p_active===1" style="margin-top: 30px;text-align: center">

          请联系域名管理员，前往 <strong>{{ cnameInfo.domain_record }}</strong> 域名 DNS 管理后台添加如下 {{ cnameInfo.r_type }} 记录。
          <el-table
              :data="domain_tData"
              border
              stripe
              v-loading="loading"
              style="width: 100%;margin-top: 20px">
            <el-table-column
                align="center"
                label="记录类型"
                prop="r_type"
                width="100">
            </el-table-column>
            <el-table-column
                align="center"
                label="主机记录"
                prop="host_r"
            >
              <template slot-scope="scope">
                <el-tooltip content="点击复制到剪贴板">
                  <el-link v-if="scope.row.host_r" v-clipboard:copy="scope.row.host_r"
                           v-clipboard:success="copy_success"
                           :underline="false">{{ scope.row.host_r }}
                  </el-link>
                </el-tooltip>
              </template>
            </el-table-column>
            <el-table-column
                align="center"
                label="记录值"
                prop="cname_r"
                width="300">
              <template slot-scope="scope">
                <el-tooltip content="点击复制到剪贴板">
                  <el-link v-if="scope.row.cname_r" v-clipboard:copy="scope.row.cname_r"
                           v-clipboard:success="copy_success"
                           :underline="false">{{ scope.row.cname_r }}
                  </el-link>
                </el-tooltip>
              </template>
            </el-table-column>
          </el-table>
          <el-alert :closable="false"
                    show-icon
                    style="margin-top: 30px"
                    title="请在域名DNS配置成功后，点击“下一步”按钮"
                    type="warning"/>

          <div style="margin-top: 20px;text-align: center;">
            <el-button type="primary" @click="p_active=0">上一步</el-button>
            <el-button type="primary" @click="checkCnameSer" :disabled="loading">下一步</el-button>
          </div>
        </div>
      </el-container>


    </el-dialog>


    <div>
      <el-input
          v-model="search_key"
          clearable
          placeholder="输入下载服务器域名"
          style="width: 30%;margin-right: 30px;margin-bottom: 5px"/>
      <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
        搜索
      </el-button>
      <div style="float: right">


        <el-tooltip content="下载页配置，可以定制部署私有下载页">
          <el-button plain type="primary" @click="configFun">
            下载页配置
          </el-button>
        </el-tooltip>
        <el-button plain type="primary" @click="addDownloadSer">
          添加下载页服务器
        </el-button>
      </div>

      <el-table
          v-loading="loading"
          :data="cname_info_list"
          border
          stripe
          style="width: 100%">

        <el-table-column
            align="center"
            fixed
            label="下载服务器域名"
            prop="domain_name">
          <template slot-scope="scope">
            <el-tooltip content="点击复制到剪贴板">
              <el-link v-if="scope.row.domain_record" v-clipboard:copy="scope.row.domain_record"
                       v-clipboard:success="copy_success"
                       :underline="false">{{ scope.row.domain_record }}
              </el-link>
            </el-tooltip>
          </template>
        </el-table-column>

        <el-table-column
            align="center"
            label="下载服务器地址"
            prop="ip_address">
        </el-table-column>

        <el-table-column
            align="center"
            label="状态"
            prop="is_enable"
            width="110">

          <template slot-scope="scope">
            <el-tooltip v-if="scope.row.is_enable === true" content="已经绑定成功" placement="left-start">
              <el-button size="small" type="success">成功
              </el-button>
            </el-tooltip>
            <el-tooltip v-else content="点击激活服务器域名绑定信息" placement="left-start">
              <el-button size="small" type="warning" @click="continueBind(scope.row)">继续绑定
              </el-button>
            </el-tooltip>

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
        <el-table-column
            align="center"
            label="备注"
            prop="description">
        </el-table-column>
        <el-table-column
            align="center"
            label="操作"
            prop="is_enable"
            width="100">

          <template slot-scope="scope">
            <el-tooltip content="删除该下载页服务器" placement="left-start">
              <el-button size="small" type="danger" @click="delCnameSer(scope.row)">删除
              </el-button>
            </el-tooltip>

          </template>

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

import {dCnameInfoFun, personalConfigInfo} from "@/restful";
import {getUserInfoFun} from '@/utils'
import {format_time} from "@/utils/base/utils";

export default {
  name: "FirUserDomain",
  data() {
    return {
      addSerInfo: {},
      cnameInfo: {},
      domain_tData: [],
      p_active: 0,
      cname_info_list: [],
      search_key: "",
      pagination: {"currentPage": 1, "total": 0, "pagesize": 10},
      loading: false,
      configVisible: false,
      addCnameVisible: false,
      config_lists: [],
      short_download_list: []
    }
  },
  methods: {
    continueBind(cname_info) {
      this.addSerInfo = cname_info
      this.addCnameVisible = true
      this.addCnameSer()
    },
    delCnameSer(cname_info) {
      this.$confirm('若下载域名绑定到该解析，同时也会删除绑定的下载域名，是否继续删除？', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        dCnameInfoFun(data => {
          if (data.code === 1000) {
            this.$message.success("删除成功")
            this.get_data_from_tabname();
          } else {
            this.$message.error("操作失败了 " + data.msg)
          }
        }, {
          methods: 'DELETE',
          data: {'domain_record': cname_info.domain_record}
        })
      })
    },
    checkCnameSer() {
      this.loading=true
      dCnameInfoFun(data => {
        this.loading=false
        if (data.code === 1000) {
          this.$message.success(this.addSerInfo.domain_record + " 添加成功")
          this.get_data_from_tabname();
          this.addDownloadSer()
          this.addCnameVisible = false
        } else {
          this.$message.error("操作失败了 " + data.msg)
        }
      }, {
        methods: 'PUT',
        data: {'act': 'check', 'domain_record': this.addSerInfo.domain_record}
      })
    },
    addCnameSer() {
      let domain_record = this.addSerInfo.domain_record
      let ip_address = this.addSerInfo.ip_address
      if (domain_record && domain_record.length > 6 && ip_address && ip_address.length > 6) {
        dCnameInfoFun(data => {
          if (data.code === 1000) {
            this.p_active = 1
            this.cnameInfo = data.data
            this.domain_tData = [this.cnameInfo]
          } else {
            this.$message.error("操作失败了 " + data.msg)
          }
        }, {
          methods: 'POST',
          data: this.addSerInfo
        })
      } else {
        this.$message.error("参数有误")
      }

    },
    addDownloadSer() {
      this.addSerInfo = {}
      this.cnameInfo = {}
      this.p_active = 0
      this.addCnameVisible = true
    },
    configFun() {
      personalConfigInfo(data => {
        if (data.code === 1000) {
          this.short_download_list = data.data
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
      this.UserCnameInfoFun(data)
    },
    UserCnameInfoFun(params) {
      this.loading = true;
      dCnameInfoFun(data => {
        if (data.code === 1000) {
          this.cname_info_list = data.data;
          this.pagination.total = data.count;

        } else {
          this.$message.error("域名绑定信息获取失败")
        }
        this.loading = false;
      }, {methods: 'GET', data: params})
    },

    format_create_time(row) {
      return format_time(row.created_time)
    },

  }, mounted() {
    getUserInfoFun(this);
    this.get_data_from_tabname();
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
