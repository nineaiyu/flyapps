<template>
  <div class="ContactUs">
    <div>
      <h3>联系我们</h3>
      <p style="color:#b2b2b2">Contact us</p>
    </div>


    <div class="content">
      <div class="item"><p>技术咨询</p>
      </div>
      <el-divider direction="vertical"/>
      <div class="item"><p>商务合作</p>
      </div>
      <el-divider direction="vertical"/>
      <div class="item"><p style="margin-bottom: 16px">应用举报</p>
      </div>
      <div>
        <el-link :href="github" :underline="false"><p><b>FlyApps</b></p></el-link>
      </div>
      <el-divider/>
      <el-tooltip content="拿出手机扫一扫" style="margin-top: 33px">
        <el-image :alt="github" :lazy="true" :src="require('@/assets/github.png')"
                  style="width: 160px">
        </el-image>
      </el-tooltip>

    </div>
  </div>
</template>

<script>
export default {
  name: "FirContact",
  data() {
    return {
      bg_img: require("@/assets/imgs/banner_1.jpg"),
      github: process.env.base_env.github
    }
  },
}
</script>

<style scoped>
.ContactUs {
  text-align: center;

}

.content {
  width: 942px;
  margin: 10px auto 160px;
  text-align: center;
}

.item {
  display: inline-block;
  font-size: 14px;
  text-align: left;
}

.item p {
  font-size: 16px;
  color: #8C9293;
}

.item p b {
  font-size: 30px;
  color: #313639;
  font-weight: 400;
  letter-spacing: 2.5px;
}

</style>
