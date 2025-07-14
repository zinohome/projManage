#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 10:46
# @Author  : ZhangJun
# @FileName: apphome.py

from fastapi_amis_admin.admin import AdminApp
from starlette.requests import Request

from construct.app import App
from fastapi_amis_admin import amis
from utils.log import log as log

appdef = App()
class AppHome(AdminApp):
    group_schema = 'Home'
    page_schema = amis.PageSchema(label='Home', title=f"{appdef.AppTitle}", icon='fa fa-bolt', sort=99)
    router_prefix = '/home'

    async def has_page_permission(self, request: Request) -> bool:
        return True
    def __init__(self, app: "AdminApp"):
        super().__init__(app)