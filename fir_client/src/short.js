import Vue from 'vue'
import Download from "@/Download";
import router from "@/router/short";


Vue.config.productionTip = false;

new Vue({
    render: h => h(Download),
    router,
}).$mount('#download');
