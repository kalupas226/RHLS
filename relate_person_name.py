import pymysql.cursors

conn = pymysql.connect(host='localhost',
                       db='Research_System',
                       user='root',
                       passwd='tyogyakuten226',
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor)

try:
    with conn.cursor() as cursor:
        get_jinbutsu_sql = "select id, name from jinbutsudens"
        cursor.execute(get_jinbutsu_sql)
        jinbutsu_records = cursor.fetchall()

        get_shishi_sql = "select id, paragraph_title, paragraph_body from hakodateshishi"
        cursor.execute(get_shishi_sql)
        shishi_records = cursor.fetchall()

        get_webmap_sql = "select id, title, description from webmaps"
        cursor.execute(get_bunkazai_sql)
        webmap_records = cursor.fetchall()

        get_digital_sql = "select id, title, contents from digitals"
        cursor.execute(get_digital_sql)
        digital_records = cursor.fetchall()

        print(jinbutsu_records[0])
        print(shishi_records[0])
        print(webmap_records[0])
        print(digital_records[0])