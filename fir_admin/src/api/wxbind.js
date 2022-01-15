import request from '@/utils/request'

export function getWxBindList(query) {
  return request({
    url: '/wxbind/info',
    method: 'get',
    params: query
  })
}

export function getWxBindInfos(pk) {
  return request({
    url: '/wxbind/info/' + pk,
    method: 'get'
  })
}

export function updateWxBindInfo(pk,data) {
  return request({
    url: '/wxbind/info/' + pk,
    method: 'put',
    data
  })
}

export function deleteWxBind(pk) {
  return request({
    url: '/wxbind/info/' + pk,
    method: 'delete'
  })
}
