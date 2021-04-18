import Vue from 'vue'
import App from "@/App";
import router from "@/router";
// import ElementUI from 'element-ui'
import 'element-ui/lib/theme-chalk/index.css'
import Vuex from 'vuex'
import qiniu from 'qiniu-js'
import oss from 'ali-oss'
//使用vue-cookies
import VueCookies from 'vue-cookies'
//导入store实例
import store from "@/store";
import {
    Aside,
    Avatar,
    Breadcrumb,
    BreadcrumbItem,
    Button,
    ButtonGroup,
    Card,
    Checkbox,
    CheckboxGroup,
    Col,
    Container,
    DatePicker,
    Dialog,
    Divider,
    Dropdown,
    DropdownItem,
    DropdownMenu,
    Footer,
    Form,
    FormItem,
    Header,
    Image,
    Input,
    InputNumber,
    Link,
    Loading,
    Main,
    Message,
    MessageBox,
    Notification,
    Option,
    OptionGroup,
    Pagination,
    Popover,
    Progress,
    RadioButton,
    RadioGroup,
    Row,
    Select,
    Slider,
    Switch,
    Table,
    TableColumn,
    TabPane,
    Tabs,
    Tag,
    Timeline,
    TimelineItem,
    Tooltip,
    Upload,
    Radio,
} from "element-ui";
import VueLazyload from 'vue-lazyload'
// 引入点击复制组件
import VueClipboard from 'vue-clipboard2'

// const qiniu = require('qiniu-js');
//
Vue.prototype.qiniu = qiniu;
Vue.prototype.oss = oss;

Vue.use(VueCookies);


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
        store.dispatch('doUserinfo', user)
    }
    next()

});


Vue.config.productionTip = false;

Vue.use(Progress);
Vue.use(OptionGroup);
Vue.use(Link);
Vue.use(Timeline);
Vue.use(TimelineItem);
Vue.use(Card);
Vue.use(RadioButton);
Vue.use(RadioGroup);
Vue.use(Avatar);
Vue.use(DropdownItem);
Vue.use(BreadcrumbItem);
Vue.use(Slider);
Vue.use(DropdownMenu);
Vue.use(Dropdown);
Vue.use(Breadcrumb);
Vue.use(Input);
Vue.use(CheckboxGroup);
Vue.use(DatePicker);
Vue.use(Button);
Vue.use(ButtonGroup);
Vue.use(Container);
Vue.use(Aside);
Vue.use(Col);
Vue.use(Header);
Vue.use(Popover);
Vue.use(Main);
Vue.use(Dialog);
Vue.use(Checkbox);
Vue.use(Pagination);
Vue.use(Select);
Vue.use(Option);
Vue.use(Table);
Vue.use(TableColumn);
Vue.use(Upload);
Vue.use(Tabs);
Vue.use(TabPane);
Vue.use(Form);
Vue.use(FormItem);
Vue.use(Divider);
Vue.use(Row);
Vue.use(Image);
Vue.use(Loading);
Vue.use(Tag);
Vue.use(Tooltip);
Vue.use(Switch);
Vue.use(Footer);
Vue.use(InputNumber);
Vue.use(Radio);
Vue.prototype.$message = Message;
Vue.prototype.$notify = Notification;
Vue.prototype.$loading = Loading.service;
Vue.prototype.$confirm = MessageBox.confirm;
Vue.prototype.$prompt = MessageBox.prompt;
Vue.prototype.$alert = MessageBox.alert;

// Vue.use(ElementUI);
Vue.use(Vuex);

Vue.use(VueLazyload, {
    loading: require('@/assets/loading.gif'),
    preLoad: 1
});

VueClipboard.config.autoSetContainer = true;
Vue.use(VueClipboard);

new Vue({
    render: h => h(App),
    router,
    store,
}).$mount('#app');
