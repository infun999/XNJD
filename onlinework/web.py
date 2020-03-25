#!/usr/bin/env python
# -*- coding:utf-8 -*-

# ===========================
# Author   :   infun999
# ===========================

import random
from lxml.html import etree
import requests

def _create_session():
    session = requests.session()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/531.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3",
        "Connection": "keep-alive"
    }
    session.headers = headers
    return session

def login(username, passw):
    """
    传入用户名和密码，返回登录后session
    :param username: 用户账号
    :param passw: 密码
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
        'username': username,
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
    return username, session


class Page:
    def __init__(self, user):
        self.userid = user[0]
        self.session = user[1]

    @property
    def worklist(self):
        url = 'http://study.xnjd.cn/study/Homework_list.action'
        return self.session.get(url=url).text

    def dowork(self, courseid: str, homeworkid: str)->str:
        """
        :param courseid: 课程编号
        :param homeworkid: 作业编号
        :return: 作业题目详情页
        """
        url = 'http://cs.xnjd.cn/course/exercise/Student_doIt.action?courseId={}&homeworkId={}'.format(courseid, homeworkid)
        return self.session.get(url=url).text

    def answer(self, coruseid: str, homeworkid: str)->str:
        """
        紧序在提交ajax_null或者ajax_all后访问
        :param coruseid:
        :param homeworkid:
        :return:
        """
        url = 'http://cs.xnjd.cn/course/exercise/Student_history.action?courseId={}&homeworkId={}'.format(coruseid, homeworkid)
        return self.session.get(url=url).text

    def captcha(self, courseid: str):
        """
        返回response.content字节流
        :param courseid: 课程编号
        :return: 图片字节流
        """
        url = 'http://cs.xnjd.cn/course/exercise/Student_validationCode.action?courseId={}&k={}'.format(courseid, str(random.random()))
        # 经302，带jsession id后获取验证码图片，注册在服务器中，session域最近唯一有效
        return self.session.get(url=url).content

    def ajax_post(self, form_data):
        url = 'http://cs.xnjd.cn/course/exercise/Ajax_stusavetmp.action?'
        return self.session.post(url=url, data=form_data)































