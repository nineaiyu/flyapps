import request from '@/utils/request'

export function getDeveloperInfo(query) {
  return request({
    url: '/developer/info',
    method: 'get',
    params: query
  })
}

export function updatedeveloperInfo(data) {
  return request({
    url: '/developer/info',
    method: 'put',
    data
  })
}

export function getBillInfo(query) {
  return request({
    url: '/bill/info',
    method: 'get',
    params: query
  })
}

export function addBillInfo(data) {
  return request({
    url: '/bill/info',
    method: 'post',
    data
  })
}
export function delBillInfo(data) {
  return request({
    url: '/bill/info',
    method: 'delete',
    data
  })
}

export function getUserBillInfo(query) {
  return request({
    url: '/bill/userinfo',
    method: 'get',
    params: query
  })
}
