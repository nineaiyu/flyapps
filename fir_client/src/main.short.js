import Vue from 'vue'
import Download from "@/Download";
import router from "@/router/download";

import 'element-ui/lib/theme-chalk/index.css'
import {
    Button,
    Container,
    Divider,
    Input,
    Link,
    Main,
    Message,
    Select,
    Option,
    Header,
    Form,
    FormItem,
    Row,
    Col,
    Notification
} from "element-ui";
import VueLazyload from 'vue-lazyload'

Vue.use(Link);
Vue.use(Input);
Vue.use(Button);
Vue.use(Container);
Vue.use(Main);
Vue.use(Divider);
Vue.use(Select);
Vue.use(Option);
Vue.use(Header);
Vue.use(Form);
Vue.use(FormItem);
Vue.use(Row);
Vue.use(Col);
Vue.prototype.$message = Message;
Vue.prototype.$notify = Notification;


Vue.config.productionTip = false;

Vue.use(VueLazyload, {
    loading: require('./assets/loading.gif'),
    preLoad: 1
});

new Vue({
    render: h => h(Download),
    router,
}).$mount('#download');
