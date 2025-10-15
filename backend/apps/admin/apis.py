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

@router.get("/actlog/monthly_activities", summary="获取近12个月的每月活动统计数据")
async def get_monthly_activities(sess: SyncSess):
    """统计本月起往前推12个月，每月记录总数，用于柱状图显示"""
    returnobj = {
        "status": 0,
        "msg": "ok",
        "data": {
            "month": [],
            "bar": []
        }
    }
    try:
        # 统计本月起往前推12个月每月的总浏览量
        query = text("""
            SELECT DATE_FORMAT(action_date, '%Y-%m') as month, SUM(record_count) as total_count
            FROM actlog_daily_stats_user
            WHERE action_date >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 11 MONTH), '%Y-%m-01')
              AND action_date <= LAST_DAY(CURDATE())
            GROUP BY month
            ORDER BY month ASC
        """)
        result = await site.engine.execute(query)
        rows = result.fetchall()
        months = []
        counts = []
        for row in rows:
            months.append(row.month)
            counts.append(int(row.total_count))
        # 如果数据不足1个月，返回示例数据
        if len(months) < 1:
            returnobj["data"]["month"] = ["2024-10", "2024-11", "2024-12", "2025-01", "2025-02", "2025-03"]
            returnobj["data"]["bar"] = [99, 122, 88, 110, 92, 101]
        else:
            returnobj["data"]["month"] = months
            returnobj["data"]["bar"] = counts
    except Exception as exp:
        print('Exception at apis.get_monthly_activities() %s ' % exp)
        traceback.print_exc()
        returnobj["status"] = 1
        returnobj["msg"] = f"查询失败: {str(exp)}"
    return returnobj

# from fastapi_user_authuser_auth.globals.deps import CurrentUser
#
# @router.get("/get_user", summary="获取当前登录用户")
# async def get_user(user: CurrentUser):
#     return user


@router.get("/actlog/activity_by_manager", summary="获取当月按经理分类的浏览量统计数据")
async def get_activity_by_manager(sess: SyncSess):
    """统计当月按act_manager分类的record_count总和排名前10的记录，返回给条形图使用的数据格式"""
    returnobj = {
        "status": 0,
        "msg": "ok",
        "data": {
            "title": {"text": "当月浏览量排名-Manager"},
            "tooltip": {},
            "legend": {"data": ["浏览次数"]},
            "xAxis": {"data": []},
            "yAxis": {},
            "series": [{"name": "浏览次数", "type": "bar", "data": []}]
        }
    }
    try:
        # SQL查询：统计当月按经理分类的活动总数，取前10名
        query = text("""
            SELECT act_manager, SUM(record_count) as total_count
            FROM actlog_daily_stats_user
            WHERE action_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
              AND action_date <= CURDATE()
            GROUP BY act_manager
            ORDER BY total_count DESC
            LIMIT 50
        """)
        result = await site.engine.execute(query)
        rows = result.fetchall()
        
        # 提取经理名和对应的活动总数
        managers = []
        counts = []
        for row in rows:
            managers.append(row.act_manager)
            counts.append(int(row.total_count))  # 确保是整数类型
        
        # 检查数据是否为空或长度不足，如果是则返回示例数据
        if not rows or len(managers) < 1:
            log.info(f"get_activity_by_manager_current_month(): 查询结果为空，返回示例数据")
            returnobj["data"]["xAxis"]["data"] = ["经理1", "经理2", "经理3", "经理4", "经理5"]
            returnobj["data"]["series"][0]["data"] = [94, 63, 48, 35, 21]
        else:
            log.debug(f"get_activity_by_manager_current_month(): 查询到{len(managers)}条数据")
            returnobj["data"]["xAxis"]["data"] = managers
            returnobj["data"]["series"][0]["data"] = counts

            
    except Exception as exp:
        print('Exception at apis.get_activity_by_manager() %s ' % exp)
        traceback.print_exc()
        returnobj["status"] = 1
        returnobj["msg"] = f"查询失败: {str(exp)}"
    
    return returnobj

@router.get("/actlog/contribution_by_manager", summary="获取当月按经理分类的贡献度统计数据")
async def get_contribution_by_manager(sess: SyncSess):
    """统计当月按act_manager分类的创建/更新操作记录总和排名前10的记录，返回给条形图使用的数据格式"""
    returnobj = {
        "status": 0,
        "msg": "ok",
        "data": {
            "title": {"text": "当月贡献度排名-Manager"},
            "tooltip": {},
            "legend": {"data": ["贡献次数"]},
            "xAxis": {"data": []},
            "yAxis": {},
            "series": [{"name": "贡献次数", "type": "bar", "data": []}]
        }
    }
    try:
        # SQL查询：统计当月按经理分类的创建/更新操作总数，取前10名
        query = text("""
            SELECT act_manager, SUM(record_count) as total_count
            FROM actlog_daily_stats_user
            WHERE action_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
              AND action_date <= CURDATE()
              AND (action_type LIKE 'create%' OR action_type LIKE 'update%')
            GROUP BY act_manager
            ORDER BY total_count DESC
            LIMIT 50
        """)
        result = await site.engine.execute(query)
        rows = result.fetchall()
        
        # 提取经理名和对应的贡献总数
        managers = []
        counts = []
        for row in rows:
            managers.append(row.act_manager)
            counts.append(int(row.total_count))  # 确保是整数类型
        
        # 检查数据是否为空或长度不足，如果是则返回示例数据
        if not rows or len(managers) < 1:
            log.info(f"get_contribution_by_manager_current_month(): 查询结果为空，返回示例数据")
            returnobj["data"]["xAxis"]["data"] = ["经理1", "经理2", "经理3", "经理4", "经理5"]
            returnobj["data"]["series"][0]["data"] = [74, 53, 38, 25, 11]
        else:
            log.debug(f"get_contribution_by_manager_current_month(): 查询到{len(managers)}条数据")
            returnobj["data"]["xAxis"]["data"] = managers
            returnobj["data"]["series"][0]["data"] = counts

            
    except Exception as exp:
        print('Exception at apis.get_contribution_by_manager() %s ' % exp)
        traceback.print_exc()
        returnobj["status"] = 1
        returnobj["msg"] = f"查询失败: {str(exp)}"
    
    return returnobj

@router.get("/actlog/activity_total", summary="获取所有活动记录总数")
async def get_activity_total(sess: SyncSess):
    """统计所有record_count的总和，返回总记录数"""
    returnobj = {
        "status": 0,
        "msg": "ok",
        "data": {
            "total_count": 0
        }
    }
    try:
        # SQL查询：统计所有record_count的总和
        query = text("""
            SELECT SUM(record_count) as total_count
            FROM actlog_daily_stats_user
        """)
        result = await site.engine.execute(query)
        row = result.fetchone()
        
        # 提取总记录数
        total_count = int(row.total_count) if row.total_count else 0
        returnobj["data"]["total_count"] = total_count
        
        # 如果没有数据，返回一个合理的默认值
        if total_count == 0:
            returnobj["data"]["total_count"] = 1000  # 设置一个默认值
        
    except Exception as exp:
        print('Exception at apis.get_activity_total() %s ' % exp)
        traceback.print_exc()
        returnobj["status"] = 1
        returnobj["msg"] = f"查询失败: {str(exp)}"
    
    return returnobj

# 以下是新增的四个接口：当月（本月1日到今天）、上自然月的浏览量和贡献度统计

@router.get("/actlog/activity_by_manager_current_month", summary="获取当月（本月1日到今天）按经理分类的浏览量统计数据（纯数据）")
async def get_activity_by_manager_current_month(sess: SyncSess):
    """统计当月（本月1日到今天）按act_manager分类的record_count总和排名前10的记录，返回纯数据 labels/values"""
    returnobj = {
        "status": 0,
        "msg": "ok",
        "data": {"labels": [], "values": []}
    }
    try:
        # SQL查询：统计当月（本月1日到今天）按经理分类的活动总数，取前10名
        query = text("""
            SELECT act_manager, SUM(record_count) as total_count
            FROM actlog_daily_stats_user
            WHERE action_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
              AND action_date <= CURDATE()
            GROUP BY act_manager
            ORDER BY total_count DESC
            LIMIT 50
        """)
        result = await site.engine.execute(query)
        rows = result.fetchall()
        log.debug(f"get_activity_by_manager_current_month() rows: {rows}")
        
        # 提取经理名和对应的活动总数
        managers = []
        counts = []
        for row in rows:
            managers.append(row.act_manager)
            counts.append(int(row.total_count))  # 确保是整数类型
        
        # 检查数据是否为空或长度不足，如果是则返回示例数据
        if not rows or len(managers) < 1:
            log.info(f"get_activity_by_manager_current_month(): 查询结果为空，返回示例数据")
            returnobj["data"]["labels"] = ["经理1", "经理2", "经理3", "经理4", "经理5"]
            returnobj["data"]["values"] = [94, 63, 48, 35, 21]
        else:
            log.debug(f"get_activity_by_manager_current_month(): 查询到{len(managers)}条数据")
            returnobj["data"]["labels"] = managers
            returnobj["data"]["values"] = counts

            
    except Exception as exp:
        print('Exception at apis.get_activity_by_manager_current_month() %s ' % exp)
        traceback.print_exc()
        returnobj["status"] = 1
        returnobj["msg"] = f"查询失败: {str(exp)}"
    
    return returnobj

@router.get("/actlog/activity_by_manager_last_month", summary="获取上自然月按经理分类的浏览量统计数据（纯数据）")
async def get_activity_by_manager_last_month(sess: SyncSess):
    """统计上自然月按act_manager分类的record_count总和排名前10的记录，返回纯数据 labels/values"""
    returnobj = {
        "status": 0,
        "msg": "ok",
        "data": {"labels": [], "values": []}
    }
    try:
        # SQL查询：统计上自然月按经理分类的活动总数，取前10名
        query = text("""
            SELECT act_manager, SUM(record_count) as total_count
            FROM actlog_daily_stats_user
            WHERE action_date >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
              AND action_date <= LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
            GROUP BY act_manager
            ORDER BY total_count DESC
            LIMIT 50
        """)
        result = await site.engine.execute(query)
        rows = result.fetchall()
        log.debug(f"get_activity_by_manager_last_month() rows: {rows}")
        
        # 提取经理名和对应的活动总数
        managers = []
        counts = []
        for row in rows:
            managers.append(row.act_manager)
            counts.append(int(row.total_count))  # 确保是整数类型
        
        # 检查数据是否为空或长度不足，如果是则返回示例数据
        if not rows or len(managers) < 1:
            log.info(f"get_activity_by_manager_last_month(): 查询结果为空，返回示例数据")
            returnobj["data"]["labels"] = ["经理1", "经理2", "经理3", "经理4", "经理5"]
            returnobj["data"]["values"] = [94, 63, 48, 35, 21]
        else:
            log.debug(f"get_activity_by_manager_last_month(): 查询到{len(managers)}条数据")
            returnobj["data"]["labels"] = managers
            returnobj["data"]["values"] = counts

            
    except Exception as exp:
        print('Exception at apis.get_activity_by_manager_last_month() %s ' % exp)
        traceback.print_exc()
        returnobj["status"] = 1
        returnobj["msg"] = f"查询失败: {str(exp)}"
    
    return returnobj

@router.get("/actlog/contribution_by_manager_current_month", summary="获取当月（本月1日到今天）按经理分类的贡献度统计数据（纯数据）")
async def get_contribution_by_manager_current_month(sess: SyncSess):
    """统计当月（本月1日到今天）按act_manager分类的创建/更新操作记录总和排名前10的记录，返回纯数据 labels/values"""
    returnobj = {
        "status": 0,
        "msg": "ok",
        "data": {"labels": [], "values": []}
    }
    try:
        # SQL查询：统计当月（本月1日到今天）按经理分类的创建/更新操作总数，取前10名
        query = text("""
            SELECT act_manager, SUM(record_count) as total_count
            FROM actlog_daily_stats_user
            WHERE action_date >= DATE_FORMAT(CURDATE(), '%Y-%m-01')
              AND action_date <= CURDATE()
              AND (action_type LIKE 'create%' OR action_type LIKE 'update%')
            GROUP BY act_manager
            ORDER BY total_count DESC
            LIMIT 50
        """)
        result = await site.engine.execute(query)
        rows = result.fetchall()
        log.debug(f"get_contribution_by_manager_current_month() rows: {rows}")
        
        # 提取经理名和对应的贡献总数
        managers = []
        counts = []
        for row in rows:
            managers.append(row.act_manager)
            counts.append(int(row.total_count))  # 确保是整数类型
        
        # 检查数据是否为空或长度不足，如果是则返回示例数据
        if not rows or len(managers) < 1:
            log.info(f"get_contribution_by_manager_current_month(): 查询结果为空，返回示例数据")
            returnobj["data"]["labels"] = ["Team1", "Team2", "Team3", "Team4", "Team5"]
            returnobj["data"]["values"] = [0, 0, 0, 0, 0]
        else:
            log.debug(f"get_contribution_by_manager_current_month(): 查询到{len(managers)}条数据")
            returnobj["data"]["labels"] = managers
            returnobj["data"]["values"] = counts

            
    except Exception as exp:
        print('Exception at apis.get_contribution_by_manager_current_month() %s ' % exp)
        traceback.print_exc()
        returnobj["status"] = 1
        returnobj["msg"] = f"查询失败: {str(exp)}"
    
    return returnobj

@router.get("/actlog/contribution_by_manager_last_month", summary="获取上自然月按经理分类的贡献度统计数据（纯数据）")
async def get_contribution_by_manager_last_month(sess: SyncSess):
    """统计上自然月按act_manager分类的创建/更新操作记录总和排名前10的记录，返回纯数据 labels/values"""
    returnobj = {
        "status": 0,
        "msg": "ok",
        "data": {"labels": [], "values": []}
    }
    try:
        # SQL查询：统计上自然月按经理分类的创建/更新操作总数，取前10名
        query = text("""
            SELECT act_manager, SUM(record_count) as total_count
            FROM actlog_daily_stats_user
            WHERE action_date >= DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL 1 MONTH), '%Y-%m-01')
              AND action_date <= LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))
              AND (action_type LIKE 'create%' OR action_type LIKE 'update%')
            GROUP BY act_manager
            ORDER BY total_count DESC
            LIMIT 50
        """)
        result = await site.engine.execute(query)
        rows = result.fetchall()
        log.debug(f"get_contribution_by_manager_last_month() rows: {rows}")
        
        # 提取经理名和对应的贡献总数
        managers = []
        counts = []
        for row in rows:
            managers.append(row.act_manager)
            counts.append(int(row.total_count))  # 确保是整数类型
        
        # 检查数据是否为空或长度不足，如果是则返回示例数据
        if not rows or len(managers) < 1:
            log.info(f"get_contribution_by_manager_last_month(): 查询结果为空，返回示例数据")
            returnobj["data"]["labels"] = ["经理1", "经理2", "经理3", "经理4", "经理5"]
            returnobj["data"]["values"] = [74, 53, 38, 25, 11]
        else:
            log.debug(f"get_contribution_by_manager_last_month(): 查询到{len(managers)}条数据")
            returnobj["data"]["labels"] = managers
            returnobj["data"]["values"] = counts
            
    except Exception as exp:
        print('Exception at apis.get_contribution_by_manager_last_month() %s ' % exp)
        traceback.print_exc()
        returnobj["status"] = 1
        returnobj["msg"] = f"查询失败: {str(exp)}"
    
    return returnobj
