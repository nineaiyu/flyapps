<template>
  <div v-if="(certification || certification === 0) && !cert_edit_flag">
    <el-form style="max-width: 400px">
      <el-form-item>
        <el-row>
          <el-col :span="24">
            <el-link v-if="certification.status === 1" :underline="false" style="font-size: x-large"
                     type="success">已经认证
            </el-link>
            <el-link v-else-if="certification.status === 0" :underline="false" style="font-size: x-large"
                     type="primary">审核中
            </el-link>
            <el-link v-else-if="certification.status === 2" :underline="false" style="font-size: x-large"
                     type="danger"
            >审核失败
            </el-link>
            <el-link v-else :underline="false" style="font-size: x-large" type="info">待认证</el-link>
          </el-col>
        </el-row>
      </el-form-item>

      <el-form-item label="真实姓名">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-link :underline="false">{{ certification.name }}</el-link>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="身份证号">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-link :underline="false">{{ certification.card }}</el-link>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item v-if="certification.mobile" label="手机号码">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-link :underline="false">{{ certification.mobile }}</el-link>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="联系地址">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-link :underline="false">{{ certification.addr }}</el-link>
          </el-col>
        </el-row>
      </el-form-item>

      <el-form-item v-if="certification.status === 2" label="审核信息" style="width: 700px">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-link :underline="false" type="danger">{{ certification.msg }}</el-link>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item v-if="certification.status === 2">
        <el-row>
          <el-col :span="24">
            <el-button type="primary" @click="recommit">重新提交审核</el-button>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item v-if="certification_status === -1">
        <el-row>
          <el-col :span="24">
            <el-button type="primary" @click="goauth">开始认证</el-button>
          </el-col>
        </el-row>
      </el-form-item>
    </el-form>
  </div>
  <div v-else>
    <el-form ref="form" :model="form">
      <el-form-item label="真实姓名">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-input v-model="form.name" :autofocus="true" clearable
                      placeholder="请输入真实姓名" prefix-icon="el-icon-user"/>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="身份证号">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-input v-model="form.card" clearable placeholder="请输入身份证号"
                      prefix-icon="el-icon-s-order"/>
          </el-col>
        </el-row>
      </el-form-item>

      <el-form-item label="居住地址">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-input v-model="form.addr" clearable placeholder="请输入现居住地址"
                      prefix-icon="el-icon-house"/>
          </el-col>
        </el-row>
      </el-form-item>


      <el-form-item v-if="change_type.sms" label="手机号码">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-input ref="phone" v-model="form.mobile" clearable
                      maxlength="11" placeholder="请输入手机号码" prefix-icon="el-icon-mobile"/>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item v-if="captcha.captcha_image" label="图片验证码">
        <el-row :gutter="11">
          <el-col :span="12">
            <el-input v-model="form.verify_code" clearable maxlength="6" placeholder="请输入图片验证码"/>
          </el-col>
          <el-col :span="6">
            <el-image
                :src="captcha.captcha_image"
                fit="contain"
                style="border-radius:4px;cursor:pointer;height: 40px" @click="get_auth_code">
            </el-image>
          </el-col>
        </el-row>
      </el-form-item>

      <el-form-item v-if="change_type.sms" label="手机验证码">
        <el-row :gutter="11">
          <el-col :span="12">
            <el-input v-model="form.auth_key" clearable maxlength="6"
                      placeholder="请输入您收到的验证码" prefix-icon="el-icon-mobile"/>
          </el-col>
          <el-col :span="6">
            <el-button plain
                       style="border-radius:4px;cursor:pointer;height: 40px;background-color: #ecf5ff;color: #dd6161"
                       type="info"
                       @click="getsmsemailcode('sms',form.mobile)">
              获取验证码
            </el-button>
          </el-col>

        </el-row>
      </el-form-item>

      <el-form-item>
        <el-row style="margin-left: 88px">
          <el-col :span="13">
            <div id="captcha" ref="captcha"></div>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="身份证号">
        <el-row :gutter="36" style="height: 40px">
          <el-col :span="19">
            <div class="appdownload">
              <el-upload
                  :before-upload="upload_one"
                  accept=".png , .jpg , .jpeg"
                  action="#"
                  drag>

                <el-tooltip v-if="user_certification.one" placement="top">
                  <div slot="content">上传身份证<i style="color: #2abb9d!important;">国徽面</i>照片</div>
                  <img :src="user_certification.one"
                       alt="国徽面照片" class="avatar">
                </el-tooltip>
                <i v-else class="avatar-uploader-icon" style="text-align: center">
                  上传身份证<i style="color: #2abb9d!important;">国徽面</i>照片
                </i>
              </el-upload>
            </div>

            <div class="appdownload">
              <el-upload
                  :before-upload="upload_two"
                  accept=".png , .jpg , .jpeg"
                  action="#"
                  drag>

                <el-tooltip v-if="user_certification.two" placement="top">
                  <div slot="content">上传身份证<i style="color: #2abb9d!important;">人像面</i>照片</div>
                  <img :src="user_certification.two"
                       alt="人像面照片" class="avatar">
                </el-tooltip>
                <i v-else class="avatar-uploader-icon" style="text-align: center">
                  上传身份证<i style="color: #2abb9d!important;">人像面</i>照片
                </i>
              </el-upload>
            </div>

            <div class="appdownload">
              <el-upload
                  :before-upload="upload_three"
                  accept=".png , .jpg , .jpeg"
                  action="#"
                  drag>
                <el-tooltip v-if="user_certification.three" placement="top">
                  <div slot="content">上传<i style="color: #2abb9d!important;">手持身份证</i>照片</div>
                  <img :src="user_certification.three"
                       alt="手持身份证照片" class="avatar">
                </el-tooltip>
                <i v-else class="avatar-uploader-icon" style="text-align: center">
                  上传<i style="color: #2abb9d!important;">手持身份证</i>照片
                </i>
              </el-upload>
            </div>
          </el-col>
        </el-row>
      </el-form-item>


      <el-form-item>
        <el-row>
          <el-col :span="24" style="margin-top: 20px">
            <el-button type="primary" @click="commit">提交</el-button>
          </el-col>
        </el-row>
      </el-form-item>

    </el-form>
  </div>
</template>

<script>
import {changeInfoFun, getAuthcTokenFun, user_certification} from "@/restful";
import {AvatarUploadUtils, geetest, getUserInfoFun} from "@/utils";
import {checkphone} from "@/utils/base/utils";

export default {
  name: "FirUserProfileCertification",
  data() {
    return {
      form: {},
      captcha: {
        captcha_image: '',
        captcha_key: '',
        verify_code: '',
        length: 8,
      },
      change_type: {email: false, sms: false},
      auth_rules: {},
      user_certification: {'one': '', 'two': '', 'three': ''},
      certification: {},
      certification_status: 0,
      cert_edit_flag: false
    }
  }, methods: {
    goauth() {
      this.cert_edit_flag = true;
      this.get_user_certification({methods: 'GET', data: {act: 'certpiccertinfo'}});
      this.get_auth_code();
    },
    recommit() {
      this.cert_edit_flag = true;
      this.get_user_certification({methods: 'GET', data: {act: 'certpiccertinfo'}});
      this.get_auth_code();
    },
    commit() {
      for (let v of Object.keys(this.form)) {
        if (this.form[v].length < 2) {
          this.$message.error("填写错误，请检查");
          return false
        }
      }
      let reg = /(^\d{15}$)|(^\d{18}$)|(^\d{17}(\d|X|x)$)/;
      if (reg.test(this.form.card) === false) {
        this.$message.error("身份证输入不合法");
        return false;
      }
      if (this.change_type.sms) {
        let checkp = checkphone(this.form.mobile);
        if (!checkp) {
          this.$message.error("手机号输入不合法");
          return false;
        }
      }
      delete this.form['email'];
      this.get_user_certification({methods: 'POST', data: this.form})
    },
    get_user_certification(params) {
      user_certification(res => {
        if (res.code === 1000) {
          if (params.methods === 'POST') {
            this.$message.success("信息提交成功，正在审核中");
            this.cert_edit_flag = false;
            this.certification_status = 0;
            getUserInfoFun(this);
            this.get_user_certification({methods: 'GET', data: {act: 'usercert'}});
          }
          if (res.data.usercert) {
            this.certification = res.data.usercert;
          } else {
            const ft = ['one', 'two', 'three'];
            if (res.data.certification && res.data.certification.length > 0) {
              for (let v of res.data.certification) {
                this.user_certification[ft[v.type - 1]] = v.certification_url;
              }
            }
            if (res.data.user_certification) {
              this.form = res.data.user_certification;
            }
          }

        } else {
          this.$message.error(res.msg)
        }
      }, params)
    },

    getsmsemailcode(act, target) {
      let picode = {
        "verify_code": this.form.verify_code,
        "captcha_key": this.captcha.captcha_key,
      };
      if (this.captcha.captcha_image) {
        if (!this.form.verify_code) {
          this.$message.error("图片验证码输入有误");
          return;
        }
        let captcha_flag = this.form.verify_code.length === this.captcha.length;
        if (this.captcha.captcha_key === '' || !this.captcha.captcha_key) {
          captcha_flag = true
        }
        if (!captcha_flag) {
          this.$message.error("图片验证码输入有误");
          return
        }
      }

      let checkp = checkphone(this.form.mobile);
      if (!checkp) {
        this.$message.error("手机号输入有误");
        return
      }

      let params = {'act': act, 'target': target, 'ext': picode, 'user_id': target, 'ftype': 'certification'};
      if (this.auth_rules.geetest) {
        geetest(this, this.form.mobile, params, (n_params) => {
          this.get_phone_code(n_params);
        })
      } else {
        this.get_phone_code(params)
      }

    },

    get_phone_code(params) {
      getAuthcTokenFun(data => {
        if (data.code === 1000) {
          let msg = '您正在进行身份认证，验证码已经发送您手机';
          this.$notify({
            title: '验证码',
            message: msg,
            type: 'success'
          });
          this.form.auth_token = data.data.auth_token;
        } else {
          this.$message.error(data.msg)
        }

      }, {"methods": 'POST', 'data': params})
    },

    get_auth_code() {
      if (this.form.verify_code) {
        this.form.verify_code = '';
      }
      changeInfoFun(data => {
        if (data.code === 1000) {
          this.change_type = data.data.change_type;
          this.auth_rules = data.data.auth_rules;
          this.captcha = this.auth_rules.captcha
          if (this.captcha.captcha_key) {
            this.form.captcha_key = this.captcha.captcha_key;
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
    upload_one(file) {
      return this.beforeAvatarUpload(file, 1)
    },
    upload_two(file) {
      return this.beforeAvatarUpload(file, 2)
    },
    upload_three(file) {
      return this.beforeAvatarUpload(file, 3)
    },
    beforeAvatarUpload(file, ptype) {
      return AvatarUploadUtils(this, file, {
        'app_id': this.$store.state.userinfo.uid,
        'upload_key': file.name,
        'ftype': 'certification',
        'ext': {'ptype': ptype}
        // eslint-disable-next-line no-unused-vars
      }, res => {
        this.get_user_certification({methods: 'GET', data: {act: 'certpic'}});
      });

    },
    init() {
      if (this.$store.state.userinfo.certification || this.$store.state.userinfo.certification === 0) {
        this.certification_status = this.$store.state.userinfo.certification;
        if (this.certification_status !== -1) {
          this.get_user_certification({methods: 'GET', data: {act: 'usercert'}});
        }
      }

    },
  }, mounted() {
    this.$store.dispatch('douserInfoIndex', 2);
    this.init();
  }, watch: {
    '$store.state.userinfo': function () {
      this.init();
    }
  }
}
</script>

<style scoped>
.el-form {
  max-width: 800px;
  margin: 0 auto;
}

.el-form-item .el-button {
  max-width: 260px;
  width: 100%;
  height: 50px;
}

.appdownload /deep/ .el-upload-dragger {
  background: #f1f1f1;
  width: 200px;
  height: 166px;
}

.appdownload /deep/ .el-icon-upload {
  margin-top: 45%;
}

.appdownload {
  float: left;
  width: 200px;
  height: 166px;
  background-color: #c2dcf1;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;
}

.avatar-uploader .el-upload:hover {
  border-color: #409EFF;
}

.avatar-uploader-icon {
  color: #8c939d;
  width: 158px;
  height: 158px;
  line-height: 158px;
  text-align: center;
}

.avatar {
  width: 178px;
  height: 178px;
  display: block;
}
</style>
