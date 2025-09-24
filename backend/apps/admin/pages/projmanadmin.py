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
from fastapi_amis_admin.crud.parser import parse_obj_to_schema
from fastapi_amis_admin.utils.pydantic import model_fields
from fastapi_user_auth.auth.schemas import SystemUserEnum
from fastapi_user_auth.globals import auth
from pygments.lexers import q
from starlette.requests import Request
from fastapi_amis_admin.admin import AdminAction
from fastapi_amis_admin.crud import CrudEnum, BaseApiOut, ItemListSchema
from fastapi_amis_admin.amis import PageSchema, TableColumn, ActionType, Action, Dialog, SizeEnum, Drawer, LevelEnum, \
    TableCRUD, TabsModeEnum, Form, AmisAPI, DisplayModeEnum, InputExcel, InputTable, Page, FormItem, SchemaNode, Group, \
    Divider
from fastapi_amis_admin.utils.translation import i18n as _
from apps.admin.swiftadmin import SwiftAdmin
from utils.actlogtool import add_act_log
from utils.log import log as log
from apps.admin.models.projman import Projman
from utils.projectIDGenerator import ProjectIDGenerator
from fastapi import Body, Depends, FastAPI, HTTPException, Request
from typing_extensions import Annotated, Literal
from fastapi_amis_admin.globals.deps import SyncSess, AsyncSess
from sqlalchemy import text, func, Select


class ProjmanAdmin(SwiftAdmin):
    group_schema = "Customers"
    page_schema = PageSchema(label='Customers', page_title='Customers', icon='fa fa-users', sort=80)
    model = Projman
    pk_name = 'id'
    list_per_page = 20
    list_filter = [
        Projman.customer_name, Projman.project_name, Projman.customer_location, Projman.business_category, Projman.project_location,
        Projman.contract_sign_date, Projman.contract_end_date, Projman.bidding_type, Projman.main_competitors
    ]
    search_fields = [
        Projman.customer_name, Projman.project_name, Projman.customer_location, Projman.business_category, Projman.project_location,
        Projman.contract_sign_date, Projman.contract_end_date, Projman.bidding_type, Projman.main_competitors
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
            "customer_id", "customer_name","sn","customer_location","customer_industry","contact_title",
            "business_category", "project_name", "project_location",
            "project_contact", "contact_phone", "service_content",
            "contract_amount", "contract_duration", "contract_sign_date",
            "contract_end_date", "expected_renewal_time", "cooperation_method",
            "is_bidding", "bidding_type", "project_number",
            "subject_matter", "budget_amount", "max_price",
            "publish_time", "deadline",
            "bid_price", "bid_date", "winning_company",
            "website_reference", "main_competitors", "others", "creator", "create_time", "update_time"
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
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(Group(body=[fld_dict["customer_location"], fld_dict["customer_industry"]]))
            customer_fld_lst.append(Group(body=[fld_dict["creator"], fld_dict["create_time"], fld_dict["update_time"]]))
            customer_tabitem = amis.Tabs.Item(title="客户基本信息", icon='fa fa-university', className="bg-blue-100",
                                         body=customer_fld_lst)

            # 项目基本信息 Tab
            project_fld_lst = []
            project_fld_lst.append(Divider())
            project_fld_lst.append(
                Group(body=[fld_dict["sn"]]))
            project_fld_lst.append(
                Group(body=[fld_dict["business_category"], fld_dict["project_name"], fld_dict["project_location"]]))
            project_fld_lst.append(Divider())
            project_fld_lst.append(
                Group(body=[fld_dict["project_contact"], fld_dict["contact_title"], fld_dict["contact_phone"]]))
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
        user = await auth.get_current_user(request)
        log.debug(f'user: {user}')
        try:
            if not bulk:
                c_form = await super().get_create_form(request, bulk)
                c_form.preventEnterSubmit = True
                fieldlist = [item for item in c_form.body]
                fld_dict = {item.name: item for item in fieldlist}
                fld_dict["creator"].value = user.nickname
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
        user = await auth.get_current_user(request)
        try:
            extra = {}
            if not bulk:
                api = f"post:{self.router_path}/item"
                #fields = self.schema_model.model_fields.values()
                fields = [field for field in model_fields(self.schema_create).values() if field.name != self.pk_name]
                # 排除 creator, create_time, update_time 字段
                # fields = [field for field in model_fields(self.schema_create).values() if field.name != self.pk_name and field.name not in ['creator', 'create_time', 'update_time']]
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
                fld_dict["creator"].value = user.nickname
                fld_dict["create_time"].value = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
                fld_dict["update_time"].value = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
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
        user = await auth.get_current_user(request)
        data = await super().on_create_pre(request, obj)
        #log.debug(data)
        generator = ProjectIDGenerator()
        data['sn'] = generator.generate_id()
        data['creator'] = user.nickname
        data['create_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        data['update_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        return data

    async def on_update_pre(
            self, request: Request, obj: Any, item_id: Union[List[str], List[int]], **kwargs,
    ) -> Dict[str, Any]:
        data = await super().on_update_pre(request, obj, item_id)
        data['update_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        return data

    @property
    def route_create(self) -> Callable:
        async def route(
            request: Request,
            data: Annotated[Union[List[self.schema_create], self.schema_create], Body()],  # type: ignore
        ) -> BaseApiOut[Union[int, self.schema_model]]:  # type: ignore
            try:
                #log.info(f"Create request received: {request.url}")
                user = await auth.get_current_user(request)
                if not await self.has_create_permission(request, data):
                    return self.error_no_router_permission(request)
                if not isinstance(data, list):
                    data = [data]
                #log.debug(f"Request data: {data}")
                try:
                    # 验证必填字段
                    required_fields = ['customer_name', 'customer_location', 'business_category', 'project_name']
                    errors = {}

                    for idx, item in enumerate(data):
                        log.debug(f"Processing item {idx + 1}")
                        # 只验证必填字段，而不是遍历所有字段
                        for field in required_fields:
                            # 安全地获取字段值，避免AttributeError
                            if hasattr(item, field):
                                value = getattr(item, field)
                                # 验证字段值不为空
                                if isinstance(value, str) and not value.strip():
                                    errors[field] = f"{field}字段不能为空"
                                    break
                                elif value is None:
                                    errors[field] = f"{field}字段不能为None"
                                    break
                            else:
                                errors[field] = f"缺少必填字段: {field}"
                                break

                        # 如果当前item有错误，跳出循环
                        if errors:
                            log.warning(f"Validation failed for item {idx + 1}: {errors}")
                            break
                
                    # 如果有验证错误，返回标准的BaseApiOut格式的错误信息
                    if len(errors) > 0:
                        error_msg = "参数验证失败: " + ", ".join([f"{k}: {v}" for k, v in errors.items()])
                        log.warning(f"Validation failed: {error_msg}")
                        # 使用标准的BaseApiOut格式返回错误
                        return BaseApiOut(
                            status=422,
                            msg=error_msg,
                            errors=errors,
                            data=None
                        )
                
                    # 只调用一次create_items方法
                    items = await self.create_items(request, data)
                except Exception as error:
                    await self.db.async_rollback()
                    log.error(f"Database error during creation: {str(error)}")
                    return self.error_execute_sql(request=request, error=error)
                result = len(items)
                if result == 1:  # if only one item, return the first item
                    result = await self.db.async_run_sync(lambda _: parse_obj_to_schema(items[0], self.schema_model, refresh=True))
                #log.info(f"Create successful, result: {result}")
                # 添加创建记录后的actlog日志，act_type为create_{result.id}
                await add_act_log(user.nickname, f"create_{result.id}")
                return BaseApiOut(data=result)
            except Exception as exp:
                log.error(f"Exception at ProjmanAdmin.route_create(): {str(exp)}")
                traceback.print_exc()
                # 确保总是返回一个有效的BaseApiOut响应
                return BaseApiOut(
                    status=500,
                    msg=f"服务器内部错误: {str(exp)}",
                    data=None
                )
        return route

    @property
    def route_update(self) -> Callable:
        async def route(
            request: Request,
            item_id: self.AnnotatedItemIdList,  # type: ignore
            data: Annotated[self.schema_update, Body()],  # type: ignore
        ):
            try:
                user = await auth.get_current_user(request)
                if not await self.has_update_permission(request, item_id, data):
                    return self.error_no_router_permission(request)  
                # 新增判断：如果提交的数据字段creator的值不等于user.nickname则返回无权限错误
                if hasattr(data, 'creator') and data.creator != user.nickname and user.nickname != 'root':
                    return self.error_no_router_permission(request)
                values = await self.on_update_pre(request, data, item_id=item_id)
                if not values:
                    return self.error_data_handle(request)
                items = await self.update_items(request, item_id, values)
                # 添加更新记录后的actlog日志，act_type为update_{item_id}
                await add_act_log(user.nickname, f"update_{item_id}")
                return BaseApiOut(data=len(items))
            except Exception as exp:
                print('Exception at SwiftAdmin.route_update() %s ' % exp)
                traceback.print_exc()

        return route


    @property
    def route_delete(self) -> Callable:
        async def route(
            request: Request,
            sess: SyncSess,
            item_id: self.AnnotatedItemIdList,  # type: ignore
        ):
            try:
                user = await auth.get_current_user(request)
                if not await self.has_delete_permission(request, item_id):
                    return self.error_no_router_permission(request)
                # 新增判断：如果提交的数据字段creator的值不等于user.nickname则返回无权限错误，但root用户除外
                query = text("""
                    SELECT * 
                    FROM projman 
                    WHERE id = :item_id
                """)
                result = sess.execute(query, {"item_id": item_id})
                rows = result.fetchall()
                #log.debug(f"rows: {rows}")
                # 将Row对象转换为字典列表
                result_list = [dict(row._asdict()) for row in rows]
                data = result_list[0]
                if hasattr(data, 'creator') and data.creator != user.nickname and user.nickname != 'root':
                    return self.error_no_router_permission(request)
                items = await self.delete_items(request, item_id)
                # 添加删除记录后的actlog日志，act_type为delete_{item_id}
                await add_act_log(user.nickname, f"delete_{item_id}")
                return BaseApiOut(data=len(items))
            except Exception as exp:
                print('Exception at SwiftAdmin.route_delete() %s ' % exp)
                traceback.print_exc()

        return route


    @property
    def route_read(self) -> Callable:
        async def route(
            request: Request,
            item_id: self.AnnotatedItemIdList,  # type: ignore
        ):
            try:
                user = await auth.get_current_user(request)
                if not await self.has_read_permission(request, item_id):
                    return self.error_no_router_permission(request)
                items = await self.read_items(request, item_id)
                # 添加读取记录后的actlog日志，act_type为read_{item_id}
                await add_act_log(user.nickname, f"read_{item_id}")
                return BaseApiOut(data=items if len(items) > 1 else items[0])
            except Exception as exp:
                print('Exception at SwiftAdmin.route_read() %s ' % exp)
                traceback.print_exc()

        return route


    @property
    def route_list(self) -> Callable:
        async def route(
            request: Request,
            sel: self.AnnotatedSelect,  # type: ignore
            paginator: Annotated[self.paginator, Depends()],  # type: ignore
            filters: Annotated[self.schema_filter, Body()] = None,  # type: ignore
        ):
            try:
                user = await auth.get_current_user(request)
                if not await self.has_list_permission(request, paginator, filters):
                    return self.error_no_router_permission(request)
                data = ItemListSchema(items=[])
                data.query = request.query_params
                if await self.has_filter_permission(request, filters):
                    data.filters = await self.on_filter_pre(request, filters)
                    if data.filters:
                        sel = sel.filter(*self.calc_filter_clause(data.filters))
                if paginator.showTotal:
                    data.total = await self.db.async_scalar(sel.with_only_columns(func.count("*")))
                    if data.total == 0:
                        return BaseApiOut(data=data)
                orderBy = self._calc_ordering(paginator.orderBy, paginator.orderDir)
                if orderBy:
                    sel = sel.order_by(*orderBy)
                sel = sel.limit(paginator.perPage).offset(paginator.offset)
                result = await self.db.async_execute(sel)
                # 添加读取列表记录后的actlog日志，act_type为list_{paginator.perPage}_{paginator.offset}
                await add_act_log(user.nickname, f"list_{paginator.perPage}_{paginator.offset}")
                return BaseApiOut(data=await self.on_list_after(request, result, data))
            except Exception as exp:
                print('Exception at SwiftAdmin.route_list() %s ' % exp)
                traceback.print_exc()

        return route

    async def filter_select(self, request: Request, sel: Select) -> Select:
        """在sel中添加权限过滤条件"""
        subject = await self.site.auth.get_current_user_identity(request)
        user = await auth.get_current_user(request)
        # 添加读取列表记录后的actlog日志，act_type为list_{paginator.perPage}_{paginator.offset}
        await add_act_log(user.nickname, f"select_{self.unique_id}")
        if subject == SystemUserEnum.ROOT:
            return sel
        return await super().filter_select(request, sel)