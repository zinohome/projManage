#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/04/03 10:12
# @Author  : ZhangJun
# @FileName: userselect.py

import os
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

import simplejson as json
from utils.log import log as log


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEF_DIR = os.path.join(BASE_DIR, 'construct')

class obj(object):
    def __init__(self, dict_):
        self.__dict__.update(dict_)

def singleton(cls):
    _instance = {}

    def inner():
        if cls not in _instance:
            _instance[cls] = cls()
        return _instance[cls]
    return inner

@singleton
class UserSelect(object):
    def __init__(self):
        self.TLS = None
        self.tls_dict = None
        self.Mission = None
        self.mission_dict = None
        self.Sales = None
        self.sales_dict = None
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        jsonpath = os.path.abspath(os.path.join(apppath, 'userselect.json'))
        try:
            with open(jsonpath, 'r', encoding="utf-8") as app_file:
                content = app_file.read()
            user_obj = json.loads(content)
            self.TLS = sorted(user_obj['TLS'], key=lambda x: x['nickname'])
            self.tls_dict = {tls["id"]: tls for tls in self.TLS}
            self.Mission = sorted(user_obj['TLS Mission'], key=lambda x: x['nickname'])
            self.mission_dict = {mission["id"]: mission for mission in self.Mission}
            self.Sales = sorted(user_obj['Global Sales'], key=lambda x: x['nickname'])
            self.sales_dict = {sales["id"]: sales for sales in self.Sales}
        except Exception as exp:
            print('Exception at UserSelect.__init__() %s ' % exp)
            traceback.print_exc()

    def find_tls_email_by_id(self, target_id):
        tls_info = self.tls_dict.get(target_id)
        if tls_info:
            return tls_info["email"]
        else:
            return "yangq@cn.ibm.com"
    def find_mission_email_by_id(self, target_id):
        mission_info = self.mission_dict.get(target_id)
        if mission_info:
            return mission_info["email"]
        else:
            return "yangq@cn.ibm.com"

    def find_sales_email_by_id(self, target_id):
        sales_info = self.sales_dict.get(target_id)
        if sales_info:
            return sales_info["email"]
        else:
            return "yangq@cn.ibm.com"

    def get_nickname(self, target_id):
        """
        从三个字典中用最快的速度根据id找到对应的nickname

        Args:
            target_id: 要查找的用户ID

        Returns:
            str: 找到的nickname，如果所有字典中都不存在，则返回"Unknown"
        """
        # 由于字典的查找是O(1)的，所以这是最快的查找方式
        # 依次检查三个字典
        if target_id in self.tls_dict:
            return self.tls_dict[target_id]["nickname"]
        if target_id in self.mission_dict:
            return self.mission_dict[target_id]["nickname"]
        if target_id in self.sales_dict:
            return self.sales_dict[target_id]["nickname"]
        # 如果所有字典中都不存在，则返回默认值
        return "Unknown"

    def get_org(self, target_id):
        """
        从三个字典中用最快的速度根据id找到对应的nickname

        Args:
            target_id: 要查找的用户ID

        Returns:
            str: 找到的nickname，如果所有字典中都不存在，则返回"Unknown"
        """
        # 由于字典的查找是O(1)的，所以这是最快的查找方式
        # 依次检查三个字典
        if target_id in self.tls_dict:
            return self.tls_dict[target_id]["organization"]
        if target_id in self.mission_dict:
            return self.mission_dict[target_id]["organization"]
        if target_id in self.sales_dict:
            return self.sales_dict[target_id]["organization"]
        # 如果所有字典中都不存在，则返回默认值
        return "Unknown"

    def get_manager(self, target_id):
        """
        从三个字典中用最快的速度根据id找到对应的nickname

        Args:
            target_id: 要查找的用户ID

        Returns:
            str: 找到的nickname，如果所有字典中都不存在，则返回"Unknown"
        """
        # 由于字典的查找是O(1)的，所以这是最快的查找方式
        # 依次检查三个字典
        if target_id in self.tls_dict:
            return self.tls_dict[target_id]["manager"]
        if target_id in self.mission_dict:
            return self.mission_dict[target_id]["manager"]
        if target_id in self.sales_dict:
            return self.sales_dict[target_id]["manager"]
        # 如果所有字典中都不存在，则返回默认值
        return "Unknown"


if __name__ == '__main__':
    userselect = UserSelect()
    log.debug(userselect.tls_dict)
    log.debug(userselect.mission_dict)
    log.debug(userselect.sales_dict)
    log.debug(userselect.get_nickname('952530'))
    log.debug(userselect.get_org('952530'))
    log.debug(userselect.get_manager('952530'))
    log.debug(userselect.get_org('952530'))
    log.debug(userselect.get_manager('952530'))

    log.debug(datetime.now().astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M"))

