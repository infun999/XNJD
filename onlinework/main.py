#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ===========================
# Author   :   infun999
# ===========================


from onlinework import core

'''
0.  准备工作：数据库写入userid 和pw
1.  实例化全局共用OBJ
2.1 



'''

#   1. 全局实例
glo_inst = core.init_global_instance()
db, pipe, form = glo_inst
#   2. 以userid开启（线程）
while True:
    # 创建用户基本对象
    userid = input("******做题模式*****\n\n输入用户学号,或E/e退出").__str__()
    if userid.lower() == 'e':
        exit(0)
    f = core.full_user(userid, global_instance=glo_inst)
    if not f:
        continue
    db, pipe, form = f[0]
    userid, user_session, user, ua, sa = f[1]
    sheetids, undo, unfinish, state, nodo = f[2]
    # 输入sheetid，完成作业
    while True:
        print('undo list:', undo)
        print('unfinish list:', unfinish)
        sheetid = input("当前用户:{}，输入'Q'或'q'切换用户操作\n输入作业编码完成作业:".format(userid))
        if sheetid.lower() == 'q':
            new_summary = ua.get_summary
            pipe.in_finish_state(userid, new_summary[3])
            break
        elif (sheetid not in undo) and (sheetid not in unfinish):
            print('作业编号{}不存在,重新输入'.format(sheetid))
            continue
        # user.dowork(sheetid)                         # 访问dowork uspage，（可不访问，模拟人为)
        # for t_form in wa.create_tempsaveform(sheetid):    # 提交tempsave AJAX请求（可不提交，模拟人为）
        #     wa.ajax_post(sheetid, method="save", interval=2)
        sa.ajax_post(sheetid)



