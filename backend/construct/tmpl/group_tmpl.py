#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  #
#  Copyright (C) 2023 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2023
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: SwiftApp
from fastapi import APIRouter
from fastapi_amis_admin.crud import SqlalchemyCrud
from core.globals import site
from fastapi_amis_admin import amis, admin
from fastapi_amis_admin.admin import AdminApp
from construct.app import App
from utils.log import log as log
{% for model in models %}
from apps.admin.pages.{{ model.name|trim }}admin import {{ model.name|trim|capitalize }}Admin
{% for submodel in model.submodels %}
from apps.admin.pages.{{ submodel.name|trim }}admin import {{ submodel.name|trim|capitalize }}Admin
{% endfor %}
{% endfor %}

appdef = App()


class {{ group_name }}(admin.AdminApp):
    group_schema = '{{ group_schema }}'
    page_schema = amis.PageSchema(label='{{ label }}', title='{{ title }}', icon='{{ icon }}', sort={{ sort }})
    router_prefix = '{{ router_prefix }}'


    def __init__(self, app: "AdminApp"):
        super().__init__(app)
{% for model in models %}
        self.register_admin({{ model.name|trim|capitalize }}Admin)
{% for submodel in model.submodels %}
        self.register_admin({{ submodel.name|trim|capitalize }}Admin)
{% endfor %}
{% endfor %}

