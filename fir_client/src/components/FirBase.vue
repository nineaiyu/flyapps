<template>
    <div ref="appbase">
        <el-dialog
                title="绑定域名"
                :visible.sync="bind_domain_sure"
                width="30%">

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
                        <h3>还差一步绑定成功</h3>
                        请联系域名管理员，前往 {{ domain_name }} 域名 DNS 管理后台添加如下 CNAME 记录。
                        <el-table
                                :data="domain_tData"
                                border
                                style="width: 100%">
                            <el-table-column
                                    prop="type"
                                    label="记录类型"
                                    width="100">
                            </el-table-column>
                            <el-table-column
                                    prop="host"
                                    label="主机记录"
                                    width="180">
                            </el-table-column>
                            <el-table-column
                                    prop="dns"
                                    label="记录值">
                            </el-table-column>
                        </el-table>
                        <el-alert title="请在域名DNS配置成功后，点击“下一步”按钮"
                                  style="margin-top: 30px"
                                  type="warning"
                                  :closable="false"
                                  show-icon/>
                    </div>
                </div>
            </div>

            <span slot="footer" class="dialog-footer">
                            <el-button style="margin-top: 12px;" @click="last">上一步</el-button>
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
                        <span :underline="false" class="domian-tip-bar">应用分发请绑定您自己的域名，平台域名可能会随时更换，将导致您的应用无法访问</span>
                        <el-button size="medium">立即绑定</el-button>
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

    export default {
        name: "FirBase",
        components: {FirFooter, FirHeader, BackToTop},
        data() {
            return {
                mousePosition: {},
                bind_domain_sure: true,
                active: 1,
                domain_name: '',
                domain_tData: [{'type': 'CNAME', 'host': 'xxx', 'dns': 'sdfsaf'}],
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
        }
        , methods: {
            next() {
                if (this.active++ > 2) this.active = 3;
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
