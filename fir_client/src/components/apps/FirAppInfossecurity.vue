<template>
  <div style="margin-top: 20px;width: 66%;margin-left: 8%">
    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :visible.sync="bind_domain_sure"
        title="绑定应用专属下载页域名"
        width="666px">
      <bind-domain v-if="bind_domain_sure" :app_id="this.currentapp.app_id" :domain_type="2"
                   transitionName="bind-app-domain"/>
    </el-dialog>
    <el-form label-width="80px">
      <el-form-item label="访问密码" label-width="200px">

        <el-tooltip placement="top">
          <div slot="content">
            {{ passwordtip.msg }}<br>
            <div v-if="passwordtip.val === 'on'">
              <el-link :underline="false" icon="el-icon-edit" @click="setaccesspassword">修改</el-link>
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
        <el-link :underline="false" style="margin-left: 20px">设置密码之后，用户需要输入密码才可以下载该应用</el-link>

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
import {apputils,} from "@/restful"
import {deepCopy} from "@/utils";
import BindDomain from "@/components/base/BindDomain";

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
    }
  },
  methods: {
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
      if (currentapp.password === '') {
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
    passwordswitch(state) {
      this.passwordflag = false;
      this.showpasswordevent(state);
      this.passwordtip.val = state;
      this.passwordflag = true;
    },
    setaccesspassword() {
      this.$prompt('', '请设置访问密码', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        closeOnClickModal: false,
        inputValue: `${this.currentapp.password}`,
      }).then(({value}) => {
        value = value.replace(/\s+/g, "");
        if (this.currentapp.password === value) {
          if (value === '') {
            this.$message({
              type: 'success',
              message: '访问密码未变'
            });
            this.passwordflag = false;
            this.setbuttondefaltpass(this.currentapp);
            return
          } else {
            return
          }
        }
        this.saveappinfo({
          "password": value,
        });
        if (value === '') {
          this.passwordswitch("off");
          this.$message({
            type: 'success',
            message: '设置成功，取消密码访问'
          });
        } else {
          this.passwordtip.msg = '访问密码:' + value;
          this.$message({
            type: 'success',
            message: '设置成功，访问密码是: ' + value
          });
        }
        this.currentapp.password = value;
        this.$store.dispatch('doucurrentapp', this.currentapp)
      }).catch(() => {
        if (this.currentapp.password === '') {
          this.passwordswitch("off")
        }
      });
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
          this.setaccesspassword()
        } else {
          this.passwordtip.msg = '访问密码:' + this.currentapp.password;
        }
      } else {
        if (this.passwordflag) {
          this.saveappinfo({
            "password": '',
          });
        }
        this.currentapp.password = '';
        this.$store.dispatch('doucurrentapp', this.currentapp);
        this.passwordtip.msg = '无访问密码'
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
      if (!this.currentapp.domain_name || this.currentapp.domain_name.length < 3) {
        if (this.$store.state.userinfo.domain_name && this.$store.state.userinfo.domain_name.length > 3) {
          this.defualt_dtitle = this.$store.state.userinfo.domain_name;
        }
      }
      this.setbuttondefault(this.currentapp);
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
  }, computed: {}
}
</script>

<style scoped>

</style>
