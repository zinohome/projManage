#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 10:12
# @Author  : ZhangJun
# @FileName: modelchecker.py

import os
import traceback
import shutil
import fastapi_amis_admin.admin.admin as file_admin
import fastapi_amis_admin.crud._sqlalchemy as file_sqlalchemy
import fastapi_user_auth.admin.admin as file_auth_admin
import fastapi_user_auth.admin.site as file_site
import fastapi_user_auth.auth.models as file_models

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
class Modelchecker():

    def check_models(self):
        # 定义文件目录 backend/construct
        basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
        # 应用目录 backend
        apppath = os.path.abspath(os.path.join(basepath, os.pardir))
        # 运行目录 backend/construct/update
        updatepath = os.path.abspath(os.path.join(apppath, 'construct/update'))
        log.debug("Check models Starting ...")
        try:
            for tfile in (file_admin, file_sqlalchemy, file_auth_admin, file_site, file_models):
                with open(tfile.__file__, "r") as rfile:
                    fline = rfile.readline()[0:12]
                    #log.debug(tfile.__name__.split('.'))
                    #log.debug(tfile.__name__.split('.')[0])
                    #log.debug(tfile.__name__.split('.')[-1])
                    if fline != "#  @Software":
                        match tfile.__name__.split('.')[-1]:
                            case "admin":
                                if tfile.__name__.split('.')[0] == 'fastapi_amis_admin':
                                    if os.path.exists(
                                        os.path.abspath(os.path.join(updatepath, 'fastapi_amis_admin/admin/admin.py'))):
                                        log.debug("Check model: %s ..." % tfile.__file__)
                                        shutil.copy(
                                            os.path.abspath(os.path.join(updatepath, 'fastapi_amis_admin/admin/admin.py')),
                                            tfile.__file__)
                                if tfile.__name__.split('.')[0] == 'fastapi_user_auth':
                                    if os.path.exists(
                                            os.path.abspath(
                                                os.path.join(updatepath, 'fastapi_user_auth/admin/admin.py'))):
                                        log.debug("Check model: %s ..." % tfile.__file__)
                                        shutil.copy(
                                            os.path.abspath(
                                                os.path.join(updatepath, 'fastapi_user_auth/admin/admin.py')),
                                            tfile.__file__)
                            case "_sqlalchemy":
                                if os.path.exists(
                                        os.path.abspath(os.path.join(updatepath, 'fastapi_amis_admin/crud/_sqlalchemy.py'))):
                                    log.debug("Check model: %s ..." % tfile.__file__)
                                    shutil.copy(
                                        os.path.abspath(os.path.join(updatepath, 'fastapi_amis_admin/crud/_sqlalchemy.py')),
                                        tfile.__file__)
                            case "site":
                                if os.path.exists(
                                        os.path.abspath(os.path.join(updatepath, 'fastapi_user_auth/admin/site.py'))):
                                    log.debug("Check model: %s ..." % tfile.__file__)
                                    shutil.copy(
                                        os.path.abspath(
                                            os.path.join(updatepath, 'fastapi_user_auth/admin/site.py')),
                                        tfile.__file__)
                            case "models":
                                if os.path.exists(
                                        os.path.abspath(os.path.join(updatepath, 'fastapi_user_auth/auth/models.py'))):
                                    log.debug("Check model: %s ..." % tfile.__file__)
                                    shutil.copy(
                                        os.path.abspath(
                                            os.path.join(updatepath, 'fastapi_user_auth/auth/models.py')),
                                        tfile.__file__)
                        #if os.path.exists(test_file.txt)
            log.debug("Check models completed ！")
        except Exception as exp:
            print('Exception at Modelchecker.check_models() %s ' % exp)
            traceback.print_exc()

if __name__ == '__main__':
    mc = Modelchecker()
    mc.check_models()