import request from '@/utils/request'

export function getDomainInfos(query) {
  return request({
    url: '/domain/info',
    method: 'get',
    params: query
  })
}

export function updateDomainInfo(data) {
  return request({
    url: '/domain/info',
    method: 'put',
    data
  })
}

export function deleteDomain(data) {
  return request({
    url: '/domain/info',
    method: 'delete',
    data
  })
}
