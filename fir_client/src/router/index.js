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


// import FirIndex from "@/components/FirIndex";
// import FirApps from "@/components/FirApps";
// import FirLogin from "@/components/FirLogin";
// import FirRegist from "@/components/FirRegist";
// import FirDownload from "@/components/FirDownload";
// import FirAppBase from "@/components/FirAppBase";
// import FirAppInfosBase from "@/components/FirAppInfosBase";
// import FirAppInfostimeline from "@/components/FirAppInfostimeline";
// import FirAppInfosbaseinfo from "@/components/FirAppInfosbaseinfo";
// import FirAppInfossecurity from "@/components/FirAppInfossecurity";
// import FirAppInfosdevices from "@/components/FirAppInfosdevices";
// import FirAppInfoscombo from "@/components/FirAppInfoscombo";
// import FirUserProfileBase from "@/components/FirUserProfileBase";
// import FirUserProfileInfo from "@/components/FirUserProfileInfo";
// import FirUserProfileChangePwd from "@/components/FirUserProfileChangePwd";
// import FirUserProfileStorage from "@/components/FirUserProfileStorage";
//
// import FirSuperSignBase from "@/components/FirSuperSignBase";

const router = new VueRouter({
    mode: 'history',
    routes: [
        {
            path: '/',
            name: 'Index',
            redirect: {name: 'FirIndex'}
        },
        {
            path: '/index',
            name: 'FirIndex',
            component: () => import("@/components/FirIndex")
        },
        {
            path: '/apps',
            // component: FirAppBase,
            component: () => import("@/components/FirAppBase"),

            children: [
                {
                    path: '',
                    name: 'FirApps',
                    component: () => import("@/components/FirApps"),
                }
                ,
                {
                    path: ':id',
                    // component: FirAppInfosBase,
                    component: () => import("@/components/FirAppInfosBase"),

                    children: [
                        {
                            path: '',
                            name: 'FirAppInfostimeline',
                            // component: FirAppInfostimeline,
                            component: () => import("@/components/FirAppInfostimeline"),

                        }
                        ,
                        {
                            path: 'info',
                            name: 'FirAppInfosbaseinfo',
                            // component: FirAppInfosbaseinfo,
                            component: () => import("@/components/FirAppInfosbaseinfo"),

                        },
                        {
                            path: 'security',
                            name: 'FirAppInfossecurity',
                            // component: FirAppInfossecurity
                            component: () => import("@/components/FirAppInfossecurity"),

                        },
                        {
                            path: 'devices',
                            name: 'FirAppInfosdevices',
                            // component: FirAppInfosdevices
                            component: () => import("@/components/FirAppInfosdevices"),

                        },
                        {
                            path: 'combo',
                            name: 'FirAppInfoscombo',
                            // component: FirAppInfoscombo,
                            component: () => import("@/components/FirAppInfoscombo"),

                        }
                    ]
                }
            ]
        },
        {
            path: '/user',
            // component: FirAppBase,
            component: () => import("@/components/FirAppBase"),

            children: [
                {
                    path: '',
                    // component: FirUserProfileBase,
                    component: () => import("@/components/FirUserProfileBase"),

                    children: [
                        {
                            path: 'info',
                            name: 'FirUserProfileInfo',
                            // component: FirUserProfileInfo,
                            component: () => import("@/components/FirUserProfileInfo"),

                        }, {
                            path: 'setpasswd',
                            name: 'FirUserProfileChangePwd',
                            // component: FirUserProfileChangePwd
                            component: () => import("@/components/FirUserProfileChangePwd"),

                        }, {
                            path: 'storage',
                            name: 'FirUserProfileStorage',
                            // component: FirUserProfileStorage
                            component: () => import("@/components/FirUserProfileStorage"),

                        }
                    ]
                }

            ]
        },
        {
            path: '/login',
            name: 'FirLogin',
            // component: FirLogin
            component: () => import("@/components/FirLogin"),

        },
        {
            path: '/supersign',
            // component: FirAppBase,
            component: () => import("@/components/FirAppBase"),

            children: [
                {
                    path: ':act',
                    name: 'FirSuperSignBase',
                    // component: FirSuperSignBase,
                    component: () => import("@/components/FirSuperSignBase"),

                }
            ]
        },
        {
            path: '/register',
            name: 'FirRegist',
            // component: FirRegist
            component: () => import("@/components/FirRegist"),

        },
        {
            path: '/:short',
            name: 'FirDownload',
            // component: FirDownload
            component: () => import("@/components/FirDownload"),

        },

    ]
});


export default router;
