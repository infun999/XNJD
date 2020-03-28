#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ===========================
# @Author   :   infun999
# @Time     :   2020/3/27 0:56
# ===========================


"""
专门更新数据库信息使用
"""


from onlinework import core


def set_account_to_db(db_instance):
    """
    :param db_instance: 数据库实例
    :return:
    """
    print('c:重新输入\nq:结束')
    log = []
    while True:
        userid = input('输入账号名:')
        if userid.lower() == 'c':
            continue
        if userid.lower() == 'q':
            return log
        pw = input('输入{}账户的密码:'.format(userid))
        if pw.lower() == 'c':
            continue
        if pw.lower() == 'q':
            return log
        if not db_instance.get_row(table_name='users', loc_key='userid', loc_value=userid):
            db_instance.init_row(table_name="users", create_key="userid", set_ori_value=userid)
            db_instance.set_item(table_name="users", loc_key="userid", loc_value=userid, set_key='pw', set_value=pw)
            log.append(userid)
        else:
            c = input('user:{} is exist, still log ? Y/N'.format(userid))
            if c.lower() == 'y':
                db_instance.set_item(table_name="users", loc_key="userid", loc_value=userid, set_key='pw', set_value=pw)
                log.append(userid)


def load_all_userid(pipe_instance):
    """调取所有用户id,   return: userid generator"""
    return pipe_instance.get_item_column(search_table='users', search_item='userid')

def useable_sheetids(pipe_instance):
    """调取所有存储完整做题信息的sheetid,   return: list"""
    useable_list = []
    sheetids_gen = pipe_instance.get_item_column(search_table='sheets', search_item='sheetid')
    for sheetid in sheetids_gen:
        if pipe_instance.out_sheet_info(sheetid) and pipe_instance.out_post_answer(sheetid):
            useable_list.append(sheetid)
    return useable_list

def store_new_post_answer(sheetid, form_instance, pipe_instance, sheetaction_instance,):
    pipe, sa, form = pipe_instance, sheetaction_instance, form_instance
    sheet_info = pipe.out_sheet_info(sheetid)
    q_ids = pipe.out_question_ids(sheetid)
    answers = pipe.out_answers(sheetid)
    if not sheet_info:
        # 访问dowork_page
        s_info = sa.get_sheet_info(sheetid)
        pipe.in_sheet_info(sheetid, sheet_info=s_info)
    if not q_ids:
        q_ids = sa.get_question_ids(sheetid)
        pipe.in_quetion_ids(sheetid, question_ids=q_ids)
    if not answers:
        # 提交AJAX_null 请求，再访问answer页面，获取answer
        sa.ajax_post(sheetid, method="submit_null")
        origin_answer = sa.get_answers(sheetid)
        pipe.in_answers(sheetid, answers=origin_answer)
    # 创建post_answer表单格式
    post_answer = form.post_answer(sheetid)
    pipe.in_post_answer(sheetid, post_answer=post_answer)
    if not post_answer:  # 数据库中有正确的question_ids、answers、sheet_info才可创建
        print('Base data error for creating post_form_answer')

def update_db(userid, useable_sheetids, global_instance, auto_skip_unfinish=False):
    f = core.full_user(userid, global_instance)
    if not f:
        return None
    db, pipe, form = f[0]
    userid, user_session, user, ua, sa = f[1]
    sheetids, undo, unfinish, state, nodo = f[2]
    for sheetid in sheetids:
        if (sheetid in useable_sheetids) or (sheetid in nodo):
            continue
        if sheetid in undo:
            pipe.init_db_if_not_exist(create_key="sheetid", set_ori_value=sheetid)
            store_new_post_answer(sheetid, form_instance=form, pipe_instance=pipe, sheetaction_instance=sa)
        if not auto_skip_unfinish and (sheetid in unfinish):
            s = input("是否跳过{}号作业Y/N？".format(sheetid))
            if s.lower() == 'y':
                continue
            pipe.init_db_if_not_exist(create_key="sheetid", set_ori_value=sheetid)
            q_list = core.manual_create_question_list(sheetid, user_instance=user, sheetaction_instance=sa, pipe_instance=pipe)
            pipe.in_quetion_ids(sheetid, q_list)
            store_new_post_answer(sheetid, form_instance=form, pipe_instance=pipe, sheetaction_instance=sa)


if __name__ == '__main__':
    glo_inst = core.init_global_instance()      # db, pipe ,form
    u_ids = useable_sheetids(glo_inst[1])
    model = input("选择模式\na:自动更新所有账户\nm:输入账户，更新单个账户\nc:在数据库中添加账户")
    if model.lower() == 'a':
        for userid in load_all_userid(pipe_instance=glo_inst[1]):
            update_db(userid=userid, useable_sheetids=u_ids, global_instance=glo_inst, auto_skip_unfinish=True)
        for userid in load_all_userid(pipe_instance=glo_inst[1]):
            update_db(userid=userid, useable_sheetids=u_ids, global_instance=glo_inst)
    elif model.lower() == 'm':
        while True:
            userid = input("输入用户账户以更新账户作业数据，输入Q/q退出").__str__()
            if userid.lower() == 'q':
                exit(0)
            update_db(userid=userid, useable_sheetids=u_ids, global_instance=glo_inst)
    elif model.lower() == 'c':
        added = set_account_to_db(glo_inst[0])
        q = input('是否更新本次输入账户作业数据Y/N')
        if q.lower() == 'y':
            for i in added:
                update_db(userid=i, useable_sheetids=u_ids, global_instance=glo_inst)
                print('本次更新{}完成'.format(added))


