<template>


  <div style="margin-top: 20px;width: 72%;margin-left: 8%">
    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :title="appletoapp_title"
        :visible.sync="bind_appletoapp_sure"
        width="1166px">
      <apple-developer-bind-app v-if="bind_appletoapp_sure" :app_id="currentapp.app_id"
                                transitionName="bind_appletoapp_app"/>
    </el-dialog>
    <el-form v-if="currentapp.type === 1 && $store.state.userinfo.supersign_active" label-width="80px">


      <el-form-item label="超级签名"
                    label-width="200px">

        <el-tooltip :content="supersign.msg" placement="top">
          <el-switch
              v-model="supersign.val"
              active-color="#13ce66"
              active-value="on"
              inactive-color="#ff4949"
              inactive-value="off"
              @change="supersignevent">
          </el-switch>
        </el-tooltip>
        <el-button v-if="!currentapp.issupersign && currentapp.count !== 0" plain
                   size="small" style="margin-left: 20px" type="info" @click="clean_app">清理该应用脏数据
        </el-button>
        <!--        <el-link v-else :underline="false" style="margin-left: 20px">超级签名，iOS专用，需要配置好苹果开发者账户，方可开启</el-link>-->
        <el-tooltip content="点击查看所使用开发者信息" placement="top">
          <el-link :disabled="supersign_disable" :underline="false" style="margin-left: 20px;color: #3875cc;"
                   @click="$router.push({name:'FirSuperSignBase',params:{act:'iosdeveloper'},query:{appidseach: currentapp.bundle_id}})">
            使用了 {{ currentapp.developer_used_count }} 开发者
          </el-link>
        </el-tooltip>
      </el-form-item>
      <el-form-item label="自动更新"
                    label-width="200px">

          <el-switch
              :disabled="supersign_disable"
              v-model="currentapp.change_auto_sign"
              active-color="#13ce66"
              :active-value="true"
              inactive-color="#ff4949"
              :inactive-value="false"
              @change="saveappinfo({change_auto_sign:currentapp.change_auto_sign})">
          </el-switch>

        <el-link :underline="false" style="margin-left: 20px">开启自动更新，新包入库或签名相关数据更改，系统将会自动更新签名包</el-link>
      </el-form-item>
      <el-form-item label="专属配置" label-width="200px">
        <el-button :disabled="supersign_disable" @click="bindAppletoapp">配置专属苹果开发账户</el-button>
        <el-link :disabled="supersign_disable" :underline="false" style="margin-left: 20px" @click="bindAppletoapp"> 拥有
          {{ currentapp.private_developer_number }} 个专属苹果开发者，使用了 {{ currentapp.private_developer_used_number }} 个设备数
        </el-link>
      </el-form-item>
      <el-form-item label="签名限额" label-width="200px">


        <el-tooltip content="本应用签名使用额度，超过该额度，新设备将无法安装本应用。0代表不限额" placement="top">
          <el-input-number v-model="currentapp.supersign_limit_number" :disabled="supersign_disable" :min="0"
                           label="签名限额" style="width: 40%;margin-right: 10px"/>
        </el-tooltip>

        <el-button :disabled="supersign_disable"
                   @click="saveappinfo({supersign_limit_number:currentapp.supersign_limit_number})"
        >保存
        </el-button>
        <el-tooltip content="点击查看使用详情" placement="top">
          <el-link :disabled="supersign_disable" :underline="false" style="margin-left: 20px" type="primary"
                   @click="$router.push({name:'FirSuperSignBase',params:{act:'useddevices'},query:{bundleid: currentapp.bundle_id}})">
            已经使用 <a style="color: #dd6161;font-size: larger">{{ currentapp.supersign_used_number }}</a>
            个设备额度
          </el-link>
        </el-tooltip>
      </el-form-item>


      <el-form-item label="签名类型" label-width="200px">
        <el-select v-model="currentapp.supersign_type" :disabled="supersign_disable"
                   placeholder="特殊签名权限" style="width: 60%;margin-right: 10px">
          <el-option v-for="st in sign_type_list" :key="st.id" :label="st.name"
                     :value="st.id"/>
        </el-select>
        <el-button :disabled="supersign_disable"
                   @click="saveappinfo({supersign_type:currentapp.supersign_type})"
        >保存
        </el-button>
      </el-form-item>


      <el-form-item label="自定义BundleID" label-width="200px">
        <el-tooltip content="新的BundleID可能会导致推送等服务失效，请了解之后进行修改" placement="top">
          <el-input v-model="currentapp.new_bundle_id" :disabled="supersign_disable" :placeholder="defualt_dtitle"
                    clearable prefix-icon="el-icon-s-data"
                    style="width: 60%;margin-right: 10px"/>
        </el-tooltip>
        <el-button :disabled="supersign_disable" @click="saveappinfo({new_bundle_id:currentapp.new_bundle_id})"
        >保存
        </el-button>
      </el-form-item>

      <el-form-item label="自定义应用名称" label-width="200px">
        <el-input v-model="currentapp.new_bundle_name" :disabled="supersign_disable" :placeholder="defualt_dtitle_name"
                  clearable prefix-icon="el-icon-s-data"
                  style="width: 60%;margin-right: 10px"/>
        <el-button :disabled="supersign_disable"
                   @click="saveappinfo({new_bundle_name:currentapp.new_bundle_name})"
        >保存
        </el-button>
      </el-form-item>

    </el-form>
    <el-link v-else :underline="false" type="warning"> 该用户暂未开通超级签权限,请联系管理员申请开通</el-link>
  </div>


</template>

<script>
import {apputils,} from "@/restful"
import {deepCopy} from "@/utils";
import AppleDeveloperBindApp from "@/components/base/AppleDeveloperBindApp";

export default {
  name: "FirAppInfossupersign",
  components: {AppleDeveloperBindApp},
  data() {
    return {
      currentapp: {},
      orgcurrentapp: {},
      supersign: {'msg': ''},
      showsupersignflag: false,
      supersign_disable: true,
      sign_type_list: [],
      sign_type: 0,
      defualt_dtitle: '',
      defualt_dtitle_name: '',
      bind_appletoapp_sure: false,
      appletoapp_title: ''
    }
  },
  methods: {
    bindAppletoapp() {
      this.appletoapp_title = "专属签名开发者信息 " + this.currentapp.name + "-" + this.currentapp.bundle_id;
      this.bind_appletoapp_sure = true;
    },
    set_default_flag() {
      this.showsupersignflag = false;
    },
    clean_app() {
      this.saveappinfo({"clean": true});
      this.currentapp.count = 0;
    },
    saveappinfo(data) {
      const loading = this.$loading({
        lock: true,
        text: '执行中,请耐心等待...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      });
      apputils(data => {
        if (data.code === 1000) {
          this.$message.success('数据更新成功');
        } else {
          this.$message.error('操作失败,' + data.msg);
          this.$store.dispatch('doucurrentapp', this.orgcurrentapp);
        }
        loading.close();
      }, {
        "methods": "PUT",
        "app_id": this.currentapp.app_id,
        "data": data
      });
    },
    setbuttonsignshow(currentapp) {
      if (currentapp.issupersign === true) {
        this.supersignevent("on");
        this.supersign.val = 'on';
      } else {
        this.supersignevent("off");
        this.supersign.val = 'off';
      }
      this.showsupersignflag = true;
    },

    setbuttondefault(currentapp) {
      this.setbuttonsignshow(currentapp);
    },

    supersignevent(newval) {
      if (newval === "on") {
        if (this.showsupersignflag) {
          this.saveappinfo({
            "issupersign": 1,
          });
          this.currentapp.issupersign = 1;
        }
        this.supersign.msg = '已经开启超级签名';
        this.supersign_disable = false
      } else {
        if (this.showsupersignflag) {
          this.saveappinfo({
            "issupersign": 0,
          });
          this.currentapp.issupersign = 0;
        }
        this.supersign.msg = '关闭';
        this.supersign_disable = true
      }
    },
    set_default_ms(currentapp) {
      this.sign_type_list = currentapp.sign_type_choice;
      if (this.currentapp.new_bundle_id && currentapp.new_bundle_id.length > 5) {
        this.defualt_dtitle = currentapp.new_bundle_id
      } else {
        this.defualt_dtitle = currentapp.bundle_id
      }
      if (this.currentapp.new_bundle_name && currentapp.new_bundle_name.length > 0) {
        this.defualt_dtitle_name = currentapp.new_bundle_name
      } else {
        this.defualt_dtitle_name = currentapp.name
      }
    },
    appinit() {
      this.currentapp = this.$store.state.currentapp;
      this.set_default_flag();
      this.orgcurrentapp = deepCopy(this.currentapp);
      this.set_default_ms(this.currentapp);
      this.setbuttondefault(this.currentapp);
    }
  },
  mounted() {
    this.$store.dispatch('doappInfoIndex', [[57, 57], [57, 57]]);
    if (!this.currentapp.app_id) {
      this.appinit();
    }
  },
  watch: {
    '$store.state.currentapp': function () {
      this.appinit();
    },
    'currentapp.new_bundle_id': function () {
      if (!this.currentapp.new_bundle_id || this.currentapp.new_bundle_id.length === 0) {
        this.defualt_dtitle = this.currentapp.bundle_id
      }
    },
    'currentapp.new_bundle_name': function () {
      if (!this.currentapp.new_bundle_name || this.currentapp.new_bundle_name.length === 0) {
        this.defualt_dtitle_name = this.currentapp.name
      }
    }
  }, computed: {}
}
</script>

<style scoped>

</style>
