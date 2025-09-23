#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  #
#  Copyright (C) 2024 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2024
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: SwiftApp

import traceback
from datetime import datetime
from fastapi_amis_admin import amis
from fastapi_amis_admin.utils.pydantic import model_fields
from fastapi_user_auth.globals import auth
from fastapi_amis_admin.crud import CrudEnum, BaseApiOut
from fastapi_amis_admin.amis import PageSchema, TableColumn, ActionType, Action, Dialog, SizeEnum, Drawer, LevelEnum, \
    TableCRUD, TabsModeEnum, Form, AmisAPI, DisplayModeEnum, InputExcel, InputTable, Page, FormItem, SchemaNode, Group, \
    Divider
from fastapi_amis_admin.utils.translation import i18n as _

from apps.admin.models.actlog import ActLog
from apps.admin.swiftadmin import SwiftAdmin
from utils.log import log as log
from fastapi import Body, Depends, FastAPI, HTTPException, Request

class ActLogAdmin(SwiftAdmin):
    group_schema = "ActLog"
    page_schema = PageSchema(label='ActLog', page_title='ActLog', icon='fa fa-folder-open', sort=80)
    model = ActLog
    pk_name = 'id'
    list_per_page = 20
    list_filter = [ActLog.act_type,ActLog.act_name,ActLog.act_org,ActLog.act_manager,ActLog.act_time]
    search_fields = [ActLog.act_type,ActLog.act_name,ActLog.act_org,ActLog.act_manager,ActLog.act_time]
    parent_class = None
    createactions = [
        {
            "type": "button",
            "actionType": "cancel",
            "icon": "fa fa-reply",
            "label": "取消",
            "primary": False
        },
        {
            "type": "button",
            "icon": "fa fa-save",
            "onEvent": {
                "click": {"actions": [{"actionType": "submit", "componentId": "form_setvalue"}]}
            },
            "label": "保存",
            "primary": True
        }
    ]
    readactions = [
        {
            "type": "button",
            "actionType": "cancel",
            "icon": "fa fa-reply",
            "label": "取消",
            "primary": False
        }
    ]
    def __init__(self, app: "AdminApp"):
        super().__init__(app)
        self.enable_bulk_create = False
        self.schema_read = None
        self.action_type = 'Drawer'


    async def get_list_table(self, request: Request) -> TableCRUD:
        '''
        headerToolbar = [
            "filter-toggler",
            "reload",
            "bulkActions",
            {"type": "columns-toggler", "align": "right"},
            {"type": "drag-toggler", "align": "right"},
            {"type": "pagination", "align": "right"},
            {
                "type": "tpl",
                "tpl": _("SHOWING ${items|count} OF ${total} RESULT(S)"),
                "className": "v-middle",
                "align": "right",
            },
        ]
        '''
        try:
            headerToolbar = [{"type": "columns-toggler", "align": "left", "draggable": False},
                             {"type": "filter-toggler", "align": "left"}]
            headerToolbar.extend(await self.get_actions(request, flag="toolbar"))
            headerToolbarright = [{"type": "export-excel", "align": "right"},
                                  {"type": "reload", "align": "right"},
                                  {"type": "bulkActions", "align": "right"}]
            headerToolbar.extend(headerToolbarright)
            itemActions = []
            if not self.display_item_action_as_column:
                itemActions = await self.get_actions(request, flag="item")
            filter_form = None
            if await self.has_filter_permission(request, None):
                filter_form = await self.get_list_filter_form(request)
            table = TableCRUD(
                api=await self.get_list_table_api(request),
                autoFillHeight=True,
                headerToolbar=headerToolbar,
                filterTogglable=True,
                filterDefaultVisible=True,
                filter=filter_form,
                syncLocation=False,
                keepItemSelectionOnPageChange=True,
                perPage=self.list_per_page,
                itemActions=itemActions,
                bulkActions=await self.get_actions(request, flag="bulk"),
                footerToolbar=[
                    "statistics",
                    "switch-per-page",
                    "pagination",
                    "load-more",
                    {
                        "type": "tpl",
                        "tpl": _("SHOWING ${items|count} OF ${total} RESULT(S)"),
                        "className": "v-middle",
                        "align": "right",
                    },
                ],
                columns=await self.get_list_columns(request),
                primaryField=self.pk_name,
                quickSaveItemApi=f"put:{self.router_path}/item/${self.pk_name}",
                defaultParams={k: v for k, v in request.query_params.items() if v},
            )
            # Append operation column
            action_columns = await self._get_list_columns_for_actions(request)
            table.columns.extend(action_columns)
            # Append inline link model column
            link_model_columns = await self._get_list_columns_for_link_model(request)
            if link_model_columns:
                table.columns.extend(link_model_columns)
                table.footable = True
            return table
        except Exception as exp:
            print('Exception at ActLogAdmin.get_list_table() %s ' % exp)
            traceback.print_exc()

    def get_tabbed_form(self,fld_dict):
        # 检查是否缺少必需字段
        REQUIRED_FIELDS = ["act_type", "act_username","act_name","act_org","act_manager","act_time"]
        # 检查是否缺少必需字段
        missing_fields = []
        for field in REQUIRED_FIELDS:
            if field not in fld_dict:
                missing_fields.append(field)
            elif fld_dict[field] is None:
                missing_fields.append(field)
        if missing_fields:
            log.error(f"缺少必需字段: {', '.join(missing_fields)}")

        try:
            # 初始化 Tabs
            formtab = amis.Tabs(tabsMode='strong')
            formtab.tabs = []
            # 客户基本信息 Tab
            customer_fld_lst = []
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(Group(body=[fld_dict["act_type"]]))
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(Group(body=[fld_dict["act_username"], fld_dict["act_name"]]))
            customer_fld_lst.append(Group(body=[fld_dict["act_org"], fld_dict["act_manager"], fld_dict["act_time"]]))
            customer_tabitem = amis.Tabs.Item(title="日志信息", icon='fa fa-info', className="bg-blue-100",
                                         body=customer_fld_lst)
            # 将所有 Tab 项添加到 Tabs 中
            formtab.tabs.append(customer_tabitem)
            return formtab
        except Exception as exp:
            print('Exception at ActLogAdmin.get_tabbed_form() %s ' % exp)
            import traceback
            traceback.print_exc()


    async def get_read_form(self, request: Request) -> Form:
        try:
            r_form = await super().get_read_form(request)
            formtab = amis.Tabs(tabsMode='strong')
            formtab.tabs = []
            fieldlist = [item for item in r_form.body]
            # 设置只读
            for item in fieldlist:
                item.disabled = True
            fld_dict = {item.name: item for item in fieldlist}
            formtab = amis.Tabs(tabsMode='strong')
            formtab.tabs = []
            formtab = self.get_tabbed_form(fld_dict)
            r_form.body = formtab
            return r_form
        except Exception as exp:
            print('Exception at ActLogAdmin.get_read_form() %s ' % exp)
            traceback.print_exc()

    async def get_create_form(self, request: Request, bulk: bool = False) -> Form:
        user = await auth.get_current_user(request)
        #log.debug(f'user: {user}')
        try:
            if not bulk:
                c_form = await super().get_create_form(request, bulk)
                c_form.preventEnterSubmit = True
                fieldlist = [item for item in c_form.body]
                fld_dict = {item.name: item for item in fieldlist}
                formtab = amis.Tabs(tabsMode='strong')
                formtab.tabs = []
                formtab = self.get_tabbed_form(fld_dict)
                c_form.body = formtab
                return c_form
            else:
                fields = [field for field in model_fields(self.schema_create).values() if field.name != self.pk_name and field.name not in ['creator', 'create_time', 'update_time']]
                #log.debug(fields)
                columns, keys = [], {}
                for field in fields:
                    column = await self.get_list_column(request, self.parser.get_modelfield(field))
                    column.quickEdit=False
                    column.id=column.name
                    #log.debug(column)
                    keys[column.name] = "${" + column.label + "}"
                    column.name = column.label
                    columns.append(column)
                #log.debug(keys)
                return Form(
                    api=AmisAPI(
                        method="post",
                        url=f"{self.router_path}/item",
                        data={"&": {"$excel": keys}},
                    ),
                    name=CrudEnum.create,
                    mode=DisplayModeEnum.normal,
                    body=[
                        InputExcel(name="excel",plainText=True),
                        InputTable(
                            name="excel",
                            showIndex=True,
                            columns=columns,
                            addable=False,
                            copyable=False,
                            editable=False,
                            removable=True,
                        ),
                    ],
                )

        except Exception as exp:
            print('Exception at ActLogAdmin.get_create_form() %s ' % exp)
            traceback.print_exc()

    async def get_update_form(self, request: Request, bulk: bool = False) -> Form:
        try:
            u_form = await super().get_update_form(request, bulk)
            u_form.preventEnterSubmit = True
            fieldlist = [item for item in u_form.body]
            fld_dict = {item.name: item for item in fieldlist}
            formtab = amis.Tabs(tabsMode='strong')
            formtab.tabs = []
            formtab = self.get_tabbed_form(fld_dict)
            u_form.body = formtab
            return u_form
        except Exception as exp:
            print('Exception at ActLogAdmin.get_update_form() %s ' % exp)
            traceback.print_exc()

