#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: ibmzhangjun@139.com
@file: actlogtool.py
@time: 2025/9/23 下午5:30
@desc: ActLog工具，用于向ActLog表添加操作记录
"""

from datetime import datetime
from zoneinfo import ZoneInfo

from starlette.requests import Request

from apps.admin.models.actlog import ActLog
from core.globals import async_db
from utils.userselect import UserSelect
from utils.log import log as log


class ActLogTool:
    """操作日志工具类，用于向ActLog表添加操作记录"""

    @staticmethod
    async def add_act_log_by_request(request: Request, act_type: str):
        """
        通过请求对象添加操作日志
        
        Args:
            request: FastAPI请求对象
            act_type: 操作类型
            
        Returns:
            ActLog: 创建的操作日志对象
        """
        try:
            # 获取当前用户信息
            user = await request.auth.get_current_user(request)
            username = user.username
            
            # 创建操作日志
            return await ActLogTool.add_act_log(username, act_type)
        except Exception as e:
            log.error(f"添加操作日志失败: {str(e)}")
            return None

    @staticmethod
    async def add_act_log(username: str, act_type: str):
        """
        添加操作日志
        
        Args:
            username: 操作用户名
            act_type: 操作类型
            
        Returns:
            ActLog: 创建的操作日志对象
        """
        try:
            # 创建UserSelect实例
            user_select = UserSelect()
            
            # 获取用户ID
            # 注意：这里需要根据实际情况从username获取user_id
            # 假设username和id是相同的，实际应用中可能需要调整
            user_id = username
            
            # 获取act_name、act_org、act_manager
            act_name = user_select.get_nickname(user_id)
            act_org = user_select.get_org(user_id)
            act_manager = user_select.get_manager(user_id)
            
            # 获取当前上海时区时间
            shanghai_time = datetime.now().astimezone(ZoneInfo("Asia/Shanghai"))
            
            # 创建ActLog对象
            act_log = ActLog(
                act_type=act_type,
                act_username=username,
                act_name=act_name,
                act_org=act_org,
                act_manager=act_manager,
                act_time=shanghai_time
            )
            
            # 添加到数据库
            async with async_db():
                async_db.add(act_log)
                await async_db.async_flush()
            
            log.info(f"添加操作日志成功: {username} - {act_type}")
            return act_log
        except Exception as e:
            log.error(f"添加操作日志失败: {str(e)}")
            return None

    @staticmethod
    async def add_act_log_with_details(username: str, act_type: str, details: dict = None):
        """
        添加带详细信息的操作日志
        
        Args:
            username: 操作用户名
            act_type: 操作类型
            details: 详细信息
            
        Returns:
            ActLog: 创建的操作日志对象
        """
        try:
            # 创建操作日志
            act_log = await ActLogTool.add_act_log(username, act_type)
            
            # 如果需要保存详细信息，可以在这里扩展
            # 注意：当前ActLog模型没有详细信息字段，实际应用中可能需要调整
            if details:
                log.info(f"操作日志详细信息: {details}")
            
            return act_log
        except Exception as e:
            log.error(f"添加带详细信息的操作日志失败: {str(e)}")
            return None


# 提供便捷的函数调用方式
async def add_act_log(username: str, act_type: str):
    """便捷函数：添加操作日志"""
    return await ActLogTool.add_act_log(username, act_type)


async def add_act_log_by_request(request: Request, act_type: str):
    """便捷函数：通过请求对象添加操作日志"""
    return await ActLogTool.add_act_log_by_request(request, act_type)


async def add_act_log_with_details(username: str, act_type: str, details: dict = None):
    """便捷函数：添加带详细信息的操作日志"""
    return await ActLogTool.add_act_log_with_details(username, act_type, details)


if __name__ == '__main__':
    import asyncio
    
    # 测试添加操作日志
    async def test_add_act_log():
        result = await add_act_log("admin", "测试操作")
        print(f"测试结果: {result}")
    
    asyncio.run(test_add_act_log())