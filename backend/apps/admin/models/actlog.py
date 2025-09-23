#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: ibmzhangjun@139.com
@file: log.py.py
@time: 2025/9/23 下午4:31
@desc: 
"""

from datetime import datetime

from aiomysql import sa
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

class ActLog(SwiftSQLModel, table=True):
    __tablename__ = 'actlog'
    id: Optional[int] = models.Field(default=None,
                                     title='ID',
                                     primary_key=True,
                                     nullable=False,
                                     index=False,
                                     amis_form_item=amis.InputText(required=True),
                                     amis_table_column=amis.TableColumn(toggled=False))
    act_type: Optional[str] = models.Field(default=None,
                                     title='操作类型',
                                     nullable=True,
                                     amis_form_item=amis.InputText(required=True),
                                     amis_table_column=amis.TableColumn(toggled=False))
    act_username: Optional[str] = models.Field(default=None,
                                     title='操作用户',
                                     nullable=True,
                                     amis_form_item=amis.InputText(required=True),
                                     amis_table_column=amis.TableColumn(toggled=False))
    act_name: Optional[str] = models.Field(default=None,
                                     title='操作人',
                                     nullable=True,
                                     amis_form_item=amis.InputText(required=True),
                                     amis_table_column=amis.TableColumn(toggled=False))
    act_time: Optional[datetime] = models.Field(default_factory=datetime.now,
                                                   title='操作时间',
                                                   nullable=True,
                                                   index=True,
                                                   amis_form_item=amis.InputDatetime(disabled=True),
                                                   amis_table_column=amis.TableColumn(toggled=False))