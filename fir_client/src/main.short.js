import Vue from 'vue'
import Download from "@/Download";
import router from "@/router/download";

import 'element-ui/lib/theme-chalk/index.css'
import {
    Button,
    Input,
    Container,
    Main,
    Message,
    Link,
    Divider

} from "element-ui";

Vue.use(Link);
Vue.use(Input);
Vue.use(Button);
Vue.use(Container);
Vue.use(Main);
Vue.use(Divider);
Vue.prototype.$message = Message;


Vue.config.productionTip = false;

new Vue({
    render: h => h(Download),
    router,
}).$mount('#download');
