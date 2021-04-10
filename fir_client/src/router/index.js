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
                }

            ]
        },
        {
            path: '/login',
            name: 'FirLogin',
            component: () => import("@/components/FirLogin"),

        },
        {
            path: '/user/supersign',
            component: () => import("@/components/FirBase"),
            children: [
                {
                    path: ':act',
                    name: 'FirSuperSignBase',
                    meta: {label: '超级签名'},
                    component: () => import("@/components/user/FirSuperSignBase"),

                }
            ]
        },
        {
            path: '/user/storage',
            component: () => import("@/components/FirBase"),
            children: [
                {
                    path: ':act',
                    name: 'FirUserStorage',
                    meta: {label: '存储管理'},
                    component: () => import("@/components/user/FirUserStorage"),

                }
            ]
        },
        {
            path: '/user/orders',
            component: () => import("@/components/FirBase"),
            children: [
                {
                    path: '',
                    name: 'FirUserOrders',
                    meta: {label: '订单详情'},
                    component: () => import("@/components/user/FirUserOrders"),

                }
            ]
        },
        {
            path: '/register',
            name: 'FirRegist',
            component: () => import("@/components/FirRegist"),

        },
        {
            path: '/:short',
            name: 'FirDownload',
            component: () => import("@/components/FirDownload"),

        },

    ]
});


export default router;
