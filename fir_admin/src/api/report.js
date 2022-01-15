import request from '@/utils/request'

export function getAppReportList(query) {
  return request({
    url: '/report/info',
    method: 'get',
    params: query
  })
}

export function getAppReportIfo(pk) {
  return request({
    url: '/report/info/' + pk,
    method: 'get'
  })
}

export function updateAppReportIfo(pk, data) {
  return request({
    url: '/report/info/' + pk,
    method: 'put',
    data
  })
}

export function deleteAppReportIfo(pk) {
  return request({
    url: '/report/info/' + pk,
    method: 'delete'
  })
}
