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
from fastapi_amis_admin.utils.pydantic import model_fields
from starlette.requests import Request
from fastapi_amis_admin.admin import AdminAction
from fastapi_amis_admin.crud import CrudEnum, BaseApiOut
from fastapi_amis_admin.amis import PageSchema, TableColumn, ActionType, Action, Dialog, SizeEnum, Drawer, LevelEnum, \
    TableCRUD, TabsModeEnum, Form, AmisAPI, DisplayModeEnum, InputExcel, InputTable, Page, FormItem, SchemaNode, Group, \
    Divider
from fastapi_amis_admin.utils.translation import i18n as _
from apps.admin.swiftadmin import SwiftAdmin
from utils.log import log as log
from apps.admin.models.projman import Projman


class ProjmanAdmin(SwiftAdmin):
    group_schema = "Customers"
    page_schema = PageSchema(label='Customers', page_title='Customers', icon='fa fa-folder-open', sort=80)
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
        self.enable_bulk_create = True
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
            print('Exception at ProjmanAdmin.get_list_table() %s ' % exp)
            traceback.print_exc()

    def get_tabbed_form(self,fld_dict):
        # 检查是否缺少必需字段
        REQUIRED_FIELDS = [
            "customer_id", "customer_name",
            "business_category", "project_name", "project_location",
            "project_contact", "contact_phone", "service_content",
            "contract_amount", "contract_duration", "contract_sign_date",
            "contract_end_date", "expected_renewal_time", "cooperation_method",
            "is_bidding", "bidding_type", "project_number",
            "subject_matter", "budget_amount", "max_price",
            "publish_time", "deadline",
            "bid_price", "bid_date", "winning_company",
            "website_reference", "main_competitors", "others", "create_time", "update_time"
        ]
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
            customer_fld_lst.append(Group(body=[fld_dict["customer_id"], fld_dict["customer_name"]]))
            customer_tabitem = amis.Tabs.Item(title="客户基本信息", icon='fa fa-university', className="bg-blue-100",
                                         body=customer_fld_lst)

            # 项目基本信息 Tab
            project_fld_lst = []
            project_fld_lst.append(Divider())
            project_fld_lst.append(
                Group(body=[fld_dict["business_category"], fld_dict["project_name"], fld_dict["project_location"]]))
            project_fld_lst.append(Divider())
            project_fld_lst.append(
                Group(body=[fld_dict["project_contact"], fld_dict["contact_phone"]]))
            project_fld_lst.append(Divider())
            project_fld_lst.append(
                Group(body=[fld_dict["service_content"]]))
            project_fld_lst.append(Divider())
            project_fld_lst.append(
                Group(body=[fld_dict["contract_amount"], fld_dict["contract_duration"]]))
            project_fld_lst.append(Divider())
            project_fld_lst.append(
                Group(body=[fld_dict["contract_sign_date"],
                            fld_dict["contract_end_date"], fld_dict["expected_renewal_time"]]))
            project_fld_lst.append(Divider())
            project_fld_lst.append(
                Group(body=[fld_dict["cooperation_method"]]))
            project_tabitem = amis.Tabs.Item(title="项目基本信息", icon='fa fa-id-card', className="bg-red-100",
                                        body=project_fld_lst)

            # 招标信息 Tab
            bidding_fld_lst = []
            bidding_fld_lst.append(Divider())
            bidding_fld_lst.append(
                Group(body=[fld_dict["is_bidding"], fld_dict["bidding_type"], fld_dict["project_number"]]))
            bidding_fld_lst.append(Divider())
            bidding_fld_lst.append(
                Group(body=[fld_dict["subject_matter"], fld_dict["budget_amount"], fld_dict["max_price"]]))
            bidding_fld_lst.append(Divider())
            bidding_fld_lst.append(
                Group(body=[fld_dict["publish_time"], fld_dict["deadline"]]))
            bidding_tabitem = amis.Tabs.Item(title="招标信息", icon='fa fa-gavel', className="bg-purple-100",
                                        body=bidding_fld_lst)

            # 中标信息 Tab
            winning_fld_lst = []
            winning_fld_lst.append(Divider())
            winning_fld_lst.append(
                Group(body=[fld_dict["bid_price"]]))
            winning_fld_lst.append(Divider())
            winning_fld_lst.append(
                Group(body=[fld_dict["bid_date"]]))
            winning_fld_lst.append(Divider())
            winning_fld_lst.append(
                Group(body=[fld_dict["winning_company"]]))
            winning_tabitem = amis.Tabs.Item(title="中标信息", icon='fa fa-trophy', className="bg-yellow-100",
                                        body=winning_fld_lst)

            # 其他参考信息 Tab
            other_fld_lst = []
            other_fld_lst.append(Divider())
            other_fld_lst.append(
                Group(body=[fld_dict["website_reference"]]))
            other_fld_lst.append(Divider())
            other_fld_lst.append(
                Group(body=[fld_dict["main_competitors"]]))
            other_fld_lst.append(Divider())
            other_fld_lst.append(
                Group(body=[fld_dict["others"]]))
            other_fld_lst.append(Divider())
            other_fld_lst.append(Group(body=[fld_dict["create_time"], fld_dict["update_time"]]))
            other_tabitem = amis.Tabs.Item(title="其他参考信息", icon='fa fa-info', className="bg-green-100",
                                      body=other_fld_lst)

            # 将所有 Tab 项添加到 Tabs 中
            formtab.tabs.append(customer_tabitem)
            formtab.tabs.append(project_tabitem)
            formtab.tabs.append(bidding_tabitem)
            formtab.tabs.append(winning_tabitem)
            formtab.tabs.append(other_tabitem)

            return formtab
        except Exception as exp:
            print('Exception at ProjmanAdmin.get_tabbed_form() %s ' % exp)
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
            print('Exception at ProjmanAdmin.get_read_form() %s ' % exp)
            traceback.print_exc()

    async def get_create_form(self, request: Request, bulk: bool = False) -> Form:
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
                fields = [field for field in model_fields(self.schema_create).values() if field.name != self.pk_name]
                columns, keys = [], {}
                for field in fields:
                    column = await self.get_list_column(request, self.parser.get_modelfield(field))
                    keys[column.name] = "${" + column.label + "}"
                    column.name = column.label
                    columns.append(column)
                return Form(
                    api=AmisAPI(
                        method="post",
                        url=f"{self.router_path}/item",
                        data={"&": {"$excel": keys}},
                    ),
                    name=CrudEnum.create,
                    mode=DisplayModeEnum.normal,
                    body=[
                        InputExcel(name="excel"),
                        InputTable(
                            name="excel",
                            showIndex=True,
                            columns=columns,
                            addable=False,
                            copyable=False,
                            editable=True,
                            removable=True,
                        ),
                    ],
                )

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
            formtab = self.get_tabbed_form(fld_dict)
            u_form.body = formtab
            return u_form
        except Exception as exp:
            print('Exception at ProjmanAdmin.get_update_form() %s ' % exp)
            traceback.print_exc()

    async def get_duplicate_form_inner(self, request: Request, bulk: bool = False) -> Form:
        try:
            extra = {}
            if not bulk:
                api = f"post:{self.router_path}/item"
                #fields = self.schema_model.model_fields.values()
                fields = [field for field in model_fields(self.schema_create).values() if field.name != self.pk_name]
                if self.schema_read:
                    extra["initApi"] = f"get:{self.router_path}/item/${self.pk_name}"

            d_form = Form(
                api=api,
                name="create",
                body=await self._conv_modelfields_to_formitems(request, fields, CrudEnum.create),
                **extra,
            )
            if not bulk:
                # 强制tab
                fieldlist = [item for item in d_form.body]
                fld_dict = {item.name: item for item in fieldlist}
                formtab = amis.Tabs(tabsMode='strong')
                formtab.tabs = []
                formtab = self.get_tabbed_form(fld_dict)
                d_form.body = formtab
            return d_form
        except Exception as exp:
            print('Exception at ProjmanAdmin.get_duplicate_form_inner() %s ' % exp)
            traceback.print_exc()
            # 显式抛出异常，以便于上层感知
            raise

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
