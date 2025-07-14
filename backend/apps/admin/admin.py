#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 10:54
# @Author  : ZhangJun
# @FileName: admin.py
import importlib
import inspect
import os

from utils.modelchecker import Modelchecker

# 更新系统库文件
mc = Modelchecker()
mc.check_models()
from core.globals import site
from construct.app import App
from utils.log import log as log

appdef = App()


# 定义文件目录 backend/apps/admin
basepath = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
# 应用目录 backend/apps
apppath = os.path.abspath(os.path.join(basepath, os.pardir))
# 运行目录 backend/apps/groups
grouppath = os.path.abspath(os.path.join(apppath, 'admin/groups'))

items = os.scandir(grouppath)
for file in items:
    if file.is_file() and file.name != '__init__.py':
        module_name = 'apps.admin.groups.' + os.path.splitext(file.name)[0]
        adminmodel = importlib.import_module(module_name)
        for name, class_ in inspect.getmembers(adminmodel, inspect.isclass):
            if name.lower() == os.path.splitext(file.name)[0]:
                log.debug("Regist admin module [ %s ] ..." % name)
                site.register_admin(class_)

#site.register_admin(AppHome)
#site.register_admin(Contractadmingroup, Customeradmingroup)


