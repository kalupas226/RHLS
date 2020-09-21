import pymysql.cursors
import re

conn = pymysql.connect(host='localhost',
                       db='Research_System',
                       user='root',
                       passwd='',
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor)

try:
    with conn.cursor() as cursor:
        cursor.execute('select id,name from jinbutsuden')
        records = cursor.fetchall()
        for record in records:
            print(re.sub(r' |　', '', record['name']))
            print(record['id'])
            rm_name = re.sub(r' |　', '', record['name'])
            cursor.execute('update jinbutsuden set name=\'%s\' where id=%d' % (rm_name, record['id']))
            conn.commit()
finally:
    print('hoge')
