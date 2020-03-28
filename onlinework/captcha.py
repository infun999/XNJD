#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ===========================
# Author   :   infun999
# ===========================

import hashlib
import random
import time
from onlinework import core
from onlinework import web
from onlinework import database
from onlinework.processdata import Pipe


class Captcha:
    @staticmethod
    def capt_src(course, user_instance,):
        """在web中也有，此处保证模块独立的完整性"""
        """
        1、 验证码以user_session为finger_print，最近唯一有效
        2、 验证码是在服务器端验证，由302跳转情况，推测是直接保存最新值形式
        3、 验证码的url中，courseId在提交作业时使用正确Id，刷取训练验证码时可随机
        """
        return user_instance.captcha(course)

    @staticmethod
    def capt_hash(capt_str):
        md5 = hashlib.md5()
        md5.update(capt_str.encode('utf-8'))
        return md5.hexdigest()


    @staticmethod
    def save_bytes_to_img(content, loca=''):
        """存储，供人工读验证码"""
        with open('{}yzm.jpg'.format(loca), 'wb') as yzm:
            yzm.write(content)

    @staticmethod
    def to_str(bytes_src):
        return str(bytes_src)


class MCaptcha:
    @staticmethod
    def manual_captcha(course, user_instance):
        bytes_src = Captcha.capt_src(course, user_instance)
        Captcha.save_bytes_to_img(bytes_src)
        print("根目录查看验证码图片'yzm.jpg'")
        return input("输入验证码:")


class ACaptcha:



    def capt_code(self, hash_cap):
        return






def captcha_api(course, user_instance):
    """API"""
    """待处理容错"""
    pipe = core.init_global_instance()[1]
    bytes_src = Captcha.capt_src(course, user_instance)
    capt_str = Captcha.to_str(bytes_src)
    capt_hash = Captcha.capt_hash(capt_str)
    # 数据库查询比较
    capt_code = pipe.out_capt_code(capt_hash)
    capt_str_indb = pipe.out_capt_str(capt_hash)
    if capt_code and capt_str == capt_str_indb:
        return capt_code
    # 2次hash值再查找
    capt_hash_t = Captcha.capt_hash(capt_hash)
    capt_code = pipe.out_capt_code(capt_hash=capt_hash_t)
    capt_str_indb = pipe.out_capt_str(capt_hash=capt_hash_t)
    if capt_code and capt_str == capt_str_indb:
        return capt_code
    # 人工处理验证码
    else:
        capt_code = MCaptcha.manual_captcha(course, user_instance)
        pipe.init_db_if_not_exist("capt_hash", capt_hash)
        pipe.in_capt_code(capt_hash, capt_code)
        pipe.in_capt_str(capt_hash, capt_str)
        return capt_code, capt_hash




# 单刷验证码训练
if __name__ == "__main__":
    glo_inst = core.init_global_instance()
    db, pipe, form = glo_inst
    while True:
        # 创建用户基本对象
        userid = input("******单刷验证码模式*****\n\n输入用户学号,或E/e退出").__str__()
        if userid.lower() == 'e':
            exit(0)
        f = core.full_user(userid, global_instance=glo_inst)
        if not f:
            continue
        db, pipe, form = f[0]
        userid, user_session, user, ua, sa = f[1]
        sheetids, undo, unfinish, state, nodo = f[2]
        while True:
            cap_cont = user.captcha(sheetids[random.randint(len(sheetids))])
            # hash_c = ACaptcha.capt_hash(cap_cont)
            # with open('./img/{}.jpg'.format(hash_c), 'wb') as f:
            #     f.write(hash_c)