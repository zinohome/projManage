#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  #
#  Copyright (C) 2024 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2024
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: SwiftApp

from datetime import datetime
from fastapi_amis_admin import models, amis
from typing import Optional
from sqlalchemy import func
from sqlmodelx import SQLModel

from core.settings import appdef


class SwiftSQLModel(SQLModel):
    class Config:
        use_enum_values = True
        from_attributes = True
        arbitrary_types_allowed = True

class Projman(SwiftSQLModel, table=True):
    __tablename__ = 'projman'
    id: Optional[int] = models.Field(default=None,
                                     title='ID',
                                     primary_key=True,
                                     nullable=False,
                                     index=False,
                                     amis_form_item=amis.InputText(required=True),
                                     amis_table_column=amis.TableColumn(toggled=False))
    sn: Optional[str] = models.Field(default=None,
                                     title='编号',
                                     primary_key=False,
                                     nullable=True,
                                     index=False,
                                     amis_form_item=amis.InputText(disabled=True, placeholder='自动生成，不需输入'),
                                     amis_table_column=amis.TableColumn(toggled=False))
    customer_id: Optional[str] = models.Field(default=None,
                                    title='客户号',
                                    nullable=True,
                                    index=False,
                                    amis_form_item=amis.InputText(required=False, placeholder='请输入六位数客户号'),
                                    amis_table_column=amis.TableColumn(toggled=True))
    customer_name: str = models.Field(default=None,
                                      title='客户名',
                                      nullable=False,
                                      index=False,
                                      amis_form_item=amis.InputText(required=True, placeholder='请输入客户名'),
                                      amis_table_column=amis.TableColumn(toggled=True))
    customer_location: Optional[str] = models.Field(default=None,
                                      title='Location',
                                      nullable=False,
                                      index=False,
                                      amis_form_item=amis.Select(options=appdef.AppVardicts['customer_location']['value'], labelField='label', valueField='value', required=True),
                                      amis_table_column=amis.TableColumn(toggled=True),
                                      amis_filter_item = amis.Select(options=appdef.AppVardicts['customer_location']['value'], labelField='label', valueField='value'))

    customer_industry: Optional[str] = models.Field(default=None,
                                                    title='行业',
                                                    nullable=True,
                                                    index=False,
                                                    amis_form_item=amis.Select(options=appdef.AppVardicts['customer_industry']['value'], labelField='label', valueField='value', required=True),
                                                    amis_table_column=amis.TableColumn(toggled=True))
    business_category: Optional[str] = models.Field(default=None,
                                                    title='业务分类',
                                                    nullable=True,
                                                    index=False,
                                                    amis_form_item=amis.Select(options=appdef.AppVardicts['business_category']['value'], labelField='label', valueField='value', required=True),
                                                    amis_table_column=amis.TableColumn(toggled=True),
                                                    amis_filter_item = amis.Select(options=appdef.AppVardicts['business_category']['value'], labelField='label', valueField='value'))
    project_name: str = models.Field(default=None,
                                     title='项目名称',
                                     nullable=False,
                                     index=False,
                                     amis_form_item=amis.InputText(required=True, placeholder='请输入项目名称'),
                                     amis_table_column=amis.TableColumn(toggled=True))
    project_location: Optional[str] = models.Field(default=None,
                                                   title='项目所在地',
                                                   nullable=True,
                                                   index=False,
                                                   amis_form_item=amis.InputText(required=False, placeholder='请输入项目所在地'),
                                                   amis_table_column=amis.TableColumn(toggled=True))
    project_contact: Optional[str] = models.Field(default=None,
                                                  title='项目联系人',
                                                  nullable=True,
                                                  index=False,
                                                  amis_form_item=amis.InputText(required=False, placeholder='请输入项目联系人'),
                                                  amis_table_column=amis.TableColumn(toggled=True))
    contact_title: Optional[str] = models.Field(default=None,
                                                  title='所属部门及职位',
                                                  nullable=True,
                                                  index=False,
                                                  amis_form_item=amis.InputText(required=False,
                                                                                placeholder='请输入项目联系人所属部门及职位，例如：采购部经理'),
                                                  amis_table_column=amis.TableColumn(toggled=True))
    contact_phone: Optional[str] = models.Field(default=None,
                                                title='联系电话',
                                                nullable=True,
                                                index=False,
                                                amis_form_item=amis.InputText(required=False, placeholder='请输入联系电话'),
                                                amis_table_column=amis.TableColumn(toggled=True))
    service_content: Optional[str] = models.Field(default=None,
                                                  title='服务内容及要求',
                                                  nullable=True,
                                                  index=False,
                                                  amis_form_item=amis.Textarea(required=False, placeholder='请输入服务内容及要求'),
                                                  amis_table_column=amis.TableColumn(toggled=True))
    contract_amount: Optional[str] = models.Field(default=None,
                                                    title='合同金额',
                                                    nullable=True,
                                                    index=False,
                                                    amis_form_item=amis.InputText(required=False, placeholder='请输入合同金额'),
                                                    amis_table_column=amis.TableColumn(toggled=True))
    contract_duration: Optional[str] = models.Field(default=None,
                                                      title='合同年限',
                                                      nullable=True,
                                                      index=False,
                                                      amis_form_item=amis.InputText(required=False, placeholder='请输入合同年限'),
                                                      amis_table_column=amis.TableColumn(toggled=True))
    contract_sign_date: Optional[str] = models.Field(default=None,
                                                     title='合同签订日期',
                                                     nullable=True,
                                                     index=False,
                                                     amis_form_item=amis.InputDatetime(format="YYYY-MM-DD", inputFormat="YYYY-MM-DD"),
                                                     amis_table_column=amis.TableColumn(toggled=True))
    contract_end_date: Optional[str] = models.Field(default=None,
                                                    title='合同到期时间',
                                                    nullable=True,
                                                    index=False,
                                                    amis_form_item=amis.InputDatetime(format="YYYY-MM-DD", inputFormat="YYYY-MM-DD"),
                                                    amis_table_column=amis.TableColumn(toggled=True))
    expected_renewal_time: Optional[str] = models.Field(default=None,
                                                        title='预计续约时间',
                                                        nullable=True,
                                                        index=False,
                                                        amis_form_item=amis.InputDatetime(format="YYYY-MM-DD", inputFormat="YYYY-MM-DD"),
                                                        amis_table_column=amis.TableColumn(toggled=True))
    cooperation_method: Optional[str] = models.Field(default=None,
                                                     title='合作方式',
                                                     nullable=True,
                                                     index=False,
                                                     amis_form_item=amis.InputText(required=False, placeholder='请输入合作方式'),
                                                     amis_table_column=amis.TableColumn(toggled=True))
    is_bidding: Optional[str] = models.Field(default=None,
                                             title='是否开标',
                                             nullable=True,
                                             index=False,
                                             amis_form_item=amis.Select(options=appdef.AppVardicts['open_bid']['value'], labelField='label', valueField='value', required=False),
                                             amis_table_column=amis.TableColumn(toggled=True))
    bidding_type: Optional[str] = models.Field(default=None,
                                               title='招标类型',
                                               nullable=True,
                                               index=False,
                                               amis_form_item=amis.Select(options=appdef.AppVardicts['bid_type']['value'], labelField='label', valueField='value', required=False),
                                               amis_table_column=amis.TableColumn(toggled=True))
    project_number: Optional[str] = models.Field(default=None,
                                                title='项目编号',
                                                nullable=True,
                                                index=False,
                                                amis_form_item=amis.InputText(),
                                                amis_table_column=amis.TableColumn(toggled=True))
    subject_matter: Optional[str] = models.Field(default=None,
                                                 title='标的物',
                                                 nullable=True,
                                                 index=False,
                                                 amis_form_item=amis.InputText(required=False, placeholder='请输入标的物，如 呼叫中心支持服务'),
                                                 amis_table_column=amis.TableColumn(toggled=True))
    budget_amount: Optional[str] = models.Field(default=None,
                                                  title='预算金额',
                                                  nullable=True,
                                                  index=False,
                                                  amis_form_item=amis.InputText(required=False, placeholder='请输入预算金额'),
                                                  amis_table_column=amis.TableColumn(toggled=True))
    max_price: Optional[str] = models.Field(default=None,
                                              title='最高限价',
                                              nullable=True,
                                              index=False,
                                              amis_form_item=amis.InputText(required=False, placeholder='请输入最高限价'),
                                              amis_table_column=amis.TableColumn(toggled=True))
    publish_time: Optional[str] = models.Field(default=None,
                                               title='发布时间',
                                               nullable=True,
                                               index=False,
                                               amis_form_item=amis.InputDatetime(format="YYYY-MM-DD HH:mm", inputFormat="YYYY-MM-DD HH:mm"),
                                               amis_table_column=amis.TableColumn(toggled=True))
    deadline: Optional[str] = models.Field(default=None,
                                           title='截至时间',
                                           nullable=True,
                                           index=False,
                                           amis_form_item=amis.InputDatetime(format="YYYY-MM-DD HH:mm", inputFormat="YYYY-MM-DD HH:mm"),
                                           amis_table_column=amis.TableColumn(toggled=True))
    bid_price: Optional[str] = models.Field(default=None,
                                              title='中标价格',
                                              nullable=True,
                                              index=False,
                                              amis_form_item=amis.InputText(required=False, placeholder='请输入中标价格'),
                                              amis_table_column=amis.TableColumn(toggled=True))
    bid_date: Optional[str] = models.Field(default=None,
                                           title='中标日期',
                                           nullable=True,
                                           index=False,
                                           amis_form_item=amis.InputDatetime(format="YYYY-MM-DD", inputFormat="YYYY-MM-DD"),
                                           amis_table_column=amis.TableColumn(toggled=True))
    winning_company: Optional[str] = models.Field(default=None,
                                                  title='中标公司',
                                                  nullable=True,
                                                  index=False,
                                                  amis_form_item=amis.InputText(required=False, placeholder='请输入中标公司'),
                                                  amis_table_column=amis.TableColumn(toggled=True))
    website_reference: Optional[str] = models.Field(default=None,
                                                    title='网址参考',
                                                    nullable=True,
                                                    index=False,
                                                    amis_form_item=amis.InputText(required=False, placeholder='可填写项目公告网址'),
                                                    amis_table_column=amis.TableColumn(toggled=True))
    main_competitors: Optional[str] = models.Field(default=None,
                                                   title='主要竞争对手',
                                                   nullable=True,
                                                   index=False,
                                                   amis_form_item=amis.InputText(required=False, placeholder='请输入主要竞争公司名称'),
                                                   amis_table_column=amis.TableColumn(toggled=True))
    others: Optional[str] = models.Field(default=None,
                                         title='其他',
                                         nullable=True,
                                         index=False,
                                         amis_form_item=amis.Textarea(required=False, placeholder='可填写其他项目关联信息，例如：供应商具体情况，招标流程，注意事项，特殊说明等。'),
                                         amis_table_column=amis.TableColumn(toggled=True))
