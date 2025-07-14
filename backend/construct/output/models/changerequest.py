#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  #
#  Copyright (C) 2023 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2023
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: SwiftApp
from datetime import date, datetime
from decimal import Decimal
from fastapi_amis_admin import models, amis
from typing import Optional, List, TYPE_CHECKING

from fastapi_amis_admin.models import Field
from sqlalchemy import func
from sqlmodel import Relationship
from sqlmodelx import SQLModel

from core import i18n as _

class SwiftSQLModel(SQLModel):
    class Config:
        use_enum_values = True
        from_attributes = True
        arbitrary_types_allowed = True

class Changerequest(SwiftSQLModel, table=True):
    __tablename__ = 'changerequest'
    id: Optional[int] = models.Field(default=None,
                                                    title='ID',
                                                    primary_key=True,
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    customer_name: str = models.Field(default=None,
                                                    title='*Customer Name/Number<br>(客户名/客户号)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    case_number: Optional[str] = models.Field(default=None,
                                                    title='Case No',
                                                    nullable=True,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    cstm_cntct_name: Optional[str] = models.Field(default=None,
                                                    title='*Customer Contact Name<br>(客户联系人)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    cstm_cntct_phone: Optional[str] = models.Field(default=None,
                                                    title='Phone',
                                                    nullable=True,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    cstm_addr: Optional[str] = models.Field(default=None,
                                                    title='*Customer Address<br>(客户客户地址)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    cstm_location: Optional[str] = models.Field(default=None,
                                                    title='*Location<br>(客户所在城市)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    sngl_pnt_sys: Optional[str] = models.Field(default="N",
                                                    title='*是否单点系统变更',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item=amis.Select(options=appdef.AppVardicts['sngl_pnt_sys']['value'], labelField='label', valueField='value'),
                                                    amis_table_column = "")
    urgency: Optional[str] = models.Field(default="2",
                                                    title='紧急程度SV(同PMH)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item=amis.Select(options=appdef.AppVardicts['urgency']['value'], labelField='label', valueField='value'),
                                                    amis_table_column = "")
    complexity: Optional[str] = models.Field(default="2",
                                                    title='Complexity<br>复杂程度',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item=amis.Select(options=appdef.AppVardicts['complexity']['value'], labelField='label', valueField='value'),
                                                    amis_table_column = "")
    ssr: Optional[str] = models.Field(default=None,
                                                    title='*SSR Contact Name<br>(负责SSR 名字)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    ssr_phone: Optional[str] = models.Field(default=None,
                                                    title='*Phone/MP',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    support_tsg_id: Optional[str] = models.Field(default=None,
                                                    title='*Support TSG ID<br>(技术支持人员名字)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    local_sdm: Optional[str] = models.Field(default=None,
                                                    title='*Local SDM<br>(SSR经理)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    proj_code: Optional[str] = models.Field(default=None,
                                                    title='*Project Code/CSP WO<br>(TSG timereport Input使用)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    cntrt_no: Optional[str] = models.Field(default=None,
                                                    title='*Contract Number',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    busnss_jstfction: Optional[str] = models.Field(default=None,
                                                    title='*Business Justification<br>(合同中对TSG现场支持的约定以及合理合规的商业理由)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item=amis.Textarea(),
                                                    amis_table_column = "")
    onsite_engineer: Optional[str] = models.Field(default=None,
                                                    title='*Onsite Engineer<br>(维修SSR名字)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    begin_date: Optional[str] = models.Field(default_factory= datetime.now,
                                                    title='Begin Date<br>(维护开始时间)',
                                                    nullable=False,
                                                    index=False,
                                                    sa_column_kwargs={"server_default": func.now()},
                                                    amis_form_item=amis.InputDatetime(disabled=False, format="YYYY-MM-DD", inputFormat="YYYY-MM-DD", maxDate="$end_date"),
                                                    amis_table_column = "")
    end_date: Optional[str] = models.Field(default_factory= datetime.now,
                                                    title='End Date<br>(计划结束时间)',
                                                    nullable=False,
                                                    index=False,
                                                    sa_column_kwargs={"server_default": func.now()},
                                                    amis_form_item=amis.InputDatetime(disabled=False, format="YYYY-MM-DD", inputFormat="YYYY-MM-DD", minDate="$begin_date"),
                                                    amis_table_column = "")
    cr_activity_brief: Optional[str] = models.Field(default=None,
                                                    title='*CR activity Brief<br>(变更描述)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item=amis.Textarea(),
                                                    amis_table_column = "")
    cr_detail_plan: Optional[str] = models.Field(default=None,
                                                    title='CR Detail Plan<br>(变更方案)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item=amis.Textarea(),
                                                    amis_table_column = "")
    machine_info: Optional[str] = models.Field(default=None,
                                                    title='*Machine Type/ModelSN/Machine Status<br>(机器型号、序列号、服务状态)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    version: Optional[str] = models.Field(default=None,
                                                    title='Microcode/Patch Level<br>(微码版本/补丁版本)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    related_ibm_software: Optional[str] = models.Field(default=None,
                                                    title='Related IBM Software<br>(相关软件名称)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    sw_version: Optional[str] = models.Field(default=None,
                                                    title='SW Version/PTF<br>(软件版本)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item = "",
                                                    amis_table_column = "")
    category: Optional[str] = models.Field(default=None,
                                                    title='*变更类型<br>(选择正确的变更类别，以便归档)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item=amis.Select(options=appdef.AppVardicts['category']['value'], labelField='label', valueField='value', multiple=True),
                                                    amis_table_column = "")
    prblm_dscrption: Optional[str] = models.Field(default=None,
                                                    title='*Problem Description and  Help needed<br>(故障现象以及所需帮助)',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item=amis.Textarea(),
                                                    amis_table_column = "")
    tsg_rvew_rslt: Optional[str] = models.Field(default="N",
                                                    title='TSG Review Result<br>审核结果',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item=amis.Select(options=appdef.AppVardicts['tsg_rvew_rslt']['value'], labelField='label', valueField='value'),
                                                    amis_table_column = "")
    tsg_onsite: Optional[str] = models.Field(default="N",
                                                    title='TSG On Site Needed',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item=amis.Select(options=appdef.AppVardicts['tsg_onsite']['value'], labelField='label', valueField='value'),
                                                    amis_table_column = "")
    tsg_comments: Optional[str] = models.Field(default=None,
                                                    title='Comments',
                                                    nullable=False,
                                                    index=False,
                                                    amis_form_item=amis.Textarea(),
                                                    amis_table_column = "")
    create_time: datetime = models.Field(default_factory= datetime.now,
                                                    title='Create Time',
                                                    nullable=False,
                                                    index=True,
                                                    amis_form_item=amis.InputDatetime(disabled=True),
                                                    amis_table_column = "")
    update_time: Optional[datetime] = models.Field(default_factory= datetime.now,
                                                    title='Update Time',
                                                    nullable=False,
                                                    index=True,
                                                    sa_column_kwargs={"onupdate": func.now(), "server_default": func.now()},
                                                    amis_form_item=amis.InputDatetime(disabled=True),
                                                    amis_table_column = "")
