<template>
  <div>

    <el-form ref="form" :model="form" label-width="90px">
      <el-form-item label="当前密码">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-input v-model="form.oldpassword" autofocus clearable placeholder="当前密码"
                      prefix-icon="el-icon-unlock" show-password/>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="新密码">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-input v-model="form.newpassword" clearable placeholder="新密码"
                      prefix-icon="el-icon-lock" show-password/>
          </el-col>
        </el-row>
      </el-form-item>

      <el-form-item label="确认密码">
        <el-row :gutter="36">
          <el-col :span="18">
            <el-input v-model="form.surepassword" clearable placeholder="确认密码"
                      prefix-icon="el-icon-lock" show-password/>
          </el-col>
        </el-row>
      </el-form-item>

      <el-form-item>
        <el-row :gutter="36">
          <el-col :span="20">
            <el-button type="primary" @click="updatepasswd">更新密码</el-button>
          </el-col>
        </el-row>
      </el-form-item>

    </el-form>


  </div>
</template>

<script>
import {userinfos} from "@/restful";

export default {
  name: "FirUserProfileChangePwd",
  data() {
    return {
      form: {
        oldpassword: '',
        newpassword: '',
        surepassword: ''
      },
    }
  }, methods: {
    updatepasswd() {
      if (this.form.newpassword === this.form.surepassword) {

        userinfos(data => {
          if (data.code === 1000) {
            this.userinfo = data.data;
            this.$message.success('密码修改成功');
          } else {
            this.$message.error('密码修改失败,' + data.msg);
          }
        }, {
          "methods": 'PUT', 'data': {
            "oldpassword": this.form.oldpassword,
            "surepassword": this.form.surepassword
          }
        });
      } else {
        this.$message.error('密码不一致');
      }
    }
  }, mounted() {
    this.$store.dispatch('douserInfoIndex', 1);
  }
}
</script>

<style scoped>
.el-form {
  max-width: 500px;
  margin: 0 auto;
}

.el-button {
  margin-top: 20px;
  max-width: 260px;
  width: 100%;
  height: 50px;
}

</style>
