#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  #
#  Copyright (C) 2023 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2023
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: SwiftApp
from fastapi import APIRouter
from fastapi_amis_admin.crud import SqlalchemyCrud
from core.globals import site
from fastapi_amis_admin import amis, admin
from fastapi_amis_admin.admin import AdminApp
from construct.app import App
from utils.log import log as log
from apps.admin.pages.changerequestadmin import ChangerequestAdmin

appdef = App()


class Changerequestgroup(admin.AdminApp):
    group_schema = 'Changerequest'
    page_schema = amis.PageSchema(label='ChangeRequest', title='ChangeRequest', icon='fa fa-bolt', sort=10)
    router_prefix = '/changerequest'


    def __init__(self, app: "AdminApp"):
        super().__init__(app)
        self.register_admin(ChangerequestAdmin)
