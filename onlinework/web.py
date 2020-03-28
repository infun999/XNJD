#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ===========================
# Author   :   infun999
# ===========================

import random
from lxml.html import etree
import requests
"""
web.py  登录用户，访问基本页面接口
"""

def _create_session():
    session = requests.session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/531.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Connection": "keep-alive"
    }
    session.headers = headers
    return session


def login(userid, passw):
    """
    传入用户名和密码，返回登录后session
    :return: 登录后session
    """
    session = _create_session()
    url = 'http://auth.xnjd.cn/login?service=http%3A%2F%2Fstudy.xnjd.cn%2Fstudy%2FHomework_list.action'
    resp = session.get(url).text
    e = etree.HTML(resp)
    lt = e.xpath('//td/input[@type="hidden"][1]/@value')[0]
    execution = e.xpath('//td/input[@type="hidden"][2]/@value')[0]
    _eventId = e.xpath('//td/input[@type="hidden"][3]/@value')[0]
    login_fd = {
        'username': userid,
        'password': passw,
        'lt': lt,
        'execution': execution,
        '_eventId': _eventId,
        'cassubmit.x': str(random.randint(1, 83)),
        'cassubmit.y': str(random.randint(1, 25))
    }
    resp = session.post(url, data=login_fd).text
    if '学习园地' not in resp:
        return None
    return userid, session


def split_id(sheetid):
    return sheetid.split('w')


class Page:
    def __init__(self, user):
        self.userid = user[0]
        self.session = user[1]

    @property
    def worklist(self):
        """作业列表页面"""
        url = 'http://study.xnjd.cn/study/Homework_list.action'
        return self.session.get(url=url).text

    def dowork(self, sheetid: str)->str:
        """作业题目详情页"""
        course, work = split_id(sheetid)
        url = 'http://cs.xnjd.cn/course/exercise/Student_doIt.action?courseId={}&homeworkId={}'.format(course, work)
        return self.session.get(url=url).text

    def answer(self, sheetid: str)->str:
        """
        紧序在提交ajax_null或者ajax_all后访问
        :return: 答案页面
        """
        course, work = split_id(sheetid)
        url = 'http://cs.xnjd.cn/course/exercise/Student_history.action?courseId={}&homeworkId={}'.format(course, work)
        return self.session.get(url=url).text

    def captcha(self, sheetid: str):
        """返回验证码content字节流"""
        course = split_id(sheetid)[0]
        url = 'http://cs.xnjd.cn/course/exercise/Student_validationCode.action?courseId={}&k={}'.format(course, str(random.random()))
        # 经302，带jsession id后获取验证码图片，注册在服务器中，session域最近唯一有效
        return self.session.get(url=url).content

    def ajax_post(self, form_data):
        """做题核心请求"""
        url = 'http://cs.xnjd.cn/course/exercise/Ajax_stusavetmp.action?'
        return self.session.post(url=url, data=form_data)
