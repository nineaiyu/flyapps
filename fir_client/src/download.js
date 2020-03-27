import Vue from 'vue'
import App from "@/App";
import router from "@/router";
import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import Vuex from 'vuex'
const qiniu = require('qiniu-js');
Vue.prototype.qiniu = qiniu;

//使用vue-cookies
import VueCookies from 'vue-cookies'

Vue.use(VueCookies);

//导入全局的geetest.js
import './assets/gt'


//导入store实例
import store from "./store";

//全局导航守卫
router.beforeEach((to, from, next) => {
    // ...

    if (VueCookies.isKey('access_token')) {
        let user = {
            username: VueCookies.get('username'),
            shop_cart_num: VueCookies.get('shop_cart_num'),
            access_token: VueCookies.get('access_token'),
            avatar: VueCookies.get('avatar'),
            notice_num: VueCookies.get('notice_num')
        };
        store.dispatch('getUser', user)
    }
    next()

});


Vue.config.productionTip = false;

Vue.use(ElementUI);
Vue.use(Vuex);


new Vue({
    render: h => h(App),
    router,
    store,
}).$mount('#app');
