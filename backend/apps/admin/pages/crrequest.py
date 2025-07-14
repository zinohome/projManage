#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  #
#  Copyright (C) 2023 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2023
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: SwiftApp
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi._compat import ModelField
from fastapi_amis_admin.admin import AdminAction
from fastapi_amis_admin.crud import CrudEnum, BaseApiOut
from fastapi_amis_admin.crud.base import SchemaFilterT, SchemaUpdateT
from fastapi_amis_admin.crud.parser import TableModelParser, parse_obj_to_schema
from fastapi_amis_admin.utils.pydantic import model_fields
from fastapi_user_auth.auth.models import User
from fastapi_user_auth.globals import auth
from pydantic._internal._decorators import mro
from sqlalchemy import Select, or_, and_, desc

from apps.admin.swiftadmin import SwiftAdmin
from core.globals import site
from typing import List, Optional, TYPE_CHECKING, Union, Dict, Any, Callable
from fastapi_amis_admin import admin, amis
from fastapi_amis_admin.amis import PageSchema, TableColumn, ActionType, Action, Dialog, SizeEnum, Drawer, LevelEnum, \
    TableCRUD, TabsModeEnum, Form, AmisAPI, DisplayModeEnum, InputExcel, InputTable, Page, FormItem, SchemaNode, Group, \
    Divider
from starlette.requests import Request
import simplejson as json
from fastapi_amis_admin.utils.translation import i18n as _
from utils.log import log as log
from apps.admin.models.changerequest import Changerequest
from utils.mailtool import MailTool
from utils.userselect import UserSelect
from typing_extensions import Annotated, Literal
from fastapi import Body


class CrRequest(SwiftAdmin):
    group_schema = "Changerequest"
    page_schema = PageSchema(label='CRRequest', page_title='CRRequest', icon='fa fa-server', sort=92)
    model = Changerequest
    pk_name = 'id'
    list_per_page = 20
    list_display = []
    #list_filter = [Changerequest.customer_name,Changerequest.cr_activity_brief,Changerequest.ssr,Changerequest.sngl_pnt_sys,Changerequest.support_tsg_id,Changerequest.begin_date,Changerequest.end_date,Changerequest.tsg_rvew_rslt]
    list_filter = [Changerequest.customer_name, Changerequest.ssr, Changerequest.support_tsg_id,
                   Changerequest.begin_date, Changerequest.end_date, Changerequest.cr_activity_brief,
                   Changerequest.tsg_rvew_rslt, Changerequest.update_time]
    search_fields = [Changerequest.customer_name,Changerequest.cr_activity_brief,Changerequest.ssr,Changerequest.sngl_pnt_sys,Changerequest.support_tsg_id,Changerequest.begin_date,Changerequest.end_date,Changerequest.tsg_rvew_rslt,Changerequest.create_time,Changerequest.update_time]
    parent_class = None
    tabsMode = TabsModeEnum.card
    admin_action_maker = [
        lambda self: AdminAction(
            admin=self,
            name="copy",
            tooltip="复制",
            flags=["item"],
            getter=lambda request: self.get_duplicate_action(request, bulk=False),
        ),
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
            "icon": "fa fa-file",
            "onEvent": {
                "click": {
                    "actions": [
                        {
                            "actionType": "setValue",
                            "componentId": "form_setvalue",
                            "args": {
                                "value": {
                                    "tsg_rvew_rslt": "Draft",
                                }
                            }
                        },
                        {
                            "actionType": "submit",
                            "componentId": "form_setvalue"
                        }
                    ]
                }
            },
            "label": "暂存",
            "disabledOn": "['Submitted', 'Approved', 'Completed'].includes(tsg_rvew_rslt)",
            "primary": True
        },
        {
            "type": "button",
            "icon": "fa fa-arrow-up",
            "onEvent": {
                "click": {
                    "actions": [
                        {
                            "actionType": "setValue",
                            "componentId": "form_setvalue",
                            "args": {
                                "value": {
                                    "tsg_rvew_rslt": "Submitted",
                                }
                            }
                        },
                        {
                            "actionType": "submit",
                            "componentId": "form_setvalue"
                        }
                    ]
                }
            },
            "label": "提交",
            "disabledOn": "['Submitted', 'Approved', 'Completed'].includes(tsg_rvew_rslt)",
            "primary": False
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

    reviewactions = [
        {
            "type": "button",
            "actionType": "cancel",
            "icon": "fa fa-reply",
            "label": "取消",
            "primary": False
        },
        {
            "type": "button",
            "icon": "fa fa-arrow-right",
            "onEvent": {
                "click": {
                    "actions": [
                        {
                            "actionType": "setValue",
                            "componentId": "form_setvalue",
                            "args": {
                                "value": {
                                    "tsg_rvew_rslt": "Approved",
                                }
                            }
                        },
                        {
                            "actionType": "submit",
                            "componentId": "form_setvalue"
                        }
                    ]
                }
            },
            "label": "审批",
            "primary": True
        },
        {
            "type": "button",
            "icon": "fa fa-arrow-left",
            "onEvent": {
                "click": {
                    "actions": [
                        {
                            "actionType": "setValue",
                            "componentId": "form_setvalue",
                            "args": {
                                "value": {
                                    "tsg_rvew_rslt": "Returned",
                                }
                            }
                        },
                        {
                            "actionType": "submit",
                            "componentId": "form_setvalue"
                        }
                    ]
                }
            },
            "label": "驳回",
            "primary": False
        },
        {
            "type": "button",
            "icon": "fa fa-stop-circle",
            "onEvent": {
                "click": {
                    "actions": [
                        {
                            "actionType": "setValue",
                            "componentId": "form_setvalue",
                            "args": {
                                "value": {
                                    "tsg_rvew_rslt": "Completed",
                                }
                            }
                        },
                        {
                            "actionType": "submit",
                            "componentId": "form_setvalue"
                        }
                    ]
                }
            },
            "label": "完成",
            "primary": False
        }
    ]

    def __init__(self, app: "AdminApp"):
        super().__init__(app)
        # 启用批量新增
        self.enable_bulk_create = False
        # 启用查看
        self.schema_read = None
        # 设置form弹出类型  Drawer | Dialog
        self.action_type = 'Drawer'

    async def get_select(self, request: Request) -> Select:
        #user = await auth.get_current_user(request)
        #log.debug(user)
        #log.debug(request.user)
        try:
            stmt = await super().get_select(request)
            return stmt.where(or_(
                Changerequest.ssr == request.user.username,
                and_(
                    Changerequest.local_sdm == request.user.username,
                    Changerequest.tsg_rvew_rslt != 'Draft'
                ),
                and_(
                    Changerequest.onsite_engineer == request.user.username,
                    Changerequest.tsg_rvew_rslt != 'Draft'
                )
            )
            )
            #).order_by(desc(Changerequest.update_time))
        except Exception as exp:
            print('Exception at CrRequest.get_select() %s ' % exp)
            traceback.print_exc()

    async def get_create_action(self, request: Request, bulk: bool = False) -> Optional[Action]:
        try:
            if not bulk:
                if self.action_type == 'Drawer':
                    return ActionType.Drawer(
                        icon="fa fa-plus pull-left",
                        label=_("Create"),
                        level=LevelEnum.primary,
                        drawer=Drawer(
                            title=_("Create") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.createactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_create_form(request, bulk=bulk),
                        ),
                    )
                else:
                    return ActionType.Dialog(
                        icon="fa fa-plus pull-left",
                        label=_("Create"),
                        level=LevelEnum.primary,
                        dialog=Dialog(
                            title=_("Create") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.createactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_create_form(request, bulk=bulk),
                        ),
                    )
            if self.action_type == 'Drawer':
                return ActionType.Dialog(
                    icon="fa fa-plus pull-left",
                    label=_("Bulk Create"),
                    level=LevelEnum.primary,
                    dialog=Dialog(
                        title=_("Bulk Create") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.createactions,
                        overlay=False,
                        closeOnOutside=False,
                        size=SizeEnum.full,
                        resizable=True,
                        width="900px",
                        body=await self.get_create_form(request, bulk=bulk),
                    ),
                )
            else:
                return ActionType.Dialog(
                    icon="fa fa-plus pull-left",
                    label=_("Bulk Create"),
                    level=LevelEnum.primary,
                    dialog=Dialog(
                        title=_("Bulk Create") + " - " + _(self.page_schema.label),
                        id="form_setvalue",
                        position="right",
                        showCloseButton=False,
                        actions=self.createactions,
                        overlay=False,
                        closeOnOutside=False,
                        size=SizeEnum.full,
                        resizable=True,
                        width="900px",
                        body=await self.get_create_form(request, bulk=bulk),
                    ),
                )
        except Exception as exp:
            print('Exception at CrRequest.get_create_action() %s ' % exp)
            traceback.print_exc()

    async def get_read_action(self, request: Request) -> Optional[Action]:
        try:
            if not self.schema_read:
                return None
            if self.action_type == 'Drawer':
                return ActionType.Drawer(
                    icon="fas fa-eye",
                    tooltip=_("View"),
                    drawer=Drawer(
                        title=_("View") + " - " + _(self.page_schema.label),
                        position="right",
                        showCloseButton=False,
                        actions=self.readactions,
                        overlay=False,
                        closeOnOutside=False,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_read_form(request),
                    ),
                )
            else:
                return ActionType.Dialog(
                    icon="fas fa-eye",
                    tooltip=_("View"),
                    dialog=Dialog(
                        title=_("View") + " - " + _(self.page_schema.label),
                        position="right",
                        showCloseButton=False,
                        actions=self.readactions,
                        overlay=False,
                        closeOnOutside=False,
                        size=SizeEnum.lg,
                        resizable=True,
                        width="900px",
                        body=await self.get_read_form(request),
                    ),
                )
        except Exception as exp:
            print('Exception at CrRequest.get_read_action() %s ' % exp)
            traceback.print_exc()

    async def get_update_action(self, request: Request, bulk: bool = False) -> Optional[Action]:
        try:
            if not bulk:
                if self.action_type == 'Drawer':
                    return ActionType.Drawer(
                        icon="fa fa-pencil",
                        tooltip=_("Update"),
                        drawer=Drawer(
                            title=_("Update") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.createactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_update_form(request, bulk=bulk),
                        ),
                    )
                else:
                    return ActionType.Dialog(
                        icon="fa fa-pencil",
                        tooltip=_("Update"),
                        dialog=Dialog(
                            title=_("Update") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.createactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_update_form(request, bulk=bulk),
                        ),
                    )
            elif self.bulk_update_fields:
                if self.action_type == 'Drawer':
                    return ActionType.Dialog(
                        label=_("Bulk Update"),
                        dialog=Dialog(
                            title=_("Bulk Update") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.createactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_update_form(request, bulk=True),
                        ),
                    )
                else:
                    return ActionType.Dialog(
                        label=_("Bulk Update"),
                        dialog=Dialog(
                            title=_("Bulk Update") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.createactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_update_form(request, bulk=True),
                        ),
                    )
            else:
                return None
        except Exception as exp:
            print('Exception at CrRequest.get_update_action() %s ' % exp)
            traceback.print_exc()

    async def get_print_action(self, request: Request) -> Optional[Action]:
        try:
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
        except Exception as exp:
            print('Exception at CrRequest.get_print_action() %s ' % exp)
            traceback.print_exc()

    async def get_print_form(self, request: Request) -> Form:
        try:
            p_form = await super().get_read_form(request)
            return p_form
        except Exception as exp:
            print('Exception at CrRequest.get_print_form() %s ' % exp)
            traceback.print_exc()

    async def get_read_form(self, request: Request) -> Form:
        try:
            r_form = await super().get_read_form(request)
            # 构建主表Read
            formtab = amis.Tabs(tabsMode='strong')
            formtab.tabs = []
            fieldlist = []
            for item in r_form.body:
                if item.name != self.pk_name:
                    fieldlist.append(item)
            fld_dict = {item.name: item for item in fieldlist}
            customer_fld_lst = []
            customer_fld_lst.append(Group(body=[fld_dict["customer_name"], fld_dict["case_number"]]))
            customer_fld_lst.append(Group(body=[fld_dict["cstm_cntct_name"], fld_dict["cstm_cntct_phone"]]))
            customer_fld_lst.append(Group(body=[fld_dict["cstm_addr"], fld_dict["cstm_location"]]))
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(
                Group(body=[fld_dict["sngl_pnt_sys"], fld_dict["urgency"], fld_dict["complexity"]]))
            customer_fld_lst.append(Divider())
            customer_fld_lst.append(Group(body=[fld_dict["create_time"], fld_dict["update_time"]]))
            basictabitem = amis.Tabs.Item(title=_('Customer'), icon='fa fa-university', className="bg-blue-100", body=customer_fld_lst)
            ssr_fld_lst = []
            ssr_fld_lst.append(Group(body=[fld_dict["ssr"], fld_dict["ssr_phone"]]))
            ssr_fld_lst.append(Group(body=[fld_dict["support_tsg_id"], fld_dict["local_sdm"]]))
            ssr_fld_lst.append(Divider())
            ssrtabitem = amis.Tabs.Item(title=_('SSR'), icon='fa fa-users', className="bg-yellow-100", body=ssr_fld_lst)
            proj_fld_lst = []
            proj_fld_lst.append(Group(body=[fld_dict["proj_code"], fld_dict["cntrt_no"]]))
            proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction"]]))
            proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction_attch"]]))
            proj_fld_lst.append(Divider())
            projtabitem = amis.Tabs.Item(title=_('Project'), icon='fa fa-id-card', className="bg-red-100", body=proj_fld_lst)
            cr_fld_lst = []
            cr_fld_lst.append(Group(body=[fld_dict["onsite_engineer"]]))
            cr_fld_lst.append(Group(body=[fld_dict["begin_date"], fld_dict["end_date"]]))
            proj_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["cr_activity_brief"]]))
            cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan"]]))
            cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan_attch"]]))
            cr_fld_lst.append(Group(body=[fld_dict["machine_info"], fld_dict["version"]]))
            cr_fld_lst.append(Group(body=[fld_dict["machine_info_attch"]]))
            cr_fld_lst.append(Group(body=[fld_dict["related_ibm_software"], fld_dict["sw_version"]]))
            cr_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["category"],fld_dict["machine_count"]]))
            cr_fld_lst.append(Divider())
            cr_fld_lst.append(Group(body=[fld_dict["prblm_dscrption"]]))
            crtabitem = amis.Tabs.Item(title=_('Change'), icon='fa fa-cogs', className="bg-green-100", body=cr_fld_lst)
            review_fld_lst = []
            review_fld_lst.append(Group(body=[fld_dict["tsg_onsite"]]))
            review_fld_lst.append(Group(body=[fld_dict["tsg_rvew_rslt"]]))
            review_fld_lst.append(Group(body=[fld_dict["tsg_comments"]]))
            review_fld_lst.append(Divider())
            review_fld_lst.append(Group(body=[fld_dict["review_history"]]))
            reviewtabitem = amis.Tabs.Item(title=_('Review'), icon='fa fa-gavel', className="bg-purple-100", body=review_fld_lst)
            formtab.tabs.append(basictabitem)
            formtab.tabs.append(ssrtabitem)
            formtab.tabs.append(projtabitem)
            formtab.tabs.append(crtabitem)
            formtab.tabs.append(reviewtabitem)
            r_form.body = formtab
            return r_form
        except Exception as exp:
            print('Exception at CrRequest.get_read_form() %s ' % exp)
            traceback.print_exc()

    async def get_create_form(self, request: Request, bulk: bool = False) -> Form:
        try:
            c_form = await super().get_create_form(request, bulk)
            c_form.preventEnterSubmit=True
            user = await auth.get_current_user(request)
            if not bulk:
                # 构建主表Create
                formtab = amis.Tabs(tabsMode='strong')
                formtab.tabs = []
                fieldlist = []
                for item in c_form.body:
                    fieldlist.append(item)
                fld_dict = {item.name: item for item in fieldlist}
                customer_fld_lst = []
                customer_fld_lst.append(Group(body=[fld_dict["customer_name"], fld_dict["case_number"]]))
                customer_fld_lst.append(Group(body=[fld_dict["cstm_cntct_name"], fld_dict["cstm_cntct_phone"]]))
                customer_fld_lst.append(Group(body=[fld_dict["cstm_addr"], fld_dict["cstm_location"]]))
                customer_fld_lst.append(Divider())
                customer_fld_lst.append(
                    Group(body=[fld_dict["sngl_pnt_sys"], fld_dict["urgency"], fld_dict["complexity"]]))
                customer_fld_lst.append(Divider())
                customer_fld_lst.append(Group(body=[fld_dict["create_time"], fld_dict["update_time"]]))
                basictabitem = amis.Tabs.Item(title=_('Customer'), icon='fa fa-university', className="bg-blue-100", body=customer_fld_lst)
                ssr_fld_lst = []
                fld_dict["ssr"].value = user.username
                ssr_fld_lst.append(Group(body=[fld_dict["ssr"], fld_dict["ssr_phone"]]))
                ssr_fld_lst.append(Group(body=[fld_dict["support_tsg_id"], fld_dict["local_sdm"]]))
                ssr_fld_lst.append(Divider())
                ssrtabitem = amis.Tabs.Item(title=_('SSR'), icon='fa fa-users', className="bg-yellow-100", body=ssr_fld_lst)
                proj_fld_lst = []
                proj_fld_lst.append(Group(body=[fld_dict["proj_code"], fld_dict["cntrt_no"]]))
                proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction"]]))
                proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction_attch"]]))
                proj_fld_lst.append(Divider())
                projtabitem = amis.Tabs.Item(title=_('Project'), icon='fa fa-id-card', className="bg-red-100", body=proj_fld_lst)
                cr_fld_lst = []
                cr_fld_lst.append(Group(body=[fld_dict["onsite_engineer"]]))
                cr_fld_lst.append(Group(body=[fld_dict["begin_date"], fld_dict["end_date"]]))
                proj_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["cr_activity_brief"]]))
                cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan"]]))
                cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan_attch"]]))
                cr_fld_lst.append(Group(body=[fld_dict["machine_info"], fld_dict["version"]]))
                cr_fld_lst.append(Group(body=[fld_dict["machine_info_attch"]]))
                cr_fld_lst.append(Group(body=[fld_dict["related_ibm_software"], fld_dict["sw_version"]]))
                cr_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["category"],fld_dict["machine_count"]]))
                cr_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["prblm_dscrption"]]))
                crtabitem = amis.Tabs.Item(title=_('Change'), icon='fa fa-cogs', className="bg-green-100", body=cr_fld_lst)
                review_fld_lst = []
                review_fld_lst.append(Group(body=[fld_dict["tsg_onsite"]]))
                review_fld_lst.append(Group(body=[fld_dict["tsg_rvew_rslt"]]))
                review_fld_lst.append(Group(body=[fld_dict["tsg_comments"]]))
                review_fld_lst.append(Divider())
                review_fld_lst.append(Group(body=[fld_dict["review_history"]]))
                reviewtabitem = amis.Tabs.Item(title=_('Review'), icon='fa fa-gavel', className="bg-purple-100", body=review_fld_lst)
                formtab.tabs.append(basictabitem)
                formtab.tabs.append(ssrtabitem)
                formtab.tabs.append(projtabitem)
                formtab.tabs.append(crtabitem)
                formtab.tabs.append(reviewtabitem)
                c_form.body = formtab
            return c_form
        except Exception as exp:
            print('Exception at CrRequest.get_create_form() %s ' % exp)
            traceback.print_exc()

    async def get_update_form(self, request: Request, bulk: bool = False) -> Form:
        try:
            u_form = await super().get_update_form(request, bulk)
            u_form.preventEnterSubmit = True
            if not bulk:
                # 构建主表Update
                formtab = amis.Tabs(tabsMode='strong')
                formtab.tabs = []
                fieldlist = []
                for item in u_form.body:
                    fieldlist.append(item)
                fld_dict = {item.name: item for item in fieldlist}
                customer_fld_lst = []
                customer_fld_lst.append(Group(body=[fld_dict["customer_name"], fld_dict["case_number"]]))
                customer_fld_lst.append(Group(body=[fld_dict["cstm_cntct_name"], fld_dict["cstm_cntct_phone"]]))
                customer_fld_lst.append(Group(body=[fld_dict["cstm_addr"], fld_dict["cstm_location"]]))
                customer_fld_lst.append(Divider())
                customer_fld_lst.append(
                    Group(body=[fld_dict["sngl_pnt_sys"], fld_dict["urgency"], fld_dict["complexity"]]))
                customer_fld_lst.append(Divider())
                customer_fld_lst.append(Group(body=[fld_dict["create_time"], fld_dict["update_time"]]))
                basictabitem = amis.Tabs.Item(title=_('Customer'), icon='fa fa-university', className="bg-blue-100", body=customer_fld_lst)
                ssr_fld_lst = []
                ssr_fld_lst.append(Group(body=[fld_dict["ssr"], fld_dict["ssr_phone"]]))
                ssr_fld_lst.append(Group(body=[fld_dict["support_tsg_id"], fld_dict["local_sdm"]]))
                ssr_fld_lst.append(Divider())
                ssrtabitem = amis.Tabs.Item(title=_('SSR'), icon='fa fa-users', className="bg-yellow-100", body=ssr_fld_lst)
                proj_fld_lst = []
                proj_fld_lst.append(Group(body=[fld_dict["proj_code"], fld_dict["cntrt_no"]]))
                proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction"]]))
                proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction_attch"]]))
                proj_fld_lst.append(Divider())
                projtabitem = amis.Tabs.Item(title=_('Project'), icon='fa fa-id-card', className="bg-red-100", body=proj_fld_lst)
                cr_fld_lst = []
                cr_fld_lst.append(Group(body=[fld_dict["onsite_engineer"]]))
                cr_fld_lst.append(Group(body=[fld_dict["begin_date"], fld_dict["end_date"]]))
                proj_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["cr_activity_brief"]]))
                cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan"]]))
                cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan_attch"]]))
                cr_fld_lst.append(Group(body=[fld_dict["machine_info"], fld_dict["version"]]))
                cr_fld_lst.append(Group(body=[fld_dict["machine_info_attch"]]))
                cr_fld_lst.append(Group(body=[fld_dict["related_ibm_software"], fld_dict["sw_version"]]))
                cr_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["category"],fld_dict["machine_count"]]))
                cr_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["prblm_dscrption"]]))
                crtabitem = amis.Tabs.Item(title=_('Change'), icon='fa fa-cogs', className="bg-green-100", body=cr_fld_lst)
                review_fld_lst = []
                review_fld_lst.append(Group(body=[fld_dict["tsg_onsite"]]))
                review_fld_lst.append(Group(body=[fld_dict["tsg_rvew_rslt"]]))
                review_fld_lst.append(Group(body=[fld_dict["tsg_comments"]]))
                review_fld_lst.append(Divider())
                review_fld_lst.append(Group(body=[fld_dict["review_history"]]))
                reviewtabitem = amis.Tabs.Item(title=_('Review'), icon='fa fa-gavel', className="bg-purple-100", body=review_fld_lst)
                formtab.tabs.append(basictabitem)
                formtab.tabs.append(ssrtabitem)
                formtab.tabs.append(projtabitem)
                formtab.tabs.append(crtabitem)
                formtab.tabs.append(reviewtabitem)
                u_form.body = formtab
            return u_form
        except Exception as exp:
            print('Exception at CrRequest.get_update_form() %s ' % exp)
            traceback.print_exc()

    async def get_duplicate_form_inner(self, request: Request, bulk: bool = False) -> Form:
        try:
            extra = {}
            if not bulk:
                api = f"post:{self.router_path}/item"
                fields = model_fields(self.schema_model).values()
                # fields = model_fields(BaseCrud._create_schema_update()).values()
                if self.schema_read:
                    #extra["initApi"] = f"get:{self.router_path}/item/${self.pk_name}"
                    extra["initApi"] = f"get:/crtool/get_duplicate_crdata/item/${self.pk_name}"
            d_form = Form(
                api=api,
                name="create",
                body=await self._conv_modelfields_to_formitems(request, fields, CrudEnum.create),
                **extra,
            )
            if not bulk:
                # 构建主表Create
                formtab = amis.Tabs(tabsMode='strong')
                formtab.tabs = []
                fieldlist = []
                for item in d_form.body:
                    fieldlist.append(item)
                fld_dict = {item.name: item for item in fieldlist}
                customer_fld_lst = []
                customer_fld_lst.append(Group(body=[fld_dict["customer_name"], fld_dict["case_number"]]))
                customer_fld_lst.append(Group(body=[fld_dict["cstm_cntct_name"], fld_dict["cstm_cntct_phone"]]))
                customer_fld_lst.append(Group(body=[fld_dict["cstm_addr"], fld_dict["cstm_location"]]))
                customer_fld_lst.append(Divider())
                customer_fld_lst.append(
                    Group(body=[fld_dict["sngl_pnt_sys"], fld_dict["urgency"], fld_dict["complexity"]]))
                customer_fld_lst.append(Divider())
                customer_fld_lst.append(Group(body=[fld_dict["create_time"], fld_dict["update_time"]]))
                basictabitem = amis.Tabs.Item(title=_('Customer'), icon='fa fa-university', className="bg-blue-100", body=customer_fld_lst)
                ssr_fld_lst = []
                ssr_fld_lst.append(Group(body=[fld_dict["ssr"], fld_dict["ssr_phone"]]))
                ssr_fld_lst.append(Group(body=[fld_dict["support_tsg_id"], fld_dict["local_sdm"]]))
                ssr_fld_lst.append(Divider())
                ssrtabitem = amis.Tabs.Item(title=_('SSR'), icon='fa fa-users', className="bg-yellow-100", body=ssr_fld_lst)
                proj_fld_lst = []
                proj_fld_lst.append(Group(body=[fld_dict["proj_code"], fld_dict["cntrt_no"]]))
                proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction"]]))
                proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction_attch"]]))
                proj_fld_lst.append(Divider())
                projtabitem = amis.Tabs.Item(title=_('Project'), icon='fa fa-id-card', className="bg-red-100", body=proj_fld_lst)
                cr_fld_lst = []
                cr_fld_lst.append(Group(body=[fld_dict["onsite_engineer"]]))
                cr_fld_lst.append(Group(body=[fld_dict["begin_date"], fld_dict["end_date"]]))
                proj_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["cr_activity_brief"]]))
                cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan"]]))
                cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan_attch"]]))
                cr_fld_lst.append(Group(body=[fld_dict["machine_info"], fld_dict["version"]]))
                cr_fld_lst.append(Group(body=[fld_dict["machine_info_attch"]]))
                cr_fld_lst.append(Group(body=[fld_dict["related_ibm_software"], fld_dict["sw_version"]]))
                cr_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["category"],fld_dict["machine_count"]]))
                cr_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["prblm_dscrption"]]))
                crtabitem = amis.Tabs.Item(title=_('Change'), icon='fa fa-cogs', className="bg-green-100", body=cr_fld_lst)
                review_fld_lst = []
                review_fld_lst.append(Group(body=[fld_dict["tsg_onsite"]]))
                review_fld_lst.append(Group(body=[fld_dict["tsg_rvew_rslt"]]))
                review_fld_lst.append(Group(body=[fld_dict["tsg_comments"]]))
                review_fld_lst.append(Divider())
                review_fld_lst.append(Group(body=[fld_dict["review_history"]]))
                reviewtabitem = amis.Tabs.Item(title=_('Review'), icon='fa fa-gavel', className="bg-purple-100", body=review_fld_lst)
                formtab.tabs.append(basictabitem)
                formtab.tabs.append(ssrtabitem)
                formtab.tabs.append(projtabitem)
                formtab.tabs.append(crtabitem)
                formtab.tabs.append(reviewtabitem)
                d_form.body = formtab
            return d_form
        except Exception as exp:
            print('Exception at CrRequest.get_duplicate_form_inner() %s ' % exp)
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
            print('Exception at CrRequest.get_duplicate_action() %s ' % exp)
            traceback.print_exc()

    async def get_review_form(self, request: Request, bulk: bool = False) -> Form:
        try:
            r_form = await super().get_update_form(request, bulk)
            r_form.preventEnterSubmit = True
            if not bulk:
                # 构建主表Update
                formtab = amis.Tabs(tabsMode='strong')
                formtab.tabs = []
                fieldlist = []
                for item in r_form.body:
                    if item.name not in ["tsg_onsite", "tsg_comments"]:
                        item.disabled = True
                    fieldlist.append(item)
                fld_dict = {item.name: item for item in fieldlist}
                customer_fld_lst = []
                customer_fld_lst.append(Group(body=[fld_dict["customer_name"], fld_dict["case_number"]]))
                customer_fld_lst.append(Group(body=[fld_dict["cstm_cntct_name"], fld_dict["cstm_cntct_phone"]]))
                customer_fld_lst.append(Group(body=[fld_dict["cstm_addr"], fld_dict["cstm_location"]]))
                customer_fld_lst.append(Divider())
                customer_fld_lst.append(
                    Group(body=[fld_dict["sngl_pnt_sys"], fld_dict["urgency"], fld_dict["complexity"]]))
                customer_fld_lst.append(Divider())
                customer_fld_lst.append(Group(body=[fld_dict["create_time"], fld_dict["update_time"]]))
                basictabitem = amis.Tabs.Item(title=_('Customer'), icon='fa fa-university', className="bg-blue-100", body=customer_fld_lst)
                ssr_fld_lst = []
                ssr_fld_lst.append(Group(body=[fld_dict["ssr"], fld_dict["ssr_phone"]]))
                ssr_fld_lst.append(Group(body=[fld_dict["support_tsg_id"], fld_dict["local_sdm"]]))
                ssr_fld_lst.append(Divider())
                ssrtabitem = amis.Tabs.Item(title=_('SSR'), icon='fa fa-users', className="bg-yellow-100", body=ssr_fld_lst)
                proj_fld_lst = []
                proj_fld_lst.append(Group(body=[fld_dict["proj_code"], fld_dict["cntrt_no"]]))
                proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction"]]))
                proj_fld_lst.append(Group(body=[fld_dict["busnss_jstfction_attch"]]))
                proj_fld_lst.append(Divider())
                projtabitem = amis.Tabs.Item(title=_('Project'), icon='fa fa-id-card', className="bg-red-100", body=proj_fld_lst)
                cr_fld_lst = []
                cr_fld_lst.append(Group(body=[fld_dict["onsite_engineer"]]))
                cr_fld_lst.append(Group(body=[fld_dict["begin_date"], fld_dict["end_date"]]))
                proj_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["cr_activity_brief"]]))
                cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan"]]))
                cr_fld_lst.append(Group(body=[fld_dict["cr_detail_plan_attch"]]))
                cr_fld_lst.append(Group(body=[fld_dict["machine_info"], fld_dict["version"]]))
                cr_fld_lst.append(Group(body=[fld_dict["machine_info_attch"]]))
                cr_fld_lst.append(Group(body=[fld_dict["related_ibm_software"], fld_dict["sw_version"]]))
                cr_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["category"],fld_dict["machine_count"]]))
                cr_fld_lst.append(Divider())
                cr_fld_lst.append(Group(body=[fld_dict["prblm_dscrption"]]))
                crtabitem = amis.Tabs.Item(title=_('Change'), icon='fa fa-cogs', className="bg-green-100", body=cr_fld_lst)
                review_fld_lst = []
                review_fld_lst.append(Group(body=[fld_dict["tsg_onsite"]]))
                review_fld_lst.append(Group(body=[fld_dict["tsg_rvew_rslt"]]))
                review_fld_lst.append(Group(body=[fld_dict["tsg_comments"]]))
                review_fld_lst.append(Divider())
                review_fld_lst.append(Group(body=[fld_dict["review_history"]]))
                reviewtabitem = amis.Tabs.Item(title=_('Review'), icon='fa fa-gavel', className="bg-purple-100", body=review_fld_lst)
                formtab.tabs.append(basictabitem)
                formtab.tabs.append(ssrtabitem)
                formtab.tabs.append(projtabitem)
                formtab.tabs.append(crtabitem)
                formtab.tabs.append(reviewtabitem)
                r_form.body = formtab
            return r_form
        except Exception as exp:
            print('Exception at CrRequest.get_review_form() %s ' % exp)
            traceback.print_exc()

    async def get_review_action(self, request: Request, bulk: bool = False) -> Optional[Action]:
        try:
            if not bulk:
                if self.action_type == 'Drawer':
                    return ActionType.Drawer(
                        icon="fa fa-share-alt",
                        tooltip=_("审批"),
                        drawer=Drawer(
                            title=_("Review") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.reviewactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_review_form(request, bulk=bulk),
                        ),
                    )
                else:
                    return ActionType.Dialog(
                        icon="fa fa-share-alt",
                        tooltip=_("审批"),
                        dialog=Dialog(
                            title=_("Review") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.reviewactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_review_form(request, bulk=bulk),
                        ),
                    )
            elif self.bulk_update_fields:
                if self.action_type == 'Drawer':
                    return ActionType.Dialog(
                        label=_("Bulk Review"),
                        dialog=Dialog(
                            title=_("Bulk Review") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.reviewactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_review_form(request, bulk=True),
                        ),
                    )
                else:
                    return ActionType.Dialog(
                        label=_("Bulk Review"),
                        dialog=Dialog(
                            title=_("Bulk Review") + " - " + _(self.page_schema.label),
                            id="form_setvalue",
                            position="right",
                            showCloseButton=False,
                            actions=self.reviewactions,
                            overlay=False,
                            closeOnOutside=False,
                            size=SizeEnum.lg,
                            resizable=True,
                            width="900px",
                            body=await self.get_review_form(request, bulk=True),
                        ),
                    )
            else:
                return None
        except Exception as exp:
            print('Exception at CrRequest.get_review_action() %s ' % exp)
            traceback.print_exc()

    async def on_create_pre(
            self,
            request: Request,
            obj: SchemaUpdateT,
            **kwargs,
    ) -> Dict[str, Any]:
        data = await super().on_create_pre(request, obj)
        data['create_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        data['update_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        return data

    async def on_update_pre(
            self,
            request: Request,
            obj: SchemaUpdateT,
            item_id: Union[List[str], List[int]],
            **kwargs,
    ) -> Dict[str, Any]:
        try:
            data = await super().on_update_pre(request, obj, item_id)
            data['update_time'] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
            if data['tsg_rvew_rslt'].strip() == 'Approved' or data['tsg_rvew_rslt'].strip() == 'Returned' or data['tsg_rvew_rslt'].strip() == 'Completed':
                addstr = f'{datetime.now().astimezone(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M")}: User {request.user.username} reviewed, action: {data["tsg_rvew_rslt"]} '
                if data['review_history'] is None or len(data['review_history'].strip()) == 0:
                    data['review_history'] = f'{addstr}'
                else:
                    data['review_history'] = f'{data["review_history"]}\n{addstr}'
            return data
        except Exception as exp:
            print('Exception at CrRequest.on_update_pre() %s ' % exp)
            traceback.print_exc()

    @property
    def route_create(self) -> Callable:
        async def route(
            request: Request,
            data: Annotated[Union[List[self.schema_create], self.schema_create], Body()],  # type: ignore
        ) -> BaseApiOut[Union[int, self.schema_model]]:  # type: ignore
            if not await self.has_create_permission(request, data):
                return self.error_no_router_permission(request)
            if not isinstance(data, list):
                data = [data]
            try:
                required_fields = ['customer_name', 'cstm_cntct_name', 'cstm_addr', 'cstm_location', 'sngl_pnt_sys',
                                   'ssr', 'ssr_phone', 'support_tsg_id', 'local_sdm', 'proj_code', 'cntrt_no',
                                   'busnss_jstfction', 'onsite_engineer', 'cr_activity_brief', 'machine_info',
                                   'category', 'prblm_dscrption']
                errors = {}
                if data[0].tsg_rvew_rslt != "Draft":
                    for k, v in vars(data[0]).items():
                        if k in required_fields and (not v or not v.strip()):
                            errors[k] = f"必须填写{k}字段"
                    rtdict = {
                        "status": 422,
                        "msg": "",
                        "errors": errors,
                        "data": None
                    }
                if len(errors) > 0:
                    return rtdict
                else:
                    items = await self.create_items(request, data)
            except Exception as error:
                await self.db.async_rollback()
                print('Exception at CrRequest.route_create() %s ' % error)
                traceback.print_exc()
                return self.error_execute_sql(request=request, error=error)
            resultlen = len(items)
            if resultlen == 1:  # if only one item, return the first item
                result = await self.db.async_run_sync(lambda _: parse_obj_to_schema(items[0], self.schema_model, refresh=True))
                if result.tsg_rvew_rslt.strip() == 'Submitted':
                    # Send email to tsg
                    snd_mail_dress = f'{UserSelect().find_tsg_email_by_id(result.support_tsg_id)}'
                    snd_mail_subject = f'TLS CR Request提交提醒：{result.ssr}提交了一份Change Request'
                    snd_mail_body = f'{result.ssr}提交了一份Change Request：\n变更客户：{result.customer_name};\n变更事件：{result.cr_activity_brief};\n请登录CRTool系统查看。'
                    if result.sngl_pnt_sys.strip() == 'Y':
                        snd_mail_dress =f'{snd_mail_dress}, {UserSelect().leader_emails_str}'
                        snd_mail_subject = f'【单点系统变更】TLS CR Request提交提醒：{result.ssr}提交了一份Change Request'
                    MailTool().send_email(snd_mail_dress, snd_mail_subject, snd_mail_body)
                if result.tsg_rvew_rslt.strip() == 'Approved':
                    # Send email to ssr
                    snd_mail_dress = f'{UserSelect().find_ssr_email_by_id(result.ssr)}'
                    snd_mail_subject = f'TLS CR Request审批提醒：Change Request已审批'
                    snd_mail_body = f'TSG已经审批了你的Change Request：\n变更客户：{result.customer_name};\n变更事件：{result.cr_activity_brief};\n请登录CRTool系统查看。'
                    MailTool().send_email(snd_mail_dress, snd_mail_subject, snd_mail_body)
            return BaseApiOut(data=result)

        return route


    @property
    def route_update(self) -> Callable:
        async def route(
            request: Request,
            item_id: self.AnnotatedItemIdList,  # type: ignore
            data: Annotated[self.schema_update, Body()],  # type: ignore
        ):
            try:
                if not await self.has_update_permission(request, item_id, data):
                    return self.error_no_router_permission(request)
                values = await self.on_update_pre(request, data, item_id=item_id)
                if not values:
                    return self.error_data_handle(request)
                try:
                    required_fields = ['customer_name', 'cstm_cntct_name', 'cstm_addr', 'cstm_location', 'sngl_pnt_sys',
                                       'ssr',
                                       'ssr_phone', 'support_tsg_id', 'local_sdm', 'proj_code', 'cntrt_no',
                                       'busnss_jstfction',
                                       'onsite_engineer', 'cr_activity_brief', 'machine_info', 'category',
                                       'prblm_dscrption']
                    errors = {}
                    if values['tsg_rvew_rslt'] != "Draft":
                        for k, v in values.items():
                            if k in required_fields and (not v or not v.strip()):
                                errors[k] = f"必须填写{k}字段"
                        rtdict = {
                            "status": 422,
                            "msg": "",
                            "errors": errors,
                            "data": None
                        }
                    if len(errors) > 0:
                        return rtdict
                    else:
                        items = await self.update_items(request, item_id, values)
                except Exception as error:
                    await self.db.async_rollback()
                    return self.error_execute_sql(request=request, error=error)
                if items[0].tsg_rvew_rslt.strip() == 'Submitted':
                    # Send email to tsg
                    snd_mail_dress = f'{UserSelect().find_tsg_email_by_id(items[0].support_tsg_id)}'
                    snd_mail_subject = f'TLS CR Request提交提醒：{items[0].ssr}提交了一份Change Request'
                    snd_mail_body = f'{items[0].ssr}提交了一份Change Request：\n变更客户：{items[0].customer_name};\n变更事件：{items[0].cr_activity_brief};\n请登录CRTool系统查看。'
                    if items[0].sngl_pnt_sys.strip() == 'Y':
                        snd_mail_dress = f'{snd_mail_dress}, {UserSelect().leader_emails_str}'
                        snd_mail_subject = f'【单点系统变更】TLS CR Request提交提醒：{items[0].ssr}提交了一份Change Request'
                    MailTool().send_email(snd_mail_dress, snd_mail_subject, snd_mail_body)
                if items[0].tsg_rvew_rslt.strip() == 'Approved':
                    # Send email to ssr
                    snd_mail_dress = f'{UserSelect().find_ssr_email_by_id(items[0].ssr)}'
                    snd_mail_subject = f'TLS CR Request审批提醒：Change Request已审批'
                    snd_mail_body = f'TSG已经审批了你的Change Request：\n变更客户：{items[0].customer_name};\n变更事件：{items[0].cr_activity_brief};\n请登录CRTool系统查看。'
                    MailTool().send_email(snd_mail_dress, snd_mail_subject, snd_mail_body)
                if items[0].tsg_rvew_rslt.strip() == 'Returned':
                    # Send email to ssr
                    snd_mail_dress = f'{UserSelect().find_ssr_email_by_id(items[0].ssr)}'
                    snd_mail_subject = f'TLS CR Request驳回提醒：Change Request已驳回'
                    snd_mail_body = f'TSG已经驳回了你的Change Request：\n变更客户：{items[0].customer_name};\n变更事件：{items[0].cr_activity_brief};\n请登录CRTool系统查看。'
                    MailTool().send_email(snd_mail_dress, snd_mail_subject, snd_mail_body)
                if items[0].tsg_rvew_rslt.strip() == 'Completed':
                    # Send email to ssr
                    snd_mail_dress = f'{UserSelect().find_ssr_email_by_id(items[0].ssr)}'
                    snd_mail_subject = f'TLS CR Request完成提醒：Change Request已完成'
                    snd_mail_body = f'TSG已经完成了你的Change Request：\n变更客户：{items[0].customer_name};\n变更事件：{items[0].cr_activity_brief};\n请登录CRTool系统查看。'
                    MailTool().send_email(snd_mail_dress, snd_mail_subject, snd_mail_body)
                return BaseApiOut(data=len(items))
            except Exception as exp:
                print('Exception at CrRequest.route_update() %s ' % exp)
                traceback.print_exc()

        return route

    @property
    def route_delete(self) -> Callable:
        async def route(
            request: Request,
            item_id: self.AnnotatedItemIdList,  # type: ignore
        ):
            if not await self.has_delete_permission(request, item_id):
                return self.error_no_router_permission(request)
            try:
                can_delete_id=[]
                for id in item_id:
                    items = await self.fetch_items(id)
                    if items[0].tsg_rvew_rslt.strip() == 'Draft':
                        can_delete_id.append(id)
                delitems = await self.delete_items(request, can_delete_id)
                return BaseApiOut(data=len(delitems))
            except Exception as error:
                await self.db.async_rollback()
                print('Exception at CrRequest.route_update() %s ' % error)
                traceback.print_exc()
                return self.error_execute_sql(request=request, error=error)
        return route