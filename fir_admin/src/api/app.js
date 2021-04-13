import request from '@/utils/request'

export function getAppInfos(query) {
  return request({
    url: '/app/info',
    method: 'get',
    params: query
  })
}

export function updateAppInfo(data) {
  return request({
    url: '/app/info',
    method: 'put',
    data
  })
}

export function getAppReleaseInfos(query) {
  return request({
    url: '/app/release/info',
    method: 'get',
    params: query
  })
}

export function updateReleaseAppInfo(data) {
  return request({
    url: '/app/release/info',
    method: 'put',
    data
  })
}
