<template>
  <el-container>
    <div style="background-color:rgba(162, 193, 230, 0.18);">
      <el-header class="header">
        <el-row :gutter="12">
          <el-col :span="12">
            <el-image :src="require('@/assets/logo.png')" alt="logo" class="logo img"/>
          </el-col>
          <el-col :offset="12" :span="12">
            <el-row :gutter="12" class="nav">
              <el-col :span="8">
                <el-link @click="$router.push({name:'FirIndex'})">首页</el-link>
              </el-col>
              <el-col :span="8">
                <el-link @click="$router.push({name:'FirService'})">服务</el-link>
              </el-col>
              <el-col :span="8">
                <el-link @click="$router.push({name:'FirNews'})">新闻</el-link>
              </el-col>
              <el-col :span="8">
                <el-link @click="$router.push({name:'FirApps'})">登录</el-link>
              </el-col>
              <el-col :span="8">
                <el-link @click="$router.push({name:'FirContact'})">联系我们</el-link>
              </el-col>
              <el-col :span="8">
                <el-link @click="github">Github</el-link>
              </el-col>
            </el-row>
          </el-col>
        </el-row>
      </el-header>
    </div>

    <div>
      <router-view/>
    </div>
    <el-tooltip content="回到顶部" placement="top">
      <back-to-top :back-position="50" :custom-style="myBackToTopStyle" :visibility-height="300"
                   transition-name="fade"/>
    </el-tooltip>
    <el-footer>
      <el-divider/>
      <FirFooter/>
    </el-footer>
  </el-container>
</template>

<script>
import FirFooter from "@/components/FirFooter";
import BackToTop from "@/components/base/BackToTop";

export default {
  name: "FirIndex",
  components: {FirFooter, BackToTop},
  data() {
    return {
      myBackToTopStyle: {
        right: '80px',
        bottom: '100px',
        width: '40px',
        height: '40px',
        'border-radius': '4px',
        'line-height': '45px',
        background: '#e7eaf1'
      },
    }
  }, methods: {
    github() {
      window.open('https://github.com/nineaiyu/FlyApps', '_blank', '');
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
}

.header {
  width: 100%;
  height: 120px;
}

.header .img {
  width: 300px;
  height: 85px;
  padding-left: 100px;
  padding-top: 8px;
}

.header .logo {
  float: left;
}

.header .nav {
  float: right;
  padding-right: 80px;

}

.header .nav .el-col {
  margin-right: 20px;
  float: left;
  list-style: none;
  width: 80px;
  height: 60px;
  line-height: 100px;
  color: #7d7d7d;
  font-size: 15px;
  font-weight: bolder;
}

.header .nav .el-link:hover {
  color: #47477d;
  font-size: 16px;
  cursor: pointer;
  touch-action: manipulation;

}

</style>
