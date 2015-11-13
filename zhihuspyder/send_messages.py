# -*- coding:utf-8 -*-
"""
    send_messages.py
    ~~~~~~~~~~~~~~~~
    读取xlsx文件所有账户，并用这些账户登陆知乎，然后在这些账户中随机选择一个给目标账户发送私信
"""
import random
import time
from torndb import Connection
from concurrent.futures import ThreadPoolExecutor
# from tornado.concurrent import run_on_executor
from tornado.escape import to_unicode

from read_infos import get_accounts
from auth import Logging, Login
from db_config import info

thread_pool = ThreadPoolExecutor(8)
db = Connection(host=info.get('host', '127.0.0.1'), database=info.get('database', 'test'),
                user=info.get('user', 'root'), password=info.get('password', ''))


# @run_on_executor(executor='thread_pool')
def send_msg(account, token_id, msg):
    username, password, cookies = account[0][0], account[0][1], account[1]
    login = Login(username, password)
    login.initialize(cookies)
    if not login.islogin():
        login.login()
        if login.send_message(token_id, msg):
            print 'send ok!'
    if login.send_message(token_id, msg):
        print 'send ok!'


def get_to_users(accounts):
    msg = u''
    counts = len(accounts)
    if counts == 0:
        print 'no accounts login!'
        return
    sql = 'SELECT user_account FROM users'
    users = db.query(sql)
    for user in users:
        token_id = user.get('user_account')
        if token_id:
            n = random.randint(0, counts-1)
            account = accounts[n]
            print account, user.get('user_account', '')[8:], msg
            send_msg(account, user.get('user_account', '')[8:], msg)
            time.sleep(random.randint(5, 10))


def login_accounts():
    # read and login, save cookies.获得一组登陆账户
    accounts = get_accounts()
    if len(accounts) == 0:
        Logging.error(u'读取账户失败，请检查表格文件.')
    print accounts
    login_accounts = list()
    count = 0
    for account in accounts[:35]:
        cookies = 'cookies'+str(count)
        login = Login(account[0], account[1])
        login.initialize(cookies)
        if not login.login():
            import os
            os.remove('captcha.gif')
            Logging.error(u'账户{}登陆失败，请检查账户和密码')
            continue
        login_accounts.append((account, cookies))
        count += 1
    # print 'login accounts are: {}'.format(str(login_accounts))
    # 随机获取登陆账户并发送消息
    return login_accounts

if __name__ == '__main__':
    print login_accounts()
    # get_to_users(login_accounts())