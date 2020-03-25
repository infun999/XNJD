#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ===========================
# Author   :   infun999
# ===========================

import time
from onlinework.captcha import Captcha
from onlinework.processdata import Parse
from onlinework.processdata import Util

"""功能模块"""

class UserAction:
    def __init__(self, user_instance):
        self.user = user_instance
        self.wlp = self.user.worklist

    def get_user_ccs(self, sheetid):
        course, work = Util.split_id(sheetid)
        resp = self.user.dowork(course, work)
        r = Parse.user_ccs(resp)
        return r if r else {}

    @property
    def get_summary(self):
        # if True:
        a = Parse.finish_state(self.wlp)
        sheetids = Parse.sheetids(self.wlp)
        undo = a[0]
        unfinish = a[1]
        state = a[2]
        return sheetids, undo, unfinish, state

    @property
    def get_sheetids(self):
        return Parse.sheetids(self.wlp)


class SheetsAction:
    pipe = None
    form = None

    @classmethod
    def connect_data_source(cls, pipe_instance, form_instance):
        SheetsAction.pipe = pipe_instance
        SheetsAction.form = form_instance

    def __init__(self, user_instance,):
        if SheetsAction.pipe and SheetsAction.form:
            self.user = user_instance
            self.userid = user_instance.userid
        else:
            raise Exception('使用SheetsAction.set_pipe(pipe_instance)初始化pipe')

    def get_sheet_info(self, sheetid):
        course, work = Util.split_id(sheetid)
        dowork_page = self.user.dowork(course, work)
        return Parse.sheet_info(dowork_page)

    def get_question_ids(self, sheetid):
        course, work = Util.split_id(sheetid)
        dowork_page = self.user.dowork(course, work)
        return Parse.question_ids(dowork_page)

    def get_answers(self, sheetid):
        course, work = Util.split_id(sheetid)
        ans_page = self.user.answer(course, work)
        return Parse.answers(ans_page)

    def create_nullform(self, sheetid):
        course, work = Util.split_id(sheetid)
        base_form = SheetsAction.form.base(self.userid, sheetid)
        ajax_null = SheetsAction.form.submit_null
        base_form.update(ajax_null)
        base_form["qulifyCode"] = Captcha.manual_captcha(self.user, course)   # 验证码
        return base_form

    def create_tempsaveform(self, sheetid):
        """1、可不使用，直接提交最终答案。 2、或处理ans_form为模拟单题保存"""
        base_form = SheetsAction.form.base(self.userid, sheetid)
        ajax_all = SheetsAction.form.submit_null
        base_form.update(ajax_all)
        ans_form = SheetsAction.pipe.out_post_answer(sheetid)
        # 每次增加一个答案
        for k, v in ans_form.items():
            _ = {}
            _[k] = v
            base_form.update(ans_form)
            yield base_form

    def create_submitform(self, sheetid):
        """CAPTCHA API"""
        course = Util.split_id(sheetid)[0]  # 取验证码用参数,非答题时取随机数也可
        base_form = SheetsAction.form.base(self.userid, sheetid)
        ajax_all = SheetsAction.form.submit_all
        ans_form = SheetsAction.pipe.out_post_answer(sheetid)
        base_form.update(ajax_all)
        base_form.update(ans_form)
        base_form["qulifyCode"] = Captcha.manual_captcha(self.user, course)    #  ***********captcha*************
        return base_form

    def ajax_post(self, sheetid, method="submit_all", interval=0):
        """
        method参数为:"save","submit_null","submit_all"
        :param method: 三种请求方式
        :param sheetid:
        :param interval: 模拟save操作时间间隔，可在方法外设置
        :return:
        """
        form_data = {}
        if method == "save":
            form_data = self.create_tempsaveform(sheetid)
            if interval > 0:
                time.sleep(interval)
        elif method == "submit_null":
            form_data = self.create_nullform(sheetid)
        elif method == "submit_all":
            form_data = self.create_submitform(sheetid)
        self.user.ajax_post(form_data)







