import request from '@/utils/request'

export function getAppInfos(query) {
  return request({
    url: '/appinfo',
    method: 'get',
    params: query
  })
}

export function updateAppInfo(data) {
  return request({
    url: '/appinfo',
    method: 'put',
    data
  })
}
