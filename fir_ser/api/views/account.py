from rest_framework.views import APIView
from api.utils.response import BaseResponse
from api.utils.auth import ExpiringTokenAuthentication
from rest_framework.response import Response
import json
import datetime
from django.conf import settings
from django_redis import get_redis_connection
from api.utils.exceptions import CommonException
from django.core.exceptions import ObjectDoesNotExist
import redis

REDIS_CONN = redis.Redis(decode_responses=True)


class AccountView(APIView):
    '''
    结算接口
    '''
    authentication_classes = [ExpiringTokenAuthentication, ]

    def get_coupon_list(self, request, course_id=None):

        now = datetime.datetime.utcnow()

        coupon_record_list = CouponRecord.objects.filter(
            account=request.user,
            status=0,
            coupon__valid_begin_date__lte=now,
            coupon__valid_end_date__gt=now,
            coupon__content_type_id=14,
            coupon__object_id=course_id

        )

        coupon_list = []

        for coupon_record in coupon_record_list:
            coupon_list.append({

                "pk": coupon_record.pk,
                "name": coupon_record.coupon.name,
                "coupon_type": coupon_record.coupon.get_coupon_type_display(),
                "money_equivalent_value": coupon_record.coupon.money_equivalent_value,
                "off_percent": coupon_record.coupon.off_percent,
                "minimum_consume": coupon_record.coupon.minimum_consume,
            })

        return coupon_list

    def post(self, request, *args, **kwargs):
        # 1 获取数据
        '''
        course_list=[{
                          "course_id":1,
                          "price_policy_id":2
                        },

                    ]

        :param request:
        :param args:
        :param kwargs:
        :return:
        '''
        user = request.user
        course_list = request.data
        print("course_list",course_list)
        print("course_list",type(course_list))
        response = BaseResponse()
        try:
            # 2 创建数据结构
            # 清空操作
            # 找到所有以account_userid_*，全部清空
            del_list = REDIS_CONN.keys(settings.ACCOUNT_KEY % (user.pk, "*"))
            if del_list:
                REDIS_CONN.delete(*del_list)

            price_list=[]
            for course_dict in course_list:

                course_id=course_dict.get("course_id")
                price_policy_id=course_dict.get("price_policy_id")
                # 校验课程是否存在
                course_obj=Course.objects.get(pk=course_id)
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
                pp=PricePolicy.objects.get(pk=price_policy_id)
                # 将课程信息加入到每一个课程结算字典中
                account_dict = {
                    "id": course_id,
                    "name": course_obj.name,
                    "course_img": course_obj.course_img,
                    "relate_price_policy": price_policy_dict,
                    "default_price": pp.price,
                    "rebate_price": pp.price,
                    "default_price_period": pp.valid_period,
                    "default_price_policy_id": pp.pk
                }
                # 课程价格加入到价格列表
                price_list.append(float(pp.price))

                # 查询当前用户拥有未使用的，在有效期的且与当前课程相关的优惠券
                account_dict["coupon_list"] = self.get_coupon_list(request, course_id)

                # 存储结算信息
                account_key = settings.ACCOUNT_KEY % (user.pk, course_id)
                REDIS_CONN.set(account_key, json.dumps(account_dict))

            # 获取通用优惠券,加入redis中

            REDIS_CONN.set("global_coupon_%s" % user.pk, json.dumps(self.get_coupon_list(request)))
            REDIS_CONN.set("total_price",sum(price_list))

        except ObjectDoesNotExist as e:
            response.code = 1001
            response.error = "课程不存在!"
        except CommonException as e:
            response.code = e.code
            response.error = e.error

        # except Exception as e:
        #     response.code = 500
        #     response.error = str(e)

        return Response(response.dict)

    def get(self, request, *args, **kwargs):

        res = BaseResponse()
        try:
            # 1 取到user_id
            user_id = request.user.id
            # 2 拼接购物车的key
            account_key = settings.ACCOUNT_KEY % (user_id, "*")
            # shopping_car_1_*
            # shopping_car_1_asdgnlaksdj
            # 3 去redis读取该用户的所有加入购物车的课程
            # 3.1 先去模糊匹配出所有符合要求的key
            all_keys = REDIS_CONN.scan_iter(account_key)

            # 3.2 循环所有的keys 得到每个可以
            account_course_list = []
            for key in all_keys:
                account_course = json.loads(REDIS_CONN.get(key))
                account_course_list.append(account_course)

            global_coupons = json.loads(REDIS_CONN.get("global_coupon_%s" % request.user.pk))
            total_price = REDIS_CONN.get("total_price")
            res.data = {
                "account_course_list": account_course_list,
                "total": len(account_course_list),
                "global_coupons": global_coupons,
                "total_price": total_price
            }

        except Exception as e:
            res.code = 1033
            res.error = "获取购物车失败"

        return Response(res.dict)

    def cal_coupon_price(self,price,coupon_info):

        print("coupon_info",coupon_info)
        coupon_type=coupon_info["coupon_type"]
        money_equivalent_value=coupon_info.get("money_equivalent_value")
        off_percent=coupon_info.get("off_percent")
        minimum_consume=coupon_info.get("minimum_consume")
        rebate_price=0
        if coupon_type == "立减券": # 立减券
            rebate_price=price-money_equivalent_value
            if rebate_price <= 0:
                rebate_price=0
        elif coupon_type == "满减券": # 满减券
             if minimum_consume > price:
                 raise CommonException(3000,"优惠券未达到最低消费")
             else:
                 rebate_price=price-money_equivalent_value
        elif coupon_type == "折扣券":
            rebate_price=price*off_percent/100

        return rebate_price

    def put(self,request, *args, **kwargs):
        '''
        choose_coupons:
            {
            choose_coupons={"1":2,"2":3,"global_coupon_id":5}
            is_beli:true
            }
        '''
        res=BaseResponse()
        # try:

        # 1 获取数据
        choose_coupons=request.data.get("choose_coupons")
        is_beli=request.data.get("is_beli")
        user_pk=request.user.pk

        # 2 获取结算课程列表
        cal_price={}
        data=self.get(request).data.get("data")
        account_course_list=data.get("account_course_list")
        print("account_course_list",account_course_list)
        '''
           account_course_list=[{
                'id': 4,
                'coupon_list': [{
                    'off_percent': None,
                    'pk': 4,
                    'money_equivalent_value': 300.0,
                    'coupon_type': '立减券',
                    'minimum_consume': 0,
                    'name': '51劳动节'
                }],
                'course_img': 'https://luffycity.com/static/frontend/course/12/Linux5周入门_1509589530.6144893.png',
                'default_price': 1500.0,
                'default_price_period': 60,
                'relate_price_policy': {
                    '5': {
                        'valid_period_text': '2个月',
                        'default': True,
                        'valid_period': 60,
                        'prcie': 1500.0
                    },
                    '4': {
                        'valid_period_text': '1个月',
                        'default': False,
                        'valid_period': 30,
                        'prcie': 1000.0
                    }
                },
                'default_price_policy_id': 5,
                'name': 'Linux系统基础5周入门精讲'
            }, {
                'id': 2,
                'coupon_list': [{
                    'off_percent': 80,
                    'pk': 3,
                    'money_equivalent_value': 0.0,
                    'coupon_type': '折扣券',
                    'minimum_consume': 0,
                    'name': '清明节活动'
                }],
                'course_img': 'https://luffycity.com/static/frontend/course/3/Django框架学习_1509095212.759272.png',
                'default_price': 300.0,
                'default_price_period': 30,
                'relate_price_policy': {
                    '3': {
                        'valid_period_text': '1个月',
                        'default': True,
                        'valid_period': 30,
                        'prcie': 300.0
                    },
                    '1': {
                        'valid_period_text': '1周',
                        'default': False,
                        'valid_period': 7,
                        'prcie': 100.0
                    },
                    '2': {
                        'valid_period_text': '2周',
                        'default': False,
                        'valid_period': 14,
                        'prcie': 200.0
                    }
                },
                'default_price_policy_id': 3,
                'name': 'Django框架学习'
            }]
        '''
        account_courses_info={}
        for account_course in account_course_list:
            temp={
                "coupon":{},
                "default_price":account_course["default_price"]
            }
            account_courses_info[account_course["id"]]=temp

            for item in account_course["coupon_list"]:

                print("choose_coupons",choose_coupons) # {'4': 4}
                print(str(account_course["id"]))

                coupon_id=choose_coupons.get(str(account_course["id"]))
                if coupon_id == item["pk"]:
                    temp["coupon"]=item

        print("account_course_info",account_courses_info)
        price_list=[]
        total_price=0
        '''
           {
                2: {
                    'coupon': {
                        'money_equivalent_value': 0.0,
                        'name': '清明节活动',
                        'pk': 3,
                        'off_percent': 80,
                        'coupon_type': '折扣券',
                        'minimum_consume': 0
                    },
                    'default_price': 200.0
                }
            }
        '''
        for key,val in account_courses_info.items():
            if not val.get("coupon"):
                price_list.append(val["default_price"])
                cal_price[key]=val["default_price"]
            else:
                coupon_info=val.get("coupon")
                default_price=val["default_price"]
                rebate_price=self.cal_coupon_price(default_price,coupon_info)
                price_list.append(rebate_price)
                cal_price[key]=rebate_price

        print("课程优惠券后价格列表price_list",price_list)
        total_price=sum(price_list)
        # 3 计算通用优惠券的价格
        global_coupon_id=choose_coupons.get("global_coupon_id")
        if global_coupon_id:

            global_coupons=data.get("global_coupons")
            print("global_coupons",global_coupons)
            global_coupon_dict={}
            for item in global_coupons:
                global_coupon_dict[item["pk"]]=item
            total_price=self.cal_coupon_price(total_price,global_coupon_dict[global_coupon_id])
            print("通用优惠券",global_coupon_dict[global_coupon_id]["coupon_type"])
            print("计算后total_price=",total_price)

        # 计算贝里
        if json.loads(is_beli):
            print("request.user.beli",request.user.beli)
            total_price=total_price-request.user.beli/10
            if total_price<0:
                total_price=0
            print("贝里数计算后",total_price)

        cal_price["total_price"]=total_price
        res.data=cal_price

        # except Exception as e:
        #     res.code=500
        #     res.msg="结算错误!"+str(e)

        return Response(res.dict)


'''
1 结算中心post添加接口数据结构:
        {
        "course_img": "https://luffycity.com/static/frontend/course/3/Django框架学习_1509095212.759272.png",
        "coupon_list": [{
            "name": "清明节活动",
            "minimum_consume": 0,
            "money_equivalent_value": 0.0,
            "off_percent": 80,
            "pk": 3,
            "coupon_type": "折扣券"
        }],
        "relate_price_policy": {
            "1": {
                "valid_period": 7,
                "valid_period_text": "1周",
                "prcie": 100.0,
                "default": true
            },
            "2": {
                "valid_period": 14,
                "valid_period_text": "2周",
                "prcie": 200.0,
                "default": false
            },
            "3": {
                "valid_period": 30,
                "valid_period_text": "1个月",
                "prcie": 300.0,
                "default": false
            }
        },
        "name": "Django框架学习",
        "default_price": 100.0,
        "id": 2,
        "default_price_period": 7,
        "default_price_policy_id": 1
    }


2 结算中心get查询接口:

{
    "data": {
        "total": 1,
        "global_coupons": [
            {
                "name": "国庆节活动通用券",
                "coupon_type": "满减券",
                "minimum_consume": 100,
                "money_equivalent_value": 50,
                "off_percent": null,
                "pk": 2
            }
        ],
        "total_price": "100.0",
        "account_course_list": [
            {
                "course_img": "https://luffycity.com/static/frontend/course/3/Django框架学习_1509095212.759272.png",
                "name": "Django框架学习",
                "relate_price_policy": {
                    "1": {
                        "valid_period": 7,
                        "prcie": 100,
                        "valid_period_text": "1周",
                        "default": true
                    },
                    "2": {
                        "valid_period": 14,
                        "prcie": 200,
                        "valid_period_text": "2周",
                        "default": false
                    },
                    "3": {
                        "valid_period": 30,
                        "prcie": 300,
                        "valid_period_text": "1个月",
                        "default": false
                    }
                },
                "coupon_list": [
                    {
                        "name": "清明节活动",
                        "coupon_type": "折扣券",
                        "minimum_consume": 0,
                        "money_equivalent_value": 0,
                        "off_percent": 80,
                        "pk": 3
                    }
                ],
                "default_price": 100,
                "id": 2,
                "default_price_period": 7,
                "default_price_policy_id": 1
            }
        ]
    },
    "code": 1000,
    "msg": ""
}


'''
