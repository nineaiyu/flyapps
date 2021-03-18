import Vue from 'vue'
import Download from "@/Download";
import router from "@/router/short";

import VueLazyload from 'vue-lazyload'

Vue.use(VueLazyload, {
    loading: require('./assets/loading.gif'),
    preLoad: 1
});
Vue.config.productionTip = false;

new Vue({
    render: h => h(Download),
    router,
}).$mount('#download');
