<template>
  <div style="margin-top: 20px;width: 100%;margin-left: 8%">
    <el-form ref="form" label-width="80px">
      <el-form-item label="应用ID" style="width: 56%">
        <el-row>
          <el-col :span="19">
            <el-input v-model="currentapp.app_id" :disabled="true"/>
          </el-col>
          <el-col :span="4">
            <el-button plain style="margin:0 8px;border-radius:4px;cursor:pointer;height: 40px" type="danger"
                       @click="delApp">删除应用
            </el-button>
          </el-col>
        </el-row>
      </el-form-item>
      <el-form-item label="使用空间" style="width: 56%">
        <el-input v-model="currentapp.storage_used" :disabled="true" :value="currentapp.storage_used"/>
      </el-form-item>
      <el-form-item label="应用名称" style="width: 56%">
        <el-input v-model="currentapp.name"/>
      </el-form-item>

      <el-form-item label="短链接" style="width: 56%">
        <el-input v-model="currentapp.short" maxlength="16" show-word-limit type="text">
          <template slot="prepend">{{ currentapp.preview_url }}/</template>
        </el-input>
      </el-form-item>

      <el-form-item label="应用图标" style="width: 56%">
        <el-upload
            :before-upload="upload_app_icon"
            :show-file-list="false"
            accept=".png , .jpg , .jpeg"
            action="#"
            class="avatar-uploader">
          <img v-if="currentapp.icon_url" :src="currentapp.icon_url"
               alt="" class="avatar">
          <i v-else class="el-icon-plus avatar-uploader-icon"/>
        </el-upload>
      </el-form-item>
      <el-form-item label="应用描述" style="width: 66%">
        <el-input v-model="currentapp.description" :autosize="{ minRows: 8, maxRows: 18}"
                  type="textarea"/>
      </el-form-item>
      <el-form-item>
        <el-row>
          <el-col :span="15">
            <el-button plain size="medium" style="width: 160px;height: 50px;font-size: large;float: right"
                       type="primary"
                       @click="saveappinfo('save')">保存信息
            </el-button>
          </el-col>
        </el-row>
      </el-form-item>
      <el-divider/>
      <el-form-item label="应用截图" style="width: 100%">

        <div class="appdownload">
          <el-tooltip v-for="(screen) in currentapp.screenshots" :key="screen.id" content="点击删除该应用截图"
                      effect="light" placement="top">
            <el-image
                :src="screen.url"
                alt=""
                class="screen-img"
                fit="scale-down" @click="delscreen(screen.id)">
              <div slot="error" class="image-slot" style="text-align: center;margin-top: 80%"
                   @click="delscreen(screen.id)">
                <i class="el-icon-picture-outline"> 加载失败</i>
              </div>
            </el-image>
          </el-tooltip>
          <div v-if="currentapp.screenshots && currentapp.screenshots.length < 5"
               class="screen-img">
            <el-upload
                :before-upload="upload_app_screen"
                accept=".png , .jpg , .jpeg"
                action="#"
                drag>
              <i class="el-icon-upload"/>
            </el-upload>
          </div>

        </div>

      </el-form-item>
    </el-form>

  </div>


</template>

<script>
import {apputils, getapppicurl, releaseapputils} from "@/restful"
import {AvatarUploadUtils} from "@/utils";

export default {
  name: "FirAppInfosbaseinfo",
  data() {
    return {
      currentapp: {},
      imageUrl: "",
      uploadconf: {},
      uploadprocess: 0,
      dialogImageUrl: '',
      dialogVisible: false,
      appinfos: {},
    }
  },
  methods: {
    // eslint-disable-next-line no-unused-vars
    delscreen(screen_id) {
      this.$confirm('确定要删除该应用截图?', '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        releaseapputils(data => {
          if (data.code === 1000) {
            this.$message.success('删除成功');
            this.getappinfo();
          } else if (data.code === 1003) {
            this.$router.push({name: 'FirApps'});
          }
        }, {
          "methods": "DELETE",
          "app_id": this.$route.params.id,
          "release_id": "screen",
          "data": {'screen_id': screen_id}
        })

      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消操作'
        });
      });
    },

    delApp() {
      //发送删除APP的操作
      this.$confirm('确认删除 ' + this.currentapp.name + ' ?')
          // eslint-disable-next-line no-unused-vars
          .then(res => {
            const loadingobj = this.$loading({
              lock: true,
              text: '操作中，请耐心等待',
              spinner: 'el-icon-loading',
              // background: 'rgba(0, 0, 0, 0.7)'
            });
            apputils(data => {
              loadingobj.close();
              if (data.code === 1000) {
                this.$message({
                  message: '删除成功',
                  type: 'success'
                });
                this.$router.push({name: 'FirApps'});
              } else {
                this.$message({
                  message: '删除失败，请联系管理员',
                  type: 'error'
                });
              }
            }, {
              "methods": "DELETE",
              "app_id": this.currentapp.app_id
            });

          })
          .catch(err => {
            this.$message.error(err)
          });
    },
    getappinfo() {
      apputils(data => {
        if (data.code === 1000) {
          this.appinfos = data.data;
          this.master_release = data.data.master_release;
          this.appinfos["icon_url"] = this.master_release.icon_url;
          this.$store.dispatch('doucurrentapp', this.appinfos);
        } else if (data.code === 1003) {
          this.$router.push({name: 'FirApps'});
        } else {
          // eslint-disable-next-line no-console
          console.log("Error");
        }
      }, {
        "methods": "GET",
        "app_id": this.currentapp.app_id
      });
    },
    saveappinfo() {
      apputils(data => {
        if (data.code === 1000) {
          this.$message.success('数据更新成功');
        } else {
          this.$message.error('操作失败,' + data.msg);
        }
      }, {
        "methods": "PUT",
        "app_id": this.currentapp.app_id,
        "data": {
          "description": this.currentapp.description,
          "short": this.currentapp.short,
          "name": this.currentapp.name,
        }
      });
    },
    upload_app_icon(file) {
      return this.beforeAvatarUpload(file, 'app')
    },
    upload_app_screen(file) {
      return this.beforeAvatarUpload(file, 'screen')
    },
    beforeAvatarUpload(file, act) {
      return AvatarUploadUtils(this, file, {
        'app_id': this.currentapp.app_id,
        'upload_key': file.name,
        'ftype': act
        // eslint-disable-next-line no-unused-vars
      }, res => {
        this.getappinfo();
      });
    }
  },
  mounted() {
    this.$store.dispatch('doappInfoIndex', [[18, 18], [18, 18]]);
    if (!this.currentapp.app_id) {
      this.currentapp = this.$store.state.currentapp;
    }
    this.uploadconf = {
      "AuthHeaders": {"Authorization": this.$cookies.get("auth_token")}
    };
  },
  watch: {
    '$store.state.currentapp': function () {
      this.currentapp = this.$store.state.currentapp;
    }
  }, computed: {
    getuppicurl() {
      return getapppicurl(this.currentapp.app_id)
    }
  }
}
</script>

<style scoped>
.appdownload /deep/ .el-upload-dragger {
  background: #f1f1f1;
  width: 155px;
  height: 288px;
}

.appdownload /deep/ .el-icon-upload {
  margin-top: 80%;
}

.avatar-uploader .el-upload {
  border: 1px dashed #d9d9d9;
  border-radius: 6px;
  cursor: pointer;
  position: relative;
  overflow: hidden;

}

.screen-img {
  width: 155px;
  height: 288px;
  margin-right: 20px;
  background-color: #f1f1f1;
  float: left
}

.screen-img:hover {
  background-color: #c2dcf1;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  width: 178px;
  height: 178px;
  line-height: 178px;
  text-align: center;
}

.avatar {
  height: 100px;
  width: 100px;
  border-radius: 10px;
  display: block;
}
</style>
