#!/usr/bin/python3
# -*- coding:utf-8 -*-
"""
@author: ibmzhangjun@139.com
@file: projectIDGenerator.py
@time: 2025/7/21 上午9:20
@desc: 
"""
import shelve
from datetime import datetime
from threading import Lock
from utils.log import log as log


class ProjectIDGenerator:
    _instance = None
    _lock = Lock()

    def __new__(cls, db_file="projid"):
        with cls._lock:
            if not cls._instance:
                cls._instance = super().__new__(cls)
                cls._instance._init_instance(db_file)
            return cls._instance

    def _init_instance(self, db_file):
        self.db_file = db_file
        self.current_year = datetime.now().strftime("%y")
        self.current_number = self._get_current_number()

    def _get_current_number(self):
        with shelve.open(self.db_file) as db:
            saved_year = db.get('year')
            current_number = db.get('number', 0)

            if saved_year != self.current_year:
                current_number = 0
                db['year'] = self.current_year
                db['number'] = current_number
            return current_number

    def _update_number(self):
        self.current_number += 1
        with shelve.open(self.db_file) as db:
            db['number'] = self.current_number

    def generate_id(self):
        """生成一个新的项目编号"""
        self._update_number()
        return f"{datetime.now().strftime('%y%m%d')}{self.current_number:04d}"


# 使用示例
if __name__ == "__main__":
    generator = ProjectIDGenerator()
    log.debug(generator.generate_id())  # 输出类似 "2307210001" 的编号