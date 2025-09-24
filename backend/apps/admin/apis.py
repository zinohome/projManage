#!/usr/bin/env python3
# -*- coding:utf-8 -*-
import traceback
from datetime import datetime
from zoneinfo import ZoneInfo

# @Time    : 2025/03/04 10:49
# @Author  : ZhangJun
# @FileName: apis.py

from fastapi import APIRouter, Path
from fastapi_amis_admin.globals.deps import SyncSess, AsyncSess
from fastapi_user_auth.globals import auth
from requests import request
from sqlalchemy import text

from core.globals import site

from utils.log import log as log

router = APIRouter()


@router.get('/hello')
async def hello(name: str = '') -> str:
    return f'hello {name}'


@router.get("/test_sync_db", summary="测试同步数据库操作")
def test_sync_db(sess: SyncSess):
    # obj=sess.get(...)
    # do something
    pass

@router.get("/crtool/get_sdm_list", summary="从数据库获取已输入的SDM姓名")
async def get_sdm_list(sess: SyncSess):
    # obj=sess.get(...)
    # do something
    sdm_list = []
    try:
        result = await site.engine.execute(text("SELECT DISTINCT local_sdm FROM changerequest"))
        rows = result.fetchall()
        result_list = [dict(row._asdict())['local_sdm'] for row in rows]
        sdm_list = [{"label": name, "value": name} for name in result_list]
    except Exception as exp:
        print('Exception at apis.get_sdm_list() %s ' % exp)
        traceback.print_exc()
    return sdm_list

@router.get("/crtool/get_duplicate_crdata/item/{item_id}")
async def get_duplicate_data(
            sess: SyncSess,
            item_id: int = Path(..., title="变更请求ID", description="需要查询的变更请求唯一标识", ge=1)
        ):
    returnobj = {}
    returnobj['status'] = 0
    returnobj['data'] = {}
    returnobj['msg'] = "success"
    returnobj['code'] = None
    try:
        user = await auth.get_current_user(request)
        query = text("""
                    SELECT * 
                    FROM projman 
                    WHERE id = :item_id
                """)
        result = sess.execute(query, {"item_id": item_id})
        rows = result.fetchall()
        # 将Row对象转换为字典列表
        result_list = [dict(row._asdict()) for row in rows]
        returnobj["data"] = result_list[0]
        returnobj["data"].pop("id", None)
        returnobj["data"]["creator"] = user.nickname
        returnobj["data"]["create_time"] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
        returnobj["data"]["update_time"] = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
    except Exception as exp:
        print('Exception at apis.get_sdm_list() %s ' % exp)
        traceback.print_exc()
    return returnobj

@router.get("/test_async_db", summary="测试异步数据库操作")
async def test_async_db(sess: AsyncSess):
    # obj=await sess.get(...)
    # do something
    pass

@router.get("/actlog/daily_activities", summary="获取一个月内每天活动统计数据")
async def get_daily_activities(sess: SyncSess):
    """统计一个月内每天record_count总数，返回给折线图使用的数据格式"""
    returnobj = {
        "status": 0,
        "msg": "ok",
        "data": {
            "date": [],
            "line": []
        }
    }
    try:
        # SQL查询：统计一个月内每天的记录总数
        query = text("""
            SELECT action_date, SUM(record_count) as total_count
            FROM actlog_daily_stats_user
            WHERE action_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY action_date
            ORDER BY action_date ASC
        """)
        result = await site.engine.execute(query)
        rows = result.fetchall()
        
        # 提取日期和对应的总数
        dates = []
        counts = []
        for row in rows:
            dates.append(row.action_date.strftime('%Y-%m-%d'))  # 转换日期格式
            counts.append(int(row.total_count))  # 确保是整数类型
        
        # 如果line数组长度小于2，返回示例数据
        if len(returnobj["data"]["line"]) < 2:
            returnobj["data"]["date"] = ["2025-09-24", "2025-09-25", "2025-09-26", "2025-09-27"]
            returnobj["data"]["line"] = [20, 30, 40, 25]
        else:
            returnobj["data"]["date"] = dates
            returnobj["data"]["line"] = counts
        
        #returnobj["data"]["date"] = ["2025-09-24", "2025-09-25", "2025-09-26"]
        #returnobj["data"]["line"] = [20, 30, 30]
        
    except Exception as exp:
        print('Exception at apis.get_daily_activities() %s ' % exp)
        traceback.print_exc()
        returnobj["status"] = 1
        returnobj["msg"] = f"查询失败: {str(exp)}"
    
    return returnobj

# from fastapi_user_authuser_auth.globals.deps import CurrentUser
#
# @router.get("/get_user", summary="获取当前登录用户")
# async def get_user(user: CurrentUser):
#     return user


@router.get("/actlog/activity_by_person", summary="获取本月按用户分类的浏览量统计数据")
async def get_activity_by_person(sess: SyncSess):
    """统计本月按act_username分类的record_count总和排名前10的记录，返回给条形图使用的数据格式"""
    returnobj = {
        "status": 0,
        "msg": "ok",
        "data": {
            "title": {"text": "上月浏览量排名-Person"},
            "tooltip": {},
            "legend": {"data": ["浏览次数"]},
            "xAxis": {"data": []},
            "yAxis": {},
            "series": [{"name": "浏览次数", "type": "bar", "data": []}]
        }
    }
    try:
        # SQL查询：统计本月按用户分类的活动总数，取前10名
        query = text("""
            SELECT act_username, SUM(record_count) as total_count
            FROM actlog_daily_stats_user
            WHERE action_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
              AND action_date <= LAST_DAY(CURDATE())
            GROUP BY act_username
            ORDER BY total_count DESC
            LIMIT 10
        """)
        result = await site.engine.execute(query)
        rows = result.fetchall()
        
        # 提取用户名和对应的活动总数
        usernames = []
        counts = []
        for row in rows:
            usernames.append(row.act_username)
            counts.append(int(row.total_count))  # 确保是整数类型
        
        # 设置返回数据
        #returnobj["data"]["xAxis"]["data"] = usernames
        #returnobj["data"]["series"][0]["data"] = counts
        
        # 如果数据长度小于2，返回示例数据
        if len(usernames) < 2:
            returnobj["data"]["xAxis"]["data"] = ["用户1", "用户2", "用户3", "用户4", "用户5"]
            returnobj["data"]["series"][0]["data"] = [84, 53, 28, 15, 11]
        else:
            returnobj["data"]["xAxis"]["data"] = usernames
            returnobj["data"]["series"][0]["data"] = counts

            
    except Exception as exp:
        print('Exception at apis.get_activity_by_person() %s ' % exp)
        traceback.print_exc()
        returnobj["status"] = 1
        returnobj["msg"] = f"查询失败: {str(exp)}"
    
    return returnobj

@router.get("/actlog/activity_by_manager", summary="获取本月按经理分类的浏览量统计数据")
async def get_activity_by_manager(sess: SyncSess):
    """统计本月按act_manager分类的record_count总和排名前10的记录，返回给条形图使用的数据格式"""
    returnobj = {
        "status": 0,
        "msg": "ok",
        "data": {
            "title": {"text": "上月浏览量排名-Manager"},
            "tooltip": {},
            "legend": {"data": ["浏览次数"]},
            "xAxis": {"data": []},
            "yAxis": {},
            "series": [{"name": "浏览次数", "type": "bar", "data": []}]
        }
    }
    try:
        # SQL查询：统计本月按经理分类的活动总数，取前10名
        query = text("""
            SELECT act_manager, SUM(record_count) as total_count
            FROM actlog_daily_stats_user
            WHERE action_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
              AND action_date <= LAST_DAY(CURDATE())
            GROUP BY act_manager
            ORDER BY total_count DESC
            LIMIT 10
        """)
        result = await site.engine.execute(query)
        rows = result.fetchall()
        
        # 提取经理名和对应的活动总数
        managers = []
        counts = []
        for row in rows:
            managers.append(row.act_manager)
            counts.append(int(row.total_count))  # 确保是整数类型
        
        # 如果数据长度小于2，返回示例数据
        if len(managers) < 2:
            returnobj["data"]["xAxis"]["data"] = ["经理1", "经理2", "经理3", "经理4", "经理5"]
            returnobj["data"]["series"][0]["data"] = [94, 63, 48, 35, 21]
        else:
            returnobj["data"]["xAxis"]["data"] = managers
            returnobj["data"]["series"][0]["data"] = counts

            
    except Exception as exp:
        print('Exception at apis.get_activity_by_manager() %s ' % exp)
        traceback.print_exc()
        returnobj["status"] = 1
        returnobj["msg"] = f"查询失败: {str(exp)}"
    
    return returnobj