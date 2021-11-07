<template>
  <transition :name="transitionName">
    <div>
      <div style="margin: 5px 20px">
        <el-steps :active="active" finish-status="success">
          <el-step title="步骤 1">

          </el-step>
          <el-step title="步骤 2">
          </el-step>
          <el-step title="步骤 3"/>
        </el-steps>
        <div style="margin-top: 20px">
          <div v-if="active===1">
            <h2>你的二级域名</h2>
            <el-input v-model="domain_name" autofocus clearable/>
          </div>
          <div v-else-if="active===2">
            <div style="text-align: center;margin: 20px 0">
              <h3>还差一步绑定成功</h3>
            </div>
            请联系域名管理员，前往 <strong>{{ domain_name }}</strong> 域名 DNS 管理后台添加如下 CNAME 记录。
            <el-table
                :data="domain_tData"
                border
                stripe
                style="width: 100%;margin-top: 20px">
              <el-table-column
                  align="center"
                  label="记录类型"
                  prop="type"
                  width="100">
              </el-table-column>
              <el-table-column
                  align="center"
                  label="主机记录"
                  prop="host"
              >
                <template slot-scope="scope">
                  <el-tooltip content="点击复制到剪贴板">
                    <el-link v-if="scope.row.host" v-clipboard:copy="scope.row.host"
                             v-clipboard:success="copy_success"
                             :underline="false">{{ scope.row.host }}
                    </el-link>
                  </el-tooltip>
                </template>
              </el-table-column>
              <el-table-column
                  align="center"
                  label="记录值"
                  prop="dns"
                  width="300">
                <template slot-scope="scope">
                  <el-tooltip content="点击复制到剪贴板">
                    <el-link v-if="scope.row.dns" v-clipboard:copy="scope.row.dns"
                             v-clipboard:success="copy_success"
                             :underline="false">{{ scope.row.dns }}
                    </el-link>
                  </el-tooltip>
                </template>
              </el-table-column>
            </el-table>
            <el-alert :closable="false"
                      show-icon
                      style="margin-top: 30px"
                      title="请在域名DNS配置成功后，点击“下一步”按钮"
                      type="warning"/>
          </div>
          <div v-else-if="active===3">
            <div v-if="!bind_status">
              <div style="text-align: center;margin: 20px 0">
                <el-link :underline="false" style="font-size: x-large"
                         type="danger">绑定失败
                </el-link>
              </div>

              <p style="margin: 10px 0">{{ b_t_msg }}正在绑定域名：<strong>{{ domain_name }}</strong></p>
              <el-row>
                <el-col :span="16"><p>系统未检出到您的CNAME记录，请检查您的配置。</p></el-col>
                <el-col :span="6">
                  <el-button plain size="small" style="margin-top: 8px" type="danger"
                             @click="remove_domain">
                    解除绑定
                  </el-button>
                </el-col>
              </el-row>
            </div>

            <div v-else>
              <div style="text-align: center;margin: 20px 0">
                <el-link :underline="false" style="font-size: x-large"
                         type="success">绑定成功
                </el-link>
              </div>

              <el-row>
                <el-col :span="16"><p>{{ b_t_msg }}已绑定域名：<strong>{{ domain_name }}</strong></p></el-col>
                <el-col :span="6">
                  <el-button plain size="small" style="margin-top: 8px" type="danger"
                             @click="remove_domain">
                    解除绑定
                  </el-button>
                </el-col>
              </el-row>

            </div>
            <el-table
                :data="domain_tData"
                border
                stripe
                style="width: 100%;margin-top: 20px">
              <el-table-column
                  align="center"
                  label="记录类型"
                  prop="type"
                  width="100">
              </el-table-column>
              <el-table-column
                  align="center"
                  label="主机记录"
                  prop="host"
              >
              </el-table-column>
              <el-table-column
                  align="center"
                  label="记录值"
                  prop="dns"
                  width="300">
              </el-table-column>
            </el-table>
            <div v-if="!bind_status" style="text-align: center;margin: 30px 0">
              <el-button plain type="success" @click="check_cname">已经修改配置，再次检查绑定</el-button>
            </div>
          </div>

        </div>
      </div>
      <div v-if="active!==3" style="margin:40px 20px 0;text-align: right">
        <el-button :disabled="bind_status|| active===1 "
                   @click="last">上一步
        </el-button>
        <el-button v-if="force_bind" @click="next(1)">强制绑定</el-button>
        <el-button v-else @click="next(0)">下一步</el-button>

      </div>

    </div>
  </transition>
</template>

<script>
import {domainFun} from "@/restful";

export default {
  name: 'BindDomain',
  props: {
    transitionName: {
      type: String,
      default: 'bind-domain'
    },
    app_id: {
      type: String,
      default: undefined
    },
    domain_type: {
      type: Number,
      default: 1
    },
    domain_state: {
      type: Boolean,
      default: false
    },
  },
  data() {
    return {
      active: 1,
      bind_status: false,
      bind_domain_sure: true,
      domain_name: '',
      domain_tData: [{'type': 'CNAME', 'host': 'xxx', 'dns': 'demo.xxx.cn'}],
      force_bind: false,
      b_t_msg: '您的账户',
    }
  },
  mounted() {
    if (this.domain_type === 2) {
      this.b_t_msg = '您的应用'
    }
    this.bind_click();
  },
  beforeDestroy() {
    this.bind_domain_sure = false;
  },
  methods: {
    copy_success() {
      this.$message.success('复制剪切板成功');
    },
    check_cname() {
      domainFun(data => {
        if (data.code === 1000) {
          if (this.active++ > 2) this.active = 3;
          this.bind_status = true;
          if (!this.app_id) {
            if (this.domain_type === 1) {
              this.$store.dispatch("dodomainshow", false);
            }
          }
          if (this.domain_state) {
            this.$store.dispatch("dosetdomainstate", true);
          }
        } else {
          if (data.code === 1004) {
            this.active = 1;
            this.domain_name = '';
          } else {
            if (this.active++ > 2) this.active = 3;
          }
          this.bind_status = false;
          this.$message.error("绑定失败 " + data.msg)
        }
      }, {methods: 'PUT', data: {app_id: this.app_id, domain_type: this.domain_type}})
    },
    remove_domain() {
      domainFun(data => {
        if (data.code === 1000) {
          this.bind_status = false;
          this.active = 1;
          this.$message.success("解除绑定成功 ");
          if (!this.app_id) {
            if (this.domain_type === 1) {
              this.$store.dispatch("dodomainshow", true);
            }
          }
          if (this.domain_state) {
            this.$store.dispatch("dosetdomainstate", true);
          }
        } else {
          this.$message.error("解除绑定失败 " + data.msg)
        }
      }, {methods: 'DELETE', data: {app_id: this.app_id, domain_type: this.domain_type}});
    },
    bind_click() {
      this.$store.dispatch("dosetdomainstate", false);
      domainFun(data => {
        if (data.code === 1000) {
          if (data.data) {
            if (data.data.domain_name) {
              this.domain_name = data.data.domain_name;
            }
            if (data.data.domain_record) {
              this.format_domain_tData(data.data.domain_record);
              if (this.active++ > 2) this.active = 3;
            }
            if (data.data.is_enable) {
              this.bind_status = true;
              if (this.active++ > 2) this.active = 3;
            }
            this.bind_domain_sure = true;
          }
        } else {
          this.$message.error("绑定失败 " + data.msg)
        }
      }, {methods: 'GET', data: {app_id: this.app_id, domain_type: this.domain_type}});
    },
    format_domain_tData(cname_domain) {
      let domain_name_list = this.domain_name.split('.');
      const d_len = domain_name_list.length;
      if (d_len === 2) {
        this.domain_tData[0].host = '@'
      } else if (d_len > 2) {
        domain_name_list.splice(domain_name_list.length - 2, 2);
        this.domain_tData[0].host = domain_name_list.join(".")
      }
      this.domain_tData[0].dns = cname_domain;
    },
    next(force_bind) {
      if (this.active === 1) {
        domainFun(data => {
          if (data.code === 1000) {
            if (data.data && data.data.cname_domain) {
              this.format_domain_tData(data.data.cname_domain);
              if (this.active++ > 2) this.active = 3;
            }
          } else {
            this.$message.error("绑定失败 " + data.msg);
            if (data.code === 1011) {
              this.force_bind = true
            }
          }
        }, {
          methods: 'POST',
          data: {
            domain_name: this.domain_name,
            app_id: this.app_id,
            domain_type: this.domain_type,
            force_bind: force_bind
          }
        })
      } else if (this.active === 2) {
        this.check_cname()
      }
    },
    last() {
      if (this.active-- < 2) this.active = 1;
    },
  }
}
</script>

<style scoped>
.dialog-footer {

}
</style>
