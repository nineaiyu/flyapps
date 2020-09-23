import Vue from 'vue'
//1.先导入
import VueRouter from 'vue-router'
//2.一定先use 一下
Vue.use(VueRouter);

// 解决push 同一个路由的错误
const originalPush = VueRouter.prototype.push;
VueRouter.prototype.push = function push(location) {
    return originalPush.call(this, location).catch(err => err)
};

// import FirDownload from "@/components/FirDownload";
const router = new VueRouter({
    mode: 'history',
    routes: [
        {
            path: '/:short',
            name: 'FirDownload',
            // component: () => import("@/components/ShortDownload")
            component: ()=>import("@/components/FirDownload")
        }
    ]
});

export default router;
