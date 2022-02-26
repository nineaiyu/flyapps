<template>
  <el-main>

    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :visible.sync="wx_pay"
        center
        width="49%">
      <div slot="title" style="margin-bottom: 10px">
        <el-row>
          <el-col :span="12">
            <p class="detail">请在<span style="color: #f89303">24小时</span>内完成支付，超时订单将自动取消。</p>
            <p class="detail">支付订单号： <span>{{ current_order_info.order_number }}</span></p>
          </el-col>
          <el-col :span="12">
            <p style="margin-top: 26px"><span class="order_text">订单金额（元）：</span><span
                class="amount">{{ format_actual_amount(current_order_info) }}</span>
            </p>
          </el-col>

        </el-row>

      </div>
      <div class="pay_wx">
        <div>
          <div :style="{background:`url(${pay_image.order_wx})  0 0/100%`}" class="icon-weixin"></div>
          <vue-qr ref="qr"
                  :correctLevel="qrinfo.correctLevel"
                  :logoCornerRadius="qrinfo.logoCornerRadius"
                  :logoScale="qrinfo.logoScale"
                  :margin="qrinfo.margin"
                  :size="266" :text="pay_code_url"
                  class="code-wrap">
          </vue-qr>
          <div class="tip-btn pay_wx"><span :style="{backgroundImage:`url(${pay_image.scan})`}" class="icon"/><span
              class="text">请使用微信扫码支付</span></div>
          <p style="margin-top: 30px">支付完成之后，请刷新该页面，确认支付状态</p>
        </div>
      </div>

    </el-dialog>

    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :visible.sync="show_order_info"
        center
        title="订单详情"
        top="6vh"
        width="780px">
      <div>

        <el-form :model="current_order_info"
                 label-width="80px" style="margin:0 auto;">

          <el-form-item label="平台订单ID" label-width="110px">
            <el-input :value="current_order_info.order_number"/>
          </el-form-item>


          <el-form-item label="第三方订单ID" label-width="110px">
            <el-input :value="current_order_info.payment_number"/>
          </el-form-item>

          <el-form-item label="付款方式" label-width="110px">
            <el-input :value="format_payment_type(current_order_info)"/>
          </el-form-item>
          <el-form-item label="订单状态" label-width="110px">
            <el-input :value="format_status_type(current_order_info)"/>
          </el-form-item>

          <el-form-item label="订单类型" label-width="110px">
            <el-input :value="format_order_type(current_order_info)"/>
          </el-form-item>
          <el-form-item label="实付金额" label-width="110px">
            <el-input :value="format_actual_amount(current_order_info)"/>
          </el-form-item>

          <el-form-item label="购买数量" label-width="110px">
            <el-input
                :value="current_order_info.actual_download_times"/>
          </el-form-item>

          <el-form-item label="赠送数量" label-width="110px">
            <el-input
                :value="current_order_info.actual_download_gift_times"/>
          </el-form-item>

          <el-form-item label="订单创建时间" label-width="110px">
            <el-input :value="format_create_time(current_order_info)"/>
          </el-form-item>

          <el-form-item label="订单支付时间" label-width="110px">
            <el-input :value="format_pay_time(current_order_info)"/>
          </el-form-item>

          <el-form-item label="订单取消时间" label-width="110px">
            <el-input :value="format_cancel_time(current_order_info)"/>
          </el-form-item>


          <el-form-item label="备注" label-width="110px">
            <el-input :value="current_order_info.description"/>
          </el-form-item>

        </el-form>


      </div>
      <span slot="footer">
                        <el-button @click="$router.push({'name':'FirContact'})"> 如对充值订单有疑问，请联系我们</el-button>
                    </span>
    </el-dialog>


    <div>
      <el-input
          v-model="order_id_seach"
          clearable
          placeholder="输入订单ID"
          style="width: 30%;margin-right: 30px;margin-bottom: 5px"/>
      <el-button icon="el-icon-search" type="primary" @click="handleCurrentChange(1)">
        搜索
      </el-button>

      <el-table
          v-loading="loading"
          :data="order_info_list"
          border
          stripe
          style="width: 100%">

        <el-table-column
            align="center"
            fixed
            label="系统订单ID"
            prop="order_number">

        </el-table-column>

        <el-table-column
            align="center"
            label="状态"
            prop="status"
            width="110">

          <template slot-scope="scope">
            <div v-if="scope.row.status === 1 || scope.row.status === 2">
              <el-button size="small"
                         type="primary" @click="goto_pay(scope.row)"> {{ format_status_type(scope.row) }}
              </el-button>
            </div>
            <div v-else-if="scope.row.status === 0">
              <el-button size="small"
                         type="success" @click="click_order_info(scope.row)"> {{ format_status_type(scope.row) }}
              </el-button>
            </div>
            <div v-else-if="scope.row.status === 4 || scope.row.status ===5|| scope.row.status ===6">
              <el-button size="small"
                         type="danger" @click="click_order_info(scope.row)"> {{ format_status_type(scope.row) }}
              </el-button>
            </div>
            <div v-else>
              <el-button size="small"
                         type="warning" @click="click_order_info(scope.row)"> {{ format_status_type(scope.row) }}
              </el-button>
            </div>

          </template>

        </el-table-column>

        <el-table-column
            :formatter="format_actual_amount"
            align="center"
            label="实付金额"
            prop="actual_amount"
            width="100">
        </el-table-column>


        <el-table-column
            align="center"
            label="购买数量"
            prop="actual_download_times"
            width="120">
        </el-table-column>

        <el-table-column
            align="center"
            label="赠送数量"
            prop="actual_download_gift_times"
            width="90">
        </el-table-column>
        <el-table-column
            :formatter="format_payment_type"
            align="center"
            label="支付方式"
            prop="payment_type"
            width="80">
        </el-table-column>

        <el-table-column
            :formatter="format_create_time"
            align="center"
            label="订单创建时间"
            prop="created_time"
            width="170"
        >
        </el-table-column>

        <el-table-column
            align="center"
            fixed="right"
            label="查看详细"
            width="145">
          <template slot-scope="scope">

            <el-button
                size="mini"
                @click="click_order_info(scope.row)">详情
            </el-button>
            <el-button v-if="scope.row.status === 1 || scope.row.status === 2"
                       size="mini" type="danger"
                       @click="cancel_order(scope.row)">取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>


    </div>
    <div style="margin-top: 20px;margin-bottom: 20px">
      <el-pagination
          :current-page.sync="pagination.currentPage"
          :page-size="pagination.pagesize"
          :page-sizes="[10, 20, 50, 100]"
          :total="pagination.total"
          layout="total,sizes, prev, pager, next"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange">
      </el-pagination>
    </div>
  </el-main>
</template>

<script>

import {my_order, order_sync} from "@/restful";
import {format_choices, getUserInfoFun} from '@/utils'
import VueQr from 'vue-qr';

export default {
  name: "FirUserOrders",
  components: {
    VueQr
  },
  data() {
    return {
      wx_pay: false,
      pay_code_url: '',
      pay_image: {
        'scan': require('@/assets/pay/pay-scan.png'),
        'order_wx': require('@/assets/pay/order-weixin.png'),
      },
      qrinfo: {
        logoScale: 0.3,
        logoCornerRadius: 12,
        correctLevel: 3,
        margin: 20
      },
      order_info_list: [],
      order_id_seach: "",
      pagination: {"currentPage": 1, "total": 0, "pagesize": 10},
      order_type_choices: [],
      status_choices: [],
      payment_type_choices: [],
      show_order_info: false,
      current_order_info: {},
      loading: false,
    }
  },
  methods: {
    cancel_order(order) {
      my_order(res => {
        if (res.code === 1000) {
          this.$message.success("操作成功");
          this.get_data_from_tabname({
            "size": this.pagination.pagesize,
            "page": this.pagination.currentPage
          })
        } else {
          this.$message.error("失败了 " + res.msg)
        }
      }, {
        methods: 'PUT', data: {order_number: order.order_number, act: 'cancel'},
      })
    },

    loop_get_order_info(order_number, c_count = 1) {
      order_sync(data => {
        c_count += 1;
        if (c_count > 30) {
          return;
        }
        if (data.code === 1000) {
          this.$message.success(data.msg);
          this.get_data_from_tabname();
          this.wx_pay = false;
        } else if (data.code === 1001) {
          return this.loop_get_order_info(order_number, c_count)
        }
      }, {
        "methods": "POST",
        data: {"order_number": order_number}
      })
    },

    goto_pay(order) {
      this.current_order_info = order;
      my_order(res => {
        if (res.code === 1000) {
          let data = res.data;
          if (data && data.url) {
            if (data && data.type === 'WX') {
              this.pay_code_url = data.url;
              this.wx_pay = true;
              this.$message.success("请用微信扫描支付");
              this.loop_get_order_info(order.order_number)
            } else if (data && data.type === 'ALI') {
              let pay_url = data.url;
              if (pay_url && pay_url.length > 10) {
                this.$message.success("正在跳转支付宝支付平台");
                window.location.href = pay_url
                // window.open(pay_url, '_blank', '');
              }
            } else {
              this.$message.error("支付获取失败 " + res.msg)
            }
          } else {
            this.$message.error("下订单异常，请联系管理员");
          }
        } else {
          this.$message.error("失败了 " + res.msg)
        }
      }, {
        methods: 'POST', data: {order_number: order.order_number},
      })
    },
    click_order_info(order) {
      if (order.status === 1 || order.status === 2) {
        my_order(res => {
          if (res.code === 1000) {
            this.get_data_from_tabname()
          } else {
            this.$message.error("失败了 " + res.msg)
          }
        }, {
          methods: 'PUT', data: {order_number: order.order_number, act: 'status'},
        });
      }
      this.show_order_info = true;
      this.current_order_info = order;

    },
    handleSizeChange(val) {
      this.pagination.pagesize = val;
      this.get_data_from_tabname({
        "size": this.pagination.pagesize,
        "page": 1
      })
    },
    handleCurrentChange(val) {
      this.pagination.currentPage = val;
      this.get_data_from_tabname({
        "size": this.pagination.pagesize,
        "page": this.pagination.currentPage
      })
    },

    get_data_from_tabname(data = {}) {
      data.order_id = this.order_id_seach.replace(/^\s+|\s+$/g, "");
      this.MyOrderFun(data)
    },

    format_payment_type(row) {
      return format_choices(row.payment_type, this.payment_type_choices)
    },

    format_status_type(row) {
      return format_choices(row.status, this.status_choices)
    },

    format_order_type(row) {
      return format_choices(row.order_type, this.order_type_choices)
    },

    format_actual_amount(row) {
      return '￥ ' + (row.actual_amount / 100).toString()
    },

    format_create_time(row) {
      return this.format_time(row.created_time)
    },

    format_pay_time(row) {
      return this.format_time(row.pay_time)
    },

    format_cancel_time(row) {
      return this.format_time(row.cancel_time)
    },

    format_time(stime) {
      if (stime) {
        stime = stime.split(".")[0].split("T");
        return stime[0] + " " + stime[1]
      } else
        return '';
    },
    MyOrderFun(params) {
      this.loading = true;
      my_order(data => {
        if (data.code === 1000) {
          this.order_info_list = data.data;
          this.pagination.total = data.count;
          this.payment_type_choices = data.payment_type_choices;
          this.status_choices = data.status_choices;
          this.order_type_choices = data.order_type_choices;
          if (this.order_info_list.length === 1) {
            this.current_order_info = this.order_info_list[0];
            let out_trade_no = this.$route.params.out_trade_no;
            if (out_trade_no) {
              this.goto_pay(this.current_order_info);
              this.$route.params.out_trade_no = undefined;
            }
          }
        } else if (data.code === 1008) {
          this.$message.error(data.msg);
        } else {
          this.$message.error("操作失败")
        }
        this.loading = false;
      }, {methods: 'GET', data: params})
    },
  }, mounted() {
    getUserInfoFun(this);
    let out_trade_no = this.$route.params.out_trade_no;
    if (out_trade_no) {
      this.order_id_seach = out_trade_no;
    }
    this.get_data_from_tabname();
  }, filters: {}
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

.icon-weixin {
  width: 137px;
  height: 35px;
  margin-left: 50px;
}

.code-wrap {
  width: 240px;
  height: 240px;
  border: 1px solid #c3c3c3;
  margin-top: 23px;
  margin-bottom: 20px;
}

.tip-btn {
  background: #2bbc4d;
  width: 240px;
  height: 60px;
}

.icon {
  width: 26px;
  height: 26px;
  background-size: 100%;
  display: inline-block;
  margin-right: 11px;
}

.text {
  font-family: PingFang-SC-Bold;
  font-size: 16px;
  color: #fff;
  letter-spacing: -.1px;
}

.pay_wx {
  display: flex;
  justify-content: center;
  align-items: center;
}

.order_text {
  font-family: PingFang-SC-Medium;
  font-size: 14px;
  color: #787e85;
  letter-spacing: 0;
  vertical-align: text-top;
}

.amount {
  font-family: Avenir-Heavy;
  font-size: 24px;
  color: #ff8000;
  letter-spacing: 0;
}
</style>
