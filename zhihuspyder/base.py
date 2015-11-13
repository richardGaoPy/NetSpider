# -*- coding:utf-8 -*-
"""
    base.py
    ~~~~~~~
"""
import re
import datetime
import json
import requests
from torndb import Connection
from tornado.gen import coroutine
from tornado.concurrent import run_on_executor
from tornado.escape import to_unicode, url_escape
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup

# import time
# import random

# from zh_auth import search_xsrf

# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

mysql_config = {
   
}


class ZHBase(object):
    def __init__(self):
        self.db = Connection(host=mysql_config.get('host', '127.0.0.1'), database=mysql_config.get('database', 'test'),
                             user=mysql_config.get('user', 'root'), password=mysql_config.get('password', ''))
        self.executor = ThreadPoolExecutor(max_workers=4)
        # self.requests = requests.Session()
        self.headers = {
            'Host': 'www.zhihu.com',
            'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:42.0) Gecko/20100101 Firefox/42.0',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'http://www.zhihu.com/topics',
        }


class GetTopics(ZHBase):
    def __init__(self, login):
        ZHBase.__init__(self)
        self.p_father = re.compile(r'<li data-id="(\d+)"><a href="(.*?)">(.*?)</a></li>')
        self.father_topic_uri = 'http://www.zhihu.com/topics'
        self.requests = login.requests

    def get_father_topics(self):
        try:
            result = self.requests.get(url=self.father_topic_uri)
        except RuntimeError as e:
            print 'curl father topic failed!'           # Write logging
            print e
        if result.status_code != 200:
            print 'requests status code is {}'.format(result.status_code)
            return
        return self.p_father.findall(result.content)

    def save_father_topics(self):
        now = str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        for topic in self.get_father_topics():
            sql = u'INSERT INTO topics (data_id, topic_name, user_counts, is_deleted, last_update) ' \
                  u'VALUES (%d, "%s", %d, %d, "%s")' % (int(topic[0]), to_unicode(topic[2]), 0, 0, now)
            print sql
            try:
                self.db.execute(sql)
                print 'save {} success'.format(str(topic))
            except RuntimeError as e:
                print 'save failed : {}'.format(str(e))


class GetSubclassTopics(ZHBase):
    def __init__(self, login):
        ZHBase.__init__(self)
        self.uri = 'http://www.zhihu.com/node/TopicsPlazzaListV2'
        self.requests = login.requests
        self.get_xsrf = login.get_xsrf()

    def get_father_info(self):
        sql = 'SELECT data_id FROM topics'
        try:
            return self.db.query(sql)
        except IOError as e:
            return []

    def get_subclass_topics(self):
        topics = self.get_father_info()
        if len(topics) == 0:
            return
        r = self.requests.get(url='http://www.zhihu.com/topics', headers=self.headers)
        if r.status_code != 200:
            print 'request topics failed!'
            return
        # with open('topics_home.html', 'wb') as fd:
        #     fd.write(r.content)
        # fd.close()
        p = re.compile(r'"user_hash":"(.*?)"', re.M)
        user_hash = p.findall(r.content)
        if len(user_hash) == 0:
            print 'get user hash failed!'
            return
        hash_id = user_hash[0]
        xsrf = self.get_xsrf
        print hash_id
        for topic in topics[:2]:
            print 'now get topic number {}`s subclass'.format(str(topic))
            offset = 0
            while True:
                fd = open('subtopics.txt', 'a')
                # uri = self.uri + '?_xsrf={}&method=next&'.format(xsrf) + params
                uri = self.uri + '?' + 'method=next&params=%7B%22topic_id%22%3A' + str(topic.get('data_id')) + \
                      '%2C%22offset%22%3A' + str(offset) + '%2C%22hash_id%22%3A%22' + str(hash_id) + '%22%7D&_xsrf=' + str(xsrf)
                r = self.requests.post(url=uri, data={}, headers=self.headers)
                if '"r":0' not in r.content:
                    print 'curl subclass topics failed!'
                    return
                contents = json.loads(r.content.replace('\\n', '').replace('\\"', '').replace('\\/', '/')).get('msg')
                if len(contents) == 0:
                    break
                for div in contents:
                    now = str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
                    soup = BeautifulSoup(div, "lxml")
                    try:
                        item = soup.find(attrs={'class': 'blk'})
                        name = item.a.strong.get_text()
                        description = item.p.get_text()
                        topic_id = item.a.get('href')[7:]
                        sql = 'INSERT INTO subclass_topics (topic_id, sub_topic_name, description, user_counts, ' \
                              'is_self, is_deleted, last_update, father_topic_id_id) VALUES ' \
                              '("%s", "%s", "%s", 0, 0, 0, "%s", 1)' % (topic_id, name, description, now)
                        print sql
                        try:
                            self.db.execute(sql)
                        except:
                            print 'failed!'
                            continue
                    except RuntimeError as e:
                        # print soup.find(attrs={'class': 'blk'})
                        print 'failed in {}'.format(str(div))
                        continue
                print '\n\n'
                # with open('sub_topics' + str(offset) + '.html', 'wb') as fd:
                #     fd.write(str(contents))
                fd.close()
                offset += 20


class GetSubclassFans(ZHBase):
    def __init__(self, uri, login):
        ZHBase.__init__(self)
        self.topic_uri = uri
        self.requests = login.requests
        self.get_xsrf = login.get_xsrf()

    def get_topic_fans(self):
        # get start mi-id.
        url = self.topic_uri + '/followers'
        r = self.requests.get(url, headers=self.headers)
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
            with open('mark_location.txt', 'a') as fd:
                fd.write('this loop begin at : \n{}'.format(str((mi_id, account, name))))
                fd.write('\n')
        else:
            return
        # began loop get users

        offset = 0
        _xsrf = self.get_xsrf
        n = 0
        while n < 11:
            print 'begin test.'
            post_data = {
                'offset': offset,
                '_xsrf': _xsrf,
                'start': mi_id[3:]
            }
            r = self.requests.post(url=url, data=post_data, headers=self.headers)
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
            self.save_users(users_list)
            # time.sleep(random.randint(20, 30))
            offset += 20
            n += 1

    # @coroutine
    def save_users(self, users):
        yield self.execute_sql(users)

    @run_on_executor
    def execute_sql(self, users):
        now = str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
        for user in users:
            try:
                sql = 'INSERT INTO users (user_number, user_account, user_name, last_update, is_queried, is_deleted) ' \
                      'VALUES ("%s", "%s", "%s", "%s", 0, 0)' % (user[0], user[1], user[2], now)
                self.db.execute(sql)
                print sql
            except:
                with open('mark_location_failed.txt', 'a') as fd:
                    fd.write(str(user) + '\n')
                fd.close()


class GetUserInfo(ZHBase):
    def __init__(self, login):
        ZHBase.__init__(self)
        self.requests = login.requests

    def get_uid_account(self):
        sql = 'SELECT id, user_account FROM users'
        for row in self.db.query(sql):
            sql = 'UPDATE users SET is_queried=1 WHERE id=%d' % int(row.get('id'))
            self.db.execute(sql)
            self.get_user_info(row.get('id'), row.get('user_account'))

    @coroutine
    def get_user_info(self, uid, account):
        yield self.get_personal_information(uid, account)

    # @run_on_executor
    def save_user_info(self, info):
        print '*' * 32
        if info:
            now = str(datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'))
            sql = 'INSERT INTO info (sex, fans_number, follows_number, social_contact, location_by_self, abstract, ' \
                  'employment, domicile, educational, last_update, user_id_id) VALUES (%s, %s, %s, "%s", "%s", "%s", ' \
                  '"%s", "%s", "%s", "%s", %s)' % (info.get('sex', 2), info.get('fans', 0), info.get('follows', 0),
                  info.get('social_contact', ''), info.get('location_by_self', ''), info.get('description', ''),
                  info.get('employment', ''), info.get('domicile', ''), info.get('education', ''), now, info.get('user_id'))
            print sql
            self.db.execute(sql)

    @coroutine
    def get_personal_information(self, id, user):
        uri = 'http://www.zhihu.com' + str(user)
        print uri
        r = self.requests.get(uri, headers=self.headers)
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
        self.save_user_info(profile_info)
        print profile_info

# if __name__ == '__main__':
#     if login():
#         print 'Spider start.'
#         topics = GetTopics()
#         topics.save_father_topics()
#
#         sub_topics = GetSubclassTopics()
#         sub_topics.get_subclass_topics()
#
#         user_info = GetUserInfo()
#         user_info.get_uid_account()
#
#         get_users = GetSubclassFans('http://www.zhihu.com/topic/19550517')
#         get_users.get_topic_fans()
