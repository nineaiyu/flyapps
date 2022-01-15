import request from '@/utils/request'

export function getDomainList(query) {
  return request({
    url: '/domain/info',
    method: 'get',
    params: query
  })
}

export function getDomainInfos(pk) {
  return request({
    url: '/domain/info/' + pk,
    method: 'get'
  })
}

export function updateDomainInfo(pk, data) {
  return request({
    url: '/domain/info/' + pk,
    method: 'put',
    data
  })
}

export function deleteDomain(pk) {
  return request({
    url: '/domain/info/' + pk,
    method: 'delete'
  })
}
