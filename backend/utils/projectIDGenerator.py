#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: ibmzhangjun@139.com
@file: projectIDGenerator.py
@time: 2025/7/21 上午9:20
@desc: 项目ID生成器，采用单例模式，确保每年从0开始计数
"""
import os
import shelve
from datetime import datetime
from threading import Lock
from utils.log import log as log

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE_DIR = os.path.join(BASE_DIR, 'projID')

class ProjectIDGenerator:
    """项目ID生成器类，采用单例模式"""
    _instance = None
    _lock = Lock()

    def __new__(cls, db_file=CACHE_DIR):
        """创建单例实例"""
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                try:
                    cls._instance._init_instance(db_file)
                except Exception as e:
                    log.error(f"初始化ProjectIDGenerator失败: {str(e)}")
                    # 确保实例有基本属性，避免后续调用报错
                    cls._instance.current_number = 0
                    cls._instance.current_year = datetime.now().strftime("%y")
            return cls._instance

    def _init_instance(self, db_file):
        """初始化实例，验证路径并加载当前编号"""
        # 加强路径验证，确保目录存在
        self.db_file = db_file
        db_dir = os.path.dirname(db_file) if os.path.dirname(db_file) else '.'
        
        # 确保目录存在
        try:
            if not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
                log.info(f"创建项目ID缓存目录: {db_dir}")
        except Exception as e:
            log.error(f"创建缓存目录失败: {str(e)}")
            # 即使目录创建失败，也继续执行，让shelve尝试使用默认路径
        
        self.current_year = datetime.now().strftime("%y")
        
        try:
            self.current_number = self._get_current_number()
        except Exception as e:
            log.error(f"获取当前编号失败: {str(e)}")
            self.current_number = 0

    def _get_current_number(self):
        """从数据库获取当前编号，如果年份变更则重置为0"""
        try:
            with shelve.open(self.db_file) as db:
                saved_year = db.get('year')
                current_number = db.get('number', 0)

                if saved_year != self.current_year:
                    current_number = 0
                    db['year'] = self.current_year
                    db['number'] = current_number
                return current_number
        except Exception as e:
            log.error(f"读取数据库失败: {str(e)}")
            return 0

    def _update_number(self):
        """更新编号并保存到数据库"""
        try:
            self.current_number += 1
            with shelve.open(self.db_file) as db:
                db['number'] = self.current_number
        except Exception as e:
            log.error(f"更新编号失败: {str(e)}")
            # 即使保存失败，也继续增加内存中的编号

    def generate_id(self):
        """生成一个新的项目编号
        
        Returns:
            str: 项目编号，格式为"年份后两位+月份+日期+4位流水号"
        """
        try:
            self._update_number()
            return f"{datetime.now().strftime('%y%m%d')}{self.current_number:04d}"
        except Exception as e:
            log.error(f"生成项目ID失败: {str(e)}")
            # 即使失败也返回一个基于时间的ID，确保程序能继续运行
            timestamp = datetime.now().strftime('%y%m%d%H%M%S')
            return f"{timestamp}ERR"


# 使用示例
if __name__ == "__main__":
    generator = ProjectIDGenerator()
    log.debug(generator.generate_id())  # 输出类似 "2307210001" 的编号