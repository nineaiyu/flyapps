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

                        },
                        {
                            path: 'supersign',
                            name: 'FirAppInfossupersign',
                            // component: FirAppInfossupersign,
                            component: () => import("@/components/FirAppInfossupersign"),

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
                            path: 'certification',
                            name: 'FirUserProfileCertification',
                            component: () => import("@/components/FirUserProfileCertification"),

                        },
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
            path: '/storage',
            // component: FirAppBase,
            component: () => import("@/components/FirAppBase"),

            children: [
                {
                    path: ':act',
                    name: 'FirUserStorage',
                    // component: FirUserProfileStorage
                    component: () => import("@/components/FirUserStorage"),

                }
            ]
        },
        {
            path: '/orders',
            component: () => import("@/components/FirAppBase"),
            children: [
                {
                    path: '',
                    name: 'FirUserOrders',
                    component: () => import("@/components/FirUserOrders"),

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
