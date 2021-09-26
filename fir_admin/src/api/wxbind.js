import request from '@/utils/request'

export function getWxBindInfos(query) {
  return request({
    url: '/wxbind/info',
    method: 'get',
    params: query
  })
}

export function updateWxBindInfo(data) {
  return request({
    url: '/wxbind/info',
    method: 'put',
    data
  })
}

export function deleteWxBind(data) {
  return request({
    url: '/wxbind/info',
    method: 'delete',
    data
  })
}
