#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ===========================
# Author   :   infun999
# ===========================


import pymongo


class XNJD:
    """实例数据库底层方法"""
    __instance = None
    __init_flag = True

    def __new__(cls, *args, **kwargs):
        if cls.__instance == None:
            cls.__instance =object.__new__(cls)
        return cls.__instance

    def __init__(self, ):
        # 初始化服务端
        self.client = pymongo.MongoClient("localhost", 27017)
        # 初始化数据库
        self.xnjd = self.client.xnjd
        XNJD.__init_flag = False

    def init_row(self, table_name, loc_key, loc_value):
        """以loc_value关键值的初始row"""
        set_data = {str(loc_key): loc_value}
        return self.xnjd[table_name].insert_one(set_data).inserted_id

    def get_row(self, table_name: str, loc_key: str, loc_value: str):
        """返回整行数据:dict"""
        try:
            r = self.xnjd[table_name].find_one({loc_key: loc_value})
        except TypeError:
            r = None
        except KeyError:
            r = None
        return r

    def get_item(self, table_name: str, loc_key: str, loc_value: str, search_key: str):
        """返回指定search_key对应的数据: str"""
        try:
            r = self.xnjd[table_name].find_one({loc_key: loc_value})[search_key]
        except TypeError:   # 查无search_key
            r = None
        except KeyError:    # 查无loc_key
            r = None
        return r

    def del_row(self, table_name: str, loc_key: str, loc_value: str):
        """删除整行数据"""
        row = self.get_row(table_name, loc_key, loc_value)
        if row:
            self.xnjd[table_name].delete_one({loc_key: loc_value})

    def del_item(self, table_name, loc_key, loc_value, del_key: str):
        """删除指定字段数据（伪删除--更新数据为''）  """
        row = self.get_row(table_name, loc_key, loc_value)
        if row:
            self.set_item(table_name, loc_key, loc_value, del_key, '')

    def set_row(self, table_name, loc_key, loc_value, set_data: dict):
        """写入多条行数据 :return: OBJ_id（成功）  或  None（失败/存在定位关键值或写入数据格式错误）"""
        row = self.get_row(table_name, loc_key, loc_value)
        if row and type(set_data) != 'dict':
            return None
        return self.xnjd[table_name].insert_one(set_data).inserted_id

    def set_item(self, table_name, loc_key, loc_value, set_key: str, set_value: str):
        """设置指定字段数据"""
        row = self.get_row(table_name, loc_key, loc_value)
        if row:
            location = {loc_key: loc_value}
            row[set_key] = set_value  # 字段 设置新键值
            self.xnjd[table_name].update_one(location, {'$set': row})


