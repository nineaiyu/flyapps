import request from '@/utils/request'

export function getStorageInfo(query) {
  return request({
    url: '/storage/info',
    method: 'get',
    params: query
  })
}

export function updateStorageInfo(data) {
  return request({
    url: '/storage/info',
    method: 'put',
    data
  })
}

