#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  #
#  Copyright (C) 2023 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2023
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: SwiftApp
from fastapi._compat import ModelField
from fastapi_amis_admin.admin import AdminAction
from fastapi_amis_admin.crud import CrudEnum
from fastapi_amis_admin.crud.base import SchemaFilterT
from fastapi_amis_admin.crud.parser import TableModelParser
from fastapi_amis_admin.utils.pydantic import model_fields
from pydantic._internal._decorators import mro

from apps.admin.swiftadmin import SwiftAdmin
from core.globals import site
from typing import List, Optional, TYPE_CHECKING, Union, Dict, Any
from fastapi_amis_admin import admin, amis
from fastapi_amis_admin.amis import PageSchema, TableColumn, ActionType, Action, Dialog, SizeEnum, Drawer, LevelEnum, \
    TableCRUD, TabsModeEnum, Form, AmisAPI, DisplayModeEnum, InputExcel, InputTable, Page, FormItem, SchemaNode
from starlette.requests import Request
import simplejson as json
from fastapi_amis_admin.utils.translation import i18n as _
from utils.log import log as log
from apps.admin.models.changerequest import Changerequest


class ChangerequestAdmin(SwiftAdmin):
    group_schema = "Changerequest"
    page_schema = PageSchema(label='ChangeRequest', page_title='ChangeRequest', icon='fa fa-bolt', sort=96)
    model = Changerequest
    pk_name = 'id'
    list_per_page = 30
    list_display = [Changerequest.id,Changerequest.customer_name,Changerequest.ssr,Changerequest.sngl_pnt_sys,Changerequest.urgency,Changerequest.complexity,Changerequest.support_tsg_id,Changerequest.begin_date,Changerequest.end_date,Changerequest.tsg_rvew_rslt]
    search_fields = []
    parent_class = None
    tabsMode = TabsModeEnum.card

    def __init__(self, app: "AdminApp"):
        super().__init__(app)
        # 启用批量新增
        self.enable_bulk_create = False
        # 启用查看
        self.schema_read = None
        # 设置form弹出类型  Drawer | Dialog
        self.action_type = 'Drawer'


    async def get_print_action(self, request: Request) -> Optional[Action]:
        if not self.schema_read:
            return None
        actiontype = ActionType.Dialog(
            icon="fas fa-print",
            tooltip=_("Print"),
            dialog=Dialog(
                title=_(self.page_schema.label),
                size=SizeEnum.lg,
                showCloseButton=False,
                actions=[
                    {
                        "type": "button",
                        "actionType": "cancel",
                        "label": "取消",
                        "Style": {
                            ".noprint": {
                                "display": "none"
                            }
                        },
                        "primary": False
                    },
                    {
                        "type": "button",
                        "label": "打印",
                        "onEvent": {
                            "click": {
                                "actions": [
                                    {
                                        "actionType": "custom",
                                        "ignoreError": False,
                                        "script": "doAction(window.print());"
                                    }
                                ]
                            }
                        },
                        "wrapperCustomStyle": {
                            ".noprint": {
                                "display": "none"
                            }
                        },
                        "primary": True
                    }
                ],
                body=await self.get_print_form(request),
            ),
        )
        return actiontype

    async def get_print_form(self, request: Request) -> Form:
        p_form = await super().get_read_form(request)
        p_form.columnCount = 2
        # 构建主表Read
        # 构建子表CRUD
        table = await self.get_sub_list_table(self.app.get_model_admin('contractdetail'), request)
        table.headerToolbar = []
        table.footerToolbar = []
        table.affixHeader = True
        table.itemActions = None
        table.columnsTogglable = False
        # 增加子表外键过滤
        table.api.data['contract_id'] = f"${self.pk_name}"
        p_form.body.append(table)
        return p_form

    async def get_read_form(self, request: Request) -> Form:
        r_form = await super().get_read_form(request)
        # 构建主表Read
        formtab = amis.Tabs(tabsMode='strong')
        formtab.tabs = []
        fieldlist = []
        for item in r_form.body:
            if item.name != self.pk_name:
                fieldlist.append(item)
        basictabitem = amis.Tabs.Item(title=_('基本信息'), icon='fa fa-square', body=fieldlist)
        formtab.tabs.append(basictabitem)

        # 构建子表CRUD
        table =await self.get_sub_list_table(self.app.get_model_admin('contractdetail'), request)
        headerToolbar = [
            {"type": "columns-toggler", "align": "left", "draggable": False},
            {"type": "reload", "align": "right"}
        ]
        table.headerToolbar = headerToolbar
        table.itemActions = None
        # 增加子表外键过滤
        table.api.data['contract_id'] = f"${self.pk_name}"
        #log.debug(table.api)
        detailtabitem = amis.Tabs.Item(title=_('合同明细'), icon='fa fa-square', body=table)
        detailtabitem.disabled = False
        formtab.tabs.append(detailtabitem)
        r_form.body = formtab
        return r_form

    async def get_read_form(self, request: Request) -> Form:
        r_form = await super().get_read_form(request)
        # 构建主表Read
        formtab = amis.Tabs(tabsMode='strong')
        formtab.tabs = []
        fieldlist = []
        for item in r_form.body:
            if item.name != self.pk_name:
                fieldlist.append(item)
        basictabitem = amis.Tabs.Item(title=_('基本信息'), icon='fa fa-square', body=fieldlist)
        formtab.tabs.append(basictabitem)
        r_form.body = formtab
        return r_form


    async def get_create_form(self, request: Request, bulk: bool = False) -> Form:
        c_form = await super().get_create_form(request, bulk)
        if not bulk:
            # 构建主表Create
            formtab = amis.Tabs(tabsMode='strong')
            formtab.tabs = []
            fieldlist = []
            for item in c_form.body:
                fieldlist.append(item)
            basictabitem = amis.Tabs.Item(title=_('基本信息'), icon='fa fa-square', body=fieldlist)
            formtab.tabs.append(basictabitem)
            c_form.body = formtab
        return c_form

    async def get_update_form(self, request: Request, bulk: bool = False) -> Form:
        u_form = await super().get_update_form(request, bulk)
        if not bulk:
            # 构建主表Update
            formtab = amis.Tabs(tabsMode='strong')
            formtab.tabs = []
            fieldlist = []
            for item in u_form.body:
                fieldlist.append(item)
            basictabitem = amis.Tabs.Item(title=_('基本信息'), icon='fa fa-square', body=fieldlist)
            formtab.tabs.append(basictabitem)
            u_form.body = formtab
        return u_form
