#!/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2025/03/04 10:28
# @Author  : ZhangJun
# @FileName: main.py

import os
from fastapi import FastAPI
from sqlmodel import SQLModel
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.staticfiles import StaticFiles

from core import settings
from core.globals import auth, site, check_db_connection
from contextlib import asynccontextmanager

from utils.batchuserreg import BatchUserReg

app = FastAPI(debug=settings.debug)
# 在app应用下每条请求处理之前都附加`request.auth`和`request.user`对象
auth.backend.attach_middleware(app)

# 安装应用
from apps import admin
admin.setup(app.router, site)

# 挂载后台管理系统
site.mount_app(app)

# 注意1: site.mount_app会默认添加site.db的session会话上下文中间件,如果你使用了其他的数据库连接,请自行添加.例如:
# from core.globals import sync_db
# app.add_middleware(sync_db.asgi_middleware) # 注意中间件的注册顺序.

# 注意2: 非请求上下文中,请自行创建session会话,例如:定时任务,测试脚本等.
# from core.globals import async_db
# async with async_db():
#     async_db.async_get(...)
#     async_db.session.get(...)
#     # do something


@app.on_event("startup")
async def startup():
    await check_db_connection()
    await site.db.async_run_sync(SQLModel.metadata.create_all, is_session=False)
    # 创建默认管理员,用户名: admin,密码: admin, 请及时修改密码!!!
    await auth.create_role_user("admin")
    # 创建默认超级管理员,用户名: root,密码: root, 请及时修改密码!!!
    await auth.create_role_user("root")
    # 创建用户
    #await BatchUserReg().reguser()
    # 运行site的startup方法,加载casbin策略等
    await site.router.startup()
    if not auth.enforcer.enforce("u:admin", site.unique_id, "page", "page"):
        await auth.enforcer.add_policy("u:admin", site.unique_id, "page", "page", "allow")

@app.get('/')
async def index():
    return RedirectResponse(url=site.router_path)


# 1.配置 CORSMiddleware
from starlette.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allow_origins,  # 允许访问的源
    allow_credentials=True,  # 支持 cookie
    allow_methods=["*"],  # 允许使用的请求方法
    allow_headers=["*"]  # 允许携带的 Headers
)

# 2. 配置静态资源目录
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, 'backend/apps/static')), name="static")

# 3.配置 Swagger UI CDN
from fastapi.openapi.docs import get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html, get_redoc_html

@app.get("/apidocs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_favicon_url="/static/favicon.png",
        swagger_css_url="/static/swagger-ui-dist@5/swagger-ui.css",
    )
@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

# 4.配置 Redoc CDN
@app.get("/apiredoc", include_in_schema=False)
async def custom_redoc_ui_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="/static/redoc@next/bundles/redoc.standalone.js",
        redoc_favicon_url="/static/favicon.png",
        with_google_fonts=False,
    )

# 要求: 用户必须登录
@app.get("/auth/get_user")
@auth.requires()
def get_user(request: Request):
    return request.user