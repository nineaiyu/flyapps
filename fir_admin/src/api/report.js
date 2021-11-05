import request from '@/utils/request'

export function getAppReportIfo(query) {
  return request({
    url: '/report/info',
    method: 'get',
    params: query
  })
}

export function updateAppReportIfo(data) {
  return request({
    url: '/report/info',
    method: 'put',
    data
  })
}

export function deleteAppReportIfo(data) {
  return request({
    url: '/report/info',
    method: 'delete',
    data
  })
}
