<template>
  <el-main>
    <el-dialog :close-on-click-modal="false" :destroy-on-close="true" :title="title"
               :visible.sync="dialogReceiverVisible" width="780px">

      <el-form ref="recevierform" :model="addreceiverinfo"
               label-width="80px" style="margin:0 auto;">


        <el-form-item label="姓名">
          <el-input v-model="addreceiverinfo.receiver_name"/>
        </el-form-item>

        <el-form-item label="邮箱">
          <el-input v-model="addreceiverinfo.email"/>
        </el-form-item>


        <!--        <el-form-item v-if="captcha.captcha_image" style="height: 40px" >-->
        <!--          <el-row style="height: 40px">-->
        <!--            <el-col :span="16">-->
        <!--              <el-input v-model="addreceiverinfo.verify_code" clearable maxlength="6"-->
        <!--                        placeholder="请输入验证码" @keyup.enter.native="onSubmit"/>-->
        <!--            </el-col>-->
        <!--            <el-col :span="8">-->
        <!--              <el-image-->
        <!--                  :src="captcha.captcha_image"-->
        <!--                  fit="contain"-->
        <!--                  style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px" @click="get_auth_code">-->
        <!--              </el-image>-->
        <!--            </el-col>-->
        <!--          </el-row>-->
        <!--        </el-form-item>-->

        <!--        <el-form-item>-->
        <!--          <el-row>-->
        <!--            <el-col :span="16">-->
        <!--              <el-input v-model="addreceiverinfo.seicode" clearable-->
        <!--                        placeholder="邮箱验证码" prefix-icon="el-icon-mobile"/>-->
        <!--            </el-col>-->
        <!--            <el-col :span="8">-->
        <!--              <el-button plain style="margin:0 4px;border-radius:4px;cursor:pointer;height: 40px" type="info"-->
        <!--                         @click="onGetCode">获取验证码-->
        <!--              </el-button>-->
        <!--            </el-col>-->
        <!--          </el-row>-->
        <!--        </el-form-item>-->

        <!--        <el-form-item>-->
        <!--          <div id="captcha" ref="captcha"></div>-->
        <!--        </el-form-item>-->


        <el-form-item label="微信">
          <el-tag v-if="addreceiverinfo.wxopenid && addreceiverinfo.wxopenid.length > 6">
            {{ addreceiverinfo.wxopenid }}
          </el-tag>
          <el-popover v-else
                      v-model="wx_visible"
                      placement="top"
                      title="打开微信扫一扫进行绑定"
                      trigger="manual">
            <div>
              <el-image :src="wx_login_qr_url" style="width: 176px;height: 166px"/>
            </div>
            <el-button slot="reference" size="small" @click="wxLogin">绑定微信</el-button>
          </el-popover>
        </el-form-item>

        <el-form-item label="备注">
          <el-input v-model="addreceiverinfo.description"/>
        </el-form-item>

        <el-button @click="saveReceiver">保存</el-button>
        <el-button @click="cancelReceiver">取消</el-button>
      </el-form>
    </el-dialog>


    <el-dialog :close-on-click-modal="false" :destroy-on-close="true" :visible.sync="dialogChangeReceiverVisible"
               title="修改消息接收人">

      <div style="text-align: left;margin-bottom: 10px">
        <div style="margin-bottom: 10px">
          <el-tag type="warning">提醒：如果以下消息接收人的信息有变更，请到“消息接收人管理”中进行修改。</el-tag>
        </div>
        消息类型：{{ notifyConfigMsg.message_type }} - {{ notifyConfigMsg.config_name }}
      </div>
      <el-table
          ref="multipleTable"
          :data="receiver_info_lists"
          border
          stripe
          style="width: 100%"
          @selection-change="handleSelectionChange">
        <el-table-column
            type="selection"
            width="55">
        </el-table-column>
        <el-table-column
            align="center"
            fixed
            label="姓名"
            prop="receiver_name"
            width="100">
        </el-table-column>
        <el-table-column
            align="center"
            label="邮箱"
            prop="email"
            width="200">
        </el-table-column>
        <el-table-column
            align="center"
            label="微信"
            prop="domain_name"
            width="260">
          <template slot-scope="scope">
            <el-popover v-if="scope.row.weixin.openid" placement="top" trigger="hover">
              <div style="float: right;margin-top: 10px">
                <el-image :src="scope.row.weixin.head_img_url" style="width: 80px;height: 80px"/>
              </div>
              <p>昵称: {{ scope.row.weixin.nickname }}</p>
              <p>性别: {{ scope.row.weixin.sex|sex_filter }}</p>
              <p>住址: {{ scope.row.weixin.address }}</p>
              <p>微信ID: {{ scope.row.weixin.openid }}</p>
              <div slot="reference" class="name-wrapper">
                <el-tag>{{ scope.row.weixin.openid }}</el-tag>
              </div>
            </el-popover>
            <el-tag v-else> /</el-tag>
          </template>
        </el-table-column>

        <el-table-column
            align="center"
            label="备注"
            prop="description">
        </el-table-column>

      </el-table>
      <div style="text-align: left;margin-bottom: 10px;margin-top: 10px">
        <el-button plain size="small" type="primary" @click="addRecevier">
          新增消息接收人
        </el-button>
      </div>
      <span slot="footer">
          <el-button @click="updateConfig(undefined)">保存</el-button>
          <el-button @click="dialogChangeReceiverVisible=false">取消</el-button>
      </span>

    </el-dialog>


    <el-tabs v-model="activeName" tab-position="top" type="border-card" @tab-click="handleClick">

      <el-tab-pane label="基本接收管理" name="config">

        <el-table
            :data="[{name:'消息类型',email:'邮件通知',weixin:'微信通知',user:'消息接收人'}]"
            :show-header="false"
            border
            stripe
            style="width: 100%">
          <el-table-column
              align="center"
              prop="name"
              width="200">
          </el-table-column>
          <el-table-column
              align="center"
              prop="email"
              width="200">
          </el-table-column>
          <el-table-column
              align="center"
              prop="weixin"
              width="200">
          </el-table-column>
          <el-table-column
              align="center"
              prop="user">
          </el-table-column>
        </el-table>

        <el-collapse v-model="activeConfig">
          <el-collapse-item v-for="info in message_type_choices" :key="info.id" :disabled="info.disabled"
                            :name="info.id">
            <template slot="title">
              <div style="width: 200px">
                <h2>{{ info.name }}</h2>
              </div>
            </template>
            <el-table
                :data="info.data"
                :show-header="false"
                border
                stripe
                style="width: 100%">
              <el-table-column
                  align="center"
                  fixed
                  prop="config_name"
                  width="200">
              </el-table-column>
              <el-table-column
                  align="center"
                  fixed
                  prop="enable_email"
                  width="200">
                <template slot-scope="scope">
                  <el-checkbox v-model="scope.row.enable_email" @change="updateConfig(scope.row)">邮件</el-checkbox>
                </template>
              </el-table-column>

              <el-table-column
                  align="center"
                  fixed
                  prop="enable_weixin"
                  width="200">
                <template slot-scope="scope">
                  <el-checkbox v-model="scope.row.enable_weixin" @change="updateConfig(scope.row)">微信</el-checkbox>
                </template>
              </el-table-column>

              <el-table-column
                  align="center"
                  fixed
                  prop="senders">
                <template slot-scope="scope">
                  <el-tag v-for="user in scope.row.senders" :key="user.id" style="margin-right: 3px" type="info">
                    {{ user.receiver_name }}
                  </el-tag>
                  <el-tag type="success">
                    <el-link :underline="false" type="success" @click="changeNotifyConfig(scope.row)">修改</el-link>
                  </el-tag>
                </template>
              </el-table-column>

            </el-table>
          </el-collapse-item>
        </el-collapse>
      </el-tab-pane>
      <el-tab-pane label="消息接收人管理" name="receiver">

        <div style="float: right;margin-bottom: 10px">

          <el-button plain type="primary" @click="addRecevier">
            新增消息接收人
          </el-button>

        </div>
        <el-table
            v-loading="loading"
            :data="receiver_info_lists"
            border
            stripe
            style="width: 100%">

          <el-table-column
              align="center"
              fixed
              label="姓名"
              prop="receiver_name"
              width="100">
          </el-table-column>
          <el-table-column
              align="center"
              label="邮箱"
              prop="email"
              width="200">
          </el-table-column>
          <el-table-column
              align="center"
              label="微信"
              prop="domain_name">
            <template slot-scope="scope">
              <el-popover v-if="scope.row.weixin.openid" placement="top" trigger="hover">
                <div style="float: right;margin-top: 10px">
                  <el-image :src="scope.row.weixin.head_img_url" style="width: 80px;height: 80px"/>
                </div>
                <p>昵称: {{ scope.row.weixin.nickname }}</p>
                <p>性别: {{ scope.row.weixin.sex|sex_filter }}</p>
                <p>住址: {{ scope.row.weixin.address }}</p>
                <p>微信ID: {{ scope.row.weixin.openid }}</p>
                <div slot="reference" class="name-wrapper">
                  <el-tag>{{ scope.row.weixin.openid }}</el-tag>
                </div>
              </el-popover>
              <el-tag v-else> /</el-tag>
            </template>
          </el-table-column>


          <el-table-column
              :formatter="formatter"
              align="center"
              label="添加时间"
              prop="create_time"
              width="170">
          </el-table-column>
          <el-table-column
              align="center"
              label="备注"
              prop="description">
          </el-table-column>
          <el-table-column
              align="center"
              label="操作"
              width="120">
            <template slot-scope="scope">
              <!--                <el-button size="small" type="text" @click="editReceiver(scope.row)">编辑</el-button>-->
              <el-button size="small" type="text" @click="deleteReceiver(scope.row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="阈值设置" name="threshold" style="text-align: center">
        <el-tag style="margin: 20px 0"> 低于阈值设置，将会出发报警，若您配置了消息接收，将会将报警信息推送至关联的接收人</el-tag>
        <div style="margin: auto;width: 700px;height: 100%">
          <el-form ref="form" :model="threshold" label-width="180px">
            <el-form-item label="下载次数不足阈值设置">
              <el-input-number v-model="threshold.notify_available_downloads" :min="0"
                               style="width: 300px;margin: 0 20px"></el-input-number>
              <el-button @click="notifyThreshold('update')">保存修改</el-button>
            </el-form-item>

            <el-form-item label="签名次数不足阈值设置">
              <el-input-number v-model="threshold.notify_available_signs" :min="0"
                               style="width: 300px;margin: 0 20px"></el-input-number>
              <el-button @click="notifyThreshold('update')">保存修改</el-button>
            </el-form-item>
          </el-form>
        </div>

      </el-tab-pane>
    </el-tabs>

  </el-main>
</template>

<script>
import {notifyConfigInfo, notifyReceiverInfo, wxBindFun, wxLoginFun} from "@/restful";
import {getUserInfoFun} from "@/utils";
import {getRandomStr} from "@/utils/base/utils";

export default {
  name: "FirUserNotify",
  data() {
    return {
      dialogReceiverVisible: false,
      captcha: {"captcha_image": '', "captcha_key": '', "length": 8},
      wx_visible: false,
      wx_login_qr_url: '',
      unique_key: '',
      userinfo: {},
      addreceiverinfo: {description: '', wxopenid: '', email: '', receiver_name: ''},
      message_type_choices: [],
      activeConfig: [],
      dialogChangeReceiverVisible: false,
      notifyConfigSelection: [],
      notifyConfigMsg: {},
      title: '',
      isedit: false,
      activeName: 'config',
      receiver_info_lists: [],
      loading: false,
      threshold: {}
    }
  }, methods: {
    addRecevier() {
      this.addreceiverinfo = {description: '', wxopenid: '', email: '', receiver_name: ''}
      this.dialogReceiverVisible = true
      this.title = '新增消息接收人'
    },
    editReceiver(receiver) {
      this.title = '编辑 ' + receiver.receiver_name + ' 消息接收人'
      this.isedit = true
      this.addreceiverinfo = receiver
      this.dialogReceiverVisible = true
    },
    updateConfig(config = undefined) {
      let data = {}
      if (config) {
        data = {
          'config': config.id,
          'enable_email': config.enable_email,
          'enable_weixin': config.enable_weixin,
          'm_type': config.message_type
        }
      } else {
        let receiver_ids = []
        for (let receiver of this.notifyConfigSelection) {
          receiver_ids.push(receiver.id)
        }
        data = {'config': this.notifyConfigMsg.id, 'receiver': receiver_ids, 'm_type': this.notifyConfigMsg.m_type}
      }

      notifyConfigInfo(data => {
        if (data.code === 1000) {
          this.$message.success('保存成功')
          if (!config) {
            this.dialogChangeReceiverVisible = false;
          }
          this.notifyConfigInfoFun();
        } else {
          this.$message.error('保存失败,' + data.msg);
        }
      }, {"methods": 'PUT', "data": data});
    },
    changeNotifyConfig(info) {
      let params = {"config": info.id, "message_type": info.m_type}
      this.dialogChangeReceiverVisible = true;
      notifyReceiverInfo(data => {
        if (data.code === 1000) {
          this.receiver_info_lists = data.data;
          this.notifyConfigMsg = data.config
          // eslint-disable-next-line no-unused-vars
          this.$nextTick(res => {
            data.data.forEach(row => {
              for (let sender of data.senders) {
                if (sender.sender === row.id) {
                  this.$refs.multipleTable.toggleRowSelection(row);
                }
              }
            });
          })
        } else {
          this.$message.error('获取失败,' + data);
        }
        this.loading = false;
      }, {"methods": 'GET', "data": params});

    },
    handleSelectionChange(val) {
      this.notifyConfigSelection = val;
    },
    // eslint-disable-next-line no-unused-vars
    handleClick(tab, event) {
      this.get_data_from_tabname(tab.name);
    },
    cancelReceiver() {
      this.dialogReceiverVisible = false;
      this.addreceiverinfo = {description: '', wxopenid: '', email: '', receiver_name: ''}
    },
    saveReceiver() {
      notifyReceiverInfo(data => {
        if (data.code === 1000) {
          this.$message.success('操作成功');
          this.dialogReceiverVisible = false;
          if (this.dialogChangeReceiverVisible) {
            this.changeNotifyConfig(this.notifyConfigMsg)
          } else {
            this.get_data_from_tabname(this.activeName);
          }
        } else {
          this.$message.error('操作失败，' + data.msg);
        }
      }, {"methods": 'POST', 'data': this.addreceiverinfo});
    },
    deleteReceiver(sinfo) {

      this.$confirm(`将要删除接收人 ${sinfo.receiver_name}, 是否继续?`, '警告', {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }).then(() => {
        notifyReceiverInfo(data => {
          if (data.code === 1000) {
            this.$message.success('删除成功');
            this.notifyReceiverInfoFun();
          }
        }, {"methods": 'DELETE', 'data': {'id': sinfo.id}})
      }).catch(() => {
        this.$message({
          type: 'info',
          message: '已取消删除'
        });
      });

    },

    notifyReceiverInfoFun() {
      this.loading = true;
      notifyReceiverInfo(data => {
        if (data.code === 1000) {
          this.receiver_info_lists = data.data;
        } else {
          this.$message.error('获取失败,' + data);
        }
        this.loading = false;
      }, {"methods": 'GET'});
    },
    setActiveConfig(message_type_choices) {
      let activeConfig = []
      for (let i of message_type_choices) {
        activeConfig.push(i.id)
      }
      this.activeConfig = activeConfig;
    },
    notifyConfigInfoFun() {
      this.loading = true;
      notifyConfigInfo(data => {
        if (data.code === 1000) {
          this.receiver_info_lists = data.data;
          this.message_type_choices = data.message_type_choices;
          this.setActiveConfig(this.message_type_choices);
        } else {
          this.$message.error('获取失败,' + data);
        }
        this.loading = false;
      }, {"methods": 'GET'});
    },
    notifyThreshold(act) {
      notifyConfigInfo(data => {
        if (data.code === 1000) {
          this.threshold = data.data
          if (act !== 'get') {
            this.$message.success('保存成功')
          }
        } else {
          this.$message.error('获取失败,' + data);
        }
        this.loading = false;
      }, {"methods": 'POST', 'data': {'act': act, 'threshold': this.threshold}});
    },

    loop_get_wx_info(wx_login_ticket, c_count = 1, unique_key = getRandomStr()) {
      if (wx_login_ticket && wx_login_ticket.length < 3) {
        this.$message.error("获取登陆码失败，请稍后再试");
        return
      }
      if (!this.wx_visible) {
        return;
      }
      wxLoginFun(data => {
        c_count += 1;
        if (c_count > 30) {
          return;
        }
        if (data.code === 1000) {
          if (this.userinfo.uid === data.data.uid) {
            if (data.data.to_user) {
              this.addreceiverinfo.wxopenid = data.data.to_user
            }
            this.$message.success("绑定成功");
            this.wx_visible = false;
          }
        } else if (data.code === 1005) {
          this.$message({
            message: data.msg,
            type: 'error',
            duration: 30000
          });
        } else if (data.code === 1004) {
          this.loop_flag = false;
        } else if (data.code === 1006) {
          return this.loop_get_wx_info(wx_login_ticket, c_count, unique_key)
        }
      }, {
        "methods": "POST",
        data: {"ticket": wx_login_ticket, "unique_key": unique_key}
      })
    },
    wxLogin() {
      this.wx_visible = !this.wx_visible;
      this.wx_login_qr_url = '';
      if (this.wx_visible) {
        wxBindFun(data => {
          if (data.code === 1000) {
            this.wx_login_qr_url = data.data.qr;
            this.loop_get_wx_info(data.data.ticket);
          } else {
            this.$message.error(data.msg);
            this.wx_visible = false;
          }
        }, {
          "methods": "POST", "data": {"unique_key": this.unique_key, "w_type": 'notify'}
        })
      }
    },

    // eslint-disable-next-line no-unused-vars
    formatter(row, column) {
      let stime = row.create_time;
      if (stime) {
        stime = stime.split(".")[0].split("T");
        return stime[0] + " " + stime[1]
      } else
        return '';
    },
    // eslint-disable-next-line no-unused-vars
    get_data_from_tabname(tabname, data = {}) {
      this.$router.push({"name": 'FirUserNotify', params: {act: tabname}});
      if (tabname === "config") {
        this.notifyConfigInfoFun();
      } else if (tabname === "receiver") {
        this.notifyReceiverInfoFun();
      } else if (tabname === "threshold") {
        this.notifyThreshold('get');
      }
    },
  }, mounted() {
    getUserInfoFun(this);
    this.userinfo = this.$store.state.userinfo;
    this.unique_key = getRandomStr();
    if (this.$route.params.act) {
      let activeName = this.$route.params.act;
      let activeName_list = ["config", "receiver", "threshold"];
      for (let index in activeName_list) {
        if (activeName_list[index] === activeName) {
          this.activeName = activeName;
          this.get_data_from_tabname(activeName);
          return
        }
      }
    }
    this.get_data_from_tabname(this.activeName);
  }, filters: {
    sex_filter: function (x) {
      let ret = '未知';
      if (x === 1) {
        ret = '男'
      } else if (x === 2) {
        ret = '女'
      }
      return ret;
    },
  }, watch: {
    '$store.state.userinfo': function () {
      this.userinfo = this.$store.state.userinfo;
    }
  }
}
</script>

<style scoped>
.el-main {
  text-align: center;
  margin: 20px auto 100px;
  width: 1166px;
  position: relative;
  padding-bottom: 1px;
  color: #9b9b9b;
  -webkit-font-smoothing: antialiased;
  border-radius: 1%;
}
</style>
