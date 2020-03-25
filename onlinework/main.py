#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ===========================
# Author   :   infun999
# ===========================


from onlinework import web
from onlinework import database
from onlinework import core
from onlinework.processdata import Form
from onlinework.processdata import Pipe
from onlinework.processdata import Util

'''
0.  准备工作：数据库写入userid 和pw
1.  实例化全局共用OBJ
2.1 



'''

# 1. 实例化全局共用 单例
db = database.XNJD()
pipe = Pipe(db)
form = Form(db, pipe)



# 2. 以userid开启（线程）
while True:
  # 2.1   ***实例单个userid对应的 OBJ: us,ua,wa***
    # 启动参数
    userid = input("输入用户学号").__str__()
    pw = pipe.out_pw(userid=userid)
    """处理密码错误问题"""
    # 登录用户会话us
    user_login = web.login(username=userid, passw=pw)
    if not user_login:
        continue
    # 实例用户身份
    user = web.Page(user=user_login)
    # 实例用户操作
    ua = core.UserAction(user_instance=user)
    # 实例作业操作
    core.SheetsAction.connect_data_source(pipe_instance=pipe, form_instance=form)
    sa = core.SheetsAction(user_instance=user)

    # 获取基本信息
    summary = ua.get_summary
    sheetids, undo, unfinish, state = summary[0], summary[1], summary[2], summary[3]

    user_ccs = pipe.out_user_ccs(userid=userid)
    if not user_ccs and undo:
        user_ccs = ua.get_user_ccs(sheetid=undo[0])
        pipe.in_user_ccs(userid=userid, user_ccs=user_ccs)

  # 2.2   ***查询本用户作业列表是否存有数据库答案，如果没有，则自动（验证码）去下载并存入数据库***
    """待处理，避免每次访问到 全主观题作业"""

    """Util 分类finish_state"""

    for sheetid in undo:
        """如果没有行，用sheetid ：sheetid 创建行"""
        pipe.init_db_if_not_exist(loc_key="sheetid", loc_value=sheetid)
        post_answer = pipe.out_post_answer(sheetid)

        if not post_answer:
            sheet_info = pipe.out_sheet_info(sheetid)
            q_ids = pipe.out_question_ids(sheetid)
            if not sheet_info and q_ids:
                # 访问dowork_page
                s_info = sa.get_sheet_info(sheetid)
                q_ids = sa.get_question_ids(sheetid)
                pipe.in_quetion_ids(sheetid, question_ids=q_ids)
                pipe.in_sheet_info(sheetid, sheet_info=s_info)
            answers = pipe.out_answers(sheetid)
            if not answers:
                # 提交AJAX_null 请求，再访问answer页面，获取answer
                sa.ajax_post(sheetid, method="submit_null")
                origin_answer = sa.get_answers(sheetid)
                pipe.in_answers(sheetid, answers=origin_answer)
            # 创建post_answer
            post_answer = form.post_answer(sheetid)
            pipe.in_post_answer(sheetid, post_answer=post_answer)
            if not post_answer:     # 数据库中有正确的question_ids、answers、sheet_info才可创建
                print('Base data error for creating post_form_answer')

  #  2.3    ***输入sheetid，完成作业***
    while True:
        # 读取未完成作业sheetids，输入sheetid

                        # finish_state = ua.get_finish_state              # 可选存储
                        # pipe.in_finish_state(userid, finish_state)      # 可选
        print(undo)
        sheetid = input("输入要完成的作业编码")
        if sheetid not in undo:
            print('作业编号{}不存在'.format(sheetid))
            continue
        course, work = Util.split_id(sheetid)
        # 访问dowork uspage，（可不访问，模拟人为）
        user.dowork(course, work)
        # 构造表单，提交tempsave AJAX请求（可不提交，模拟人为）
        # for t_form in wa.create_tempsaveform(sheetid):
        #     wa.ajax_post(sheetid, method="save", interval=2)

        sa.ajax_post(sheetid)



