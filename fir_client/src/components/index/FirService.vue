<template>
  <div class="Service">
    <div>
      <h3>我们的服务</h3>
      <p style="color:#b2b2b2">The Best Service You Never See</p>
    </div>
    <div class="Service-container">
      <transition name="el-zoom-in-center">
        <el-row v-show="show" :gutter="20">
          <el-col v-for="(item,index) in serviceList" :key="index" :span="6">
            <div class="Service-item Service-item-wrapper">
              <div class="Service-item-top">
                <h4>{{ item.title }}</h4>
                <i/>
                <p>{{ item.eng_title }}</p>
              </div>
              <div class="Service-item-img">
                <img :src="item.img" alt="服务">
              </div>
              <div class="Service-item-border"></div>
            </div>

          </el-col>
        </el-row>
      </transition>

    </div>
  </div>
</template>

<script>
export default {
  name: "FirService",
  data() {
    return {
      show: false,
      serviceList: [
        {
          id: 'section-1',
          title: '高性能应用分发',
          eng_title: 'High performance app distribution',
          img: require('@/assets/imgs/service1.jpg')
        }, {
          id: 'section-2',
          title: 'iOS超级签名',
          eng_title: 'IOS super signature',
          img: require('@/assets/imgs/service2.jpg')
        }, {
          id: 'section-3',
          title: '多维下载权限',
          eng_title: 'Multi download permission',
          img: require('@/assets/imgs/service3.jpg')
        }, {
          id: 'section-4',
          title: '应用自定义域名',
          eng_title: 'Custom domain name',
          img: require('@/assets/imgs/service4.jpg')
        }
      ]
    }
  },
  mounted() {
    this.show = true;
  }
}
</script>

<style scoped>
.Service {
  text-align: center;
}

.Service-container {
  width: 1170px;
  padding: 30px 50px;
  margin-right: auto;
  margin-left: auto;
}

.Service-item {
  margin-bottom: 50px;
}

.Service-item-wrapper {
  cursor: pointer;
  background: rgba(244, 244, 244, 1);
  overflow: hidden;
  position: relative;
}

.Service-item-top {
  width: 100%;
  height: 120px;
  /*padding: 30px;*/
  text-align: center;
}

.Service-item-top > i {
  display: inline-block;
  width: 25px;
  height: 2px;
  background: #28f;
}

.Service-item-top > p {
  color: #b2b2b2;
  opacity: 0;
  transform: translateY(10px);
  transition: all .5s ease;
}

.Service-item-img {
  width: 100%;
  overflow: hidden;
}

.Service-item-img img {
  width: 100%;
  transition: all 0.5s ease;
}

.Service-item-border {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  margin: auto;
  z-index: 9999999;
  width: 100%;
  height: 100%;
  transition: all 0.5s ease;
  border: 1px solid #000;
  opacity: 0;
}

.Service-item-wrapper:hover .Service-item-top > i {
  opacity: 0;
}

.Service-item-wrapper:hover .Service-item-top > p {
  opacity: 1;
  transform: translateY(-10px);
}

.Service-item-wrapper:hover .Service-item-img > img {
  transform: scale(1.1, 1.1);
}

.Service-item-wrapper:hover > .Service-item-border {
  /*opacity: 1;*/
  width: 90%;
  height: 90%;
}
</style>
