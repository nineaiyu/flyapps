<template>
  <div style="margin-top: 20px;width: 66%;margin-left: 8%">
    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :visible.sync="bind_domain_sure"
        title="绑定应用专属下载页域名"
        width="666px">
      <bind-domain v-if="bind_domain_sure" :app_id="this.currentapp.app_id" :c_domain_name="this.currentapp.domain_name"
                   :domain_type="2" transitionName="bind-app-domain"/>
    </el-dialog>
    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :visible.sync="download_password_sure"
        center
        title="应用下载授权码设置"
        width="900px">

      <el-dialog
          :visible.sync="makeTokenVisible"
          append-to-body
          center
          title="下载授权码生成"
          width="500px">

        <el-form ref="form" :model="makeTokenInfo" label-width="110px">
          <el-form-item label="指定授权码" style="width: 400px">
            <el-tag>当存在指定授权码，授权码长度和生成数量被禁用</el-tag>
            <el-input v-model="makeTokenInfo.token" clearable placeholder="输入指定下载授权码"></el-input>
          </el-form-item>
          <el-form-item label="授权码长度">
            <el-input-number v-model="makeTokenInfo.token_length" :disabled="tokendisable" :max="32"
                             :min="4"></el-input-number>
            <el-tag style="margin-left: 5px">授权码长度为4-32之间</el-tag>

          </el-form-item>
          <el-form-item label="生成数量">
            <el-input-number v-model="makeTokenInfo.token_number" :disabled="tokendisable" :max="1024"
                             :min="1" :step="20"></el-input-number>
            <el-tag style="margin-left: 5px">单次最多可生成1024个</el-tag>

          </el-form-item>
          <el-form-item label="最大使用次数">
            <el-input-number v-model="makeTokenInfo.token_max_used_number" :disabled="makeTokenInfo.bind_status"
                             :max="1024"
                             :min="0"></el-input-number>
            <el-tag style="margin-left: 5px">0表示不限使用次数</el-tag>
          </el-form-item>
          <el-form-item v-if="currentapp.type===1 && currentapp.issupersign" label="是否绑定设备">
            <el-tooltip placement="top">
              <div slot="content">
                <span v-if="makeTokenInfo.bind_status"> 开启绑定设备</span>
                <span v-else> 关闭绑定设备</span>
              </div>
              <el-switch
                  v-model="makeTokenInfo.bind_status"
                  :active-value="true"
                  :inactive-value="false"
                  active-color="#13ce66"
                  inactive-color="#ff4949">
              </el-switch>
            </el-tooltip>
            <el-tag style="margin-left: 5px">绑定设备之后，二次自动进行设备授权下载应用</el-tag>
          </el-form-item>
        </el-form>
        <span slot="footer">
            <el-button @click="cancelDownloadToken">取消</el-button>
            <el-button @click="makeDownloadToken">生成</el-button>
        </span>

      </el-dialog>

      <el-input
          v-model="dpwdsearch"
          :placeholder="dpwdtitle"
          clearable
          style="width: 30%;margin-right: 30px;margin-bottom: 10px"/>

      <el-button icon="el-icon-search" type="primary" @click="handleSearch(1)">
        搜索
      </el-button>

      <div style="float: right;width: 400px;text-align: right">
        <el-button style="margin:0 10px 5px" @click="makeTokenVisible=true">
          生成下载授权码
        </el-button>
        <el-button plain style="margin: 0 10px 5px" type="warning" @click="cleanToken('all')">清空所有授权码</el-button>
        <el-button plain style="margin: 5px 10px 5px" type="warning" @click="cleanToken('invalid')">清理无效授权码</el-button>
        <el-button plain style="margin: 5px 10px 5px" type="warning" @click="cleanToken('some')">清理选中授权码</el-button>

      </div>

      <el-table
          v-loading="loading"
          :data="app_download_token_list"
          border
          stripe
          style="width: 100%"
          @selection-change="tokenHandleSelectionChange">
        <el-table-column
            align="center"
            type="selection"
            width="55">
        </el-table-column>
        <el-table-column
            align="center"
            label="授权码"
            prop="token"
        >
          <template slot-scope="scope">
            <el-tooltip content="点击复制">
              <el-link v-clipboard:copy="format_copy_text(scope.row.token)" v-clipboard:success="copy_success"
                       :underline="false">
                {{ scope.row.token }}
              </el-link>
            </el-tooltip>
          </template>
        </el-table-column>

        <el-table-column
            :formatter="tokenformatter"
            align="center"
            label="生成日期"
            prop="create_time"
            width="160">
        </el-table-column>
        <el-table-column
            align="center"
            label="使用次数"
            prop="used_count"
            width="100"
        >
          <template slot-scope="scope">
            <span v-if="scope.row.max_limit_count === 0">不限次数</span>
            <span v-else>{{ scope.row.used_count }}</span>
          </template>
        </el-table-column>
        <el-table-column
            align="center"
            label="最大可用次数"
            prop="max_limit_count"
            width="130">
          <template slot-scope="scope">
            <span v-if="scope.row.max_limit_count === 0">不限次数</span>
            <span v-else>{{ scope.row.max_limit_count }}</span>
          </template>
        </el-table-column>
        <div v-if="currentapp.type===1 && currentapp.issupersign">
          <el-table-column
              align="center"
              label="绑定设备"
              prop="bind_status"
              width="60">
            <template slot-scope="scope">
              <el-tag v-if="scope.row.bind_status">是</el-tag>
              <el-tag v-else type="info">否</el-tag>
            </template>
          </el-table-column>
          <el-table-column
              align="center"
              label="设备ID"
              prop="bind_udid">
          </el-table-column>
        </div>
        <el-table-column
            align="center"
            fixed="right"
            label="操作"
            width="120">
          <template slot-scope="scope">
            <div>
              <el-tooltip content="重置使用次数" placement="top">
                <el-button
                    size="mini"
                    @click="resetDownloadUsed(scope.row)">重置
                </el-button>
              </el-tooltip>
            </div>
          </template>
        </el-table-column>

      </el-table>
      <div style="margin-top: 20px">
        <el-pagination
            :current-page.sync="pagination.currentPage"
            :page-size="pagination.pagesize"
            :page-sizes="[10, 20, 50, 100]"
            :total="pagination.total"
            layout="total,sizes, prev, pager, next"
            @size-change="tokenHandleSizeChange"
            @current-change="tokenHandleCurrentChange">
        </el-pagination>
      </div>
      <span slot="footer">
            <el-button @click="closeDownloadTokenInfo">关闭</el-button>
            </span>

    </el-dialog>

    <el-form label-width="80px">
      <el-form-item label="下载授权码" label-width="200px">
        <el-tooltip placement="top">
          <div slot="content">
            {{ passwordtip.msg }}<br>
            <div v-if="passwordtip.val === 'on'">
              <el-link :underline="false" icon="el-icon-edit" @click="handleSearch(1)">查看配置下载授权码</el-link>
            </div>
          </div>
          <el-switch
              v-model="passwordtip.val"
              active-color="#13ce66"
              active-value="on"
              inactive-color="#ff4949"
              inactive-value="off"
              @change="showpasswordevent">
          </el-switch>

        </el-tooltip>
        <el-popover
            placement="top"
            trigger="hover">
          <el-link :underline="false" icon="el-icon-edit" @click="handleSearch(1)">查看配置下载授权码</el-link>
          <el-link slot="reference" :underline="false" style="margin-left: 20px">设置授权码之后，用户需要输入授权码才可以下载该应用</el-link>
        </el-popover>

      </el-form-item>

      <el-form-item label="下载页显示" label-width="200px">

        <el-tooltip :content="downtip.msg" placement="top">
          <el-switch
              v-model="downtip.val"
              active-color="#13ce66"
              active-value="on"
              inactive-color="#ff4949"
              inactive-value="off"
              @change="showdownloadevent">
          </el-switch>
        </el-tooltip>
        <el-link :underline="false" style="margin-left: 20px">默认开启，关闭之后用户无法通过短连接访问下载该应用</el-link>

      </el-form-item>
      <el-form-item label="应用专属域名" label-width="200px">

        <el-input :placeholder="defualt_dtitle" :value="currentapp.domain_name"
                  clearable prefix-icon="el-icon-download"
                  style="width: 60%;margin-right: 10px"/>
        <el-button @click="bind_domain_sure=true">设置域名</el-button>
      </el-form-item>

      <el-form-item label="微信内访问简易模式" label-width="200px">

        <el-tooltip :content="wxeasytypetip.msg" placement="top">
          <el-switch
              v-model="wxeasytypetip.val"
              :disabled="wxeasy_disable"
              active-color="#13ce66"
              active-value="on"
              inactive-color="#ff4949"
              inactive-value="off"
              @change="wxeasytypeevent">
          </el-switch>
        </el-tooltip>
        <el-link :underline="false" style="margin-left: 20px">默认开启，可以最大限度避免微信内举报封停，如果绑定域名，可以关闭</el-link>
      </el-form-item>
      <el-form-item label="微信内访问跳转第三方平台" label-width="200px">

        <el-tooltip :content="wxredirecttip.msg" placement="top">
          <el-switch
              v-model="wxredirecttip.val"
              active-color="#13ce66"
              active-value="on"
              inactive-color="#ff4949"
              inactive-value="off"
              @change="wxredirectevent">
          </el-switch>
        </el-tooltip>
        <el-link :underline="false" style="margin-left: 20px">默认开启，如果配置第三方平台，在微信内访问直接跳转</el-link>

      </el-form-item>


    </el-form>
  </div>
</template>

<script>
import {appDownloadToken, apputils,} from "@/restful"
import {deepCopy} from "@/utils";
import BindDomain from "@/components/base/BindDomain";
import {format_time} from "@/utils/base/utils";

export default {
  name: "FirAppInfossecurity",
  components: {BindDomain},
  data() {
    return {
      currentapp: {},
      orgcurrentapp: {},
      downtip: {'msg': ''},
      passwordtip: {'msg': ''},
      wxeasytypetip: {'msg': ''},
      wxredirecttip: {'msg': ''},
      passwordflag: false,
      showdownloadflag: false,
      wxeasytypeflag: false,
      wxredirectflag: false,
      wxeasy_disable: false,
      defualt_dtitle: '专属下载页域名',
      bind_domain_sure: false,
      download_password_sure: false,
      app_download_token_list: [],
      loading: false,
      makeTokenVisible: false,
      tokendisable: false,
      pagination: {"currentPage": 1, "total": 0, "pagesize": 10},
      dpwdsearch: '',
      dpwdtitle: '输入下载授权码',
      makeTokenInfo: {token: '', token_length: 6, token_number: 20, token_max_used_number: 0, bind_status: false},
      multipleSelection: []

    }
  },
  methods: {
    format_copy_text(token) {
      return this.currentapp.preview_url + "/" + this.currentapp.short + "?password=" + token
    },
    copy_success() {
      this.$message.success('复制剪切板成功');
    },
    cleanToken(act) {
      appDownloadToken(data => {
        this.loading = false
        if (data.code === 1000) {
          this.$message.success("操作成功")
          this.handleSearch(1)
        } else {
          this.$message.error("操作失败了 " + data.msg)
        }
      }, {
        methods: 'PUT',
        app_id: this.currentapp.app_id,
        data: {'act': act, 'tokens': this.format_token(this.multipleSelection)}
      })
    },
    format_token(token_info_list) {
      let format_token_list = []
      for (let token_info of token_info_list) {
        format_token_list.push(token_info.token)
      }
      return format_token_list
    },
    tokenHandleSelectionChange(val) {
      this.multipleSelection = val;
    },
    cancelDownloadToken() {
      this.makeTokenInfo = {token: '', token_length: 6, token_number: 20, token_max_used_number: 0, bind_status: false}
      this.makeTokenVisible = false
    },
    resetDownloadUsed(info) {
      appDownloadToken(data => {
        this.loading = false
        if (data.code === 1000) {
          this.$message.success("重置成功")
          this.showDownloadBase()
        } else {
          this.$message.error("操作失败了 " + data.msg)
        }
      }, {
        methods: 'PUT', app_id: this.currentapp.app_id, data: {'token': info.token}
      })
    },
    makeDownloadToken() {
      appDownloadToken(data => {
        this.loading = false
        if (data.code === 1000) {
          this.cancelDownloadToken()
          this.$message.success("下载授权码生成成功")
          this.showDownloadBase()
        } else {
          this.$message.error("操作失败了 " + data.msg)
        }
      }, {
        methods: 'POST', app_id: this.currentapp.app_id, data: this.makeTokenInfo
      })
    },
    handleSearch(val) {
      this.pagination.currentPage = val;
      this.showDownloadBase()
    },
    showDownloadBase() {
      this.showDownloadToken({
        "size": this.pagination.pagesize,
        "page": this.pagination.currentPage,
        "dpwdsearch": this.dpwdsearch.replace(/^\s+|\s+$/g, "")
      })
    },
    showDownloadToken(data) {
      this.loading = true
      appDownloadToken(data => {
        this.loading = false
        if (data.code === 1000) {
          this.download_password_sure = true;
          this.app_download_token_list = data.data
          this.pagination.total = data.count
        } else {
          this.$message.error("获取失败了 " + data.msg)
        }
      }, {
        methods: 'GET', app_id: this.currentapp.app_id, data: data
      })
    },
    closeDownloadTokenInfo() {
      this.download_password_sure = false;
    },
    tokenHandleSizeChange(val) {
      this.pagination.pagesize = val;
      this.pagination.currentPage = 1;
      this.showDownloadBase();
    },
    tokenHandleCurrentChange(val) {
      this.pagination.currentPage = val;
      this.showDownloadBase();
    },

    // eslint-disable-next-line no-unused-vars
    tokenformatter(row, column) {
      return format_time(row.create_time)
    },
    set_default_flag() {
      this.passwordflag = false;
      this.showdownloadflag = false;
      this.wxeasytypeflag = false;
      this.wxredirectflag = false;
    },
    save_app_domain() {
      this.saveappinfo({
        "domain_name": this.currentapp.domain_name,
      });
    },
    saveappinfo(data) {
      apputils(data => {
        if (data.code === 1000) {
          this.$message.success('数据更新成功');
        } else {
          this.$message.error('操作失败,' + data.msg);
          this.$store.dispatch('doucurrentapp', this.orgcurrentapp);
        }
      }, {
        "methods": "PUT",
        "app_id": this.currentapp.app_id,
        "data": data
      });
    },
    setbuttondefaltpass(currentapp) {
      if (currentapp.need_password === false) {
        this.passwordtip.val = 'off';
        this.showpasswordevent("off");
      } else {
        this.passwordtip.val = 'on';
        this.showpasswordevent("on");
      }
      this.passwordflag = true;
    },
    setbuttondefaltshow(currentapp) {
      if (currentapp.isshow === true) {
        this.showdownloadevent("on");
        this.downtip.val = 'on';
      } else {
        this.showdownloadevent("off");
        this.downtip.val = 'off';
      }
      this.showdownloadflag = true;
    },
    setxeasytypeshow(currentapp) {
      if (currentapp.wxeasytype === true) {
        this.wxeasytypeevent("on");
        this.wxeasytypetip.val = 'on';
      } else {
        this.wxeasytypeevent("off");
        this.wxeasytypetip.val = 'off';
      }
      this.wxeasytypeflag = true;

      this.wxeasy_disable = !this.$store.state.userinfo.domain_name && !this.currentapp.domain_name;
    },
    setwxredirectshow(currentapp) {
      if (currentapp.wxredirect === true) {
        this.wxredirectevent("on");
        this.wxredirecttip.val = 'on';
      } else {
        this.wxredirectevent("off");
        this.wxredirecttip.val = 'off';
      }
      this.wxredirectflag = true;
    },
    setbuttondefault(currentapp) {
      this.setbuttondefaltpass(currentapp);
      this.setbuttondefaltshow(currentapp);
      this.setxeasytypeshow(currentapp);
      this.setwxredirectshow(currentapp);
    },
    showdownloadevent(newval) {
      if (newval === "on") {
        if (this.showdownloadflag) {
          this.saveappinfo({
            "isshow": 1,
          });
          this.currentapp.isshow = 1;
        }
        this.downtip.msg = '下载页对所有人可见';
      } else {
        if (this.showdownloadflag) {
          this.saveappinfo({
            "isshow": 0,
          });
          this.currentapp.isshow = 0;
        }
        this.downtip.msg = '下载页不可见'
      }
    },
    showpasswordevent(newval) {
      if (newval === "on") {
        if (this.passwordflag) {
          this.saveappinfo({
            "need_password": 1,
          });
          this.currentapp.need_password = 1;
        }
        this.passwordtip.msg = '已经开启授权码下载功能'

      } else {
        if (this.passwordflag) {
          this.saveappinfo({
            "need_password": 0,
          });
          this.currentapp.need_password = 0;
        }
        this.passwordtip.msg = '未开启授权码下载功能'
      }
    },

    wxeasytypeevent(newval) {
      if (newval === "on") {
        if (this.wxeasytypeflag) {
          this.saveappinfo({
            "wxeasytype": 1,
          });
          this.currentapp.wxeasytype = 1;
        }
        this.wxeasytypetip.msg = '已经开启微信内访问简易模式';
      } else {
        if (this.wxeasytypeflag) {
          this.saveappinfo({
            "wxeasytype": 0,
          });
          this.currentapp.wxeasytype = 0;
        }
        this.wxeasytypetip.msg = '关闭'
      }
    },

    wxredirectevent(newval) {
      if (newval === "on") {
        if (this.wxredirectflag) {
          this.saveappinfo({
            "wxredirect": 1,
          });
          this.currentapp.wxredirect = 1;
        }
        this.wxredirecttip.msg = '已经开启微信内自动跳转第三方平台';
      } else {
        if (this.wxredirectflag) {
          this.saveappinfo({
            "wxredirect": 0,
          });
          this.currentapp.wxredirect = 0;
        }
        this.wxredirecttip.msg = '关闭'
      }
    },

    appinit() {
      this.currentapp = this.$store.state.currentapp;
      this.set_default_flag();
      this.orgcurrentapp = deepCopy(this.currentapp);
      this.setbuttondefault(this.currentapp);
      if (this.currentapp.type === 1 && this.currentapp.issupersign) {
        this.dpwdtitle = '输入下载授权码或者设备udid'
      } else {
        this.dpwdtitle = '输入下载授权码'
      }
    }
  },
  mounted() {
    this.$store.dispatch('doappInfoIndex', [[31, 31], [31, 31]]);
    if (!this.currentapp.app_id) {
      this.appinit();
    }
  },
  watch: {
    '$store.state.currentapp': function () {
      this.appinit();
    },
    'makeTokenInfo.token': function () {
      this.tokendisable = !!(this.makeTokenInfo.token && this.makeTokenInfo.token.length > 0);
    },
    'makeTokenInfo.bind_status': function () {
      if (this.makeTokenInfo.bind_status) {
        this.makeTokenInfo.token_max_used_number = 1;
      }
    }
  }, computed: {}
}
</script>

<style scoped>

</style>
