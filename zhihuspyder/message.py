# -*- coding:utf-8 -*-
"""
    message.py
    ~~~~~~~~~~
    send message to user
"""
# from zh_auth import *
import re
from tornado import escape
# from torndb import Connection

# db = Connection(host='127.0.0.1', database='zhihu', user='root', password='')

default_headers = {'X-Requested-With': 'XMLHttpRequest',
                   'Referer': 'http://www.zhihu.com',
                   'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; WOW64)'
                                 ' AppleWebKit/537.36 (KHTML, like Gecko)'
                                 ' Chrome/43.0.2357.132 Safari/537.36',
                   'Host': 'www.zhihu.com'}


def send_message(login=None, url_token='', message=''):
    url = u'http://www.zhihu.com/node/MemberProfileCardV2?params='
    url_params = '{"url_token":"%s"}' % url_token
    escape_url = escape.url_escape(url_params, plus=False)
    url += escape_url
    r = login.requests.get(url=url, headers=default_headers)
    p = re.compile(r'data-pm-hash="(.*?)">', re.M)
    dd = p.findall(r.content)
    if len(dd) == 0:
        return
    dxsrf = login.get_xsrf()
    msg_data = {
        'member_id': str(dd[0]),
        'content': escape.to_unicode(message),
        'token': '',
        '_xsrf': dxsrf,
    }
    print msg_data
    uri = u'http://www.zhihu.com/inbox/post'
    msg_r = login.requests.post(url=uri, data=msg_data, headers=default_headers)
    print msg_r.content
    p = re.compile(r'"r":0', re.S)
    send_status = p.findall(msg_r.content)
    if len(send_status) == 0:
        print 'Send message failed!'
        return False
    print 'Send message OK!'
    return True


# if __name__ == '__main__':
#     login()
#     sql = 'SELECT user_account FROM users'
#     count = 0
#     accounts = list()
#     for account in db.query(sql):
#         accounts.append(account.get('user_account'))
#     print accounts
#     count = 0
#     for account in accounts:
#         try:
#             status = send_message(account[8:], 'hello')
#             if not status:
#                 print count
#                 break
#             count += 1
#         except RuntimeError as e:
#             print e
#     print count
#     print len(accounts)
