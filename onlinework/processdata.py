#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ===========================
# Author   :   infun999
# ===========================


import re, time, json
from lxml.html import etree
"""
class Parse：    解析网页
class Pipe ：    处理数据存取
class Form :     构建访问答案页和提交作业等请求的表单
class Util :     辅助工具
"""


# 解析网页
class Parse:
    """解析网页数据"""
    @staticmethod
    def answers(answer_page):
        """
        返回正确答案编号列表字符串 like：    "['1', '3', '1', '2', '4']"
        """
        ans = re.findall(r'正确答案：</font>(.*)</td></tr>', answer_page)        # 解析不定项选择错误"B C D"    # 解析判断题"说法错误"---0，”说法正确“---1
        answers = []
        for i in ans:
            if len(i) == 1:
                answers.append(str(ord(i)-64))
            elif i == '说法错误':
                answers.append('0')
            elif i == '说法正确':
                answers.append('1')
            else:
                i = i.replace('A', '1')
                i = i.replace('B', '2')
                i = i.replace('C', '3')
                i = i.replace('D', '4')
                i = i.replace('E', '5')
                i = i.replace(' ', '|')
                answers.append(i)
        return answers

    @staticmethod
    def question_ids(dowork_page):
        """返回:去重后，带小题目有序编号"""
        q_list = []
        q_nums = re.findall(r'answer_(\w+)', dowork_page)
        for i in q_nums:
            if i not in q_list:
                q_list.append(i)
        return q_list

    @staticmethod
    def work_title(dowork_page):
        """仅适用undo, unfinish , nodo页面，返回当前作业标题"""
        e = etree.HTML(dowork_page)
        return str(e.xpath('//form//td//td//td/text()')[0])     # 此XPATH接近于取题目表述

    @staticmethod
    def question_detail(dowork_page):
        """
        解析问题描述
        :param dowork_page: 做题页面
        :return: 详题列表
        """
        pass

    @staticmethod
    def sheet_info(dowork_page,):
        """题目页面综合信息"""
        sheet_info = {}
        e = etree.HTML(dowork_page)
        sheet_info["course_code"] = str(e.xpath('//*[@id="glo_course_code"]/@value')[0])
        sheet_info["homework_id"] = str(e.xpath('//*[@id="glo_homework_id"]/@value')[0])
        sheet_info["all_ex"] = str(e.xpath('//*[@id="glo_allExerciseId"]/@value')[0])
        sheet_info["all_type"] = str(e.xpath('//*[@id="glo_allType"]/@value')[0])
        sheet_info["course_url"] = str(e.xpath('//*[@id="course_url"]/@value')[0])
        sheet_info["repeat_type"] = str(e.xpath('//*[@id="repeat_type"]/@value')[0])
        return sheet_info

    @staticmethod
    def user_ccs(dowork_page):
        """用户基本信息center_code,class_code,student_code"""
        user_ccs = {}
        e = etree.HTML(dowork_page)
        user_ccs["student_id"] = str(e.xpath('//*[@id="glo_student_id"]/@value')[0])
        user_ccs["center_code"] = str(e.xpath('//*[@id="center_code"]/@value')[0])
        user_ccs["class_code"] = str(e.xpath('//*[@id="class_code"]/@value')[0])
        return user_ccs

    @staticmethod
    def sheetids(worklist_page):
        """本学期所有作业编号like：24w96格式(从作业列表页面,url中获取)"""
        sheetids = list()
        e = etree.HTML(worklist_page)
        # 所有作业的url list
        url_list = e.xpath('//*[@id="courseList"]//a/@href')
        partten = re.compile(r'\d+&homeworkId=\d+')
        for url in url_list:
            # 提取课程和作业编号
            t = partten.findall(url)[0]
            t = re.sub(r'&homeworkId=', 'w', t)
            sheetids.append(t)
        return sheetids

    @staticmethod
    def finish_state(worklist_page):
        """用户作业完成状态"""
        sheetids = Parse.sheetids(worklist_page)
        undo_list = []
        unfinish_list = []
        finish_state = {}
        nodo_list = []
        e = etree.HTML(worklist_page)
        total = e.xpath('//*[@id="courseList"]//td[3]')

        undo = e.xpath('//*[@id="courseList"]//td[5]')
        did = e.xpath('//*[@id="courseList"]//td[5]/span')
        j = 0
        for i in range(len(total)):
            # 总题数和 客观题数
            n = re.findall(r'\d*', total[i].text)
            t = n[0]    # 总量
            s = n[7]    # 客观题量
            # 未做作业或 完成题数为0
            if undo[i].text.strip():
                d = '0'  # 未做过作业，完成数量设为0
            else:
                d = re.sub(r'[\u4e00-\u9fa5]', "", did[j].text).strip()    # 完成题目数量
                j += 1
            finish_state[sheetids[i]] = t + '|' + s + '|' + d
            # finish_state      sheetid|总量|客观题量|已完成量
            if s != '0' and d == '0':
                undo_list.append(sheetids[i])
            elif s != d and d != '0':
                unfinish_list.append(sheetids[i])
            elif s == '0':
                nodo_list.append(sheetids[i])
        return undo_list, unfinish_list, finish_state, nodo_list


# 处理数据存取
class Pipe:
    """处理内存与数据库的传输和格式转换"""
    __instance = None
    __init_flag = True

    def __new__(cls, *args, **kwargs):
        if cls.__instance == None:
            cls.__instance =object.__new__(cls)
        return cls.__instance

    def __init__(self, db_instance):
        self.db = db_instance
        Pipe.__init_flag = False

    # 处理字典--字典类型
    def in_row(self, table_name, loc_key, loc_value, dict_data: dict):
        """仅能写不存在loc_value关键值的行，否则返回None"""
        _id = self.db.set_row(table_name, loc_key, loc_value, dict_data)
        return _id

    def out_row(self, table_name, loc_key, loc_value)->dict:
        r = self.db.get_row(table_name, loc_key, loc_value)
        return r if r else {}

    # 处理字符串--字符串类型
    def in_pw(self, userid, pw):
        pw = pw.__str__()
        self.db.set_item(table_name="users", loc_key="userid", loc_value=userid, set_key="pw", set_value=pw)

    def out_pw(self, userid):
        return self.db.get_item(table_name="users", loc_key="userid", loc_value=userid, search_key="pw")

    def in_capt_str(self, capt_hash, capt_str):
        self.db.set_item("captcha", "capt_hash", capt_hash, "capt_str", capt_str)

    def out_capt_str(self, capt_hash):
        self.db.get_item("captcha", "capt_hash", capt_hash, "capt_str", )

    def in_capt_code(self, capt_hash, capt_code):
        self.db.set_item("captcha", "capt_hash", capt_hash, "capt_code", capt_code)

    def out_capt_code(self, capt_hash):
        self.db.get_item("captcha", "capt_hash", capt_hash, "capt_code", )

    # 处理列表--字符串类型
    def in_quetion_ids(self, sheetid, question_ids: list):
        q_ids = question_ids.__str__()
        self.db.set_item("sheets", "sheetid", sheetid, "question_ids", q_ids)

    def out_question_ids(self, sheetid)->list:
        _ = self.db.get_item("sheets", "sheetid", sheetid, "question_ids")
        r = eval(_) if _ else []
        return r

    def in_answers(self, sheetid, answers: list):
        ans = answers.__str__()
        self.db.set_item("sheets", "sheetid", sheetid, "answers", ans)

    def out_answers(self, sheetid) -> list:
        _ = self.db.get_item("sheets", "sheetid", sheetid, "answers")
        r = eval(_) if _ else []
        return r

    def in_finish_state(self, userid, finish_state: list):
        finish_state = finish_state.__str__()
        self.db.set_item("users", "userid", userid, "finish_state", finish_state)

    def out_finish_state(self, userid) -> list:
        _ = self.db.get_item("users", "userid", userid, "finish_state")
        r = eval(_) if _ else []
        return r

    # 处理字典--字符串类型
    def in_user_ccs(self, userid, user_ccs: dict):
        user_ccs = json.dumps(user_ccs)
        self.db.set_item("users", "userid", userid, "user_ccs", user_ccs)

    def out_user_ccs(self, userid)->dict:
        _ = self.db.get_item("users", "userid", userid, "user_ccs")
        r = json.loads(_) if _ else {}
        return r

    def in_sheet_info(self, sheetid, sheet_info: dict):
        sheet_info = json.dumps(sheet_info)
        self.db.set_item("sheets", "sheetid", sheetid, "sheet_info", sheet_info)

    def out_sheet_info(self, sheetid)->dict:
        _ = self.db.get_item(table_name="sheets", loc_key="sheetid", loc_value=sheetid, search_key="sheet_info")
        r = json.loads(_) if _ else {}
        return r

    def in_post_answer(self, sheetid, post_answer: dict):
        post_answer = json.dumps(post_answer)
        self.db.set_item("sheets", "sheetid", sheetid, "post_answer", post_answer)

    def out_post_answer(self, sheetid)->dict:
        _ = self.db.get_item("sheets", "sheetid", sheetid, "post_answer")
        r = json.loads(_) if _ else {}
        return r

    # 特殊方法：检查是否初始化row
    """因数据库底层方法是用update来实现的set_xxx，至少需要loc_key，loc_value的初始值"""
    def init_db_if_not_exist(self, create_key: str, set_ori_value):
        """
        create_key:指定"userid"\"sheetid"\"hash_cap"\"hash_q"
        :param loc_key:     自定义各表唯一定位关键字段
        :param loc_value:   自定义各表唯一定位关键值
        :return:
        """
        d = {
            "userid": "users",
            "sheetid": "sheets",
            "capt_hash": "captcha",
            "quest_hash": "qa_detail"
        }
        row = self.db.get_row(d[create_key], create_key, set_ori_value)
        if not row:
            self.db.init_row(d[create_key], create_key, set_ori_value)

    # 特殊方法： 查询字段列
    def get_item_column(self, search_table, search_item):
        table = self.db.get_table(table_name=search_table)
        for row in table:
            yield row[search_item]

    # 特殊方法: 删除验证码code
    def del_capt_code(self, capt_hash):
        self.db.del_item("captcha", "capt_hash", capt_hash, "capt_code")


# 构建表单
class Form:
    """处理数据构建网页请求表单"""
    __instance = None
    __init_flag = True

    def __new__(cls, *args, **kwargs):
        if cls.__instance == None:
            cls.__instance =object.__new__(cls)
        return cls.__instance

    def __init__(self, db_instance, pipe_instance):
        self.db = db_instance
        self.pipe = pipe_instance
        Form.__init_flag = False

    def base(self, userid, sheetid):
        """用户所有作业通用的基本表单"""
        user_ccs = self.pipe.out_user_ccs(userid)
        sheet_info = self.pipe.out_sheet_info(sheetid)
        t = str(time.asctime(time.localtime()))
        form = {
            "all_ex": sheet_info["all_ex"],
            "course_code": sheet_info["course_code"],
            "homework_id": sheet_info["homework_id"],
            "student_id": user_ccs["student_id"],
            "all_type": sheet_info["all_type"],
            "course_url": sheet_info["course_url"],
            "timestamp": t + ' GMT 0800 (中国标准时间)',
            "repeat_type": sheet_info["repeat_type"],
        }
        return form

    def temp_save(self, userid):
        """提交临时保存时，需附加在基本表单base上，（用于模拟点击选项时的临时保存）"""
        user_ccs = self.pipe.out_user_ccs(userid)
        form = {
            "method": "savetmpontime",
            "center_code": user_ccs["center_code"],
            "class_code": user_ccs["class_code"],
            "lefttime": "0|0"
        }
        return form

    @property
    def submit_all(self):
        """提交最终作业，需附加在基本表单base上（用于最终提交）"""
        form = {
            "method": "submithomework",
            "center_code": "",
            "class_code": "",
            "lefttime": "|0",
            "homework_type": "%E8%AE%A1%E5%AE%8C%E6%88%90%E9%A2%98%E7%9B%AE%E6%95%B0",
        }
        return form

    @property
    def submit_null(self):
        """提交临时保存时，需附加在基本表单base上（提交请求后，再访问答案页面获取答案）"""
        form = {
            "method": "submithomework",
            "center_code": "",
            "class_code": "",
            "lefttime": "|0",
            "homework_type": "%E8%AE%A1%E5%AE%8C%E6%88%90%E9%A2%98%E7%9B%AE%E6%95%B0",
        }
        return form

    def post_answer(self, sheetid)->dict:
        """pipe_out数据，调用专门处理方法handle_answers：构建提交格式的答案"""
        question_ids = self.pipe.out_question_ids(sheetid)
        answers = self.pipe.out_answers(sheetid)
        sheet_info = self.pipe.out_sheet_info(sheetid)
        all_ex = sheet_info["all_ex"]
        all_type = sheet_info["all_type"]
        return Util.handle_answers(question_ids, answers, all_ex, all_type)


class Util:
    # 处理AJAX-post请求中答案格式
    @staticmethod
    def handle_answers(questions: list, answers: list, all_ex: str, all_type: str):

        """
        将题目编号和答案编号转为可提交form_data的dict
        :param q:   dowork_page处理后题目编号 # q=['9860','9861','9862','9863','9864','9865','9866','9867','9868','9869','9870', '9871','9872','9873', '9874', '9875', '9876', '9877', '9878', '9879', '9880', '9881','9882','9883', '9884', '10060_1', '10060_2', '10060_3', '10060_4', '10060_5', '10061_1', '10061_2', '10061_3', '10061_4', '10061_5', '10062_1', '10062_2', '10062_3', '10062_4', '10062_5', '10086_1', '10086_2', '10086_3', '10086_4', '10086_5', '10086_6', '10086_7', '10086_8', '10086_9', '10086_10']
        :param a:   answer_page处理后答案编号 # a=[3, 1, 1, 2, 4, 3, 3, 3, 3, 4, 2, 4, 4, 4, 2, 1, 1, 2, 4, 3, 3, 3, 1, 2, 4, 4, 3, 2, 3, 3, 3, 3, 2, 1, 4, 1, 2, 4, 1, 2, 1, 3, 1, 2, 3, 4, 2, 3, 1, 4]
        :param all_ex: 内建题目编号 # all_ex = '9860|9861|9862|9863|9864|9865|9866|9867|9868|9869|9870|9871|9872|9873|9874|9875|9876|9877|9878|9879|9880|9881|9882|9883|9884|84048|10060|10061|10062|10086'
        :param all_type: 内建题目类型 # all_type = '1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|1|4|5|5|5|5'
        :return: 符合提交作业的答题form表单
        """
        try:
            ans_d = {}
            questions = [re.findall(r'(\d+)', q)[0] for q in questions]  # 保留主题目编号
            all_ex = all_ex.split('|')
            all_type = all_type.split('|')
            le = len(all_type)
            for i in range(le, 0, -1):  # c为准备answer.pop()的答案数量
                if all_type[i - 1] == '1':  # 单选
                    c = 1
                elif all_type[i - 1] == '2':  # 不定项
                    c = 1
                elif all_type[i - 1] == '3':  # 判断
                    c = 1
                elif all_type[i - 1] == '4':  # 主观题
                    c = 0
                elif all_type[i - 1] == '5':  # 多子选择题目 大题
                    c = questions.count(all_ex[i - 1])  # 计数大题编号下小题数量
                else:
                    c = 0

                if c == 1:  # 单选，判断，不定项
                    ans_d['answer_' + all_ex[i - 1]] = answers.pop().__str__()
                elif c > 1:  # 大选择题
                    t = []
                    for j in range(c, 0, -1):  # 取小题个数次 答案（倒序）
                        t.append(j.__str__() + '_' + answers.pop())  # like: ['5_1','4_4','3_1','2_4','1_3']
                    t.reverse()
                    t = '|'.join(t)  # like: '1_3|2_4|3_1|4_2|5_4'
                    ans_d['answer_' + all_ex[i - 1]] = t
            return ans_d
        except:
            return None

    @staticmethod
    def manual_handle_question_ids(all_ex, all_type):
        """
        （做过，但是未完成的work，需要人工辅助处理，构建题目list）方法中默认不定项选择为5个选项。带子题目的大题，需要手动输入子题目数量
        :param all_ex: 题目编号
        :param all_type: 题型
        :return: 统一格式的question_ids
        """
        q_ids = []
        all_ex = all_ex.split('|')
        all_type = all_type.split('|')
        le = len(all_type)
        k = 0
        for i in range(le):
            if all_type[i] in ['1', '3']:  # 单选、判断题计1个， 主观题抛弃
                q_ids.append(all_ex[i])
            elif all_type[i] == '2':  # 不定项(默认5个选项）计5个
                for j in range(5):
                    q_ids.append(all_ex[i] + '_' + str(j + 1))
            elif all_type[i] == '5':  # 多子选择题目 大题， 人工确定个数
                k += 1
                c = input('输入第{}个大题{}(type=5的第{}个题)的子题目个数'.format(i + 1, all_ex[i], k))
                for j in range(int(c)):
                    q_ids.append(all_ex[i] + '_' + str(j + 1))
        return q_ids

    # 分割sheetid为课程号和作业号
    @staticmethod
    def split_id(sheetid):
        return sheetid.split('w')



