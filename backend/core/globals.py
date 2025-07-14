#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 10:15
# @Author  : ZhangJun
# @FileName: globals.py

from sqlalchemy_database import AsyncDatabase, Database
from fastapi_user_auth.admin import AuthAdminSite
from fastapi_user_auth.auth import Auth
from fastapi_user_auth.auth.backends.jwt import JwtTokenStore
from sqlalchemy import QueuePool, text

from core.settings import settings
from utils.log import log as log
from core import i18n as _

# 创建异步数据库引擎
async_db = AsyncDatabase.create(
    url=settings.database_url_async,
    session_options={
        "expire_on_commit": False,
    },
    # 连接池配置
    isolation_level="READ COMMITTED",
    pool_size=10,  # 连接池大小
    max_overflow=10,  # 最大溢出连接数
    pool_timeout=30,  # 连接池超时时间
    pool_recycle=3600,  # 连接回收时间
    pool_pre_ping=True,  # 连接前测试
)
# 创建同步数据库引擎
sync_db = Database.create(
    url=settings.database_url,
    session_options={
        "expire_on_commit": False,
    },
    # 连接池配置
    isolation_level="READ COMMITTED",
    poolclass=QueuePool,  # 使用队列连接池
    pool_size=10,  # 连接池大小
    max_overflow=10,  # 最大溢出连接数
    pool_timeout=30,  # 连接池超时时间
    pool_recycle=3600,  # 连接回收时间
    pool_pre_ping=True,  # 连接前测试
)


async def check_db_connection():
    """检查数据库连接是否正常"""
    try:
        async with async_db.engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            if result.scalar() == 1:
                log.info("数据库连接正常")
            else:
                log.warning("数据库连接测试返回意外结果")
    except Exception as e:
        log.error(f"数据库连接测试失败: {str(e)}")
        raise

auth = Auth(db=async_db, token_store=JwtTokenStore(secret_key=settings.secret_key))
site = AuthAdminSite(settings, engine=async_db, auth=auth)
auth = site.auth
site.UserAuthApp.page_schema.sort = -99


