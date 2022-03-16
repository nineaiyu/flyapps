<template>
  <el-container>
    <div style="margin: 10px 0 10px 0 ;position:absolute;right:20px;top:auto;">
      <el-button icon="el-icon-arrow-left" round @click="$router.go(-1)"/>
      <el-button icon="el-icon-s-home" round @click="$router.push({name:'FirIndex'})"/>

    </div>
    <el-header>

      <div>
        <span>登录</span>
      </div>

    </el-header>
    <el-main>

      <el-form ref="form" :model="form">

        <el-tabs v-model="activeName">
          <el-tab-pane v-if="allow_ways.up" label="用户名登录" name="username">
            <el-form-item>
              <el-input v-model="form.email" autofocus clearable placeholder="用户名"
                        prefix-icon="el-icon-user"/>
            </el-form-item>
          </el-tab-pane>
          <el-tab-pane v-if="allow_ways.sms || allow_ways.email" :label="rutitle+'登录'" name="smsemail">
            <el-form-item>
              <el-input v-model="form.email" :placeholder="rutitle" autofocus clearable
                        prefix-icon="el-icon-user"/>
            </el-form-item>
          </el-tab-pane>

        </el-tabs>

        <el-form-item v-if="is_captcha">
          <el-input v-model="form.password" clearable placeholder="密码"
                    prefix-icon="el-icon-lock"
                    show-password @keyup.enter.native="onSubmit"/>
        </el-form-item>
        <el-form-item v-else>
          <el-input v-model="form.password" clearable placeholder="密码"
                    prefix-icon="el-icon-lock" show-password/>
        </el-form-item>
        <el-form-item v-if="captcha.captcha_image" style="height: 40px">
          <el-row style="height: 40px">
            <el-col :span="16">
              <el-input v-model="form.verify_code" clearable maxlength="6"
                        placeholder="请输入验证码" @keyup.enter.native="onSubmit"/>
            </el-col>
            <el-col :span="8">
              <el-image
                  :src="captcha.captcha_image"
                  fit="contain"
                  style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px" @click="get_auth_code">
              </el-image>
            </el-col>
          </el-row>
        </el-form-item>

        <el-form-item>
          <div id="captcha" ref="captcha"></div>
        </el-form-item>

        <el-form-item>
          <el-button :disabled="login_disable" type="danger" @click="onSubmit">登录</el-button>
        </el-form-item>

        <el-form-item v-if="register_enable">
          <el-button plain type="primary" @click="onRegister">注册</el-button>
        </el-form-item>
        <el-form-item>
          <el-link :underline="false" plain @click="$router.push({name: 'FirResetPwd'})">忘记密码</el-link>
        </el-form-item>

        <div v-if="allow_ways.third && JSON.stringify(allow_ways.third).indexOf('true')!==-1" class="other-way">
          <hr>
          <span class="info">或使用以下账户登录</span>

          <el-popover
              v-if="allow_ways.third && allow_ways.third.wxp"
              v-model="wx_visible"
              placement="top"
              title="微信扫码关注公众号登录"
              trigger="manual">
            <div>
              <el-image :src="wx_login_qr_url" style="width: 176px;height: 166px"/>
            </div>
            <el-button slot="reference"
                       size="small" style="color: #1fc939;border: 1px solid rgba(31,201,57,.5); width: 110px"
                       @click="wxLogin">微信
            </el-button>
          </el-popover>

        </div>
      </el-form>


    </el-main>


  </el-container>

</template>

<script>
import {loginFun, set_auth_token, wxLoginFun} from "@/restful";
import {geetest} from "@/utils";
import {checkEmail, checkphone, getRandomStr} from "@/utils/base/utils";

export default {
  name: "FirLogin",
  data() {
    return {
      form: {
        email: '',
        password: '',
        verify_code: ''
      },
      captcha: {"captcha_image": '', "captcha_key": '', "length": 8},
      auth_rules: {},
      activeName: 'username',
      allow_ways: {'third': {}},
      rutitle: '',
      rctitle: '',
      register_enable: false,
      login_disable: false,
      wx_login_qr_url: '',
      wx_visible: false,
      loop_flag: false,
      unique_key: ''
    }
  },
  methods: {

    set_cookie_and_token(data) {
      this.$cookies.remove("auth_token");
      this.$cookies.set("token", data['token'], 3600 * 24 * 30);
      this.$cookies.set("username", data.userinfo.username, 3600 * 24 * 30);
      this.$cookies.set("first_name", data.userinfo.first_name, 3600 * 24 * 30);
      this.$store.dispatch("doUserinfo", data.userinfo);
      set_auth_token();
      this.$router.push({name: 'FirApps'})
    },
    loop_get_wx_info(wx_login_ticket, c_count = 1, unique_key = getRandomStr()) {
      if (wx_login_ticket && wx_login_ticket.length < 3) {
        this.$message.error("获取登陆码失败，请稍后再试");
        return
      }
      if (!this.wx_visible) {
        return;
      }
      wxLoginFun(data => {
        c_count += 1;
        if (c_count > 30) {
          return;
        }
        if (data.code === 1000) {
          this.set_cookie_and_token(data);
        } else if (data.code === 1005) {
          this.wx_visible = false;
          this.loop_flag = false;
          this.$message({
            message: data.msg,
            type: 'error',
            duration: 30000
          });
        } else if (data.code === 1004) {
          this.loop_flag = false;
        } else if (data.code === 1006) {
          return this.loop_get_wx_info(wx_login_ticket, c_count, unique_key)
        }
      }, {
        "methods": "POST",
        data: {"ticket": wx_login_ticket, "unique_key": unique_key}
      })
      // }, 3000)

    },
    wxLogin() {
      this.wx_visible = !this.wx_visible;
      this.wx_login_qr_url = '';
      if (this.wx_visible) {
        wxLoginFun(data => {
          if (data.code === 1000) {
            this.wx_login_qr_url = data.data.qr;
            this.loop_flag = true;
            this.loop_get_wx_info(data.data.ticket);
          } else {
            this.$message.error(data.msg);
            this.wx_visible = false;
            this.loop_flag = false;
          }
        }, {
          "methods": "GET", "data": {"unique_key": this.unique_key}
        })
      } else {
        this.loop_flag = false;
      }
    },
    is_captcha() {
      let captcha_flag = this.form.verify_code.length === this.captcha.length;
      if (this.captcha.captcha_key === '' || !this.captcha.captcha_key) {
        captcha_flag = true
      }
      return captcha_flag
    },
    onSubmit() {
      let email = this.form.email;
      let password = this.form.password;
      let verify_code = this.form.verify_code;
      let login_type = 'up';
      let captcha_flag = this.form.verify_code.length === this.captcha.length;
      if (this.captcha.captcha_key === '' || !this.captcha.captcha_key) {
        captcha_flag = true
      }
      if (captcha_flag) {

        if (this.activeName === "username") {
          if (email.length < 6) {
            this.$message({
              message: '用户名至少6位',
              type: 'error'
            });
            return
          }

        } else if (this.activeName === "smsemail") {
          let checkp = checkphone(this.form.email);
          let checke = checkEmail(this.form.email);
          if (!checkp && !checke) {
            this.$message({
              message: '邮箱或者手机号输入有误',
              type: 'error'
            });
            return
          }
          if (checkp) {
            login_type = 'sms';
          } else if (checke) {
            login_type = 'email';
          }
        } else {
          this.$message({
            message: '未知登录方式',
            type: 'error'
          });
          return
        }
        if (password.length > 6) {
          let params = {
            "username": email,
            "password": password,
            "verify_code": verify_code,
            "captcha_key": this.captcha.captcha_key,
            "login_type": login_type,
          };
          this.login_disable = true;
          if (this.auth_rules.geetest) {
            geetest(this, this.form.email, params, (n_params) => {
              this.do_login(n_params);
            })
          } else {
            this.do_login(params)
          }
        } else {
          this.$message({
            message: '密码长度过短',
            type: 'warning'
          });
        }
      } else {
        this.$message({
          message: '验证码有误',
          type: 'warning'
        });
      }
    },
    do_login(params) {
      loginFun(data => {
        if (data.code === 1000) {
          this.$message({
            message: '登录成功',
            type: 'success'
          });
          this.set_cookie_and_token(data);
        } else {
          this.$message({
            message: data.msg,
            type: 'error'
          });
          this.get_auth_code();
        }
        this.login_disable = false;
      }, {
        "methods": "POST",
        "data": params
      });
    },
    onRegister() {
      this.$router.push({name: 'FirRegist'})
    },
    set_activename() {
      if (this.allow_ways.up) {
        this.activeName = 'username';
      } else {
        this.activeName = 'smsemail';
      }
    },
    set_rtitle() {
      this.rutitle = '';
      if (this.allow_ways.sms) {
        this.rutitle = this.rutitle + '手机号 ';
      }
      if (this.allow_ways.email) {
        this.rutitle = this.rutitle + '邮箱 ';
      }

      this.rutitle = this.rutitle.trim().replace(' ', '或');
    },
    get_auth_code() {
      loginFun(data => {
        if (data.code === 1000) {
          this.auth_rules = data.data.auth_rules
          this.captcha = this.auth_rules.captcha;
          this.allow_ways = data.data.login_type;
          this.register_enable = data.data.register_enable;
          this.form.verify_code = '';
          this.set_rtitle();
          this.set_activename();
        } else {
          this.$message({
            message: data.msg,
            type: 'error'
          });
        }
      }, {
        "methods": "GET",
        "data": {}
      });
    },
  },
  mounted() {
    this.get_auth_code();
    this.unique_key = getRandomStr();
  }, created() {
  }
}
</script>

<style scoped>

.other-way {
  position: relative;
  text-align: center;
}

.other-way hr {
  height: 1px;
  margin: 30px 0;
  border: 0;
  background-color: #e4e7ed;
}

.other-way span.info {
  font-size: 12px;
  line-height: 1;
  position: absolute;
  top: -6px;
  left: 50%;
  padding: 0 10px;
  transform: translate(-50%, 0);
  color: #9ba3af;
}

.el-container {
  margin: 10px auto;
  width: 1266px;
}

.el-header {
  margin-top: 13%;
}

.el-form {
  max-width: 360px;
  margin: 0 auto;
}

.el-form-item .el-button {
  max-width: 360px;
  /*padding: 16px 20px;*/
  width: 100%;
  position: relative;
  height: 50px;

}

.el-header {
  text-align: center;
  overflow: hidden;
  margin-bottom: 50px
}


.el-header div span {
  font-size: 24px;
  display: inline-block;
  vertical-align: middle;
  padding: 8px 40px
}

.el-header div:before, .el-header div:after {
  content: ' ';
  display: inline-block;
  vertical-align: middle;
  width: 50%;
  height: 1px;
  background-color: #babfc3;
  margin: 0 0 0 -50%
}

.el-header div {
  text-align: center
}

.el-header div:after {
  margin: 0 -50% 0 0
}
</style>
