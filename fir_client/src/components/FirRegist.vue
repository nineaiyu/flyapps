<template>
  <el-container>
    <div style="margin: 10px 0 10px 0 ;position:absolute;right:20px;top:auto;">
      <el-button icon="el-icon-arrow-left" round @click="$router.go(-1)"/>
      <el-button icon="el-icon-s-home" round @click="$router.push({name:'FirIndex'})"/>

    </div>
    <el-header>

      <div>
        <span>注册</span>
      </div>

    </el-header>
    <el-main v-if="allow_r">

      <el-form ref="form" :model="form">

        <el-form-item v-if="allow_ways.code">
          <el-input v-model="form.icode" clearable placeholder="邀请码必填" prefix-icon="el-icon-postcard"
          />
        </el-form-item>

        <el-form-item>
          <el-input v-model="form.email" :placeholder="rutitle" autofocus clearable
                    prefix-icon="el-icon-user"/>
        </el-form-item>

        <el-form-item v-if="captcha.captcha_image" style="height: 40px">
          <el-row style="height: 40px">
            <el-col :span="16">
              <el-input v-model="form.authcode" clearable maxlength="6" placeholder="请输入图片验证码"/>
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
          <el-row>
            <el-col :span="16">
              <el-input v-model="form.seicode" clearable
                        placeholder="验证码" prefix-icon="el-icon-mobile"/>
            </el-col>
            <el-col :span="8">
              <el-button plain style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px" type="info"
                         @click="getphonecode">获取验证码
              </el-button>
            </el-col>
          </el-row>
        </el-form-item>


        <el-form-item>
          <el-input v-model="form.password" clearable placeholder="密码"
                    prefix-icon="el-icon-lock" show-password/>
        </el-form-item>
        <el-form-item>
          <el-input v-model="form.password2" clearable placeholder="确认密码"
                    prefix-icon="el-icon-lock" show-password @keyup.enter.native="onRegist"/>
        </el-form-item>

        <el-form-item>
          <div id="captcha" ref="captcha"></div>
        </el-form-item>

        <el-form-item>
          <el-button :disabled="register_disable" type="danger" @click="onRegist">注册</el-button>
        </el-form-item>

        <el-form-item>
          <el-button plain type="primary" @click="onLogin">我是老用户,要登录</el-button>
        </el-form-item>
      </el-form>


    </el-main>


  </el-container>
</template>

<script>
import {getAuthTokenFun, registerFun} from "@/restful";
import {checkEmail, checkphone, geetest} from "@/utils";

export default {
  name: "FirRegist",
  data() {
    return {
      form: {
        email: '',
        password: '',
        password2: '',
        authcode: '',
        srccode: '',
        seicode: '',
        authtoken: '',
        icode: '',
        auth_token: '',

      },
      captcha: {"captcha_image": '', "captcha_key": '', "length": 8},
      allow_r: false,
      allow_ways: {},
      rutitle: '',
      register_disable: false,
    }
  },
  methods: {
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
      registerFun(data => {
        if (data.code === 1000) {
          let jdata = data.data;
          if (jdata.enable) {
            this.allow_r = true;
            this.allow_ways = jdata.register_type;
            this.form.authcode = '';
            this.set_rtitle();
            this.captcha = data.data;
          } else {
            this.allow_r = false;
            this.$message({
              message: "该服务器不允许注册",
              type: 'error'
            });
          }
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
    do_get_auth_token(params) {
      getAuthTokenFun(data => {
        if (data.code === 1000) {
          this.$notify({
            title: '验证码',
            message: '您正在进行注册，验证码已经发送您',
            type: 'success'
          });
          this.form.auth_token = data.data.auth_token;
        } else {
          this.$message({
            message: data.msg,
            type: 'error'
          });
        }
      }, {"methods": 'POST', 'data': params})
    },
    getphonecode() {
      let act = 'up';
      if (!this.docheck()) {
        return
      }
      if (checkphone(this.form.email)) {
        act = 'sms'
      }
      if (checkEmail(this.form.email)) {
        act = 'email'
      }
      let authcode = this.form.authcode;
      let captcha_flag = authcode.length === this.captcha.length;
      if (this.captcha.captcha_key === '' || !this.captcha.captcha_key) {
        captcha_flag = true
      }
      if (captcha_flag) {
        let picode = {
          "authcode": authcode,
          "captcha_key": this.captcha.captcha_key,
          "icode": this.form.icode,
        };
        let params = {'act': act, 'target': this.form.email, 'ext': picode};
        if (this.captcha.geetest) {
          geetest(this, this.form.email, params, (n_params) => {
            this.do_get_auth_token(n_params);
          })
        } else {
          this.do_get_auth_token(params);
        }
      } else {
        this.$message({
          message: '图片验证码有误',
          type: 'warning'
        });
      }

    },
    docheck() {
      let checkp = checkphone(this.form.email);
      let checke = checkEmail(this.form.email);

      if (this.allow_ways.sms && this.allow_ways.email) {
        if (!checke && !checkp) {
          this.$message({
            message: '请输入正确的邮箱地址或手机号码',
            type: 'warning'
          });
          return 0
        }
      } else {
        if (this.allow_ways.email) {
          if (!checke) {
            this.$message({
              message: '请输入正确的邮箱地址',
              type: 'warning'
            });
            return 0
          }
        }
        if (this.allow_ways.sms) {
          if (!checkp) {
            this.$message({
              message: '请输入正确的手机号码',
              type: 'warning'
            });
            return 0
          }
        }
      }
      if (this.allow_ways.code && this.form.icode.length === 0) {
        this.$message({
          message: '请输入邀请码',
          type: 'warning'
        });
        return 0
      }
      return 1
    },
    do_register(params) {
      registerFun(data => {
        if (data.code === 1000) {
          this.$message({
            message: '注册成功',
            type: 'success'
          });
          this.$router.push({name: 'FirLogin'})
        } else {
          this.$message({
            message: data.msg,
            type: 'error'
          });
          this.get_auth_code();
        }
      }, {
        "methods": "POST",
        "data": params
      });
      this.register_disable = false;
    },
    onRegist() {
      let email = this.form.email;
      let password = this.form.password;
      let password2 = this.form.password2;
      if (!this.docheck()) {
        return
      }
      let authcode = this.form.authcode;
      let captcha_flag = authcode.length === this.captcha.length;
      if (this.captcha.captcha_key === '' || !this.captcha.captcha_key) {
        captcha_flag = true
      }
      if (captcha_flag) {
        if (password === password2 && password.length >= 6) {
          let params = {
            "username": email,
            "password": password,
            "password2": password2,
            "auth_token": this.form.auth_token,
            "auth_key": this.form.seicode
          };
          this.register_disable = true;
          if (this.captcha.geetest) {
            geetest(this, this.form.email, params, (n_params) => {
              this.do_register(n_params);
            })
          } else {
            this.do_register(params);
          }

        } else {
          this.$message({
            message: '密码不一致或者密码长度小于6',
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
    onLogin() {
      this.$router.push({name: 'FirLogin'})
    },
  }
  ,
  created() {
  }, mounted() {
    this.get_auth_code();
  }
}
</script>

<style scoped>

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
