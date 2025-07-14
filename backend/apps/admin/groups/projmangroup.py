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
from apps.admin.pages.crrequest import CrRequest
from apps.admin.pages.crreview import CrReview

appdef = App()


class Projmangroup(admin.AdminApp):
    group_schema = 'Projman'
    page_schema = amis.PageSchema(label='Projman', title='Projman', icon='fa fa-folder', sort=10)
    router_prefix = '/projman'


    def __init__(self, app: "AdminApp"):
        super().__init__(app)
        self.register_admin(ChangerequestAdmin)
        self.register_admin(CrRequest)
        self.register_admin(CrReview)
