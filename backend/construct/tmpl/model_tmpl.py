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

class {{ model_name|trim|capitalize }}(SwiftSQLModel, table=True):
    __tablename__ = '{{ tablename }}'
{% for field in fields %}
    {{ field.name }}: {% if field.optional %}Optional[{% endif %}{{ field.type }}{% if field.optional %}]{% endif %} = models.Field({% if field.default_factory != None %}default_factory= {{ field.default_factory }}{% else %}default={{ field.default }}{% endif %},
                                                    title='{{ field.title }}',
                                                    {% if field.primary_key == True %}
                                                    primary_key={{ field.primary_key }},
{% endif %}
{% if field.foreign_key != None %}
                                                    foreign_key='{{ field.foreign_key }}',
{% endif %}
                                                    nullable={{ field.nullable }},
                                                    index={{ field.index }},
{% if field.sa_column_kwargs != None %}
                                                    sa_column_kwargs={{ field.sa_column_kwargs }},
{% endif %}
{% if field.amis_form_item|trim != '' %}
                                                    amis_form_item={{ field.amis_form_item }},
{% else %}
                                                    amis_form_item = "",
{% endif %}
{% if field.amis_table_column|trim != '' %}
                                                    amis_table_column={{ field.amis_table_column }})
{% else %}
                                                    amis_table_column = "")
{% endif %}
{% endfor %}
