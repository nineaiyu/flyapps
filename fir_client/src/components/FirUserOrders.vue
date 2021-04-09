<template>
    <el-main>


        <el-dialog title="微信支付，请扫描进行支付，支付完成之后，将订单进行关联"
                   :visible.sync="wx_pay"
                   width="880px"
                   :close-on-click-modal="false"
                   :close-on-press-escape="false"
                   center
        >
            <el-row :gutter="8">
                <el-col :span="12" style="text-align: center">
                    <el-image :src="require('../assets/wx_pay.jpg')" style="width: 320px;height: 320px"
                              fit="fit"></el-image>
                    <el-link>用微信扫描二维码</el-link>
                </el-col>
                <el-col :span="12">
                    <el-link type="warning"> 支付完成之后，打开订单详情，将订单编号复制出来，进行绑定</el-link>
                    <div style="margin-top: 20px">
                        <el-input style="width: 55%"
                                  placeholder="订单编号"
                                  v-model="sure_order_info.wx_order_id">
                        </el-input>
                        <el-button style="margin-left: 20px" @click="sure_order">查询</el-button>
                        <el-button style="margin-left: 10px" @click="sure_order">关联</el-button>
                    </div>
                </el-col>
            </el-row>

        </el-dialog>

        <el-dialog
                :visible.sync="show_order_info"
                width="780px"
                :close-on-click-modal="false"
                :close-on-press-escape="false"
                title="订单详情"
                top="6vh"
                center>
            <div>

                <el-form :model="current_order_info"
                         label-width="80px" style="margin:0 auto;">

                    <el-form-item label-width="110px" label="平台订单ID">
                        <el-input :value="current_order_info.order_number"/>
                    </el-form-item>


                    <el-form-item label-width="110px" label="第三方订单ID">
                        <el-input :value="current_order_info.payment_number"/>
                    </el-form-item>

                    <el-form-item label-width="110px" label="付款方式">
                        <el-input :value="format_payment_type(current_order_info)"/>
                    </el-form-item>
                    <el-form-item label-width="110px" label="订单状态">
                        <el-input :value="format_status_type(current_order_info)"/>
                    </el-form-item>

                    <el-form-item label-width="110px" label="订单类型">
                        <el-input :value="format_order_type(current_order_info)"/>
                    </el-form-item>
                    <el-form-item label-width="110px" label="实付金额">
                        <el-input :value="format_actual_amount(current_order_info)"/>
                    </el-form-item>

                    <el-form-item label-width="110px" label="购买数量">
                        <el-input
                                :value="current_order_info.actual_download_times"/>
                    </el-form-item>

                    <el-form-item label-width="110px" label="赠送数量">
                        <el-input
                                :value="current_order_info.actual_download_gift_times"/>
                    </el-form-item>

                    <el-form-item label-width="110px" label="订单创建时间">
                        <el-input :value="format_create_time(current_order_info)"/>
                    </el-form-item>

                    <el-form-item label-width="110px" label="订单支付时间">
                        <el-input :value="format_pay_time(current_order_info)"/>
                    </el-form-item>

                    <el-form-item label-width="110px" label="订单取消时间">
                        <el-input :value="format_cancel_time(current_order_info)"/>
                    </el-form-item>


                    <el-form-item label-width="110px" label="备注">
                        <el-input :value="current_order_info.description"/>
                    </el-form-item>

                </el-form>


            </div>


            <span slot="footer">
                        如对订单有疑问，请联系 nineven@qq.com
                    </span>
        </el-dialog>


        <div>
            <el-input
                    style="width: 30%;margin-right: 30px;margin-bottom: 10px"
                    v-model="order_id_seach"
                    clearable
                    placeholder="输入订单ID"/>
            <el-button type="primary" icon="el-icon-search" @click="handleCurrentChange(pagination.currentPage)">
                搜索
            </el-button>

            <el-table
                    :data="order_info_list"
                    v-loading="loading"
                    border
                    stripe
                    style="width: 100%">

                <el-table-column
                        fixed
                        prop="order_number"
                        label="系统订单ID">

                </el-table-column>

                <el-table-column
                        prop="status"
                        label="状态"
                        align="center"
                        width="130">

                    <template slot-scope="scope">
                        <div v-if="scope.row.status === 1">
                            <el-button @click="goto_pay(scope.row)"
                                       type="primary" size="small"> 去支付
                            </el-button>
                        </div>
                        <div v-else-if="scope.row.status === 0">
                            <el-button @click="click_order_info(scope.row)"
                                       type="success" size="small"> {{ format_status_type(scope.row)}}
                            </el-button>
                        </div>
                        <div v-else-if="scope.row.status === 4 || scope.row.status ===5">
                            <el-button @click="click_order_info(scope.row)"
                                       type="danger" size="small"> {{ format_status_type(scope.row)}}
                            </el-button>
                        </div>
                        <div v-else>
                            <el-button @click="click_order_info(scope.row)"
                                       type="warning" size="small"> {{ format_status_type(scope.row)}}
                            </el-button>
                        </div>


                    </template>


                </el-table-column>

                <el-table-column
                        :formatter="format_actual_amount"
                        prop="actual_amount"
                        label="实付金额"
                        width="100">
                </el-table-column>


                <el-table-column
                        prop="actual_download_times"
                        label="购买数量"
                        width="120">
                </el-table-column>

                <el-table-column
                        prop="actual_download_gift_times"
                        label="赠送数量"
                        width="100">
                </el-table-column>

                <el-table-column
                        :formatter="format_create_time"
                        prop="created_time"
                        label="订单创建时间"
                >
                </el-table-column>

                <el-table-column
                        fixed="right"
                        label="查看详细"
                        width="100">
                    <template slot-scope="scope">

                        <el-button
                                size="mini"
                                @click="click_order_info(scope.row)">详情
                        </el-button>

                    </template>
                </el-table-column>
            </el-table>


        </div>
        <div style="margin-top: 20px;margin-bottom: 20px">
            <el-pagination
                    @size-change="handleSizeChange"
                    @current-change="handleCurrentChange"
                    :current-page.sync="pagination.currentPage"
                    :page-sizes="[10, 20, 50, 100]"
                    :page-size="pagination.pagesize"
                    layout="total,sizes, prev, pager, next"
                    :total="pagination.total">
            </el-pagination>
        </div>
    </el-main>
</template>

<script>

    import {my_order, userinfos} from "../restful";

    export default {
        name: "FirUserOrders",
        data() {
            return {
                order_info_list: [],
                order_id_seach: "",
                pagination: {"currentPage": 1, "total": 0, "pagesize": 10},
                order_type_choices: [],
                status_choices: [],
                payment_type_choices: [],
                show_order_info: false,
                current_order_info: {},
                wx_pay: false,
                sure_order_info: {wx_order_id: ''},
                loading: false
            }
        },
        methods: {
            sure_order() {
                my_order(res => {
                    // 应该跳转到第三方平台进行支付，然后第三方回调
                    if (res.code === 1000) {
                        this.$message.success("支付成功");
                        this.get_data_from_tabname({
                            "size": this.pagination.pagesize,
                            "page": this.pagination.currentPage
                        });
                    } else {
                        this.$message.error("失败了 " + res.msg)
                    }
                }, {
                    methods: 'PUT', data: {sure_order_info: this.sure_order_info},
                })
            },
            goto_pay(order) {
                this.wx_pay = true;
                this.sure_order_info.order_number = order.order_number;
                // my_order(res => {
                //     // 应该跳转到第三方平台进行支付，然后第三方回调
                //     if (res.code === 1000) {
                //         this.$message.success("支付成功");
                //         this.get_data_from_tabname({
                //             "size": this.pagination.pagesize,
                //             "page": this.pagination.currentPage
                //         });
                //     } else {
                //         this.$message.error("失败了 " + res.msg)
                //     }
                // }, {
                //     methods: 'PUT', data: {order_number: order.order_number},
                // })
            },
            click_order_info(order) {
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

            format_choices(key, obj) {
                for (let i = 0; i < obj.length; i++) {
                    if (key === obj[i].id) {
                        return obj[i].name
                    }
                }
                return "未知"
            },

            format_payment_type(row) {
                return this.format_choices(row.payment_type, this.payment_type_choices)
            },

            format_status_type(row) {
                return this.format_choices(row.status, this.status_choices)
            },

            format_order_type(row) {
                return this.format_choices(row.order_type, this.order_type_choices)
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

                    } else if (data.code === 1008) {
                        this.$message.error(data.msg);
                    } else {
                        this.$message.error("操作失败")
                    }
                    this.loading = false;
                }, {methods: 'GET', data: params})
            },
            getUserInfoFun() {
                userinfos(data => {
                    if (data.code === 1000) {
                        this.$store.dispatch("doUserinfo", data.data);
                    } else {
                        this.$message.error("用户信息获取失败")
                    }
                }, {"methods": "GET"})
            },

        }, mounted() {
            this.getUserInfoFun();
            this.get_data_from_tabname()
        }, filters: {}
    }
</script>

<style scoped>
    .el-main {
        margin: 10px auto 100px;
        width: 1166px;
        position: relative;
        padding-bottom: 1px;
        background-color: #bfe7f9;
        color: #9b9b9b;
        -webkit-font-smoothing: antialiased;
        border-radius: 1%;
    }

</style>
