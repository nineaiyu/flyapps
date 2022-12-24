import request from '@/utils/request'

export function login(data) {
  return request({
    url: '/login',
    method: 'post',
    data
  })
}

export function getInfo(token) {
  return request({
    url: '/user/info',
    method: 'get',
    params: { token }
  })
}

export function logout() {
  return request({
    url: '/user/logout',
    method: 'post'
  })
}

export function getUserInfos(query) {
  return request({
    url: '/userinfo',
    method: 'get',
    params: query
  })
}

export function updateUserInfo(data) {
  return request({
    url: '/userinfo',
    method: 'put',
    data
  })
}

export function getCertificationInfo(query) {
  return request({
    url: '/certification/info',
    method: 'get',
    params: query
  })
}
export function updateCertificationInfo(data) {
  return request({
    url: '/certification/info',
    method: 'put',
    data
  })
}

export function resetPassword(data) {
  return request({
    url: '/user/info',
    method: 'post',
    data
  })
}
