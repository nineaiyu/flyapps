import request from '@/utils/request'

export function getOrderList(query) {
  return request({
    url: '/order/info',
    method: 'get',
    params: query
  })
}

export function getOrderInfo(pk) {
  return request({
    url: '/order/info/' + pk,
    method: 'get'
  })
}

export function updateOrderInfo(pk, data) {
  return request({
    url: '/order/info/' + pk,
    method: 'put',
    data
  })
}
export function deleteOrderInfo(pk) {
  return request({
    url: '/order/info/' + pk,
    method: 'delete'
  })
}
export function createOrderInfo(data) {
  return request({
    url: '/order/info',
    method: 'post',
    data
  })
}

