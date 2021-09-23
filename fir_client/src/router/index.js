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
            path: '/home',
            component: () => import("@/components/index/FirIndexTem"),
            children: [
                {
                    path: '',
                    name: 'FirIndex',
                    component: () => import("@/components/index/FirIndexBody"),
                },
                {
                    path: 'service',
                    name: 'FirService',
                    component: () => import("@/components/index/FirService")
                },
                {
                    path: 'news',
                    name: 'FirNews',
                    component: () => import("@/components/index/FirNews")
                },
                {
                    path: 'contact',
                    name: 'FirContact',
                    component: () => import("@/components/index/FirContact")
                },
            ]
        },

        {
            path: '/apps',
            component: () => import("@/components/FirBase"),
            children: [
                {
                    path: '',
                    name: 'FirApps',
                    component: () => import("@/components/apps/FirApps"),
                }
                ,
                {
                    path: ':id',
                    component: () => import("@/components/apps/FirAppInfosBase"),
                    children: [
                        {
                            path: '',
                            name: 'FirAppInfostimeline',
                            component: () => import("@/components/apps/FirAppInfostimeline"),
                        }
                        ,
                        {
                            path: 'info',
                            name: 'FirAppInfosbaseinfo',
                            component: () => import("@/components/apps/FirAppInfosbaseinfo"),
                        },
                        {
                            path: 'security',
                            name: 'FirAppInfossecurity',
                            component: () => import("@/components/apps/FirAppInfossecurity"),
                        },
                        {
                            path: 'devices',
                            name: 'FirAppInfosdevices',
                            component: () => import("@/components/apps/FirAppInfosdevices"),
                        },
                        {
                            path: 'combo',
                            name: 'FirAppInfoscombo',
                            component: () => import("@/components/apps/FirAppInfoscombo"),
                        },
                        {
                            path: 'supersign',
                            name: 'FirAppInfossupersign',
                            component: () => import("@/components/apps/FirAppInfossupersign"),
                        }
                    ]
                }
            ]
        },
        {
            path: '/user',
            component: () => import("@/components/FirBase"),
            children: [
                {
                    path: '',
                    component: () => import("@/components/user/FirUserProfileBase"),
                    children: [
                        {
                            path: 'info',
                            name: 'FirUserProfileInfo',
                            meta: {label: '个人资料'},
                            component: () => import("@/components/user/FirUserProfileInfo"),

                        }, {
                            path: 'setpasswd',
                            name: 'FirUserProfileChangePwd',
                            meta: {label: '修改密码'},
                            component: () => import("@/components/user/FirUserProfileChangePwd"),

                        }, {
                            path: 'certification',
                            name: 'FirUserProfileCertification',
                            meta: {label: '实名认证'},
                            component: () => import("@/components/user/FirUserProfileCertification"),

                        },
                    ]
                },
                {
                    path: 'supersign',
                    component: () => import("@/components/user/FirSuperSignBase"),
                    children: [
                        {
                            path: ':act',
                            name: 'FirSuperSignBase',
                            meta: {label: '超级签名'},
                        }
                    ]
                },
                {
                    path: 'storage',
                    component: () => import("@/components/user/FirUserStorage"),
                    children: [
                        {
                            path: ':act',
                            name: 'FirUserStorage',
                            meta: {label: '存储管理'},
                        }
                    ]
                },
                {
                    path: 'orders',
                    name: 'FirUserOrders',
                    meta: {label: '订单详情'},
                    component: () => import("@/components/user/FirUserOrders"),
                },
                {
                    path: 'domain',
                    name: 'FirUserDomain',
                    meta: {label: '绑定域名详情'},
                    component: () => import("@/components/user/FirUserDomain"),
                },
                {
                    path: 'supersign-help',
                    name: 'FirSuperSignHelp',
                    meta: {label: '密钥获取帮助'},
                    component: () => import("@/components/user/FirSuperSignHelp"),
                }
            ]
        },
        {
            path: '/login',
            name: 'FirLogin',
            component: () => import("@/components/FirLogin"),

        },
        {
            path: '/register',
            name: 'FirRegist',
            component: () => import("@/components/FirRegist"),

        },
        {
            path: '/reset/pwd',
            name: 'FirResetPwd',
            component: () => import("@/components/FirResetPwd"),

        },
        {
            path: '/:short',
            name: 'FirDownload',
            component: () => import("@/components/FirDownload"),

        },
    ]
});


export default router;
