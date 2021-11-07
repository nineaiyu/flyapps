<template>
  <div class="main">
    <div class="user-info">

      <el-upload
          :before-upload="beforeAvatarUpload"
          :show-file-list="false"
          accept=".png , .jpg , .jpeg"
          action="#"
          class="avatar-uploader">
        <img v-if="imageUrl" :src="imageUrl" class="avatar">
        <i v-else class="el-icon-plus avatar-uploader-icon"></i>
      </el-upload>

      <div class="name">
        <input v-model="userinfo.first_name" maxlength="8" @focusout="update_name">
      </div>

      <div class="user_pro_tabs">

        <el-row :gutter="12" class="row">
          <el-col :offset="3" :span="tspan">
            <div class="col-4">
              <a ref="userinfo" class="" @click="$router.push({name:'FirUserProfileInfo'})">
                        <span>
                            <i class="el-icon-user"></i>
                        </span>
                个人资料
              </a>
            </div>
          </el-col>
          <el-col :span="tspan">
            <div class="col-4">
              <a ref="changepwd" class="" @click="$router.push({name:'FirUserProfileChangePwd'})">
                <span><i class="el-icon-lock"></i></span>
                修改密码
              </a>
            </div>

          </el-col>

          <el-col :span="6">
            <div class="col-4">
              <a ref="storage" class="" @click="$router.push({name:'FirUserProfileCertification'})">
                <span><i class="el-icon-coin"></i></span>
                实名认证
              </a>
            </div>

          </el-col>

        </el-row>

      </div>
      <div style="margin-top: 50px">
        <router-view></router-view>
      </div>

    </div>

  </div>
</template>

<script>
import {getuserpicurl, userinfos} from '@/restful';
import {AvatarUploadUtils} from "@/utils";

export default {
  name: "FirUserProfileBase",
  data() {
    return {
      imageUrl: '',
      userinfo: {},
      uploadconf: {},
      tspan: 6,
    }
  },
  methods: {
    updateUserInfo(datainfo) {
      userinfos(data => {
        if (data.code === 1000) {
          this.userinfo = data.data;
          this.$store.dispatch("doUserinfo", data.data);
          this.$store.dispatch('doucurrentapp', {});
          this.imageUrl = data.data.head_img;
          if (datainfo.data) {
            this.$message.success("更新成功")
          }
        } else {
          this.$message.error("更新失败")
        }
      }, datainfo)
    },
    update_name() {
      this.updateUserInfo({"methods": 'PUT', 'data': {"first_name": this.userinfo.first_name}});
    },
    beforeAvatarUpload(file) {
      return AvatarUploadUtils(this, file, {
        'app_id': this.userinfo.uid,
        'upload_key': file.name,
        'ftype': 'head'
        // eslint-disable-next-line no-unused-vars
      }, res => {
        this.updateUserInfo({"methods": 'GET'});
      });

    },
    setfunactive(item) {
      for (let key in this.$refs) {
        if (key === item) {
          this.$refs[key].classList.add('active');
        } else {
          this.$refs[key].classList.remove('active');
        }
      }
    },
    autoSetInfoIndex() {
      if (this.$store.state.userInfoIndex === 0) {
        this.setfunactive('userinfo');
      } else if (this.$store.state.userInfoIndex === 1) {
        this.setfunactive('changepwd');
      } else if (this.$store.state.userInfoIndex === 2) {
        this.setfunactive('storage');
      }
    }
  }, mounted() {
    this.autoSetInfoIndex();
    this.updateUserInfo({"methods": 'GET'});
  }, watch: {
    '$store.state.userInfoIndex': function () {
      this.autoSetInfoIndex();
    },
  }, filters: {}, computed: {
    getuppicurl() {
      return getuserpicurl()
    }
  }
}
</script>

<style scoped>
.main {
  position: relative;
  padding-bottom: 1px;
  color: #9b9b9b;
  -webkit-font-smoothing: antialiased;
  border-radius: 1%;
}

.user-info {
  position: relative;
  text-align: center;
  margin: 46px auto 100px;
  width: 1166px;
}

.avatar {
  height: 100px;
  width: 100px;
  border-radius: 50%;
  display: block;
}

.name {
  text-align: center;
  padding-bottom: 20px;

}

.name input {
  text-align: center;
  color: #889eff;
  margin: 36px auto 0;
  width: 280px;
  padding: 0;
  border: none;
  background-color: transparent;
  font-size: 30px;
}

.user_pro_tabs a {
  width: 100%;
  font-size: 16px;
  text-align: center;
  display: inline-block;
  line-height: 48px;
  height: 48px;
  border-bottom: 1px solid #BABFC3;
  text-decoration: none;
  color: #BABFC3;

}

.user_pro_tabs a > span {
  margin-right: 16px;
  vertical-align: middle
}

.user_pro_tabs a.active {
  color: #7e5ef8;
  border-bottom-color: #7e5ef8
}


</style>
