om rest_framework.views import APIView
from rest_framework.viewsets import ViewSetMixin, ModelViewSet

from api.utils.response import BaseResponse

from rest_framework.response import Response

from api.models import Course, CourseDetail, PricePolicy
from django.core.exceptions import ObjectDoesNotExist
from api.utils.exceptions import CommonException
from django_redis import get_redis_connection
from django.conf import settings
from api.utils.auth import ExpiringTokenAuthentication

import json
from api.utils.permission import LoginUserPermission
import redis

REDIS_CONN = redis.Redis(decode_responses=True)


class ShoppingCarView(APIView):
    """
    1030 加入购物车失败
    """
    authentication_classes = [ExpiringTokenAuthentication, ]

    def post(self, request):
        res = BaseResponse()
        try:
            # 1 获取前端传过来的course_id 以及price_policy_id user_id
            course_id = request.data.get("course_id", "")
            price_policy_id = request.data.get("price_policy_id", "")
            user_id = request.user.id
            # 2 验证数据的合法性
            # 2.1 验证course_id是否合法
            course_obj = Course.objects.get(pk=course_id)
            # 2.2 校验价格策略是否能合法

            # 查找课程关联的价格策略
            price_policy_list = course_obj.price_policy.all()
            price_policy_dict = {}
            for price_policy in price_policy_list:
                price_policy_dict[price_policy.pk] = {
                    "prcie": price_policy.price,
                    "valid_period": price_policy.valid_period,
                    "valid_period_text": price_policy.get_valid_period_display(),
                    "default": price_policy.pk == price_policy_id
                }

            if price_policy_id not in price_policy_dict:
                raise CommonException(1001, "价格策略异常!")

                # 3 构建我们想要的数据结构
                # 价格策略对象
            pp = PricePolicy.objects.get(pk=price_policy_id)
            course_info = {
                "id": course_id,
                "name": course_obj.name,
                "course_img": course_obj.course_img,
                "relate_price_policy": price_policy_dict,
                "default_price": pp.price,
                "default_price_period": pp.valid_period,
                "default_price_policy_id": pp.pk

            }

            # 4 写入redis
            # 4.1 先拼接购物车的key
            shopping_car_key = settings.SHOPPING_CAR_KEY % (user_id, course_id)
            # 4.2 写入redis
            print("------>")
            REDIS_CONN.set(shopping_car_key, json.dumps(course_info))
            res.msg = "加入购物车成功!"

        except CommonException as e:
            res.code = e.code
            res.error = e.error
        except Exception as e:
            res.code = 1030
            res.error = "加入购物车失败!"

        return Response(res.dict)

    def get(self, request):
        res = BaseResponse()
        try:
            # 1 取到user_id
            user_id = request.user.id
            # 2 拼接购物车的key
            shopping_car_key = settings.SHOPPING_CAR_KEY % (user_id, "*")
            print("shopping_car_key",shopping_car_key)
            # shopping_car_1_*
            # shopping_car_1_asdgnlaksdj
            # 3 去redis读取该用户的所有加入购物车的课程
            # 3.1 先去模糊匹配出所有符合要求的key
            all_keys = REDIS_CONN.keys(shopping_car_key)
            print("all_keys",all_keys)
            # 3.2 循环所有的keys 得到每个可以
            shopping_car_list = []
            for key in all_keys:
                print("key",key)
                course_info = json.loads(REDIS_CONN.get(key))
                shopping_car_list.append(course_info)

            res.data = {"shopping_car_list": shopping_car_list, "total": len(shopping_car_list)}

        except Exception as e:
            res.code = 1033
            res.error = "获取购物车失败"
        print("res.dict",res.dict)
        return Response(res.dict)

    def put(self, request):
        res = BaseResponse()
        try:
            # 1 获取前端传过来的course_id 以及price_policy_id
            course_id = request.data.get("course_id", "")
            price_policy_id = request.data.get("price_policy_id", "")
            user_id = request.user.id
            # 2 校验数据的合法性
            # 2.1 校验course_id是否合法
            shopping_car_key = settings.SHOPPING_CAR_KEY % (user_id, course_id)
            if not REDIS_CONN.exists(shopping_car_key):
                res.code = 1035
                res.error = "课程不存在"
                return Response(res.dict)
            # 2.2 判断价格策略是否合法
            course_info = REDIS_CONN.hgetall(shopping_car_key)
            price_policy_dict = json.loads(course_info["price_policy_dict"])
            if str(price_policy_id) not in price_policy_dict:
                res.code = 1036
                res.error = "所选的价格策略不存在"
                return Response(res.dict)
            # 3 修改redis中的default_policy_id
            course_info["default_policy_id"] = price_policy_id
            # 4 修改信息后写入redis
            REDIS_CONN.hmset(shopping_car_key, course_info)
            res.data = "更新成功"
        except Exception as e:
            res.code = 1034
            res.error = "更新价格策略失败"
        return Response(res.dict)

    def delete(self, request):
        res = BaseResponse()
        try:
            # 获取前端传过来的course_id
            course_id = request.data.get("course_id", "")
            user_id = request.user.id
            # 判断课程id是否合法
            shopping_car_key = settings.SHOPPING_CAR_KEY % (user_id, course_id)
            if not REDIS_CONN.exists(shopping_car_key):
                res.code = 1039
                res.error = "删除的课程不存在"
                return Response(res.dict)
            # 删除redis中的数据
            REDIS_CONN.delete(shopping_car_key)
            res.data = "删除成功"
        except Exception as e:
            res.code = 1037
            res.error = "删除失败"
        return Response(res.dict)


'''
1 post接口构建数据结构:
    {
        "id": 2,
        "default_price_period": 14,
        "relate_price_policy": {
            "1": {
                "valid_period": 7,
                "valid_period_text": "1周",
                "default": false,
                "prcie": 100.0
            },
            "2": {
                "valid_period": 14,
                "valid_period_text": "2周",
                "default": true,
                "prcie": 200.0
            },
            "3": {
                "valid_period": 30,
                "valid_period_text": "1个月",
                "default": false,
                "prcie": 300.0
            }
        },
        "name": "Django框架学习",
        "course_img": "https://luffycity.com/static/frontend/course/3/Django框架学习_1509095212.759272.png",
        "default_price": 200.0
    }



2 get接口查询数据结构:

{
    "data": {
        "total": 2,
        "shopping_car_list": [
            {
                "id": 2,
                "default_price_period": 14,
                "relate_price_policy": {
                    "1": {
                        "valid_period": 7,
                        "valid_period_text": "1周",
                        "default": false,
                        "prcie": 100
                    },
                    "2": {
                        "valid_period": 14,
                        "valid_period_text": "2周",
                        "default": true,
                        "prcie": 200
                    },
                    "3": {
                        "valid_period": 30,
                        "valid_period_text": "1个月",
                        "default": false,
                        "prcie": 300
                    }
                },
                "name": "Django框架学习",
                "course_img": "https://luffycity.com/static/frontend/course/3/Django框架学习_1509095212.759272.png",
                "default_price": 200
            },
            {
                "id": 4,
                "default_price_period": 30,
                "relate_price_policy": {
                    "4": {
                        "valid_period": 30,
                        "valid_period_text": "1个月",
                        "default": true,
                        "prcie": 1000
                    },
                    "5": {
                        "valid_period": 60,
                        "valid_period_text": "2个月",
                        "default": false,
                        "prcie": 1500
                    }
                },
                "name": "Linux系统基础5周入门精讲",
                "course_img": "https://luffycity.com/static/frontend/course/12/Linux5周入门_1509589530.6144893.png",
                "default_price": 1000
            }
        ]
    },
    "code": 1000,
    "msg": ""
}

'''
