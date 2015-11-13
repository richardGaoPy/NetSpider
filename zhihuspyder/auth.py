# -*- coding:utf-8 -*-
"""
    auth.py
    ~~~~~~~
    from:https://github.com/egrcc/zhihu-python/blob/master/auth.py
    define Login class
"""

import os
import platform
import random
import re
import json
import cookielib
import requests
import termcolor
from tornado import escape

# from base import GetTopics, GetSubclassTopics, GetUserInfo, GetSubclassFans

default_headers = {'X-Requested-With': 'XMLHttpRequest',
                   'Referer': 'http://www.zhihu.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64)'
                                 ' AppleWebKit/537.36 (KHTML, like Gecko)'
                                 ' Chrome/43.0.2357.132 Safari/537.36',
                   'Host': 'www.zhihu.com'}


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
        self.requests = requests.Session()

    def initialize(self, cookie):
        self.requests.cookies = cookielib.LWPCookieJar(cookie)
        try:
            self.requests.cookies.load(ignore_discard=True)
        except:
            pass

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
            Logging.info(u"我们无法探测你的作业系统，请自行打开验证码 %s 文件，并输入验证码。"
                         % os.path.join(os.getcwd(), image_name) )
        captcha_code = raw_input('Enter pin_code:')
        return captcha_code

    def get_captcha(self):
        url = "http://www.zhihu.com/captcha.gif"
        r = self.requests.get(url, params={"r": random.random()} )
        if int(r.status_code) != 200:
            raise NetworkError(u"验证码请求失败")
        image_name = u"captcha." + r.headers['content-type'].split("/")[1]
        # open( image_name, "wb").write(r.content)
        with open(image_name, 'wb') as fd:
            fd.write(r.content)
        fd.close()
        from yunsu import get_pincode
        results = get_pincode()
        print results
        p = re.compile(r'<Result>(.*?)</Result>', re.M)
        captcha_code = p.findall(results)[0]
        captcha_code = str(captcha_code)
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

    def build_form(self):
        if re.match(r"^1\d{10}$", self.username): account_type = "phone_num"
        elif re.match(r"^\S+\@\S+\.\S+$", self.username): account_type = "email"
        else: raise AccountError(u"帐号类型错误")
        form = {account_type: self.username, "password": self.password, "remember_me": True }

        form['_xsrf'] = self.get_xsrf()
        form['captcha'] = self.get_captcha()
        return form

    def upload_form(self, form):
        if "email" in form: url = "http://www.zhihu.com/login/email"
        elif "phone_num" in form: url = "http://www.zhihu.com/login/phone_num"
        else: raise ValueError(u"账号类型错误")

        headers = {
            'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36",
            'Host': "www.zhihu.com",
            'Origin': "http://www.zhihu.com",
            'Pragma': "no-cache",
            'Referer': "http://www.zhihu.com/",
            'X-Requested-With': "XMLHttpRequest"
        }

        r = self.requests.post(url, data=form, headers=headers)
        if int(r.status_code) != 200:
            raise NetworkError(u"表单上传失败!")

        if r.headers['content-type'].lower() == "application/json":
            try:
                result = json.loads(r.content)
            except Exception as e:
                Logging.error(u"JSON解析失败！")
                Logging.debug(e)
                Logging.debug(r.content)
                result = {}
            if result["r"] == 0:
                Logging.success(u"登录成功！" )
                return {"result": True}
            elif result["r"] == 1:
                Logging.success(u"登录失败！" )
                return {"error": {"code": int(result['errcode']), "message": result['msg'], "data": result['data'] } }
            else:
                Logging.warn(u"表单上传出现未知错误: \n \t %s )" % ( str(result) ) )
                return {"error": {"code": -1, "message": u"unknow error"} }
        else:
            Logging.warn(u"无法解析服务器的响应内容: \n \t %s " % r.text )
            return {"error": {"code": -2, "message": u"parse error"} }

    def islogin(self):
        # check session
        url = "http://www.zhihu.com/settings/profile"
        r = self.requests.get(url, allow_redirects=False)
        status_code = int(r.status_code)
        if status_code == 301 or status_code == 302:
            # 未登录
            return False
        elif status_code == 200:
            return True
        else:
            Logging.warn(u"网络故障")
            return None

    # def read_account_from_config_file(config_file="config.ini"):
    #     # NOTE: The ConfigParser module has been renamed to configparser in Python 3.
    #     #       The 2to3 tool will automatically adapt imports when converting your sources to Python 3.
    #     #       https://docs.python.org/2/library/configparser.html
    #     from ConfigParser import ConfigParser
    #     cf = ConfigParser()
    #     if os.path.exists(config_file) and os.path.isfile(config_file):
    #         Logging.info(u"正在加载配置文件 ...")
    #         cf.read(config_file)
    #
    #         email = cf.get("info", "email")
    #         password = cf.get("info", "password")
    #         if email == "" or password == "":
    #             Logging.warn(u"帐号信息无效")
    #             return (None, None)
    #         else: return (email, password)
    #     else:
    #         Logging.error(u"配置文件加载失败！")
    #         return (None, None)

    def login(self):
        if self.islogin():
            Logging.success(u"你已经登录过咯")
            return True

        form_data = self.build_form()
        print form_data
        """
            result:
                {"result": True}
                {"error": {"code": 19855555, "message": "unknow.", "data": "data" } }
                {"error": {"code": -1, "message": u"unknow error"} }
        """
        result = self.upload_form(form_data)
        print result
        if "error" in result:
            if result["error"]['code'] == 1991829:
                # 验证码错误
                Logging.error(u"验证码输入错误，请准备重新输入。" )
                return self.login()
            else:
                Logging.warn(u"unknow error.")
                return False
        elif "result" in result and result['result'] == True:
            # 登录成功
            Logging.success(u"登录成功！" )
            self.requests.cookies.save()
            # os.remove('verify.gif')
            return True

    def send_message(self, url_token='', message=''):
        url = u'http://www.zhihu.com/node/MemberProfileCardV2?params='
        url_params = '{"url_token":"%s"}' % url_token
        escape_url = escape.url_escape(url_params, plus=False)
        url += escape_url
        r = self.requests.get(url=url, headers=default_headers)
        p = re.compile(r'data-pm-hash="(.*?)">', re.M)
        dd = p.findall(r.content)
        if len(dd) == 0:
            return
        dxsrf = self.get_xsrf()
        msg_data = {
            'member_id': str(dd[0]),
            'content': escape.to_unicode(message),
            'token': '',
            '_xsrf': dxsrf,
        }
        print msg_data
        uri = u'http://www.zhihu.com/inbox/post'
        msg_r = self.requests.post(url=uri, data=msg_data, headers=default_headers)
        print msg_r.content
        p = re.compile(r'"r":0', re.S)
        send_status = p.findall(msg_r.content)
        if len(send_status) == 0:
            print 'Send message failed!'
            with open('failed_users.txt', 'a') as fd:
                fd.write(str(url_token))
                fd.write('\n')
            return False
        print 'Send message OK!'
        return True



# def send_message(requests=None, token='', msg=''):
#     pass
#
if __name__ == '__main__':
    # -----------------test------------------
    login = Login('kbcuqm640845@163.com', 'dywff53')
    login.initialize('cookies3')
    # print login.get_captcha()
    print login.login()
    print login.requests.cookies
    login.send_message('kalipy', 'hello')
    # # topics = GetTopics(login)
    # # topics.save_father_topics()
    # sub_topics = GetSubclassTopics(login)
    # sub_topics.get_subclass_topics()
    # # get_users = GetSubclassFans('http://www.zhihu.com/topic/19550517', login)
    # # get_users.get_topic_fans()
    # # user_info = GetUserInfo(login)
    # # user_info.get_uid_account()
    # # ------------------main------------------
    # accounts = list()       # (user, password)
    # zh_users = list()
    # count = 0
    # login_user = list()
    # for account in accounts:
    #     login = Login(account)
    #     login.initialize('cookies'+str(count))
    #     if login.login():
    #         login_user.append(account)
    #     else:
    #         print 'check the account {}'.format(str(account))
    # _max = len(login_user)
    # while True:
    #     cookie_id = random.randint(0, _max)
    #     login = Login(login_user[cookie_id])
    #     login.initialize()
    #     if not login.islogin():
    #         login.login()
    #         send_message(login.requests)
    #     send_message(login.requests)




