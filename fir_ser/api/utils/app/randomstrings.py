#!/usr/bin/env python
# -*- coding:utf-8 -*-
# project: 3月 
# author: liuyu
# date: 2020/3/6
import uuid

def make_from_user_uuid(userinfo):
    user_id = userinfo.uid
    random_str = uuid.uuid1().__str__().split("-")[0:-1]
    user_ran_str=uuid.uuid5(uuid.NAMESPACE_DNS, user_id).__str__().split("-")
    user_ran_str.extend(random_str)
    new_str = "".join(user_ran_str)
    return new_str

def make_app_uuid(userinfo,bundleid):
    user_id = userinfo.uid
    app_uuid=uuid.uuid5(uuid.NAMESPACE_DNS, "%s"%(user_id+bundleid)).__str__().split("-")
    fapp_uuid = "".join(app_uuid)
    return fapp_uuid

def make_random_uuid():
    random_str = uuid.uuid1().__str__().split("-")
    return "".join(random_str)




