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
from zoneinfo import ZoneInfo
from typing import List, Optional, Union, Dict, Any, Callable

from fastapi_amis_admin import amis
from starlette.requests import Request
from fastapi_amis_admin.admin import AdminAction
from fastapi_amis_admin.crud import CrudEnum, BaseApiOut
from fastapi_amis_admin.amis import PageSchema, TableColumn, ActionType, Action, Dialog, SizeEnum, Drawer, LevelEnum, \
    TableCRUD, TabsModeEnum, Form, AmisAPI, DisplayModeEnum, InputExcel, InputTable, Page, FormItem, SchemaNode, Group, \
    Divider
from fastapi_amis_admin.utils.translation import i18n as _
from apps.admin.swiftadmin import SwiftAdmin
from apps.admin.models.projman import Projman


class ProjmanAdmin(SwiftAdmin):
    group_schema = "Projman"
    page_schema = PageSchema(label='项目管理', page_title='项目管理', icon='fa fa-folder-open', sort=80)
    model = Projman
    pk_name = 'id'
    list_per_page = 20
    list_filter = [
        Projman.customer_id, Projman.customer_name, Projman.business_category,
        Projman.project_name, Projman.project_location, Projman.project_contact,
        Projman.cooperation_method, Projman.is_bidding, Projman.bidding_type,
        Projman.project_number, Projman.subject_matter, Projman.contract_sign_date,
        Projman.contract_end_date, Projman.update_time
    ]
    search_fields = [
        Projman.customer_id, Projman.customer_name,
        Projman.project_name, Projman.main_competitors, Projman.others
    ]
    parent_class = None
    tabsMode = TabsModeEnum.card
    admin_action_maker = [
        lambda self: AdminAction(
            admin=self,
            name="copy",
            tooltip="复制",
            flags=["item"],
            getter=lambda request: self.get_duplicate_action(request, bulk=False),
        )
    ]

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

    # 项目管理Tab页面布局（可根据实际字段分组优化）
    @staticmethod
    def get_tabbed_form(fld_dict):
        proj_fld_lst1 = []
        proj_fld_lst1.append(
            Group(body=[fld_dict["customer_id"], fld_dict["customer_name"], fld_dict["business_category"]]))
        proj_fld_lst1.append(Group(body=[
            fld_dict["project_name"], fld_dict["project_location"], fld_dict["project_contact"],
            fld_dict["contact_phone"]
        ]))
        proj_fld_lst1.append(Divider())
        proj_fld_lst1.append(
            Group(body=[
                fld_dict["service_content"], fld_dict["contract_amount"],
                fld_dict["contract_duration"], fld_dict["contract_sign_date"], fld_dict["contract_end_date"],
                fld_dict["expected_renewal_time"]
            ])
        )
        proj_fld_lst1.append(Divider())
        proj_fld_lst1.append(
            Group(body=[
                fld_dict["cooperation_method"], fld_dict["is_bidding"], fld_dict["bidding_type"],
                fld_dict["main_competitors"]
            ])
        )
        proj_fld_lst1.append(Divider())

        proj_fld_lst1.append(
            Group(body=[
                fld_dict["project_number"], fld_dict["subject_matter"], fld_dict["budget_amount"],
                fld_dict["max_price"],
                fld_dict["publish_time"], fld_dict["deadline"]
            ])
        )
        proj_fld_lst1.append(Divider())
        proj_fld_lst1.append(
            Group(body=[
                fld_dict["bid_price"], fld_dict["bid_date"], fld_dict["winning_company"], fld_dict["website_reference"]
            ])
        )
        proj_fld_lst1.append(Divider())
        proj_fld_lst1.append(
            Group(body=[fld_dict["others"]])
        )
        proj_fld_lst1.append(Divider())
        proj_fld_lst1.append(
            Group(body=[fld_dict["create_time"], fld_dict["update_time"]])
        )

        # 主分tab
        tabitem = amis.Tabs.Item(
            title=_('基础信息'),
            icon='fa fa-folder-open',
            className="bg-blue-100",
            body=proj_fld_lst1
        )
        return tabitem

    async def get_read_form(self, request: Request) -> Form:
        try:
            r_form = await super().get_read_form(request)
            formtab = amis.Tabs(tabsMode='strong')
            formtab.tabs = []
            fieldlist = [item for item in r_form.body]
            fld_dict = {item.name: item for item in fieldlist}
            formtab.tabs.append(self.get_tabbed_form(fld_dict))
            r_form.body = formtab
            return r_form
        except Exception as exp:
            print('Exception at ProjmanAdmin.get_read_form() %s ' % exp)
            traceback.print_exc()

    async def get_create_form(self, request: Request, bulk: bool = False) -> Form:
        try:
            c_form = await super().get_create_form(request, bulk)
            c_form.preventEnterSubmit = True
            fieldlist = [item for item in c_form.body]
            fld_dict = {item.name: item for item in fieldlist}
            formtab = amis.Tabs(tabsMode='strong')
            formtab.tabs = []
            formtab.tabs.append(self.get_tabbed_form(fld_dict))
            c_form.body = formtab
            return c_form
        except Exception as exp:
            print('Exception at ProjmanAdmin.get_create_form() %s ' % exp)
            traceback.print_exc()

    async def get_update_form(self, request: Request, bulk: bool = False) -> Form:
        try:
            u_form = await super().get_update_form(request, bulk)
            u_form.preventEnterSubmit = True
            fieldlist = [item for item in u_form.body]
            fld_dict = {item.name: item for item in fieldlist}
            formtab = amis.Tabs(tabsMode='strong')
            formtab.tabs = []
            formtab.tabs.append(self.get_tabbed_form(fld_dict))
            u_form.body = formtab
            return u_form
        except Exception as exp:
            print('Exception at ProjmanAdmin.get_update_form() %s ' % exp)
            traceback.print_exc()

    async def get_duplicate_form_inner(self, request: Request, bulk: bool = False) -> Form:
        try:
            extra = {}
            api = f"post:{self.router_path}/item"
            fields = self.schema_model.__fields__.values()
            if self.schema_read:
                extra["initApi"] = f"get:{self.router_path}/item/${self.pk_name}"

            d_form = Form(
                api=api,
                name="create",
                body=await self._conv_modelfields_to_formitems(request, fields, CrudEnum.create),
                **extra,
            )
            # 强制tab
            fieldlist = [item for item in d_form.body]
            fld_dict = {item.name: item for item in fieldlist}
            formtab = amis.Tabs(tabsMode='strong')
            formtab.tabs = []
            formtab.tabs.append(self.get_tabbed_form(fld_dict))
            d_form.body = formtab
            return d_form
        except Exception as exp:
            print('Exception at ProjmanAdmin.get_duplicate_form_inner() %s ' % exp)
            traceback.print_exc()

    async def get_duplicate_form(self, request: Request, bulk: bool = False) -> Form:
        d_form = await self.get_duplicate_form_inner(request, bulk)
        d_form.preventEnterSubmit = True
        return d_form

    async def get_duplicate_action(self, request: Request, bulk: bool = False) -> Optional[Action]:
        try:
            if not bulk:
                if self.action_type == 'Drawer':
                    return ActionType.Drawer(
                        icon="fa fa-copy",
                        tooltip=_("复制"),
                        drawer=Drawer(
                            title=_("复制") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.createactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_duplicate_form(request, bulk=bulk),
                        ),
                    )
                else:
                    return ActionType.Dialog(
                        icon="fa fa-copy",
                        tooltip=_("复制"),
                        dialog=Dialog(
                            title=_("复制") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.createactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_duplicate_form(request, bulk=bulk),
                        ),
                    )
            else:
                return None
        except Exception as exp:
            print('Exception at ProjmanAdmin.get_duplicate_action() %s ' % exp)
            traceback.print_exc()

    async def on_create_pre(
            self, request: Request, obj: Any, **kwargs,
    ) -> Dict[str, Any]:
        data = await super().on_create_pre(request, obj)
        data['create_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        data['update_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        return data

    async def on_update_pre(
            self, request: Request, obj: Any, item_id: Union[List[str], List[int]], **kwargs,
    ) -> Dict[str, Any]:
        data = await super().on_update_pre(request, obj, item_id)
        data['update_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        return data
