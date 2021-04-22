import request from '@/utils/request'

export function getOrderInfo(query) {
  return request({
    url: '/order/info',
    method: 'get',
    params: query
  })
}

export function updateOrderInfo(data) {
  return request({
    url: '/order/info',
    method: 'put',
    data
  })
}

