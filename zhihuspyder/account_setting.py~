# -*- coding:utf-8 -*-

import requests
import json
import time
import re
import os

from tornado import escape

from read_infos import get_accounts

_url = 'http://www.zhihu.com'
_captcha_pre = 'http://www.zhihu.com/captcha.gif?r='
_login_url = 'http://www.zhihu.com/login/email'
_session = requests.Session()
default_headers = {'X-Requested-With': 'XMLHttpRequest',
                   'Referer': 'http://www.zhihu.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64)'
                                 ' AppleWebKit/537.36 (KHTML, like Gecko)'
                                 ' Chrome/43.0.2357.132 Safari/537.36',
                   'Host': 'www.zhihu.com'}


def _getcaptcha():
    """
    :return: captcha number
    """
    global _session
    captcha_url = _captcha_pre + str(int(time.time() * 1000))
    r = _session.get(captcha_url)
    img = open('captcha.gif', 'wb')
    img.write(r.content)
    img.close()
    print 'save ok!'


def _getxsrf():
    """get _xsrf infos"""
    global _session
    html = _session.get(_url)
    pattern = re.compile(r'name="_xsrf" value="(.*)"', flags=0)
    _xsrf = pattern.findall(html.text)[0]
    return _xsrf


def _readconfig():
    """read login user info from config"""
    f = open('config', 'r')
    _cojson = json.loads(f.read())
    return _cojson['phone_num'], _cojson['password']


def login(email, password):
    """login"""
    # global default_headers
    print(u'--使用账号登录--')
    from yunsu import get_pincode
    xsrf = _getxsrf()
    print xsrf
    _getcaptcha()
    results = get_pincode()
    p = re.compile(r'<Result>(.*?)</Result>', re.M)
    captcha_code = p.findall(results)[0]
    captcha = str(captcha_code)
    postdata = {
        '_xsrf': xsrf,
        'password': password,
        'captcha': captcha,
        'email': email,
        'remember_me': 'true',
    }
    print postdata
    # captcha = raw_input(u'请查看图片，输入验证码：\n')
    os.remove('captcha.gif')
    _json = _session.post(_login_url, data=postdata)
    if _json.json()['r'] == 0:
        print(u'账号登录成功！')
        _xsrf = _getxsrf()
        p = re.compile(r'"r":0')

        # 更改密码
        password_data = {
            'password': 'Hdj2015',
            'password_repeat': 'Hdj2015',
            '_xsrf': _xsrf
        }
        response = _session.post(url='http://www.zhihu.com/settings/account/update_password', data=password_data)
        print response.content
        pp = re.compile(r'"success": true')
        p_status = pp.findall(response.content)
        if len(p_status) == 0:
            print u'修改密码失败。'
        print u'修改密码成功'

        # 修改个人简介
        profile_data = {
            '_xsrf': _xsrf,
            'method': 'save',
        }
        p_r = _session.post(url='http://www.zhihu.com/node/ProfileHeaderV2?params=%7B%22data%22%3A%7B%22description%22%3A%22%5Cu6211%5Cu662f%5Cu6d3b%5Cu52a8%5Cu5bb6http%3A%2F%2Fwww.huodongjia.com%2F%5Cu7684%5Cu5de5%5Cu4f5c%5Cu4eba%5Cu5458%5Cuff0c%5Cu63d0%5Cu4f9b%5Cu4f1a%5Cu8bae%5Cu67e5%5Cu8be2%5Cu4e0e%5Cu62a5%5Cu540d%5Cu670d%5Cu52a1%5Cuff0c%5Cu8bda%5Cu631a%5Cu9080%5Cu8bf7%5Cu60a8%5Cu4f7f%5Cu7528%5Cu6d3b%5Cu52a8%5Cu5bb6%5Cu62a5%5Cu540d%5Cu4f1a%5Cu8bae%5Cu3002%22%7D%7D', data=profile_data, headers=default_headers)
        # p = re.compile(r'"r":0')
        print p_r.content
        p_status = p.findall(p_r.content)
        if len(p_status) == 0:
            print u'修改个人简介失败。'
        print u'修改个人简介成功'

        # 设置关注话题
        data_4 = {
            '_xsrf': _xsrf,
            'follow_ids': '19800,3324,99,1990,12452,4217,2955'
        }
        r = _session.post(url='http://www.zhihu.com/topics/follow', data=data_4)
        print r.content
        p_status = p.findall(r.content)
        if len(p_status) == 0:
            print u'关注话题失败。'
        print u'关注话题成功'

        # 设置自我说明
        data_5 = {
            '_xsrf': _xsrf,
            'method': 'add_headline',
        }
        r_5 = _session.post(url='http://www.zhihu.com/node/Guide2?params=%7B%22headline%22%3A%22%5Cu79fb%5Cu52a8%5Cu4e92%5Cu8054%5Cu7f51%5Cu3001%5Cu4e92%5Cu8054%5Cu7f51%2B%5Cu3001%5Cu4e91%5Cu8ba1%5Cu7b97%22%7D', data=data_5, headers=default_headers)
        # print escape.to_unicode(r_5.request.body)
        print escape.to_unicode(r_5.content)
        p_status = p.findall(r_5.content)
        if len(p_status) == 0:
            print u'setting profile failed!'
        print u'setting profile ok!'

        # 关注活动家问题
        follow_data = {
            '_xsrf': _xsrf,
            'method': 'follow_question',
        }
        url_3_1 = 'http://www.zhihu.com/node/QuestionFollowBaseV2?params=%7B%22question_id%22%3A%222680990%22%7D'
        url_3_2 = 'http://www.zhihu.com/node/QuestionFollowBaseV2?params=%7B%22question_id%22%3A%222681057%22%7D'
        r_3_1 = _session.post(url=url_3_1, data=follow_data, headers=default_headers)
        print escape.to_unicode(r_3_1.content)
        r_3_2 = _session.post(url=url_3_2, data=follow_data, headers=default_headers)
        print escape.to_unicode(r_3_2.content)
        _session.cookies.clear()
    else:
        print '*' * 32
        print 'failed!'
        with open('wrongaccounts.txt', 'a') as fd:
            fd.write(str(email) + ' - ' + str(password) + 'login failed! maybe password has changed.\n')
        fd.close()

        _session.cookies.clear()


if __name__ == '__main__':
    # for account in get_accounts():
    #     try:
    #         login(account[0], account[1])
    #     except:
    #         with open('setting_log.txt', 'a') as fd:
    #             fd.write(str(account) + ' settingfailed!\n')
    login('jing95173yan@163.com', 'mgcuvs1')


