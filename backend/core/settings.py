#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 10:17
# @Author  : ZhangJun
# @FileName: settings.py

import os
import sys
from pathlib import Path
from typing import List, Optional

from fastapi_amis_admin.admin.settings import Settings as AmisSettings
from construct.app import App

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.append(BACKEND_DIR.__str__())
appdef = App()
class Settings(AmisSettings):
    name: str = 'Swiftapp'
    host: str = '127.0.0.1'
    port: int = 8000
    secret_key: str = ''
    allow_origins: Optional[List[str]] = None

# 设置FAA_GLOBALS环境变量
os.environ.setdefault("FAA_GLOBALS", "core.globals")

settings = Settings(_env_file=os.path.join(BACKEND_DIR, '.env'))
for key, value in appdef.Consdict['Settings'].items():
    if key == 'allow_origins':
        settings.__setattr__(key, value.split(","))
    else:
        settings.__setattr__(key, value)

if __name__ == '__main__':
    print(settings)
