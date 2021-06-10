import request from '@/utils/request'

export function getDevicesInfo(query) {
  return request({
    url: '/devices/info',
    method: 'get',
    params: query
  })
}

export function updatedevicesInfo(data) {
  return request({
    url: '/devices/info',
    method: 'put',
    data
  })
}
