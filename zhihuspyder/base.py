# -*- coding:utf-8 -*-
"""
    base.py
    ~~~~~~~

"""
import re
import json
import datetime
from torndb import Connection
from tornado.gen import coroutine
from requests.cookies import create_cookie, RequestsCookieJar
from tornado.concurrent import run_on_executor
from tornado.escape import to_unicode, url_escape
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

from zh_auth import login, requests, search_xsrf

import sys
reload(sys)
sys.setdefaultencoding('utf8')

db = Connection(host='127.0.0.1', database='zhihu', user='root', password='', charset='utf8')
executor = ThreadPoolExecutor(max_workers=16)


class GetTopics(object):
    def __init__(self):
        # self.executor = ThreadPoolExecutor(16)
        self.p_father = re.compile(r'<li data-id="(\d+)"><a href="(.*?)">(.*?)</a></li>')
        self.father_topic_uri = 'http://www.zhihu.com/topics'
        self.result = None

    def get_father_topics(self):
        try:
            self.result = requests.get(url=self.father_topic_uri)
        except:
            return
        if self.result.status_code != 200:
            print 'requests status code is {}'.format(self.result.status_code)
            return
        with open('father_topics.html', 'wb') as fd:
            fd.write(self.result.content)
        fd.close()
        return self.p_father.findall(self.result.content)

    def save_father_topics(self):
        now = str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        for topic in self.get_father_topics():
            sql = u'INSERT INTO topics (data_id, topic_name, user_counts, is_deleted, last_update) ' \
                  u'VALUES (%d, "%s", %d, %d, "%s")' % (int(topic[0]), to_unicode(topic[2]), 0, 0, now)
            print sql
            try:
                db.execute(sql)
                print 'save {} success'.format(str(topic))
            except RuntimeError as e:
                print 'save failed : {}'.format(str(e))


headers = {
    'Host': 'www.zhihu.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://www.zhihu.com/topics',
}


class GetSubclassTopics(object):
    def __init__(self):
        self.father_name = u'互联网'

    def get_subclass_topics(self):
        uri = 'http://www.zhihu.com/topics#{}'.format(self.father_name)
        print uri
        xsrf = search_xsrf('http://www.zhihu.com')
        print xsrf

        params = {"topic_id":112,"offset":0,"hash_id":"58689eac41efbb9fa11d680a06f2bbef"}
        params = url_escape(str(params), plus=False).replace('%27', '%22').replace('%20', '')
        print params
        print '\n'
        post_data = {
            '_xsrf': xsrf,
            'method': 'next',
            'params': params
        }

        try:
            response = requests.post(url='http://www.zhihu.com/node/TopicsPlazzaListV2', data=post_data, headers=headers)
            print response.request.body
            print response.status_code
            # if response.status_code != 200:
            #     print 'response status code :{}'.format(response.status_code)
            #     return
            # with open('subclass_topics.html', 'wb') as fd:
            #     fd.write(response.content)
            # fd.close()
        except IOError as e:
            print 'net or io wrong'


def get_topic_fans(url):
    # get start mi-id.
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print 'get users failed!'
        return
    soup = BeautifulSoup(r.content, 'lxml')
    first_user = soup.find(attrs={'class': 'zm-person-item'})
    mi_id = first_user.get('id', None)
    if mi_id:
        account = first_user.h2.a.get('href', '')
        name = first_user.h2.a.get_text()
        print mi_id, account, name
    else:
        return
    # began loop get users

    offset = 0
    _xsrf = search_xsrf()
    while True:
        print 'begin test.'
        post_data = {
            'offset': offset,
            '_xsrf': _xsrf,
            'start': mi_id[3:]
        }
        r = requests.post(url=url, data=post_data, headers=headers)
        if r.status_code != 200 and '"r":0' not in r.content:
            print r.content
            print r.status_code
            return
        soup_test = BeautifulSoup(r.content.replace('\\n', '').replace('\\"', '').replace('\\/', '/'), 'lxml')
        users_item = soup_test.find_all(attrs={'class': 'zm-person-item'})
        users_list = list()
        if users_item:
            for user_item in users_item:
                mi_id = user_item.get('id', None)
                user = user_item.find(attrs={'class': 'zm-list-content-title'})
                account = user.a.get('href', None)
                name = user.a.get_text()
                users_list.append((mi_id, account, name.decode('raw_unicode_escape')))
        print users_list
        offset += 20


def get_users(url):
    offset = 40
    xsrf = search_xsrf(requests, 'http://www.zhihu.com')
    start = ''
    p_mi = re.compile(r'<div class="zm-person-item" id="mi-(\d+)">', re.M)
    p_user = re.compile(r'<h2 class="zm-list-content-title"><a href="(.*?)">(.*?)</a></h2>', re.M)
    # first get follows
    try:
        r = requests.get(url, headers=headers)
        if r.status_code  != 200:
            pass        # Logging there
        mi_list = p_mi.findall(r.content)
        user_list = p_user.findall(r.content)
        users_info = zip(mi_list, user_list)
        with open('mark_user.txt', 'wb') as fd:
            fd.write(str(users_info[1]))
        fd.close()
        start = users_info[-1][0]
    except:
        print 'request method get failed.'
        return
    # sql = 'INSERT INTO users (user_number, user_name, user_account, last_update, is_queried, is_deleted) VALUES ("%s", "%s", "%s", "%s", 0, 0)'
    now = str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
    for user in users_info:
        # user = str(user[0]) + ', ' + to_unicode(user[1][1]) + ', ' + str(user[1][0]) + ', ' + str(now)
        sql = 'INSERT INTO users (user_number, user_name, user_account, last_update, is_queried, is_deleted) ' \
              'VALUES ("%s", "%s", "%s", "%s", 0, 0)' % (user[0], to_unicode(user[1][1]), user[1][0], str(now))
        try:
            db.execute(sql)
            print 'execute sql {} success'.format(sql)
        except RuntimeError as e:
            print 'failed this, look logging for detail!'
            continue


    # change page
    n = 1
    p_mi_v2 = re.compile(r'"mi-(\d+)">')
    p_user_v2 = re.compile(r'<h2 class="zm-list-content-title"><a href="(.*?)">(.*?)</a></h2>')
    while n:
        # offset += 40
        data = {
            '_xsrf': xsrf,
            'offset': offset,
            'start': start
        }
        r = requests.post(url='http://www.zhihu.com/topic/19550517/followers', data=data, headers=headers)
        content = r.content.replace(r'\"', '"').replace('\/', '/')
        if '"r":0' not in content:
            print 'get user list failed.'   # write loging
        with open('follows_content.html', 'wb') as fd:
            fd.write(content)
        fd.close()
        n = 0
        # mis = p_mi_v2.findall(r.content)
        # print mis
        # print len(mis)
        # users = p_user_v2.findall(r.content)
        # print users
        # print len(mis)

        mi_list = p_mi_v2.findall(content)
        user_list = p_user_v2.findall(content)
        users_info = zip(mi_list, user_list)

        print mi_list
        print user_list
        print users_info
        start = users_info[-1][0]
        for user in users_info:
            print user

        now = str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        for user in users_info:
            name = to_unicode(user[1][1])
            print name
            # user = str(user[0]) + ', ' + to_unicode(user[1][1]) + ', ' + str(user[1][0]) + ', ' + str(now)
            sql = 'INSERT INTO users (user_number, user_name, user_account, last_update, is_queried, is_deleted) ' \
                  'VALUES ("%s", "%s", "%s", "%s", 0, 0)' % (user[0], name, user[1][0], str(now))
            try:
                db.execute(sql)
                print 'execute sql {} success'.format(sql)
            except RuntimeError as e:
                print 'failed this, look logging for detail!'
                continue
        offset += 20


def get_personal_information(user):
    uri = 'http://www.zhihu.com' + str(user)
    print uri
    r = requests.get(uri, headers=headers)
    if r.status_code != 200:
        print 'get {} failed!'.format(uri)
        return
    soup = BeautifulSoup(r.content, "lxml")
    # get people main info
    main_info = soup.find(attrs={"class": 'zm-profile-header-main'})
    attention_info = soup.find(attrs={"class": 'zm-profile-side-following zg-clear'})
    # sex info
    sex = 2
    if main_info.find(attrs={'class': 'icon icon-profile-male'}):
        sex = 1
    elif main_info.find(attrs={'class': 'icon icon-profile-female'}):
        sex = 0
    else:
        pass
    print 'sex : {}'.format(sex)
    # social contact
    contact = ''
    contact_info = main_info.find(attrs={'class': 'zm-profile-header-user-weibo'})
    if contact_info:
        p = re.compile(r'href="(.*?)"', re.M)
        contact_info = str(contact_info)
        temp = p.findall(contact_info)
        if len(temp) == 0:
            pass
        else:
            contact = temp[0]
    print 'social contact(sina) : {}'.format(contact)
    # people's domicile
    domicile = ''
    domicile_info = main_info.find(attrs={'class': 'location item'})
    if domicile_info:
        domicile = domicile_info.get('title', '')
    print 'domicile : {}'.format(domicile)
    # location by self
    location_self = ''
    location_by_self = main_info.find(attrs={'class': 'business item'})
    if location_by_self:
        location_self = location_by_self.get('title', '')
    print 'location by self : {}'.format(location_self)
    # industry or employment - position
    industry = ''
    employment = ''
    position = ''
    employment_item = main_info.find(attrs={'class': 'employment item'})
    if employment_item:
        employment = employment_item.get('title', '')
    position_item = main_info.find(attrs={'class': 'position item'})
    if position_item:
        position = position_item.get('title', '')
    if True:
        industry = str(employment) + ' - ' + str(position)
    print 'employment : {}'.format(industry)
    # occupations
    # occupations = u'Now not need.'
    # print 'occupations : {}'.format(occupations)
    # education
    education_info = ''
    education = ''
    education_extra = ''
    education_item = main_info.find(attrs={'class': 'education item'})
    if education_item:
        education = education_item.get('title', '')
    education_extra_item = main_info.find(attrs={'class': 'education-extra item'})
    if education_extra_item:
        education_extra = education_extra_item.get('title', '')
    if True:
        education_info = str(education) + ' - ' + str(education_extra)
    print 'education information : {}'.format(education_info)
    # description
    description = ''
    description_info = main_info.find(attrs={'class': 'fold-item'})
    if description_info:
        description = description_info.span.get_text()
    print 'description : {}'.format(description)
    # fans follows numbers
    fans = 0
    follows = 0
    if attention_info:
        p = re.compile(r'<strong>(\d+)</strong>', re.M)
        numbers = p.findall(str(attention_info))
        if len(numbers) == 2:
            fans = numbers[0]
            follows = numbers[1]
    print 'fans number : {}'.format(fans)
    print 'follows number : {}'.format(follows)
    return {'sex': sex, 'social_contact': contact, 'domicile': domicile,
            'location_by_self': location_self, 'employment': industry, 'education': education_info,
            'description': description, 'fans': fans, 'follows': follows}


class GetSubclassFans(object):
    def __init__(self, uri):
        self.topic_uri = uri
        self.executor = ThreadPoolExecutor(max_workers=16)

    def get_topic_fans(self):
        # get start mi-id.
        url = self.topic_uri + '/followers'
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print 'get users failed!'
            return
        soup = BeautifulSoup(r.content, 'lxml')
        first_user = soup.find(attrs={'class': 'zm-person-item'})
        mi_id = first_user.get('id', None)
        if mi_id:
            account = first_user.h2.a.get('href', '')
            name = first_user.h2.a.get_text()
            print mi_id, account, name
        else:
            return
        # began loop get users

        offset = 0
        _xsrf = search_xsrf()
        while True:
            print 'begin test.'
            post_data = {
                'offset': offset,
                '_xsrf': _xsrf,
                'start': mi_id[3:]
            }
            r = requests.post(url=url, data=post_data, headers=headers)
            if r.status_code != 200 and '"r":0' not in r.content:
                print r.content
                print r.status_code
                return
            soup_test = BeautifulSoup(r.content.replace('\\n', '').replace('\\"', '').replace('\\/', '/'), 'lxml')
            users_item = soup_test.find_all(attrs={'class': 'zm-person-item'})
            users_list = list()
            if users_item:
                for user_item in users_item:
                    # p = re.compile(r'mi-(\d+)')
                    mi_id = str(user_item.get('id', None))
                    user = user_item.find(attrs={'class': 'zm-list-content-title'})
                    account = user.a.get('href', None)
                    name = user.a.get_text()
                    print (mi_id, account, name.decode('raw_unicode_escape'))
                    users_list.append((mi_id, account, name.decode('raw_unicode_escape')))
            # print users_list
            self.save_users(users_list)
            offset += 20

    @coroutine
    def save_users(self, users):
        yield self.execute_sql(users)

    @run_on_executor
    def execute_sql(self, users):
        now = str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        for user in users:
            sql = 'INSERT INTO users (user_number, user_account, user_name, last_update, is_queried, is_deleted) ' \
                  'VALUES ("%s", "%s", "%s", "%s", 0, 0)' % (user[0], user[1], user[2], now)
            db.execute(sql)
            print sql


class GetUserInfo(object):
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=16)

    def get_uid_account(self):
        sql = 'SELECT id, user_account FROM users'
        for row in db.query(sql):
            self.get_user_info(row.get('id'), row.get('user_account'))

    @coroutine
    def get_user_info(self, id, account):
        yield self.get_personal_information(id, account)

    @run_on_executor
    def save_user_info(self, info):
        # sql = 'INSERT INTO info (sex, fans_number, follows_number, social_contact, location_by_self, abstract, ' \
        #       'employment, domicile, educational, last_update, user_id_id) VALUES (%d, %d, %d, "%s", "%s", "%s", ' \
        #       '"%s", "%s", "%s", "%s", %d)'
        if info:
            now = str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
            sql = 'INSERT INTO info (sex, fans_number, follows_number, social_contact, location_by_self, abstract, ' \
                  'employment, domicile, educational, last_update, user_id_id) VALUES (%s, %s, %s, "%s", "%s", "%s", ' \
                  '"%s", "%s", "%s", "%s", %s)' % (info.get('sex', 2), info.get('fans', 0), info.get('follows', 0),
                  info.get('social_contact', ''), info.get('location_by_self', ''), info.get('description', ''),
                  info.get('employment', ''), info.get('domicile', ''), info.get('education', ''), now, info.get('user_id'))
            print sql
            db.execute(sql)

    @coroutine
    def get_personal_information(self, id, user):
        uri = 'http://www.zhihu.com' + str(user)
        print uri
        r = requests.get(uri, headers=headers)
        if r.status_code != 200:
            print 'get {} failed!'.format(uri)
            return
        soup = BeautifulSoup(r.content, "lxml")
        # get people main info
        main_info = soup.find(attrs={"class": 'zm-profile-header-main'})
        attention_info = soup.find(attrs={"class": 'zm-profile-side-following zg-clear'})
        # sex info
        sex = 2
        if main_info.find(attrs={'class': 'icon icon-profile-male'}):
            sex = 1
        elif main_info.find(attrs={'class': 'icon icon-profile-female'}):
            sex = 0
        else:
            pass
        print 'sex : {}'.format(sex)
        # social contact
        contact = ''
        contact_info = main_info.find(attrs={'class': 'zm-profile-header-user-weibo'})
        if contact_info:
            p = re.compile(r'href="(.*?)"', re.M)
            contact_info = str(contact_info)
            temp = p.findall(contact_info)
            if len(temp) == 0:
                pass
            else:
                contact = temp[0]
        print 'social contact(sina) : {}'.format(contact)
        # people's domicile
        domicile = ''
        domicile_info = main_info.find(attrs={'class': 'location item'})
        if domicile_info:
            domicile = domicile_info.get('title', '')
        print 'domicile : {}'.format(domicile)
        # location by self
        location_self = ''
        location_by_self = main_info.find(attrs={'class': 'business item'})
        if location_by_self:
            location_self = location_by_self.get('title', '')
        print 'location by self : {}'.format(location_self)
        # industry or employment - position
        industry = ''
        employment = ''
        position = ''
        employment_item = main_info.find(attrs={'class': 'employment item'})
        if employment_item:
            employment = employment_item.get('title', '')
        position_item = main_info.find(attrs={'class': 'position item'})
        if position_item:
            position = position_item.get('title', '')
        if True:
            industry = str(employment) + ' - ' + str(position)
        print 'employment : {}'.format(industry)
        # occupations
        # occupations = u'Now not need.'
        # print 'occupations : {}'.format(occupations)
        # education
        education_info = ''
        education = ''
        education_extra = ''
        education_item = main_info.find(attrs={'class': 'education item'})
        if education_item:
            education = education_item.get('title', '')
        education_extra_item = main_info.find(attrs={'class': 'education-extra item'})
        if education_extra_item:
            education_extra = education_extra_item.get('title', '')
        if True:
            education_info = str(education) + ' - ' + str(education_extra)
        print 'education information : {}'.format(education_info)
        # description
        description = ''
        description_info = main_info.find(attrs={'class': 'fold-item'})
        if description_info:
            description = description_info.span.get_text()
        print 'description : {}'.format(description)
        # fans follows numbers
        fans = 0
        follows = 0
        if attention_info:
            p = re.compile(r'<strong>(\d+)</strong>', re.M)
            numbers = p.findall(str(attention_info))
            if len(numbers) == 2:
                fans = numbers[0]
                follows = numbers[1]
        print 'fans number : {}'.format(fans)
        print 'follows number : {}'.format(follows)
        profile_info = {'user_id': id, 'sex': sex, 'social_contact': contact, 'domicile': domicile,
                        'location_by_self': location_self, 'employment': industry, 'education': education_info,
                        'description': description, 'fans': fans, 'follows': follows}
        yield self.save_user_info(profile_info)

if __name__ == '__main__':
    login()
    print requests.cookies
    # user_info = GetUserInfo()
    # user_info.get_uid_account()

    get_users = GetSubclassFans('http://www.zhihu.com/topic/19550517')
    get_users.get_topic_fans()

    # print get_personal_information('/people/zonyitoo')       # ok
    # xsrf = search_xsrf('http://www.zhihu.com')
    # get_topic_fans('http://www.zhihu.com/topic/19550517/followers')
    # get_users('http://www.zhihu.com/topic/19550517/followers')
    # topics = GetTopics()
    # topics.save_father_topics()
    # sub_topics = GetSubclassTopics()
    # sub_topics.get_subclass_topics()
