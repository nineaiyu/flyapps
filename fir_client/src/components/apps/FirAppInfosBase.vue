<template>
  <div class="main">
    <div class="page-app app-info">
      <div class="banner">
        <div class="middle-wrapper">
          <div @click="defaulttimeline">
            <img ref="icon_url" :src="icon_url" alt="" class="appicon" style="width:100px; height:100px">
          </div>
          <div class="badges">
            <el-tooltip content="复制到剪切板" placement="top">
                             <span v-clipboard:copy="appinfos.preview_url"
                                   v-clipboard:success="copy_success"
                                   class="bundleid short"
                             >&nbsp;{{ appinfos.preview_url }}</span>
            </el-tooltip>

            <el-popover
                placement="right"
                width="288">
              <div style="text-align: center; margin: 0">
                <vue-qr ref="qr"
                        :correctLevel="qrinfo.correctLevel" :logoCornerRadius="qrinfo.logoCornerRadius"
                        :logoScale="qrinfo.logoScale"
                        :logoSrc="icon_url"
                        :margin="qrinfo.margin" :size="266"
                        :text="appinfos.preview_url">
                </vue-qr>
                <el-button size="small" type="primary" @click="save_qr()">保存本地</el-button>
              </div>

              <span slot="reference" class="short ng-scope">下载码</span>
            </el-popover>


            <span>{{ master_release.release_type |getapptype }}</span>
            <el-tooltip content="下载量" placement="top">
              <span><i class="el-icon-cloudy"/><b class="short">{{ appinfos.count_hits }}</b></span>
            </el-tooltip>
            <span class="bundleid ng-binding">BundleID<b class="ng-binding">
                          <el-tooltip content="复制到剪切板" placement="top">
                             <span v-clipboard:copy="appinfos.bundle_id"
                                   v-clipboard:success="copy_success"
                                   class="bundleid short"
                             >&nbsp;{{ appinfos.bundle_id }}</span>
                        </el-tooltip>
                        </b></span>
            <span class="version ng-scope">{{ master_release.minimum_os_version }}&nbsp; 或者高版本</span>
            <span v-if="appinfos.issupersign" class="short ng-scope">超级签</span>

          </div>
          <div class="actions">
            <el-button v-if="appinfos.status!==1" type="danger">该应用被封禁,请联系管理员</el-button>
            <el-button v-else class="download" icon="el-icon-view" @click="appDownload(appinfos)">
              预览
            </el-button>
          </div>

          <div class="tabs-container">
            <el-row :gutter="1">
              <el-col :span="3">
                <a ref="baseinfo" class="" @click="baseinfo"><i class="el-icon-document"/>基本信息</a>
              </el-col>

              <el-col :span="3">
                <a ref="security" class="" @click="security"><i class="el-icon-set-up"/>应用管理</a>
              </el-col>

              <el-col :span="3">
                <a ref="combo" class="" @click="combo"><i class="el-icon-copy-document"
                                                          style="transform:rotateX(180deg);"/>应用合并</a>
              </el-col>

              <el-col v-if="appinfos.type===1  || appinfos.issupersign "
                      :span="3">
                <a ref="supersign" class="" @click="supersign"><i
                    class="el-icon-ship"/>超级签名</a>
              </el-col>

              <el-col v-if="(appinfos.type===1 && master_release.release_type ===1) || appinfos.issupersign "
                      :span="3">
                <a ref="devices" class="" @click="devices"><i class="el-icon-mobile-phone"/>设备列表</a>
              </el-col>

            </el-row>
          </div>
        </div>
      </div>

      <div>
        <div class="block" style="margin-top: -46px;color: #d5f9f9">
          <el-slider
              v-model="$store.state.appInfoIndex[0]"
              :max="100"
              :show-tooltip="false"
              range>
          </el-slider>
        </div>
        <el-container style="padding-top: 20px;max-width: 96%">
          <router-view/>
        </el-container>
      </div>
    </div>
  </div>

</template>

<script>
import {apputils} from "@/restful";
import VueQr from 'vue-qr';
import {getUserInfoFun} from "@/utils";

export default {
  name: "FirAppInfosBase",
  components: {
    VueQr
  },
  data() {
    return {
      qrinfo: {
        logoScale: 0.3,
        logoCornerRadius: 12,
        correctLevel: 3,
        margin: 20
      },
      icon_url: "",
      appinfos: {status: 1, preview_url: ''},
      master_release: {},
      allapp: [],
      activity: {
        editing: false
      },
    }
  },
  methods: {
    copy_success() {
      this.$message.success('复制剪切板成功');
    },
    save_qr() {
      let dtype = "I";
      if (this.master_release.release_type === 0) {
        dtype = "A";
      }
      let a = document.createElement('a');
      // 下载图名字
      a.download = this.appinfos.name + '_' + dtype + "_下载码";
      //url
      a.href = this.$refs.qr.$el.src;
      //合成函数，执行下载
      a.dispatchEvent(new MouseEvent('click'))
    },
    setfunactive(item, index) {
      for (let key in this.$refs) {
        if (key === "qr") continue;
        if (key === item) {
          if (this.$refs[key]) {
            this.$refs[key].classList.add('active');
            this.$store.dispatch('doappInfoIndex', [[index, index], [index, index]]);
          }
        } else {
          if (this.$refs[key]) {
            this.$refs[key].classList.remove('active');
          }
        }
      }
    },
    appDownload(appinfo) {
      window.open(appinfo.preview_url, '_blank', '');
    },
    defaulttimeline() {
      this.setfunactive('timeline', 5);
      this.$router.push({name: 'FirAppInfostimeline'});
    },
    baseinfo() {
      this.setfunactive('baseinfo', 18);
      this.$router.push({name: 'FirAppInfosbaseinfo'});
    },
    security() {
      this.setfunactive('security', 31);
      this.$router.push({name: 'FirAppInfossecurity'});

    },
    combo() {
      this.setfunactive('combo', 44);
      this.$router.push({name: 'FirAppInfoscombo'});
    },
    devices() {
      this.setfunactive('devices', 70);
      this.$router.push({name: 'FirAppInfosdevices'});
    },
    supersign() {
      this.setfunactive('supersign', 57);
      this.$router.push({name: 'FirAppInfossupersign'});
    },
    set_icon_url() {
      this.icon_url = this.$store.state.currentapp.master_release.icon_url;
    },
  }, created() {

  }, filters: {
    getapptype: function (type) {
      let ftype = '';
      if (type === 0) {
        ftype = 'Android'
      } else {
        ftype = 'iOS'
      }
      return ftype
    },
  },
  computed: {}, mounted() {
    getUserInfoFun(this);
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
      "app_id": this.$route.params.id
    });
    if (this.$store.state.currentapp.master_release) {
      this.set_icon_url()
    }
  }, watch: {
    '$store.state.currentapp.master_release.icon_url': function () {
      this.set_icon_url()
    },
    '$store.state.currentapp': function () {
      this.appinfos = this.$store.state.currentapp;
    },
  }, destroyed() {
    this.$store.dispatch('doucurrentapp', {});
  }

}
</script>

<style scoped>
.main {
  margin: 40px auto 100px;
  position: relative;
  padding-bottom: 1px;
  color: #9b9b9b;
  -webkit-font-smoothing: antialiased;
  border-radius: 1%;
}

.appicon {
  overflow: hidden;
  margin-left: 10px;
  border-radius: 17.544%;
}

.page-app {
  padding-bottom: 0;
  width: 1166px;
  margin: 10px auto 100px;
}

.page-app .banner {
  padding-top: 60px;
  padding-bottom: 40px;
  border-bottom: 1px solid rgba(208, 208, 208, .5);
  background-color: #ffffff;
  border-radius: 10px;
}

.page-app .banner .actions {
  position: absolute;
  right: 0;
  top: 0;
}

.page-app .banner .actions .download {
  display: block;
  min-width: 150px;
  padding: 10px 20px;
  border-radius: 5px;
  font-size: 14px;
  margin: 0 12px 12px 12px
}


.page-app .banner .actions .download {
  text-align: center;
  text-decoration: none;
  color: #3ab2a7;
  border: 1px solid;
  background-color: transparent
}


.page-app .banner .middle-wrapper {
  position: relative
}


.page-app .badges {
  margin-left: 160px;
  font-size: 12px;
  line-height: initial;
  position: relative;
  margin-top: -100px;
}

.page-app .badges > span {
  position: relative;
  display: inline-block;
  margin-right: 8px;
  padding: 4px 8px;
  border: 1px solid;
  border-radius: 5px
}


.page-app .badges .short {
  color: #6f6ef8
}

.page-app .badges .short:hover {
  cursor: pointer;
}

.page-app .badges b {
  display: inline-block;
  padding-left: 12px;
  height: 100%;
  font-weight: 400
}

.page-app .badges b:before {
  position: absolute;
  top: 0;
  width: 0;
  height: 100%;
  border-left: 1px solid;
  content: ' ';
  margin-left: -6px
}

.page-app .tabs-container {
  margin-top: 40px;
  margin-left: 160px
}

.page-app .tabs-container .el-row {
  margin: 10px auto;
}

.page-app .tabs-container .el-row .el-col {
  margin-right: 30px;
  border-left: 1px solid;
}

.page-app .tabs-container .el-row .el-col a {
  display: block;
  padding-left: 15px;
  color: #599b1a;
  text-decoration: none;
  -webkit-transition: all .5s;
  transition: all .5s
}

.page-app .tabs-container .el-row .el-col a > i {
  display: block;
  margin-bottom: 14px;
  height: 22px;
  font-size: 22px
}

.page-app .tabs-container .el-row .el-col a.active {
  color: #4a4a4a
}

.page-app .tabs-container .el-row .el-col:nth-child(6) {
  display: none
}

.page-app .has-devices .tabs-container .el-row .el-col:nth-child(6) {
  display: inline-block
}


</style>
