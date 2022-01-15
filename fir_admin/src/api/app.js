import request from '@/utils/request'

export function getAppList(query) {
  return request({
    url: '/app/info',
    method: 'get',
    params: query
  })
}

export function getAppInfos(pk) {
  return request({
    url: '/app/info/' + pk,
    method: 'get'
  })
}

export function updateAppInfo(pk, data) {
  return request({
    url: '/app/info/' + pk,
    method: 'put',
    data
  })
}

export function deleteApp(pk) {
  return request({
    url: '/app/info/' + pk,
    method: 'delete'
  })
}

export function getAppReleaseList(query) {
  return request({
    url: '/app/release/info',
    method: 'get',
    params: query
  })
}

export function getAppReleaseInfos(pk) {
  return request({
    url: '/app/release/info/' + pk,
    method: 'get'
  })
}

export function updateReleaseAppInfo(pk, data) {
  return request({
    url: '/app/release/info/' + pk,
    method: 'put',
    data
  })
}
export function downloadAppReleaseInfos(data) {
  return request({
    url: '/app/release/info',
    method: 'post',
    data
  })
}
