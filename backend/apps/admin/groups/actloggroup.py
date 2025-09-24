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

from apps.admin.pages.actchart import ActChartAdmin
from apps.admin.pages.actlogadmin import ActLogAdmin
from core.globals import site
from fastapi_amis_admin import amis, admin
from fastapi_amis_admin.admin import AdminApp
from construct.app import App
from utils.log import log as log
from apps.admin.pages.changerequestadmin import ChangerequestAdmin
from apps.admin.pages.crrequest import CrRequest
from apps.admin.pages.crreview import CrReview

appdef = App()


class ActLoggroup(admin.AdminApp):
    group_schema = 'ActLog'
    page_schema = amis.PageSchema(label='ActLog', title='ActLog', icon='fa fa-folder', sort=10)
    router_prefix = '/actlog'


    def __init__(self, app: "AdminApp"):
        super().__init__(app)
        self.register_admin(ActLogAdmin)
        self.register_admin(ActChartAdmin)

