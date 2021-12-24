<template>
  <el-main>

    <el-row style="margin-bottom: 5px">
      <el-col :span="3">
        <el-radio-group v-model="searchfromtype">
          <el-radio-button icon="el-icon-mobile-phone" label="android"><i
              class="iconfont icon-android2"/>
          </el-radio-button>
          <el-radio-button label="ios"><i class="iconfont icon-ios"/>
          </el-radio-button>
        </el-radio-group>

      </el-col>
      <el-col :span="8">
        <el-row>
          <el-col :span="18">
            <el-input
                v-model="keysearch"
                clearable
                placeholder="请输入名称搜索"
                @click="searchapps"
                @keyup.enter.native="searchapps">
            </el-input>
          </el-col>
          <el-col :span="6">

            <el-button icon="el-icon-search" @click="searchFun">
            </el-button>
          </el-col>
        </el-row>
      </el-col>

      <el-col :offset="5" :span="8">
        <el-row>
          <el-col :span="8">
            <el-checkbox v-model="checkAll" :indeterminate="isIndeterminate" style="margin-top: 10px"
                         @change="handleCheckAllChange">当前页全选【{{ checkedQrcodes.length }}】
            </el-checkbox>
          </el-col>
          <el-col :span="13" style="float: right">
            <el-button @click="savemany">批量保存选中下载码到本地</el-button>
          </el-col>
        </el-row>
      </el-col>
    </el-row>

    <el-row id="showqr">
      <el-checkbox-group v-model="checkedQrcodes" @change="handlecheckedQrcodesChange">
        <el-col v-for="appinfo in qrcode_info_list" :key="appinfo.app_id" :span="5" style="margin-left: 40px">
          <el-checkbox :label="appinfo.app_id" border style="height: 320px">
            <el-card :body-style="{textAlign:'center',padding:'8px'}" shadow="hover">
              <vue-qr :callback="qrback"
                      :correctLevel="qrinfo.correctLevel" :logoCornerRadius="qrinfo.logoCornerRadius"
                      :logoScale="qrinfo.logoScale"
                      :logoSrc="appinfo.master_release.icon_url"
                      :margin="qrinfo.margin" :qid="appinfo.app_id"
                      :size="200"
                      :text="short_url(appinfo)">
              </vue-qr>
              <div style="margin: 5px 0 5px">
                <i v-if="appinfo.type === 1" class=" type-icon iconfont icon-ios"/>
                <i v-if="appinfo.type === 0" class="type-icon iconfont icon-android2"/>
                &nbsp;
                <span>{{ appinfo.name }}</span>
                <div class="bottom clearfix">
                  <el-popover placement="top" trigger="hover" >
                       <span v-clipboard:copy="short_url(appinfo)"
                             v-clipboard:success="copy_success"
                       >{{ short_url(appinfo) }}</span>
                    <div slot="reference" class="name-wrapper">
                      <el-button plain size="small" type="primary" @click="go_download(appinfo)">预览</el-button>
                      <el-button plain size="small" type="primary" @click="save_qr(appinfo)">保存本地</el-button>
                    </div>
                  </el-popover>
                </div>
              </div>
            </el-card>
          </el-checkbox>
        </el-col>
      </el-checkbox-group>
    </el-row>

  </el-main>
</template>

<script>

import {qrcodeinfo} from "@/restful";
import {getScrollHeight, getScrollTop, getUserInfoFun, getWindowHeight} from '@/utils'
import VueQr from 'vue-qr';

export default {
  name: "FirUserQrcode",
  components: {
    VueQr
  },
  data() {
    return {
      has_next: false,
      firstloadflag: true,
      query: {'page': 1, size: 20},
      searchflag: false,
      keysearch: '',
      searchfromtype: '',
      loadingobj: null,
      checkAll: false,
      checkedQrcodes: [],
      isIndeterminate: false,
      allQrcodeAppid: [],
      qrcode_info_list: [],
      orgqrcode_info_list: [],
      qrcode_img_info: {},
      qrinfo: {
        logoScale: 0.3,
        logoCornerRadius: 12,
        correctLevel: 3,
        margin: 10
      },
    }
  },
  methods: {
    copy_success() {
      this.$message.success('复制剪切板成功');
    },
    auto_load() {
      if (getScrollTop() + getWindowHeight() >= getScrollHeight()) {
        if (this.has_next) {      //先判断下一页是否有数据
          if (this.autoloadflag) {
            this.autoloadflag = false;
            if (this.qrcode_info_list.length === 0) {
              this.query.page = 1;
            } else {
              this.query.page += 1;
            }
            if (this.searchfromtype !== '') {
              this.query.type = this.searchfromtype;
            }
            this.UserQrcodeFun(this.query);
          }

        }
      }
    },
    init_value() {
      this.checkAll = false;
      this.checkedQrcodes = [];
      this.isIndeterminate = false;
      this.qrcode_info_list = [];
      this.orgqrcode_info_list = [];
      this.checkedQrcodes = [];
      this.allQrcodeAppid = [];
      this.qrcode_img_info = {};
    },
    searchFun() {
      let keysearch = this.keysearch.replace(/^\s+|\s+$/g, "");
      if (keysearch === '') {
        this.searchflag = false;
        this.init_value();
        this.query.page = 1;
        if (this.searchfromtype) {
          this.UserQrcodeFun({"type": this.searchfromtype});
        } else {
          this.UserQrcodeFun({});
        }
      } else {
        this.searchflag = true
      }
      if (this.searchflag) {
        this.qrcode_info_list = [];
        this.orgqrcode_info_list = [];
        if (this.searchfromtype) {
          this.UserQrcodeFun({"type": this.searchfromtype, 'page': 1, size: 999});
        } else {
          this.UserQrcodeFun({'page': 1, size: 999});
        }
      }
    },
    searchapps() {
      let keysearch = this.keysearch.replace(/^\s+|\s+$/g, "");
      let newqrcode_info_list = [];
      for (let i = 0; i < this.orgqrcode_info_list.length; i++) {
        if (this.orgqrcode_info_list[i].name.search(keysearch) >= 0) {
          newqrcode_info_list.push(this.orgqrcode_info_list[i]);
        }
      }
      if (keysearch === "") {
        this.qrcode_info_list = this.orgqrcode_info_list.slice();
      } else {
        this.qrcode_info_list = newqrcode_info_list.slice();
      }

    },
    get_appinfo_from_appid(app_id) {
      for (let i = 0; i < this.qrcode_info_list.length; i++) {
        if (app_id === this.qrcode_info_list[i].app_id) {
          return this.qrcode_info_list[i];
        }
      }
    },
    savemany() {
      for (let i = 0; i < this.checkedQrcodes.length; i++) {
        this.save_qr(this.get_appinfo_from_appid(this.allQrcodeAppid[i]))
      }
    },
    handleCheckAllChange(val) {
      this.checkedQrcodes = val ? this.allQrcodeAppid : [];
      this.isIndeterminate = false;
    },
    handlecheckedQrcodesChange(value) {
      let checkedCount = value.length;
      this.checkAll = checkedCount === this.allQrcodeAppid.length;
      this.isIndeterminate = checkedCount > 0 && checkedCount < this.allQrcodeAppid.length;
    },
    go_download(appinfo) {
      window.open(this.short_url(appinfo), '_blank', '');
    },
    qrback(dataUrl, id) {
      this.qrcode_img_info[id] = dataUrl;
      this.allQrcodeAppid.push(id);
    },
    short_url(appinfo) {
      return appinfo.preview_url+ '/' + appinfo.short;
    },
    save_qr(appinfo) {
      let dtype = "I";
      if (appinfo.master_release.release_type === 0) {
        dtype = "A";
      }
      let a = document.createElement('a');
      // 下载图名字
      a.download = appinfo.name + '_' + dtype + "_下载码";
      a.href = this.qrcode_img_info[appinfo.app_id];
      //合成函数，执行下载
      a.dispatchEvent(new MouseEvent('click'))
    },
    UserQrcodeFun(params) {
      this.loadingobj = this.$loading({
        lock: true,
        text: '加载中',
        spinner: 'el-icon-loading',
        // background: 'rgba(0, 0, 0, 0.7)'
      });
      qrcodeinfo(data => {
        if (data.code === 1000) {
          if (this.firstloadflag) {
            window.addEventListener('scroll', this.auto_load);
            this.firstloadflag = false
          }
          this.autoloadflag = true;
          this.qrcode_info_list = this.qrcode_info_list.concat(data.data);
          this.has_next = data.has_next;
          this.orgqrcode_info_list = this.qrcode_info_list.slice(); //深拷贝
          this.hdata = data.hdata;
          this.searchapps();

        } else {
          this.$message.error("信息获取失败")
        }
        this.loadingobj.close();
      }, {methods: 'GET', data: params})
    },


  }, mounted() {
    getUserInfoFun(this);
    this.UserQrcodeFun()
  },
  watch: {

    // eslint-disable-next-line no-unused-vars
    keysearch: function (val, oldVal) {
      // this.searchapps()
      let keysearch = this.keysearch.replace(/^\s+|\s+$/g, "");
      if (keysearch === "") {
        this.searchFun()
      }
    },
    // eslint-disable-next-line no-unused-vars
    searchfromtype: function (val, oldVal) {
      this.qrcode_info_list = [];
      this.query.page = 1;
      // this.keysearch='';
      this.searchFun();
      // this.getappsFun({"type": this.searchfromtype});
    },
  }
}
</script>

<style scoped>
.el-main {
  margin: 20px auto 100px;
  width: 1166px;
  position: relative;
  padding-bottom: 1px;
  color: #9b9b9b;
  -webkit-font-smoothing: antialiased;
  border-radius: 1%;
}

.bottom {
  margin-top: 10px;
}

.clearfix:before,
.clearfix:after {
  display: table;
  content: "";
}

.clearfix:after {
  clear: both
}

#showqr /deep/ .el-checkbox__input {
  display: none;
}

</style>
