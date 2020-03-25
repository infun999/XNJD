#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ===========================
# Author   :   infun999
# ===========================

import hashlib
from onlinework import web
from onlinework import database
from onlinework.processdata import Pipe


class Captcha:
    @staticmethod
    def save_to_img(content):
        """存储，供人工读验证码"""
        with open('yzm.jpg', 'wb') as f:
            f.write(content)

    @staticmethod
    def capt_hash(capt_con):
        capt_con = str(capt_con)
        md5 = hashlib.md5()
        md5.update(capt_con.encode('utf-8'))
        return md5.hexdigest()

    @staticmethod
    def capt_con(user_instance, course: str):
        """在web中也有，此处保证模块独立的完整性"""
        """
        1、 验证码以user_session为finger_print，最近唯一有效
        2、 验证码是在服务器端验证，由302跳转情况，推测是直接保存最新值形式
        3、 验证码的url中，courseId在提交作业时使用正确Id，刷取训练验证码时可随机
        """
        return user_instance.captcha(course)

    def capt_str(self, con_c):
        return str(con_c)

    def capt_code(self, hash_c):
        return

    @staticmethod
    def manual_captcha(user_instance, course):
        con = Captcha.capt_con(user_instance, course)
        Captcha.save_to_img(con)
        print("根目录查看验证码图片'yzm.jpg'")
        return input("输入验证码:")










# 单刷验证码训练
if __name__ == "__main__":
    db = database.XNJD()
    pipe = Pipe(db)

    userid = input("输入用户学号").__str__()  # tyf?
    pw = pipe.out_pw(userid)
    """处理密码错误问题"""
    # 实例用户会话session
    user_login = web.login(userid, pw)
    user = web.Page(user=user_login)

