<template>
  <transition :name="transitionName">
    <div>
      <div style="text-align: center">
        <el-transfer
            v-model="choices_data"
            :button-texts="['', '']"
            :data="app_developer_lists"
            :format="{
              noChecked: '${total}',
              hasChecked: '${checked}/${total}'
            }"
            :left-default-checked="left_data"
            :props="s_props"
            :right-default-checked="right_data"
            :titles="s_titles"
            filterable
            style="text-align: left; display: inline-block"
            @change="handleChange">
          <div slot-scope="{ option }" style="height: 60px;display: block">
            <el-popover v-if="app_id" placement="left" trigger="hover">
              <el-tag v-if="option.app_private_number > 0">专属应用账户，存在其他应用单独使用该开发者</el-tag>
              <el-tag v-else type="info">公共应用账户，所有应用公用此开发者</el-tag>
              <p>开发者ID: {{ option.issuer_id }} </p>
              <p>应用签名数: {{ option.app_used_number }} </p>
              <p>已分配专属应用数: {{ option.app_private_number }} </p>
              <p>开发者账户已使用设备数: {{ option.developer_used_number }}</p>
              <p>开发者账户可用设备数: {{ 100 - option.developer_used_number }}</p>
              <p>由于您设置可用设备数: {{ option.usable_number }} ,所以现在可用设备数: {{
                  option.usable_number - option.developer_used_number > 0
                      ? option.usable_number - option.developer_used_number : 0
                }}</p>
              <p>证书到期时间: {{ option.cert_expire_time }}</p>
              <p v-if="option.app_usable_number > 0">
                分配数量:
                <el-input-number v-model="option.app_usable_number" :max="100" :min="1"
                                 label="分配数量" size="small"/>
                <el-button size="small" style="margin-left: 10px" @click="saveNumber(option)">保存修改</el-button>
              </p>
              <p>描述: {{ option.description }}</p>

              <div slot="reference" class="name-wrapper">
                <div>{{ option.issuer_id }} - {{
                    option.usable_number - option.developer_used_number > 0
                        ? option.usable_number - option.developer_used_number : 0
                  }} - {{ option.description }}
                </div>
              </div>
            </el-popover>
            <el-popover v-if="issuer_id" placement="left" trigger="hover">
              <p>应用ID: {{ option.app_id }} </p>
              <p>应用名称: {{ option.name }} </p>
              <p>应用BundleId: {{ option.bundle_id }} </p>
              <p>短连接: {{ option.short }} </p>
              <p v-if="option.app_usable_number>0">
                分配数量:
                <el-input-number v-model="option.app_usable_number" :max="100" :min="1"
                                 label="分配数量" size="small"/>
                <el-button size="small" style="margin-left: 10px" @click="saveNumber(option)">保存修改</el-button>
              </p>
              <p>使用数量: {{ option.app_used_number }}</p>
              <p>描述: {{ option.description }}</p>
              <div slot="reference" class="name-wrapper">
                <div><span v-if="option.app_usable_number>0">{{ option.app_usable_number }} - </span> {{ option.name }}
                  -
                  {{ option.bundle_id }} - {{ option.app_id }}
                </div>
              </div>
            </el-popover>

          </div>
          <el-button slot="left-footer" class="transfer-footer" @click="getinfos">刷新</el-button>
          <el-button slot="right-footer" class="transfer-footer" @click="saveAppleApps">保存</el-button>
          <el-link v-if="issuer_id" slot="right-footer" :underline="false" style="margin-left: 20px">已经分配
            {{ app_private_used_number }} 还有 {{ 100 - app_private_used_number }} 可分配使用
          </el-link>
        </el-transfer>
      </div>
    </div>

  </transition>
</template>

<script>
import {developerBindAppFun, iosdeveloper} from "@/restful";

export default {
  name: 'AppleDeveloperBindApp',
  props: {
    transitionName: {
      type: String,
      default: 'appledeveloperbind'
    },
    app_id: {
      type: String,
      default: undefined
    },
    issuer_id: {
      type: String,
      default: undefined
    },
  },
  data() {
    return {
      app_developer_lists: [],
      left_data: [],
      right_data: [],
      choices_data: [],
      choices_data_list: [],
      s_props: {},
      s_titles: [],
      app_private_used_number: 100
    };
  },
  mounted() {
    this.getinfos()
  },
  methods: {
    get_choice_data_from_key(key_list) {
      let n_data = [];
      let field = 'app_id'
      if (this.app_id) {
        field = 'issuer_id'
      }
      this.app_private_used_number = 0
      for (let i = 0; i < this.app_developer_lists.length; i++) {
        for (let j = 0; j < key_list.length; j++) {
          if (key_list[j] === this.app_developer_lists[i][field]) {
            n_data.push(this.app_developer_lists[i])
            this.app_private_used_number += this.app_developer_lists[i]['app_usable_number']
          }
        }
      }
      return [n_data, this.app_private_used_number]
    },
    handleChange(value,) {
      this.get_choice_data_from_key(value)
    },
    saveNumber(infos) {
      if (this.get_choice_data_from_key(this.choices_data)[1] > 100) {
        this.$message.warning("超出最大分配额度，请注意，尽量保证所有应用分配额度总和为 100")
      }
      developerBindAppFun(data => {
        if (data.code === 1000) {
          // this.$message.success("数据保存成功")
          // this.choices_data = this.format_data(data.data)
        } else {
          this.$message.error("数据更新失败" + data.msg)
        }
        this.getinfos()
      }, {
        methods: 'PUT',
        data: {'app_id': this.app_id, 'issuer_id': this.issuer_id, 'infos': infos}
      })
    },
    getinfos() {
      if (this.issuer_id) {
        this.s_props = {
          key: 'app_id',
          label: 'name',
        }
        this.s_titles = ['可分配苹果应用', '已分配苹果应用']
        this.getBindInfo({act: 'apps'})
      } else {
        this.s_props = {
          key: 'issuer_id',
          label: 'issuer_id',
          disabled: 'is_disabled'
        }
        this.s_titles = ['可分配签名开发者账户', '已分配签名开发者账户']
        this.iosdeveloperFun()
      }
      this.getBindInfo({})
    },
    saveAppleApps() {
      developerBindAppFun(data => {
        if (data.code === 1000) {
          // this.$message.success("数据保存成功")
          // this.choices_data = this.format_data(data.data)
        } else {
          this.$message.error("数据更新失败" + data.msg)
        }
        this.getinfos()
      }, {
        methods: 'POST',
        data: {'app_id': this.app_id, 'issuer_id': this.issuer_id, 'choices_data': this.choices_data}
      })
    },
    iosdeveloperFun() {
      this.loadingfun = this.$loading({
        lock: true,
        text: '执行中,请耐心等待...',
        spinner: 'el-icon-loading',
        background: 'rgba(0, 0, 0, 0.7)'
      });
      iosdeveloper(data => {
            if (data.code === 1000) {
              this.app_developer_lists = data.data;
            }
            this.loadingfun.close()
          }
          ,
          {"methods": 'GET', "data": {app_id: this.app_id, issuer_id: this.issuer_id}})
    },
    getBindInfo(params) {
      if (this.issuer_id) {
        params.issuer_id = this.issuer_id
      }
      if (this.app_id) {
        params.app_id = this.app_id
      }
      developerBindAppFun(data => {
        if (data.code === 1000) {
          if (params.act === 'apps') {
            this.app_developer_lists = data.data
            this.get_choice_data_from_key(this.choices_data)
          } else {
            this.choices_data_list = data.data;
            this.choices_data = this.format_data(data.data)
            this.get_choice_data_from_key(this.choices_data)
            this.$message.success("数据获取成功")
          }
        } else {
          this.$message.error("数据获取失败" + data.msg)
        }
      }, {methods: 'GET', data: params})
    },
    format_data(data) {
      let n_data = [];
      let field = 'app_id'
      if (this.app_id) {
        field = 'issuer_id'
      }
      this.app_private_used_number = 0
      if (data && data.length > 0) {
        for (let i = 0; i < data.length; i++) {
          n_data.push(data[i][field])
        }
      }
      return n_data
    },
    format_data_number() {

    },
  }
}
</script>

<style scoped>
/deep/ .el-transfer-panel {
  width: 460px;
}

/*/deep/ .el-transfer-panel__item {*/
/*  height: 60px;*/
/*}*/
.transfer-footer {
  text-align: center;
  float: right;
}
</style>
