# -*- coding:utf-8 -*-
"""
    auth.py
    ~~~~~~~
    from:https://github.com/egrcc/zhihu-python/blob/master/auth.py
    define Login class
"""

import os
import sys
import time
import platform
import random
import re
import json
import cookielib
import requests
import termcolor


class Logging(object):
    """login class."""
    flag = True

    @staticmethod
    def error(msg):
        if Logging.flag:
            print ''.join([termcolor.colored('ERROR', 'red'), ':', termcolor.colored(msg, 'white')])

    @staticmethod
    def warn(msg):
        if Logging.flag:
            print ''.join([termcolor.colored('WARN', 'yellow'), ':', termcolor.colored(msg, 'white')])

    @staticmethod
    def info(msg):
        if Logging.flag:
            print ''.join([termcolor.colored('INFO', 'magenta'), ':', termcolor.colored(msg, 'white')])

    @staticmethod
    def debug(msg):
        if Logging.flag:
            print ''.join([termcolor.colored('DEBUG', 'magenta'), ':', termcolor.colored(msg, 'white')])

    @staticmethod
    def success(msg):
        if Logging.flag:
            print ''.join([termcolor.colored('SUCCESS', 'green'), ':', termcolor.colored(msg, 'white')])


# Exception class
class LoginPasswordError(Exception):
    def __init__(self, message):
        if isinstance(message, str) or message == '':
            self.message = u'error account or password'
        else:
            self.message = message
        Logging.error(self.message)


class NetworkError(Exception):
    def __init__(self, message):
        if isinstance(message, str) or message == '':
            self.message = u'network exception.'
        else:
            self.message = message
        Logging.error(self.message)


class AccountError(Exception):
    def __init__(self, message):
        if isinstance(message, str) or message == '':
            self.message = u'account exception.'
        else:
            self.message = message
        Logging.error(self.message)


class Login(object):
    """login zhi_hu class"""
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.requests = requests.session()
        self.cookies = cookielib.LWPCookieJar('cookies')
        # requests.cookies.load
        login_phone_url = 'http://www.zhihu.com/login/phone_num'
        login_email_url = 'http://www.zhihu.com/login/email'

    def get_captcha(self):
        url = "http://www.zhihu.com/captcha.gif"
        r = self.requests.get(url, params={"r": random.random()})
        if int(r.status_code) != 200:
            raise NetworkError(u"验证码请求失败")
        image_name = u"verify." + r.headers['content-type'].split("/")[1]
        open(image_name, "wb").write(r.content)
        """
            System platform: https://docs.python.org/2/library/platform.html
        """
        Logging.info(u"正在调用外部程序渲染验证码 ... ")
        if platform.system() == "Linux":
            Logging.info(u"Command: xdg-open %s &" % image_name)
            os.system("xdg-open %s &" % image_name)
        elif platform.system() == "Darwin":
            Logging.info(u"Command: open %s &" % image_name)
            os.system("open %s &" % image_name)
        elif platform.system() == "SunOS":
            os.system("open %s &" % image_name)
        elif platform.system() == "FreeBSD":
            os.system("open %s &" % image_name)
        elif platform.system() == "Unix":
            os.system("open %s &" % image_name)
        elif platform.system() == "OpenBSD":
            os.system("open %s &" % image_name)
        elif platform.system() == "NetBSD":
            os.system("open %s &" % image_name)
        elif platform.system() == "Windows":
            os.system("open %s &" % image_name)
        else:
            Logging.info(u"我们无法探测你的作业系统，请自行打开验证码 %s 文件，并输入验证码。" % os.path.join(os.getcwd(), image_name) )

        captcha_code = raw_input('Enter pin_code:')
        return captcha_code

    def get_xsrf(self):
        url = 'http://www.zhihu.com'
        r = self.requests.get(url)
        if int(r.status_code) != 200:
            raise NetworkError
        results = re.compile(r"\<input\stype=\"hidden\"\sname=\"_xsrf\"\svalue=\"(\S+)\"", re.DOTALL).findall(r.text)
        if len(results) < 1:
            Logging.info(u'read xsrf from server failed')
            return
        return results[0]

    def build_data(self):
        pass