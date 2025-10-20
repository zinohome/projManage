#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#  #
#  Copyright (C) 2024 ZinoHome, Inc. All Rights Reserved
#  #
#  @Time    : 2024
#  @Author  : Zhang Jun
#  @Email   : ibmzhangjun@139.com
#  @Software: SwiftApp

import traceback
from datetime import datetime
from fastapi_amis_admin import amis, admin
from fastapi_amis_admin.utils.pydantic import model_fields
from fastapi_user_auth.globals import auth
from fastapi_amis_admin.crud import CrudEnum, BaseApiOut
from fastapi_amis_admin.amis import PageSchema, TableColumn, ActionType, Action, Dialog, SizeEnum, Drawer, LevelEnum, \
    TableCRUD, TabsModeEnum, Form, AmisAPI, DisplayModeEnum, InputExcel, InputTable, Page, FormItem, SchemaNode, Group, \
    Divider, Grid, Card, Html, Tpl, Chart, Service, Table
from fastapi_amis_admin.utils.translation import i18n as _

from apps.admin.models.actlog import ActLog
from apps.admin.swiftadmin import SwiftAdmin
from core.globals import site
from utils.log import log as log
from fastapi import Body, Depends, FastAPI, HTTPException, Request

class ActChartAdmin(admin.PageAdmin):
    group_schema = "ActLog"
    page_schema = PageSchema(
        label='Activity Chart',
        page_title='Activity Chart Dashboard',
        icon='fa fa-bar-chart',
        sort=90
    )
    # Configure page information directly through the page class property;
    page = Page()
    
    # 获取当前月份用于动态显示
    current_month = datetime.now().strftime('%Y年%m月')
    
    # 获取上个月份用于动态显示
    from datetime import timedelta
    last_month_date = datetime.now().replace(day=1) - timedelta(days=1)
    last_month = last_month_date.strftime('%Y年%m月')
    
    page.body = [
                # 添加自定义CSS样式
                Html(
                    html="""
                    <style>
                    .bg-light-blue {
                        background-color: #e3f2fd !important;
                    }
                    </style>
                    """
                ),
                # 第一行：一整栏
                Grid(
                    columns=[{
                        "body": [
                            Card(
                                title="Activity Overview",
                                body=[
                                    # 柱状图配置（直接由 Chart 发起请求，避免父子数据时序问题）
                                    Chart(
                                        api="/actlog/monthly_activities",
                                        height="180px",
                                        replaceChartOption=False,
                                        setOptionOpts={
                                            "notMerge": False,
                                            "lazyUpdate": False
                                        },
                                        interval=10000,
                                        config={
                                            "title": {
                                            "text": "近12个月浏览量"
                                            },
                                            "tooltip": {},
                                            "legend": {
                                                "data": ["浏览次数"]
                                            },
                                            "xAxis": {
                                                "type": "category"
                                            },
                                            "yAxis": {
                                                "type": "value"
                                            },
                                            "series": [{
                                                "type": "bar"
                                            }]
                                        },
                                        dataFilter="""
                                                    const d = data?.data || data || {};
                                                    const xAxisData = Array.isArray(d.labels) ? d.labels : (Array.isArray(d.month) ? d.month : []);
                                                    const seriesData = Array.isArray(d.values) ? d.values : (Array.isArray(d.bar) ? d.bar : []);
                                                    const items = xAxisData.map((name, i) => ({ name, value: Number(seriesData?.[i] ?? 0) }));
                                                    return {
                                                      animation: true,
                                                      animationDuration: 500,
                                                      animationDurationUpdate: 500,
                                                      animationEasing: 'cubicOut',
                                                      animationEasingUpdate: 'cubicOut',
                                                      title: { text: '近12个月浏览量' },
                                                      tooltip: {},
                                                      legend: { data: ['浏览次数'] },
                                                      xAxis: { type: 'category', data: xAxisData },
                                                      yAxis: { type: 'value' },
                                                      series: [{
                                                        id: 'bar-main',
                                                        type: 'bar',
                                                        data: items,
                                                        animation: true,
                                                        barMaxWidth: 60,
                                                        label: { show: true, position: 'top', formatter: ({ value }) => value },
                                                        emphasis: { focus: 'series' }
                                                      }]
                                                    };"""
                                    )
                                ]
                            )
                        ],
                        "lg": 12,  # 大屏幕占12格（一整行）
                        "md": 12,  # 中等屏幕占12格
                        "sm": 12   # 小屏幕占12格
                    }]
                ),
                
                # 第二行：两栏布局
                Grid(
                    style={"height": "300px"},
                    columns=[
                        {
                            "body": [
                                Card(
                                    header=Card.Header(
                                        title=f"{current_month}浏览量排名-Manager"
                                    ),
                                    bodyClassName="p-1",
                                    style={"height": "100%"},
                                    body=[
                                        Service(
                                            api="/actlog/manager_ranking_current_month",
                                            body=Table(
                                                source="${items}",
                                                columns=[
                                                    TableColumn(
                                                        name="rank",
                                                        label="排名",
                                                        width=60,
                                                        type="text"
                                                    ),
                                                    TableColumn(
                                                        name="manager", 
                                                        label="Manager",
                                                        type="tpl",
                                                        tpl="${number > 0 ? '<span style=\"background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;\">' + manager + '</span>' : manager}"
                                                    ),
                                                    TableColumn(
                                                        name="number",
                                                        label="浏览次数",
                                                        width=100,
                                                        type="tpl",
                                                        tpl="${number > 0 ? '<span style=\"background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;\">' + number + '</span>' : number}",
                                                    )
                                                ],
                                                placeholder="暂无数据",
                                                className="table-striped",
                                                autoFillHeight=True,
                                                style={"height": "250px", "overflow": "auto"},
                                            )
                                        )
                                    ]
                                )
                            ],
                            "lg": 6,   # 大屏幕占6格（一半宽度）
                            "md": 6,   # 中等屏幕占6格
                            "sm": 12   # 小屏幕占12格（自动换行）
                        },
                        {
                            "body": [
                                Card(
                                    header=Card.Header(
                                        title=f"{last_month}浏览量排名-Manager"
                                    ),
                                    bodyClassName="p-1",
                                    style={"height": "100%"},
                                    body=[
                                        Service(
                                            api="/actlog/manager_ranking_last_month",
                                            body=Table(
                                                source="${items}",
                                                columns=[
                                                    TableColumn(
                                                        name="rank",
                                                        label="排名",
                                                        width=60,
                                                        type="text"
                                                    ),
                                                    TableColumn(
                                                        name="manager", 
                                                        label="Manager",
                                                        type="tpl",
                                                        tpl="${number > 0 ? '<span style=\"background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;\">' + manager + '</span>' : manager}"
                                                    ),
                                                    TableColumn(
                                                        name="number",
                                                        label="浏览次数",
                                                        width=100,
                                                        type="tpl",
                                                        tpl="${number > 0 ? '<span style=\"background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;\">' + number + '</span>' : number}",
                                                    )
                                                ],
                                                placeholder="暂无数据",
                                                className="table-striped",
                                                autoFillHeight=True,
                                                style={"height": "250px", "overflow": "auto"},
                                            )
                                        )
                                    ]
                                )
                            ],
                            "lg": 6,   # 大屏幕占6格
                            "md": 6,   # 中等屏幕占6格
                            "sm": 12   # 小屏幕占12格
                        }
                    ]
                ),
                
                # 第三行：两栏布局
                Grid(
                    style={"height": "300px"},
                    columns=[
                        {
                            "body": [
                                Card(
                                    header=Card.Header(
                                        title=f"{current_month}贡献度排名-Manager"
                                    ),
                                    bodyClassName="p-1",
                                    style={"height": "100%"},
                                    body=[
                                        Service(
                                            api="/actlog/manager_contribution_current_month",
                                            body=Table(
                                                source="${items}",
                                                columns=[
                                                    TableColumn(
                                                        name="rank",
                                                        label="排名",
                                                        width=60,
                                                        type="text"
                                                    ),
                                                    TableColumn(
                                                        name="manager", 
                                                        label="Manager",
                                                        type="tpl",
                                                        tpl="${number > 0 ? '<span style=\"background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;\">' + manager + '</span>' : manager}"
                                                    ),
                                                    TableColumn(
                                                        name="number",
                                                        label="贡献记录",
                                                        width=100,
                                                        type="tpl",
                                                        tpl="${number > 0 ? '<span style=\"background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;\">' + number + '</span>' : number}",
                                                    )
                                                ],
                                                placeholder="暂无数据",
                                                className="table-striped",
                                                autoFillHeight=True,
                                                style={"height": "250px", "overflow": "auto"},
                                            )
                                        )
                                    ]
                                )
                            ],
                            "lg": 6,   # 大屏幕占6格
                            "md": 6,   # 中等屏幕占6格
                            "sm": 12   # 小屏幕占12格
                        },
                        {
                            "body": [
                                Card(
                                    header=Card.Header(
                                        title=f"{last_month}贡献度排名-Manager"
                                    ),
                                    bodyClassName="p-1",
                                    style={"height": "100%"},
                                    body=[
                                        Service(
                                            api="/actlog/manager_contribution_last_month",
                                            body=Table(
                                                source="${items}",
                                                columns=[
                                                    TableColumn(
                                                        name="rank",
                                                        label="排名",
                                                        width=60,
                                                        type="text"
                                                    ),
                                                    TableColumn(
                                                        name="manager", 
                                                        label="Manager",
                                                        type="tpl",
                                                        tpl="${number > 0 ? '<span style=\"background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;\">' + manager + '</span>' : manager}"
                                                    ),
                                                    TableColumn(
                                                        name="number",
                                                        label="贡献记录",
                                                        width=100,
                                                        type="tpl",
                                                        tpl="${number > 0 ? '<span style=\"background-color: #ffeb3b; padding: 2px 4px; border-radius: 3px;\">' + number + '</span>' : number}",
                                                    )
                                                ],
                                                placeholder="暂无数据",
                                                className="table-striped",
                                                autoFillHeight=True,
                                                style={"height": "250px", "overflow": "auto"},
                                            )
                                        )
                                    ]
                                )
                            ],
                            "lg": 6,   # 大屏幕占6格
                            "md": 6,   # 中等屏幕占6格
                            "sm": 12   # 小屏幕占12格
                        }
                    ]
                )
            ]