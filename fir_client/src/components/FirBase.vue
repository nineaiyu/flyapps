<template>
  <div ref="appbase">
    <el-dialog
        :close-on-click-modal="false"
        :close-on-press-escape="false"
        :title="bind_domain_title"
        :visible.sync="bind_domain_sure"
        width="666px">
      <bind-domain v-if="bind_domain_sure" :domain_type="bind_domain_type"
                   :transitionName="`bind-user-domain`+ bind_domain_type"/>
    </el-dialog>
    <canvas ref="canvas" class="canvas" @mouseleave="canvas_leave" @mousemove="canvas_move"/>
    <el-container>
      <div v-if="$store.state.show_domain_msg" style="margin: -5px 20px">
        <el-alert
            :closable="false"
            center
            effect="dark"
            type="error">
          <div slot="title">
            <span class="domian-tip-bar">应用分发请绑定您自己的域名，平台分发域名可能因不可违因素更换，将导致您的应用无法访问</span>
            <el-button size="small" @click="bind_domain_type=1,bind_domain_sure=true">立即绑定</el-button>
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
      <el-tooltip content="回到顶部" placement="top">
        <back-to-top :back-position="50" :custom-style="myBackToTopStyle" :visibility-height="300"
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
      bind_domain_title: '绑定下载页域名',
      bind_domain_type: 1,
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
        if (this.$store.state.domain_action === 2) {
          this.bind_domain_title = '绑定下载码域名';
          this.bind_domain_type = 0
        } else {
          this.bind_domain_title = '绑定下载页域名';
          this.bind_domain_type = 1
        }
        this.$store.dispatch("dodomainaction", 0);
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
/deep/ .el-alert{
  padding: 2px 16px;
}
</style>
