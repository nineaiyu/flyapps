#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Date: 2018/9/18

"""
    点播服务
"""

from .base import BaseAliYunAPI


class AliYunVod(BaseAliYunAPI):

    VERSION = "2017-03-21"

    API_BASE_URL = "http://vod.cn-shanghai.aliyuncs.com/"

    def get_play_auth(self, video_id, timeout):
        """获取播放 `auth`

        Parameters
        ----------
        video_id : string

            视频 `vid`

        timeout: string

            获取到的播放 `key` 的有效时间

        Returns
        -------
        dict
        """

        data = {
            "VideoId": video_id,
            "AuthInfoTimeout": timeout
        }

        return self._get(action="GetVideoPlayAuth", data=data)

    def get_play_info(
        self, video_id, formats=None, timeout=None, stream_type=None, definition=None,
        result_type=None, output_type=None,
    ):
        """获取播放 `auth`

        Parameters
        ----------
        video_id : string

            视频 `vid`

        formats: string
            视频流格式，多个用逗号分隔。支持格式：mp4 m3u8 mp3
            默认获取所有格式的流

        timeout: string
            播放地址过期时间，单位：秒。
            最小值为1（未指定时，以URL鉴权中用户设置的默认有效时长为准），最大值无限制。
            只有开启了 URL鉴权 才会生效。

        stream_type: string
            视频流类型，多个用逗号分隔。支持类型：video audio
            默认获取所有类型的流。

        definition: string
            视频流清晰度，多个用逗号分隔。取值范围：FD（流畅）LD（标清）SD（高清）HD（超清）OD（原画）2K（2K）4K（4K）
            默认获取所有清晰度的流。

        result_type: string
            返回数据类型。取值范围 ：
                Single（每种清晰度和格式只返回一路最新转码完成的流）
                Multiple（每种清晰度和格式返回所有转码完成的流）
            默认为Single类型。

        output_type: string
            输出地址类型。取值范围 ：
                oss（回源地址）
                cdn（加速地址）
            默认为cdn类型。注意：仅支持播放格式为mp4的oss地址

        Returns
        -------
        dict
        """

        data = {
            "VideoId": video_id,
            "Formats": formats,
            "AuthTimeout": timeout,
            "StreamType": stream_type,
            "Definition": definition,
            "ResultType": result_type,
            "OutputType": output_type
        }

        return self._get(action="GetPlayInfo", data=data)

    def query_flow_data(
        self, domain_name=None, start_time=None, end_time=None, time_merge=None, interval=None,
        location_name_en=None, isp_name_en=None,
    ):
        """查询流量数据

        获取加速域名的网络流量监控数据，单位：byte。
        不指定StartTime和EndTime时，默认读取过去24小时的数据。也可以按指定的起止时间查询。

        注意：
            支持域名批量查询，多个域名用半角逗号分隔。
            最多可获取近90天的数据。

        Parameters
        ----------
        domain_name : string
            要查询的域名。若为空，则默认返回所有加速域名的合并数据。支持批量查询，多个域名用半角逗号分隔。

        start_time: string
            获取数据起始时间点。日期格式按照ISO8601表示法，使用UTC时间。
            若为空，则默认读取最近24小时的数据。

        end_time: string
            结束时间。需大于起始时间，日期格式按照ISO8601表示法，使用UTC时间。格式为：YYYY-MM-DDThh:mmZ。

        time_merge: string
            时间合并。取值范围：
                on：默认值。每条记录的时间间隔会根据时间跨度进行合并。
                off：返回5分钟粒度数据，最大时间跨度为31天。

        interval: string
            查询数据的时间粒度。单位：秒，取值范围：300 3600 14400 28800 86400
            默认值：300

        location_name_en: string
            区域英文名。默认为所有区域。

        isp_name_en: string
            运营商英文名。默认为所有运营商。

        Returns
        -------
        dict
        """

        data = {
            "DomainName": domain_name,
            "StartTime": start_time,
            "EndTime": end_time,
            "TimeMerge": time_merge,
            "Interval": interval,
            "LocationNameEn": location_name_en,
            "IspNameEn": isp_name_en
        }

        return self._get(action="DescribeDomainFlowData", data=data)

    def query_bps_data(
        self, domain_name=None, start_time=None, end_time=None, time_merge=None, interval=None,
        location_name_en=None, isp_name_en=None,
    ):
        """查询网络带宽

        获取加速域名的网络带宽监控数据，单位：bit/second。
        不指定StartTime和EndTime时，默认读取过去24小时的数据。也可以按指定的起止时间查询。

        注意：
            支持域名批量查询，多个域名用半角逗号分隔。
            最多可获取近90天的数据。

        Parameters
        ----------
        domain_name : string
            要查询的域名。若为空，则默认返回所有加速域名的合并数据。支持批量查询，多个域名用半角逗号分隔。

        start_time: string
            获取数据起始时间点。日期格式按照ISO8601表示法，使用UTC时间。
            若为空，则默认读取最近24小时的数据。

        end_time: string
            结束时间。需大于起始时间，日期格式按照ISO8601表示法，使用UTC时间。格式为：YYYY-MM-DDThh:mmZ。

        time_merge: string
            时间合并。取值范围：
                on：默认值。每条记录的时间间隔会根据时间跨度进行合并。
                off：返回5分钟粒度数据，最大时间跨度为31天。

        interval: string
            查询数据的时间粒度。单位：秒，取值范围：300 3600 14400 28800 86400
            默认值：300

        location_name_en: string
            区域英文名。默认为所有区域。

        isp_name_en: string
            运营商英文名。默认为所有运营商。

        Returns
        -------
        dict
        """

        data = {
            "DomainName": domain_name,
            "StartTime": start_time,
            "EndTime": end_time,
            "TimeMerge": time_merge,
            "Interval": interval,
            "LocationNameEn": location_name_en,
            "IspNameEn": isp_name_en
        }

        return self._get(action="DescribeDomainBpsData", data=data)
