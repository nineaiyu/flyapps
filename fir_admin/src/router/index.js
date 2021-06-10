import Vue from 'vue'
import Router from 'vue-router'

Vue.use(Router)

/* Layout */
import Layout from '@/layout'

/**
 * Note: sub-menu only appear when route children.length >= 1
 * Detail see: https://panjiachen.github.io/vue-element-admin-site/guide/essentials/router-and-nav.html
 *
 * hidden: true                   if set true, item will not show in the sidebar(default is false)
 * alwaysShow: true               if set true, will always show the root menu
 *                                if not set alwaysShow, when item has more than one children route,
 *                                it will becomes nested mode, otherwise not show the root menu
 * redirect: noRedirect           if set noRedirect will no redirect in the breadcrumb
 * name:'router-name'             the name is used by <keep-alive> (must set!!!)
 * meta : {
    roles: ['admin','editor']    control the page roles (you can set multiple roles)
    title: 'title'               the name show in sidebar and breadcrumb (recommend set)
    icon: 'svg-name'/'el-icon-x' the icon show in the sidebar
    breadcrumb: false            if set false, the item will hidden in breadcrumb(default is true)
    activeMenu: '/example/list'  if set path, the sidebar will highlight the path you set
  }
 */

/**
 * constantRoutes
 * a base page that does not have permission requirements
 * all roles can be accessed
 */
export const constantRoutes = [
  {
    path: '/login',
    component: () => import('@/views/login/index'),
    hidden: true
  },

  {
    path: '/404',
    component: () => import('@/views/404'),
    hidden: true
  },

  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [{
      path: 'dashboard',
      name: 'Dashboard',
      component: () => import('@/views/dashboard/index'),
      meta: { title: 'Dashboard', icon: 'dashboard' }
    }]
  },

  {
    path: '/user',
    component: Layout,
    redirect: '/user/list',
    name: 'user',
    meta: {
      title: '用户管理',
      icon: 'el-icon-s-help'
    },
    children: [
      {
        path: 'list',
        name: 'user_info_list',
        component: () => import('@/views/userinfos/list'),
        meta: { title: '用户列表', icon: 'form' }
      },
      {
        path: 'edit/:id(\\d+)',
        component: () => import('@/views/userinfos/edit'),
        name: 'user_info_edit',
        meta: { title: '编辑信息', noCache: true, activeMenu: '/user/list' },
        hidden: true
      }
    ]
  },
  {
    path: '/apps',
    component: Layout,
    redirect: '/apps/list',
    name: 'apps',
    meta: {
      title: '应用管理',
      icon: 'el-icon-s-help'
    },
    children: [
      {
        path: 'list',
        name: 'app_info_list',
        component: () => import('@/views/appinfos/list'),
        meta: { title: '应用列表', icon: 'form' }
      },
      {
        path: 'edit/:id(\\d+)',
        component: () => import('@/views/appinfos/edit'),
        name: 'app_info_edit',
        meta: { title: '编辑信息', noCache: true, activeMenu: '/apps/list' },
        hidden: true
      },
      {
        path: 'release/:app_id(\\d+)/list',
        name: 'app_release_info_list',
        component: () => import('@/views/appinfos/AppReleaseList'),
        meta: { title: '版本记录', noCache: true, activeMenu: '/apps/list' },
        hidden: true
      },
      {
        path: 'release/:app_id(\\d+)/edit/:id(\\d+)',
        name: 'app_release_info_edit',
        component: () => import('@/views/appinfos/AppReleaseDetail'),
        meta: { title: '版本记录', noCache: true, activeMenu: '/apps/list' },
        hidden: true
      }
    ]
  },
  {
    path: '/storage',
    component: Layout,
    children: [
      {
        path: 'list',
        name: 'storage_info_list',
        component: () => import('@/views/storage/list'),
        meta: { title: '存储管理', icon: 'form' }
      },
      {
        path: 'edit/:id(\\d+)',
        component: () => import('@/views/storage/Detail'),
        name: 'storage_info_edit',
        meta: { title: '编辑信息', noCache: true, activeMenu: '/storage/list' },
        hidden: true
      }
    ]
  }, {
    path: '/authentication',
    component: Layout,
    children: [
      {
        path: 'list',
        name: 'user_authentication_info_list',
        component: () => import('@/views/authentication/list'),
        meta: { title: '用户实名认证', icon: 'form' }
      },
      {
        path: 'edit/:id(\\d+)',
        component: () => import('@/views/authentication/Detail'),
        name: 'user_authentication_info_edit',
        meta: { title: '编辑信息', noCache: true, activeMenu: '/authentication/list' },
        hidden: true
      }
    ]
  }, {
    path: '/order',
    component: Layout,
    children: [
      {
        path: 'list',
        name: 'order_info_list',
        component: () => import('@/views/order/list'),
        meta: { title: '订单管理', icon: 'form' }
      },
      {
        path: 'edit/:id(\\d+)',
        component: () => import('@/views/order/Detail'),
        name: 'order_info_edit',
        meta: { title: '编辑信息', noCache: true, activeMenu: '/order/list' },
        hidden: true
      }
    ]
  }, {
    path: '/supersign',
    component: Layout,
    redirect: '/supersign/developer',
    name: '超级签名',
    meta: {
      title: '超级签名',
      icon: 'nested'
    },
    children: [
      {
        path: 'developer',
        name: 'developer',
        redirect: '/supersign/developer/list',
        component: () => import('@/views/supersign/index'),
        children: [
          {
            path: 'list',
            name: 'developer_user_info_list',
            component: () => import('@/views/supersign/developer/list'),
            meta: { title: '苹果开发者', icon: 'form' }
          },
          {
            path: 'edit/:id(\\d+)',
            component: () => import('@/views/supersign/developer/Detail'),
            name: 'developer_user_info_edit',
            meta: { title: '编辑信息', noCache: true, activeMenu: '/supersign/list' },
            hidden: true
          }
        ]
      },
      {
        path: 'devices',
        name: 'devices',
        redirect: '/supersign/devices/list',
        component: () => import('@/views/supersign/index'),
        children: [
          {
            path: 'list',
            name: 'devices_info_list',
            component: () => import('@/views/supersign/devices/list'),
            meta: { title: '设备消耗', icon: 'form' }
          },
        ]
      }
    ]
  }, {
    path: '/settings',
    component: Layout,
    redirect: '/settings/email',
    name: 'settings',
    meta: { title: '系统设置', icon: 'el-icon-s-help' },
    children: [
      {
        path: 'email',
        name: 'email',
        component: () => import('@/views/table/index'),
        meta: { title: '邮箱设置', icon: 'table' }
      },
      {
        path: 'sms',
        name: 'sms',
        component: () => import('@/views/tree/index'),
        meta: { title: '短信设置', icon: 'tree' }
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('@/views/tree/index'),
        meta: { title: '注册设置', icon: 'tree' }
      },
      {
        path: 'login',
        name: 'login',
        component: () => import('@/views/tree/index'),
        meta: { title: '登录设置', icon: 'tree' }
      },
      {
        path: 'geetest',
        name: 'geetest',
        component: () => import('@/views/tree/index'),
        meta: { title: '极验验证', icon: 'tree' }
      },
      {
        path: 'captcha',
        name: 'captcha',
        component: () => import('@/views/tree/index'),
        meta: { title: '图片验证', icon: 'tree' }
      }
    ]
  },

  {
    path: '/nested',
    component: Layout,
    redirect: '/nested/menu1',
    name: 'Nested',
    meta: {
      title: 'Nested',
      icon: 'nested'
    },
    children: [
      {
        path: 'menu1',
        component: () => import('@/views/nested/menu1/index'), // Parent router-view
        name: 'Menu1',
        meta: { title: 'Menu1' },
        children: [
          {
            path: 'menu1-1',
            component: () => import('@/views/nested/menu1/menu1-1'),
            name: 'Menu1-1',
            meta: { title: 'Menu1-1' }
          },
          {
            path: 'menu1-2',
            component: () => import('@/views/nested/menu1/menu1-2'),
            name: 'Menu1-2',
            meta: { title: 'Menu1-2' },
            children: [
              {
                path: 'menu1-2-1',
                component: () => import('@/views/nested/menu1/menu1-2/menu1-2-1'),
                name: 'Menu1-2-1',
                meta: { title: 'Menu1-2-1' }
              },
              {
                path: 'menu1-2-2',
                component: () => import('@/views/nested/menu1/menu1-2/menu1-2-2'),
                name: 'Menu1-2-2',
                meta: { title: 'Menu1-2-2' }
              }
            ]
          },
          {
            path: 'menu1-3',
            component: () => import('@/views/nested/menu1/menu1-3'),
            name: 'Menu1-3',
            meta: { title: 'Menu1-3' }
          }
        ]
      },
      {
        path: 'menu2',
        component: () => import('@/views/nested/menu2/index'),
        meta: { title: 'menu2' }
      }
    ]
  },

  {
    path: 'external-link',
    component: Layout,
    children: [
      {
        path: 'https://panjiachen.github.io/vue-element-admin-site/#/',
        meta: { title: '官方首页', icon: 'link' }
      }
    ]
  },

  // 404 page must be placed at the end !!!
  { path: '*', redirect: '/404', hidden: true }
]

const createRouter = () => new Router({
  // mode: 'history', // require service support
  scrollBehavior: () => ({ y: 0 }),
  routes: constantRoutes
})

const router = createRouter()

// Detail see: https://github.com/vuejs/vue-router/issues/1234#issuecomment-357941465
export function resetRouter() {
  const newRouter = createRouter()
  router.matcher = newRouter.matcher // reset router
}

export default router
