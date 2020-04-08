#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/8
import uuid
import string
import random
import time
from threading import Thread
from django.core.cache import cache
from fir_ser.settings import CACHE_KEY_TEMPLATE

'''
        user = cache.get(token)
        delta = datetime.timedelta(weeks=2) - delta
        cache.set(token_obj.key, token_obj.user, min(delta.total_seconds(), 3600 * 24 * 7))
'''

class DownloadToken(object):

    def make_token(self,release_id,time_limit=60):

        token_key = "%s%s"%(CACHE_KEY_TEMPLATE.get("make_token_key"),release_id)
        make_token_key = cache.get(token_key)
        if make_token_key:
            return make_token_key
        else:
            random_str = uuid.uuid1().__str__().split("-")[0:-1]
            user_ran_str = uuid.uuid5(uuid.NAMESPACE_DNS, release_id).__str__().split("-")
            user_ran_str.extend(random_str)
            new_str = "".join(user_ran_str)
            cache.set(new_str, {
                "atime":time.time()+time_limit,
                "data":release_id
            }, time_limit)
            cache.set(token_key,new_str,time_limit-1)
            return new_str

    def verify_token(self,token,release_id):
        try:
            values = cache.get(token)
            if release_id in values.get("data",None):
                return True
        except Exception as e:
            print(e)
            return False

        return False


class DownloadTokenLocal(object):


    TokenLists = []
    flag={'stat':1}
    def __init__(self):
        self.auto_clean_totken()


    def make_token(self,release_id,time_limit=60):
        random_str = uuid.uuid1().__str__().split("-")[0:-1]
        user_ran_str = uuid.uuid5(uuid.NAMESPACE_DNS, release_id).__str__().split("-")
        user_ran_str.extend(random_str)
        new_str = "".join(user_ran_str)
        self.TokenLists.append({new_str:{
            "atime":time.time()+time_limit,
            "data":release_id
        }})
        return new_str

    def verify_token(self,token,release_id):
        try:
            for itoken in self.TokenLists:
                if itoken.get(token,None):
                    if release_id in itoken.get(token,None).get("data",None):
                        return True
        except Exception as e:
            print(e)
            return False

        return False

    def auto_clean_totken(self):
        if self.flag.get("stat"):
            t=Thread(target=self.clean_Token)
            t.start()
            self.flag["stat"]=0

    def clean_Token(self):
        while True:
            ncount = len(self.TokenLists)
            ntime = time.time()
            for itokendic in self.TokenLists:
                for token, data in itokendic.items():
                    if int(ntime) - int(data["atime"]) > 0:
                            self.TokenLists.remove(itokendic)
            print("开始清理token，现在token:%s  清理token:%s 剩余token:%s"%(ncount,ncount-len(self.TokenLists),len(self.TokenLists)))
            time.sleep(30)


def generateTokenForMedium(medium):
    if medium == 'email':
        return generateAlphanumericTokenOfLength(32)
    elif medium == 'wechat':
        return 'WeChat'
    else:
        return generateNumericTokenOfLength(6)

def generateNumericTokenOfLength(length):
    return "".join([random.choice(string.digits) for _ in range(length)])

def generateAlphanumericTokenOfLength(length):
    return "".join([random.choice(string.digits + string.ascii_lowercase + string.ascii_uppercase) for _ in range(length)])
