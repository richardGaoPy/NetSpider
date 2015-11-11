# -*- coding:utf8 -*-

import json
import requests
import re
import datetime
import MySQLdb


from multiprocessing import Pool

#  自己的数据库
db_conf = {
   
}

db = MySQLdb.connect(host=db_conf.get('host'), user=db_conf.get('user'), port=db_conf.get('port'),
                     passwd=db_conf.get('password'), db=db_conf.get('db'), charset='utf8')
cursor = db.cursor()

uris = [
    'http://www.228.com.cn/s/yanchanghui/?j=1&p=%d',
    'http://www.228.com.cn/s/huajuwutaiju/?j=1&p=%d',
    'http://www.228.com.cn/s/yinyuehui/?j=1&p=%d',
    'http://www.228.com.cn/s/wudaobalei/?j=1&p=%d',
    'http://www.228.com.cn/s/xiquzongyi/?j=1&p=%d',
    'http://www.228.com.cn/s/tiyusaishi/?j=1&p=%d',
    'http://www.228.com.cn/s/ertongqinzi/?j=1&p=%d',
]

# uris = [
#     'http://www.228.com.cn/s/yanchanghui/?j=1&p=%d',
# ]

ticket_url = u'http://www.228.com.cn/ticket-%s.html'


def get_products(uri):
    """"""
    count = 1
    while True:
        url = uri % count
        r = requests.get(url)
        data = json.loads(r.text)
        products = data.get('products')
        if len(products) == 0:
            break
        now = datetime.datetime.utcnow()
        for product in products:
           try:
                item = dict()
                item['title'] = product.get('name')
                item['type'] = product.get('typeaname')
                item['price'] = product.get('prices')
                item['city'] = product.get('cityname')
                item['room'] = product.get('vname')
                item['date'] = product.get('alldate')
                item['name'] = product.get('performer')
                ticket_id = product.get('productid')
                ticket_uri = ticket_url % ticket_id
                item['time'], item['content'] = get_time_content(ticket_uri)

                sql = u"INSERT INTO yongle.live_house (h_title, h_type, h_price, h_content, created_at, is_deleted) VALUES " \
                      u"('%s', '%s', '%s', '%s', '%s', 0)" % (item['title'], item['type'], item['price'], item['content'], now)
                print sql
                cursor.execute(sql)
                db.commit()
                print 'oh, yes!!!'
                lid = int(cursor.lastrowid)
                sql_city = u"INSERT INTO yongle.live_house_city (h_city, h_room, created_at, lid_id) VALUES " \
                           u"('%s', '%s', '%s', %d)" % (item['city'], item['room'], now, lid)
                # print sql_city
                sql_date = u"INSERT INTO yongle.live_house_date (h_date, h_time, created_at, lid_id) VALUES " \
                           u"('%s', '%s', '%s', %d)" % (item['date'], item['time'], now, lid)
                # print sql_date
                sql_name = u"INSERT INTO yongle.live_house_name (h_name, lid_id) VALUES ('%s', %d)" % (item['name'], lid)
                # print sql_name
                cursor.execute(sql_city)
                cursor.execute(sql_date)
                cursor.execute(sql_name)
                db.commit()
                # time.sleep(random.randint(3, 5))
           except:
                with open('logging.txt', 'w+') as fd:
                    fd.write(str(product.get('name')) + ' failed!')
                    fd.write('\n')
                fd.close()
                print 'oh, no!'
                continue
        # print products_list
        count += 1
        # time.sleep(random.randint(5, 8))


def get_time_content(url):
    r = requests.get(url)
    dd = r.text.replace("'", "")
    r_time = re.compile(r'<li type="date" event="1" d="(.*?)" cc="(.*?)" title="(.*?)">')
    items = r_time.findall(dd)
    # print text      # date list
    time = []
    for i in items:
        time.append(i[2])
    time_str = ','.join(time)
    # print time_str  # time results.

    r_infos = re.compile(r'<div class="lives-info">(.*?)<div class="lives-info" style="display:none;">',
                         re.S | re.M)
    content = r_infos.findall(dd)[0]
    content = u'<div class="lives-info">' + content
    content = content.replace("'", "")
    # print content
    return time_str, content


if __name__ == "__main__":
    print '*' * 32
    # pool = Pool(4)
    # pool.map(get_products, uris)
    # pool.close()
    # pool.join()
    # db.close()
    # os.system('halt')
    for uri in uris:
        get_products(uri)