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
    Divider, Grid, Card, Html, Tpl, Chart
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
    page.body = [
                # 第一行：一整栏
                Grid(
                    columns=[{
                        "body": [
                            Card(
                                title="Activity Overview",
                                body=[
                                    amis.Service(
                                        api="/actlog/activity_total",
                                        body=[
                                            Tpl(
                                                tpl="<div style='font-size: 18px; font-weight: bold; text-align: center; padding: 5px 0;'>总浏览量：${total_count}</div>",
                                                dataFilter="return {total_count: data?.data?.total_count || 0}"
                                            )
                                        ]
                                    )
                                ]
                            )
                        ],
                        "lg": 12,  # 大屏幕占12格（一整行）
                        "md": 12,  # 中等屏幕占12格
                        "sm": 12   # 小屏幕占12格
                    }]
                ),
                # 第一行：一整栏
                Grid(
                    columns=[{
                        "body": [
                            Card(
                                title="Activity Overview",
                                body=[
                                    # 柱状图配置
                                    amis.Service(
                                        api="/actlog/monthly_activities",
                                        body=[
                                            Chart(
                                                height="180px",
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
                                                dataFilter="""config.title.text = '近12个月浏览量';
                                                            config.xAxis.data = data.month || [];
                                                            config.series[0].data = data.bar || [];
                                                            return config;"""
                                            )
                                        ]
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
                    columns=[
                        {
                            "body": [
                                Card(
                                    title="Monthly User Activity",
                                    body=[
                                        amis.Service(
                                            api="/actlog/activity_by_manager_current_month",
                                            body=[
                                                Chart(
                                                    height="180px",
                                                    config={
                                                        "title": {
                                                            "text": "当月浏览量排名-Manager"
                                                        },
                                                        "tooltip": {},
                                                        "legend": {
                                                            "data": ["浏览次数"]
                                                        },
                                                        "xAxis": {
                                                            "type": "category",
                                                            "data": "${data?.xAxis?.data || []}"
                                                        },
                                                        "yAxis": {
                                                            "type": "value"
                                                        },
                                                        "series": [{
                                                            "name": "浏览次数",
                                                            "type": "bar",
                                                            "data": "${data?.series?.[0]?.data || []}"
                                                        }]
                                                    },
                                                    dataFilter="""config.title = data.title || {text: '当月浏览量排名-Manager'};
                                                                config.tooltip = data.tooltip || {};
                                                                config.legend = data.legend || {data: ['浏览次数']};
                                                                config.xAxis = data.xAxis || {type: 'category', data: []};
                                                                config.yAxis = data.yAxis || {};
                                                                config.series = data.series || [{name: '浏览次数', type: 'bar', data: []}];
                                                                return config;"""
                                                )
                                            ]
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
                                    title="Monthly User Activity",
                                    body=[
                                        amis.Service(
                                            api="/actlog/activity_by_manager_last_month",
                                            body=[
                                                Chart(
                                                    height="180px",
                                                    config={
                                                        "title": {
                                                            "text": "上月浏览量排名-Manager"
                                                        },
                                                        "tooltip": {},
                                                        "legend": {
                                                            "data": ["浏览次数"]
                                                        },
                                                        "xAxis": {
                                                            "type": "category",
                                                            "data": "${data?.xAxis?.data || []}"
                                                        },
                                                        "yAxis": {
                                                            "type": "value"
                                                        },
                                                        "series": [{
                                                            "name": "浏览次数",
                                                            "type": "bar",
                                                            "data": "${data?.series?.[0]?.data || []}"
                                                        }]
                                                    },
                                                    dataFilter="""config.title = data.title || {text: '上月浏览量排名-Manager'};
                                                                config.tooltip = data.tooltip || {};
                                                                config.legend = data.legend || {data: ['浏览次数']};
                                                                config.xAxis = data.xAxis || {type: 'category', data: []};
                                                                config.yAxis = data.yAxis || {};
                                                                config.series = data.series || [{name: '浏览次数', type: 'bar', data: []}];
                                                                return config;"""
                                                )
                                            ]
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
                    columns=[
                        {
                            "body": [
                                Card(
                                    title="Monthly User Activity",
                                    body=[
                                        amis.Service(
                                            api="/actlog/contribution_by_manager_current_month",
                                            body=[
                                                Chart(
                                                    height="180px",
                                                    config={
                                                        "title": {
                                                            "text": "当月贡献度排名-Manager"
                                                        },
                                                        "tooltip": {},
                                                        "legend": {
                                                            "data": ["贡献次数"]
                                                        },
                                                        "xAxis": {
                                                            "type": "category",
                                                            "data": "${data?.xAxis?.data || []}"
                                                        },
                                                        "yAxis": {
                                                            "type": "value"
                                                        },
                                                        "series": [{
                                                            "name": "贡献次数",
                                                            "type": "bar",
                                                            "data": "${data?.series?.[0]?.data || []}"
                                                        }]
                                                    },
                                                    dataFilter="""config.title = data.title || {text: '当月贡献度排名-Manager'};
                                                                config.tooltip = data.tooltip || {};
                                                                config.legend = data.legend || {data: ['贡献次数']};
                                                                config.xAxis = data.xAxis || {type: 'category', data: []};
                                                                config.yAxis = data.yAxis || {};
                                                                config.series = data.series || [{name: '贡献次数', type: 'bar', data: []}];
                                                                return config;"""
                                                )
                                            ]
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
                                    title="Monthly User Activity",
                                    body=[
                                        # 修改第三行右侧栏的图表，替换重复的/actlog/monthly_activities调用
                                        amis.Service(
                                            api="/actlog/contribution_by_manager_last_month",  # 使用贡献度数据替代
                                            body=[
                                                Chart(
                                                    height="180px",
                                                    config={
                                                        "title": {"text": "上月贡献度排名-Manager"},
                                                        "tooltip": {},
                                                        "legend": {"data": ["贡献次数"]},
                                                        "xAxis": {
                                                            "type": "category",
                                                            "data": "${data?.xAxis?.data || []}"
                                                        },
                                                        "yAxis": {"type": "value"},
                                                        "series": [{
                                                            "name": "贡献次数",
                                                            "type": "bar",
                                                            "data": "${data?.series?.[0]?.data || []}"
                                                        }]
                                                    },
                                                    dataFilter="""config.title = data.title || {text: '上月贡献度排名-Manager'};
                                                            config.tooltip = data.tooltip || {};
                                                            config.legend = data.legend || {data: ['贡献次数']};
                                                            config.xAxis = data.xAxis || {type: 'category', data: []};
                                                            config.yAxis = data.yAxis || {};
                                                            config.series = data.series || [{name: '贡献次数', type: 'bar', data: []}];
                                                            return config;"""
                                                )
                                            ]
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