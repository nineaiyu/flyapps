import request from '@/utils/request'

export function getDeveloperList(query) {
  return request({
    url: '/developer/info',
    method: 'get',
    params: query
  })
}

export function getDeveloperInfo(pk) {
  return request({
    url: '/developer/info/' + pk,
    method: 'get'
  })
}

export function updatedeveloperInfo(pk, data) {
  return request({
    url: '/developer/info/' + pk,
    method: 'put',
    data
  })
}

export function getBillList(query) {
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
export function delBillInfo(pk) {
  return request({
    url: '/bill/info/' + pk,
    method: 'delete'
  })
}

export function getUserBillInfo(query) {
  return request({
    url: '/bill/userinfo',
    method: 'get',
    params: query
  })
}
