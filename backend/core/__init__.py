#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 10:14
# @Author  : ZhangJun
# @FileName: __init__.py.py

from fastapi_amis_admin import i18n

from core.settings import settings

i18n.set_language(settings.language)
