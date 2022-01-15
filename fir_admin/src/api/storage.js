import request from '@/utils/request'

export function getStorageList(query) {
  return request({
    url: '/storage/info',
    method: 'get',
    params: query
  })
}

export function getStorageInfo(pk) {
  return request({
    url: '/storage/info/' + pk,
    method: 'get'
  })
}

export function updateStorageInfo(pk, data) {
  return request({
    url: '/storage/info/' + pk,
    method: 'put',
    data
  })
}

export function changeStorageInfo(data) {
  return request({
    url: '/storage/change',
    method: 'put',
    data
  })
}
