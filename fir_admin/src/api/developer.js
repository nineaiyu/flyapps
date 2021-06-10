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
