<template>
    <div ref="appbase">
        <el-dialog
                title="绑定下载页域名"
                :close-on-click-modal="false"
                :close-on-press-escape="false"
                :visible.sync="bind_domain_sure"
                width="666px">
            <bind-domain transitionName="bind-user-domain"/>
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
                        <span :underline="false"
                              class="domian-tip-bar">应用分发请绑定您自己的域名，平台分发域名可能因不可违因素更换，将导致您的应用无法访问</span>
                        <el-button size="medium" @click="bind_domain_sure=true">立即绑定</el-button>
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
    import BindDomain from "@/components/base/BindDomain";
    import {show_beautpic,} from "@/utils";

    export default {
        name: "FirBase",
        components: {FirFooter, FirHeader, BackToTop, BindDomain},
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
            '$store.state.userinfo': function () {
                if (this.$store.state.userinfo.domain_name) {
                    this.$store.dispatch("dodomainshow", false);
                } else {
                    this.$store.dispatch("dodomainshow", true);
                }
            },
            '$store.state.domain_action': function () {
                if (this.$store.state.domain_action) {
                    this.$store.dispatch("dodomainaction", false);
                    this.bind_domain_sure = true;
                }
            },
        }
        , methods: {
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
