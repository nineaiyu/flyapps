import request from '@/utils/request'

export function getDevicesList(query) {
  return request({
    url: '/devices/info',
    method: 'get',
    params: query
  })
}

