<template>
  <div style="background-color: rgba(162,193,230,0.18);">
    <el-container class="navbar-wrapper">
      <el-dialog
          :visible.sync="dialogVisible"
          center
          title="API  Token"
          width="30%"
      >
        <span>可用于调用公开 API，可用于登录 fly-cli，请勿泄露您的 token</span>
        <el-main>
          <el-tooltip content="点击复制到剪贴板">
            <el-link v-if="token" v-clipboard:copy="token" v-clipboard:success="copy_success" :underline="false"
                     type="primary">{{ token }}
            </el-link>
          </el-tooltip>
        </el-main>
        <span slot="footer" class="dialog-footer">
                <el-button type="primary" @click="maketoken">重新生成</el-button>
             </span>
      </el-dialog>
      <el-row :gutter="20">
        <el-col :span="14" style="padding-top: 36px;margin-left: 60px">
          <el-breadcrumb separator-class="el-icon-arrow-right" style="height: 60px;font-size: 20px">
            <el-breadcrumb-item :to="{ name:'FirIndex' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item :to="{ name:'FirApps'}">我的应用</el-breadcrumb-item>

            <el-breadcrumb-item v-if="this.route_info.label" :to="{ name:route_info.name}">{{
                this.route_info.label
              }}
            </el-breadcrumb-item>

            <el-breadcrumb-item v-if="$store.state.currentapp.name"
                                :to="{name: 'FirAppInfostimeline', params: {id: $store.state.currentapp.app_id}}">
              {{ $store.state.currentapp.name }}
            </el-breadcrumb-item>

          </el-breadcrumb>
        </el-col>
        <el-col :push="2" :span="2" style="padding-top: 16px;">
          <div class="block">
            <el-avatar :size="66" :src="$store.state.userinfo.head_img"></el-avatar>
          </div>
        </el-col>
        <el-col :push="2" :span="4" style="padding-top: 16px">
          <el-dropdown style="padding-top: 12px;" @command="handleCommand">
            <el-button plain round type="primary">
              {{ $store.state.userinfo.first_name }}<i class="el-icon-arrow-down el-icon--right"></i>
            </el-button>
            <el-dropdown-menu slot="dropdown">
              <el-dropdown-item command="userinfo">个人资料</el-dropdown-item>
              <el-dropdown-item command="apitoken">API token</el-dropdown-item>
              <el-dropdown-item command="setdomian">设置域名</el-dropdown-item>
              <el-dropdown-item v-if="$store.state.userinfo.role>1" command="setadvert">宣传广告
              </el-dropdown-item>
              <el-dropdown-item v-if="$store.state.userinfo.storage_active" command="storage">存储管理
              </el-dropdown-item>
              <el-dropdown-item v-if="$store.state.userinfo.supersign_active" command="supersign">超级签名
              </el-dropdown-item>
              <el-dropdown-item command="myorder">订单信息</el-dropdown-item>
              <el-dropdown-item command="contact">联系我们</el-dropdown-item>
              <el-dropdown-item command="qrcode">下载码</el-dropdown-item>
              <el-dropdown-item command="exit">退出</el-dropdown-item>

            </el-dropdown-menu>
          </el-dropdown>

        </el-col>

      </el-row>


    </el-container>
  </div>
</template>

<script>
import {apitoken, logout} from '@/restful'

export default {
  name: "FirHeader",
  data() {
    return {
      current_user: {},
      appName: '',
      token: '',
      dialogVisible: false,
      route_info: {'name': '', 'label': ''},
    }
  }, methods: {
    copy_success() {
      this.$message.success('复制剪切板成功');
    },
    maketoken() {
      this.$confirm('该操作将导致老秘钥失效，确认重新生成新的密钥么?', '警告', {
        type: 'warning'
      })
          // eslint-disable-next-line no-unused-vars
          .then(res => {
            apitoken(data => {
              if (data.code === 1000) {
                this.token = data.data.token;
                this.$message({
                  type: 'success',
                  message: '重新生成成功!'
                });
              } else {
                this.$message.error("失败了 " + data.msg)
              }
            }, {methods: 'PUT', token: this.token});
          })
          .catch(err => {
            this.$message.error(err)
          });
    },
    handleCommand(command) {
      if (command === 'userinfo') {
        this.$router.push({name: 'FirUserProfileInfo'})
      } else if (command === 'storage') {
        this.$router.push({name: 'FirUserStorage', params: {act: "change"}})
      } else if (command === 'supersign') {
        this.$store.dispatch('doucurrentapp', {});
        this.$router.push({"name": 'FirSuperSignBase', params: {act: "iosdeveloper"}})
      } else if (command === 'apitoken') {
        apitoken(data => {
          if (data.code === 1000) {
            this.token = data.data.token;
            this.dialogVisible = true;
          } else {
            this.dialogVisible = false;
            this.$message.error("获取失败了 " + data.msg)
          }
        }, {methods: 'GET', token: this.token});

      } else if (command === 'setdomian') {
        this.$router.push({"name": 'FirUserDomain'})
      } else if (command === 'setadvert') {
        this.$router.push({"name": 'FirUserAdvert'})
      } else if (command === 'myorder') {
        this.$router.push({"name": 'FirUserOrders'})
      } else if (command === 'qrcode') {
        this.$router.push({"name": 'FirUserQrcode'})
      } else if (command === 'contact') {
        this.$router.push({"name": 'FirContact'})
      } else if (command === 'exit') {
        logout(data => {
          if (data.code === 1000) {
            this.$message.success("退出成功");
            this.$cookies.remove("token");
            this.$cookies.remove("auth_token");
            this.$cookies.remove("username");
            this.$cookies.remove("first_name");
            this.$store.dispatch('doucurrentapp', {});
            this.$store.dispatch('doUserinfo', {});
            this.$router.push({name: 'FirLogin'});
          } else {
            this.$message.error("退出失败")
          }
        }, {})
      }
    },
    init_route_name() {
      if (this.$route.meta) {
        this.route_info.label = this.$route.meta.label;
        this.route_info.name = this.$route.name;
      }
    },

  }, created() {
    this.appName = this.$route.params.id
  }, watch: {
    $route: function () {
      this.appName = this.$route.params.id;
      this.init_route_name();
    }
  }, mounted() {
    this.init_route_name();
  }
}
</script>

<style scoped>

.el-container, .el-row {
  margin: 10px auto;
  width: 1166px;
}

.navbar-wrapper {
  font-size: 0;
  border-radius: 10px;
}

.el-dropdown {
  vertical-align: top;
}

.el-dropdown + .el-dropdown {
  margin-left: 15px;
}

.el-icon-arrow-down {
  font-size: 12px;
}


</style>
