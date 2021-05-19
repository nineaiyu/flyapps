<template>
    <div ref="appbase">
        <el-dialog
                title="绑定下载页域名"
                :close-on-click-modal="false"
                :close-on-press-escape="false"
                :visible.sync="bind_domain_sure"
                width="666px">

            <div style="margin: 5px 20px">
                <el-steps :active="active" finish-status="success">
                    <el-step title="步骤 1">

                    </el-step>
                    <el-step title="步骤 2">
                    </el-step>
                    <el-step title="步骤 3"></el-step>
                </el-steps>
                <div style="margin-top: 20px">
                    <div v-if="active===1">
                        <h2>你的二级域名</h2>
                        <el-input clearable autofocus v-model="domain_name"></el-input>
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
                                    prop="type"
                                    label="记录类型"
                                    align="center"
                                    width="100">
                            </el-table-column>
                            <el-table-column
                                    prop="host"
                                    align="center"
                                    label="主机记录"
                            >
                            </el-table-column>
                            <el-table-column
                                    prop="dns"
                                    align="center"
                                    label="记录值"
                                    width="300">
                            </el-table-column>
                        </el-table>
                        <el-alert title="请在域名DNS配置成功后，点击“下一步”按钮"
                                  style="margin-top: 30px"
                                  type="warning"
                                  :closable="false"
                                  show-icon/>
                    </div>
                    <div v-else-if="active===3">
                        <div v-if="!bind_status">
                            <div style="text-align: center;margin: 20px 0">
                                <el-link :underline="false" type="danger"
                                         style="font-size: x-large">绑定失败
                                </el-link>
                            </div>

                            <p style="margin: 10px 0">您的账户正在绑定域名：<strong>{{ domain_name }}</strong></p>
                            <el-row>
                                <el-col :span="16"><p>系统未检出到您的CNAME记录，请检查您的配置。</p></el-col>
                                <el-col :span="6">
                                    <el-button type="danger" size="small" plain style="margin-top: 8px"
                                               @click="remove_domain">
                                        解除绑定
                                    </el-button>
                                </el-col>
                            </el-row>
                        </div>

                        <div v-else>
                            <div style="text-align: center;margin: 20px 0">
                                <el-link :underline="false" type="success"
                                         style="font-size: x-large">绑定成功
                                </el-link>
                            </div>

                            <el-row>
                                <el-col :span="16"><p>您的账户已绑定域名：<strong>{{ domain_name }}</strong></p></el-col>
                                <el-col :span="6">
                                    <el-button type="danger" size="small" plain style="margin-top: 8px"
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
                                    prop="type"
                                    label="记录类型"
                                    align="center"
                                    width="100">
                            </el-table-column>
                            <el-table-column
                                    prop="host"
                                    align="center"
                                    label="主机记录"
                            >
                            </el-table-column>
                            <el-table-column
                                    prop="dns"
                                    align="center"
                                    label="记录值"
                                    width="300">
                            </el-table-column>
                        </el-table>
                        <div v-if="!bind_status" style="text-align: center;margin: 30px 0">
                            <el-button @click="check_cname" type="success" plain>已经修改配置，再次检查绑定</el-button>
                        </div>
                    </div>

                </div>
            </div>

            <span slot="footer" class="dialog-footer" v-if="active!==3">
                            <el-button style="margin-top: 12px;" @click="last"
                                       :disabled="bind_status|| active===1 ">上一步</el-button>
            <el-button style="margin-top: 12px;" @click="next">下一步</el-button>

                    </span>
        </el-dialog>

        <canvas ref="canvas" class="canvas" @mousemove="canvas_move" @mouseleave="canvas_leave"/>
        <el-container>
            <div style="margin: -5px 20px" v-if="$store.state.show_domain_msg">
                <el-alert
                        center
                        type="error"
                        :closable="false"
                        effect="dark">
                    <div slot="title">
                        <span :underline="false" class="domian-tip-bar">应用分发请绑定您自己的域名，平台分发域名可能因不可违因素更换，将导致您的应用无法访问</span>
                        <el-button size="medium" @click="bind_click">立即绑定</el-button>
                    </div>
                </el-alert>
            </div>
            <el-header>
                <FirHeader/>
            </el-header>
            <div class="pbody">
                <router-view/>
            </div>
            <el-footer>
                <el-divider/>
                <FirFooter/>
            </el-footer>
            <el-tooltip placement="top" content="回到顶部">
                <back-to-top :custom-style="myBackToTopStyle" :visibility-height="300" :back-position="50"
                             transition-name="fade"/>
            </el-tooltip>
        </el-container>
    </div>

</template>

<script>
    import FirHeader from "@/components/FirHeader";
    import FirFooter from "@/components/FirFooter";
    import BackToTop from "@/components/base/BackToTop";
    import {show_beautpic,} from "@/utils";
    import {domainFun} from "@/restful";

    export default {
        name: "FirBase",
        components: {FirFooter, FirHeader, BackToTop},
        data() {
            return {
                mousePosition: {},
                bind_domain_sure: false,
                active: 1,
                domain_name: '',
                bind_status: false,
                domain_tData: [{'type': 'CNAME', 'host': 'xxx', 'dns': 'demo.xxx.cn'}],
                myBackToTopStyle: {
                    right: '80px',
                    bottom: '100px',
                    width: '40px',
                    height: '40px',
                    'border-radius': '4px',
                    'line-height': '45px',
                    background: '#e7eaf1'
                }
            }
        },
        mounted() {
            let canvas = this.$refs.canvas;
            show_beautpic(this, canvas, 200);
        }, watch: {
            '$store.state.userinfo.domain_name': function () {
                if (this.$store.state.userinfo.domain_name) {
                    this.$store.dispatch("dodomainshow", false);
                } else {
                    this.$store.dispatch("dodomainshow", true);
                }
            },
            '$store.state.domain_action': function () {
                if (this.$store.state.domain_action) {
                    this.$store.dispatch("dodomainaction", false);
                    this.bind_click()
                }
            },
        }
        , methods: {
            check_cname() {
                domainFun(data => {
                    if (data.code === 1000) {
                        if (this.active++ > 2) this.active = 3;
                        this.bind_status = true;
                        this.$store.dispatch("dodomainshow", false);
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
                }, {methods: 'PUT', data: {}})
            },
            remove_domain() {
                domainFun(data => {
                    if (data.code === 1000) {
                        this.bind_status = false;
                        this.active = 1;
                        this.$message.success("解除绑定成功 ");
                        this.$store.dispatch("dodomainshow", true);
                    } else {
                        this.$message.error("解除绑定失败 " + data.msg)
                    }
                }, {methods: 'DELETE', data: {}});
            },
            bind_click() {
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
                }, {methods: 'GET', data: {}});
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
            next() {
                if (this.active === 1) {
                    domainFun(data => {
                        if (data.code === 1000) {
                            if (data.data && data.data.cname_domain) {
                                this.format_domain_tData(data.data.cname_domain);
                                if (this.active++ > 2) this.active = 3;
                            }
                        } else {
                            this.$message.error("绑定失败 " + data.msg)
                        }
                    }, {methods: 'POST', data: {domain_name: this.domain_name}})
                } else if (this.active === 2) {
                    this.check_cname()
                }
            },
            last() {
                if (this.active-- < 2) this.active = 1;
            },
            canvas_move(e) {
                this.mousePosition.x = e.pageX;
                this.mousePosition.y = e.pageY;
            },
            // eslint-disable-next-line no-unused-vars
            canvas_leave(e) {
                let canvas = this.$refs.canvas;
                this.mousePosition.x = canvas.width / 2;
                this.mousePosition.y = canvas.height / 2;
            },
        }
    }
</script>

<style scoped>
    .pbody {
        padding-top: 30px;
    }

    .domian-tip-bar {
        line-height: 43px;
        color: #fff;
        font-weight: 500;
        font-size: medium;
        margin-right: 20px;
    }
</style>
