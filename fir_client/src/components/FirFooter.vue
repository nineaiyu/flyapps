<template>
  <div class="ifooter">

    <div style="width: 300px; margin: 0 auto; padding: 5px 0;">
      <el-link :underline="false"> {{ footer.copyright }}</el-link>
    </div>
    <div style="width: 300px; margin: 0 auto; padding: 5px 0;">
      <a :href="footer.gongAnBeiAn.url"
         rel="noopener"
         style="display: inline-block; text-decoration: none; height: 20px; line-height: 20px;" target="_blank">
        <img alt="" src="@/assets/beianlogo.png" style="float: left;"/>
        <el-link :underline="false"
                 style="float: left; height: 20px; line-height: 20px; margin: 0 0 0 5px; color: #939393;">
          {{ footer.gongAnBeiAn.text }}
        </el-link>
      </a>

    </div>

    <div>
      <div style="width: 200px; margin: 0 auto; padding: 5px 0;">
        <el-link :href="footer.ipcBeiAn.url" :underline="false" rel="nofollow noopener"
                 target="_blank">{{ footer.ipcBeiAn.text }}
        </el-link>
      </div>
    </div>
  </div>
</template>

<script>
const footer = process.env.base_env.footer
export default {
  name: "FirFooter",
  data() {
    return {
      footer
    }
  }
}
</script>

<style scoped>
.ifooter {
  margin: 20px auto 100px;
  width: 1166px;
  text-align: center;
  font-size: 0;
  border-radius: 10px;
}

</style>
