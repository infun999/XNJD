#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ===========================
# Author   :   infun999
# ===========================

import time
from onlinework.captcha import captcha_api
from onlinework.processdata import Parse
from onlinework import web
from onlinework import database
from onlinework.processdata import Form
from onlinework.processdata import Pipe
from onlinework.processdata import Util

"""
核心功能模块
UserAction:账号信息数据操作类
SheetAction:做题功能操作类
实现逻辑
"""



"""账号信息数据操作类"""
class UserAction:
    def __init__(self, user_instance):
        self.user = user_instance
        self.wlp = self.user.worklist

    def get_user_ccs(self, sheetid):
        resp = self.user.dowork(sheetid)
        r = Parse.user_ccs(resp)
        return r if r else {}

    @property
    def get_summary(self):
        a = Parse.finish_state(self.wlp)
        sheetids = Parse.sheetids(self.wlp)
        undo = a[0]
        unfinish = a[1]
        state = a[2]
        nodo = a[3]
        return sheetids, undo, unfinish, state, nodo

    @property
    def get_sheetids(self):
        return Parse.sheetids(self.wlp)


"""做题功能操作类"""
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
        dowork_page = self.user.dowork(sheetid)
        return Parse.sheet_info(dowork_page)

    def get_question_ids(self, sheetid):
        dowork_page = self.user.dowork(sheetid)
        return Parse.question_ids(dowork_page)

    def get_answers(self, sheetid):
        ans_page = self.user.answer(sheetid)
        return Parse.answers(ans_page)

    def create_nullform(self, sheetid):
        """空答案请求的完整form;...CAPTCHA API IN """
        course, work = Util.split_id(sheetid)
        base_form = SheetsAction.form.base(self.userid, sheetid)
        ajax_null = SheetsAction.form.submit_null
        base_form.update(ajax_null)
        capt_code, capt_hash = captcha_api(course, user_instance=self.user)
        base_form["qulifyCode"] = capt_code
        return base_form, capt_hash

    def create_tempsaveform(self, sheetid):
        """每次增加一个答案的模拟临时保存的generator"""
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
        """最终提交作业的完整form...CAPTCHA API IN"""
        course = Util.split_id(sheetid)[0]  # 取验证码用参数,非答题时取随机数也可
        base_form = SheetsAction.form.base(self.userid, sheetid)
        ajax_all = SheetsAction.form.submit_all
        ans_form = SheetsAction.pipe.out_post_answer(sheetid)
        base_form.update(ajax_all)
        base_form.update(ans_form)
        capt_code, capt_hash = captcha_api(course, user_instance=self.user)
        base_form["qulifyCode"] = capt_code
        return base_form, capt_hash

    def ajax_post(self, sheetid, method="submit_all", interval=0):
        """method参数为:"save","submit_null","submit_all",选择请求提交方法
        :param method: 三种请求方式
        :param sheetid:
        :param interval: 模拟save操作时间间隔，可在方法外设置sleep
        :return:
        """
        form_data = {}
        capt_hash = ''
        if method == "save":
            form_data = self.create_tempsaveform(sheetid)
            if interval > 0:
                time.sleep(interval)
        elif method == "submit_null":
            form_data, capt_hash = self.create_nullform(sheetid)
        elif method == "submit_all":
            form_data, capt_hash = self.create_submitform(sheetid)
        resp = self.user.ajax_post(form_data).text
        self._handle_if_wrong_submit(method=method, sheetid=sheetid, capt_hash=capt_hash, ajax_resp=resp)

    def _handle_if_wrong_submit(self, method, sheetid, capt_hash, ajax_resp):
        """有访问逻辑顺序要求，主要用于删除验证码，wrong_submit也可能是人工构建question_ids造成"""
        if 'codeError' in ajax_resp:
            print('{}验证码错误'.format(sheetid))
            self.pipe.del_capt_code(capt_hash)
        elif method == 'submit_all':
            s = self.user.get_summary
            if sheetid in s[1] or sheetid in s[2]:
                print('作业号{}未成功提交'.format(sheetid))
                if len(self.pipe.out_question_ids(sheetid)) != len(self.pipe.out_answers(sheetid)):
                    print('作业号{},问题数量与答案数量不等，检查数据库'.format(sheetid))





"""实现逻辑"""


def init_global_instance():
    """初始化全局实例，return: db, pipe, form"""
    db = database.XNJD()
    pipe = Pipe(db)
    form = Form(db, pipe)
    return db, pipe, form


def get_user_summary(user_obj):
    """
    :param user_obj: user_login[0], user_login[1], user, ua, sa
    :return: [0]学期作业编号sheetids:lsit
             [1]未做过的作业编号undo:list
             [2]未做完的作业编号unfinish:list,
             [3]以上汇总概览state:list
             [4]全主观题编号nodo:list
    """
    ua = user_obj[3]
    return ua.get_summary


def gen_user_obj(userid, global_instance):
    """user基本对象之间的生成逻辑
    :param userid:
    :param global_instances: 全局实例类依次db, pipe, form
    :return: [0]userid  用户id：str
            [1]user_session  登录后的session:obj
            [2]user  带session访问页面实例类:insctance
            [3]ua  用户页面操作:instance
            [4]sa  作业页面操作:instance
    """
    db, pipe, form = global_instance
    pw = pipe.out_pw(userid=userid)
    user_login = web.login(userid=userid, passw=pw)
    if not user_login:
        return None
    userid = user_login[0]
    user_session = user_login[1]
    # 带合法身份获取网页信息的实例
    user = web.Page(user=user_login)
    # 操作用户基本功能的实例
    ua = UserAction(user_instance=user)
    # 操作作业的实例
    SheetsAction.connect_data_source(pipe_instance=pipe, form_instance=form)
    sa = SheetsAction(user_instance=user)
    return userid, user_session, user, ua, sa


def check_user_ccs(global_instance, user_obj, user_summery):
    """ 判断是否为可完成用户的逻辑
        本项目中,user_ccs参数是必要参数，每个作业均可获取(提交任意正确答案后则不可获取)
        所以以是否能获取此参数作为最终判断
    """
    pipe = global_instance[1]
    userid = user_obj[0]
    ua = user_obj[3]
    undo_list = user_summery[1]
    unfinish = user_summery[2]
    nodo = user_summery[4]
    user_ccs = pipe.out_user_ccs(userid=userid)
    if user_ccs:
        return True
    elif undo_list or unfinish or nodo:
        sheetid = undo_list.pop() if undo_list else unfinish.pop() if unfinish else nodo.pop()
        user_ccs = ua.get_user_ccs(sheetid=sheetid)
        pipe.in_user_ccs(userid=userid, user_ccs=user_ccs)
        return True
    else:
        return False


def manual_create_question_list(sheetid, user_instance, sheetaction_instance, pipe_instance):
    """人工辅助创建question_ids的逻辑"""
    sheet_info = pipe_instance.out_sheet_info(sheetid)
    if not sheet_info:
        sheet_info = sheetaction_instance.get_sheet_info(sheetid)
        pipe_instance.in_sheet_info(sheetid, sheet_info)
    all_ex = sheet_info["all_ex"]
    all_type = sheet_info["all_type"]
    dowork_page = user_instance.dowork(sheetid)
    title = Parse.work_title(dowork_page)
    print("部分做完的作业:", title, '\n', "all_ex:", all_ex, '\n', "all_type", all_type)
    c = input('是否存储本题号页面txt文件到项目handle_q_list文件夹中Y/N？')
    if c.lower() == 'y':
        sheetaction_instance.ajax_post(sheetid=sheetid, method="submit_null")
        answer_page = user_instance.answer(sheetid)
        answer = Parse.answers(answer_page)
        pipe_instance.in_answers(sheetid, answer)
        with open('./handle_q_list/{}做题页面.txt'.format(sheetid), 'w') as f:
            f.write(dowork_page)
        with open('./handle_q_list/{}答案页面.txt'.format(sheetid), 'w') as f:
            f.write(answer_page)
    return Util.manual_handle_question_ids(all_ex, all_type)


def full_user(userid, global_instance):
    """用户的完整登录和实例化对象逻辑
    return：
    global_instance: db, pipe, form
    user_obj: userid, user_session, user, ua, sa
    user_summery: sheetids, undo, unfinish, state, nodo
    """
    user_obj = gen_user_obj(userid, global_instance)
    if not user_obj :
        print('用户{}登录失败'.format(userid))
        return None
    userid, user_session, user, ua, sa = user_obj
    user_summary = get_user_summary(user_obj)
    get_ccs = check_user_ccs(global_instance, user_obj, user_summary)
    if not get_ccs:
        print('用户{}已完成全部作业，或无法获取ccs'.format(userid))
        return None
    return global_instance, user_obj, user_summary





