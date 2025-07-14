#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 10:51
# @Author  : ZhangJun
# @FileName: crud.py

from fastapi import APIRouter
from fastapi_amis_admin.crud import SqlalchemyCrud

#from apps.admin.models.contractdetail import Contractdetail
from core.globals import site

from construct.app import App

from utils.log import log as log

router = APIRouter(prefix='/admin/test', tags=['test'])
#contractdetail_crud = SqlalchemyCrud(model=Contractdetail, engine=site.engine, pk_name='contractdetail_id').register_crud()
#site.router.include_router(contractdetail_crud.router)

