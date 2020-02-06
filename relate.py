# -*- coding: utf-8 -*-
import mysql.connector

connector = mysql.connector.connect(host="localhost", db="Research_System", user="root", passwd="tyogyakuten226", charset="utf8")
cursor = connector.cursor()

# cursor.execute("TRUNCATE TABLE Relation_with_hakodateshishi")
# cursor.execute("TRUNCATE TABLE Relation_with_jinbutsuden")
# cursor.execute("TRUNCATE TABLE Relation_with_hakodateshishi_more")
# cursor.execute("TRUNCATE TABLE Relation_with_jinbutsuden_more")
cursor.execute("TRUNCATE TABLE Relation_with_shishi")
cursor.execute("TRUNCATE TABLE Relation_with_jinbutsu")
connector.commit()

#それぞれの特徴語の類義語との一致を調べる関数
def synonymMatch(record1,record2):
    sql_synonym = "select synonym1,synonym2,synonym3,synonym4,synonym5 from Synonym where original_word=%s"
    cursor.execute(sql_synonym, (record1,))
    synonym_words = cursor.fetchall()
    if synonym_words:
        synonym_words = synonym_words[0]
        for synonym in synonym_words:
            if ''.join(synonym) == record2:
                return record1 + "(" + synonym + ")"
    else:
        return False

#文化財のtfidf
sql_webmap_tfidf = "select webmap_id, tfidf1, tfidf2, tfidf3, tfidf4, tfidf5 from Webmap_tfidf;"
cursor.execute(sql_webmap_tfidf)
webmap_tfidf_records = cursor.fetchall()

#函館市史のtfidf
sql_shishi_tfidf = "select hakodateshishi_id, tfidf1, tfidf2, tfidf3, tfidf4, tfidf5 from hakodateshishi_tfidf;"
cursor.execute(sql_shishi_tfidf)
shishi_tfidf_records = cursor.fetchall()

id = 0

for webmap_record in webmap_tfidf_records:
    for shishi_record in shishi_tfidf_records:
        id_flag = 0
        r_word = ["","","","",""]
        for i in range(1,6):
            for j in range(1,6):
                if webmap_record[i] and shishi_record[j]:
                    synonym = synonymMatch(webmap_record[i],shishi_record[j])
                    if webmap_record[i] == shishi_record[j] or synonym:
                        if id_flag==0:
                            id+=1
                            id_flag=1
                        if webmap_record[i] == shishi_record[j]:
                            r_word[i-1] = webmap_record[i]
                        else:
                            r_word[i-1] = synonym
                        match_words = 0
                        for w in r_word:
                            if w:
                                match_words += 1
                        sql_webmap_url = "select url from webmap where id=%s"
                        sql_shishi_url = "select url from hakodateshishi where id=%s"
                        cursor.execute(sql_webmap_url, (webmap_record[0],))
                        webmap_url = cursor.fetchall()
                        cursor.execute(sql_shishi_url, (shishi_record[0],))
                        shishi_url = cursor.fetchall()
                        print(id, webmap_record[0], shishi_record[0], r_word[0],r_word[1],r_word[2],r_word[3],r_word[4], match_words, str(webmap_url[0]), str(shishi_url[0]))
                        cursor.execute('INSERT INTO Relation_with_shishi (id, webmap_id, shishi_id, word1, word2, word3, word4, word5, match_words, \
                            webmap_url, shishi_url) \
                            VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE \
                            webmap_id=%s, shishi_id=%s, word1=%s, word2=%s, word3=%s, word4=%s, word5=%s, match_words=%s,webmap_url=%s, shishi_url=%s',
                            (id, webmap_record[0], shishi_record[0], r_word[0],r_word[1],r_word[2],r_word[3],r_word[4], match_words, str(webmap_url[0]), str(shishi_url[0]),
                            webmap_record[0], shishi_record[0], r_word[0],r_word[1],r_word[2],r_word[3],r_word[4], match_words, str(webmap_url[0]), str(shishi_url[0])))
                        connector.commit()
                        # if webmap_record[i] == shishi_record[j]:
                        #     cursor.execute('INSERT INTO Relation_with_hakodateshishi (webmap_id, hakodateshishi_id, relate_word, webmap_url, hakodateshishi_url)\
                        #       VALUES( %s, %s, %s, %s, %s)', (webmap_record[0], shishi_record[0], webmap_record[i], str(webmap_url[0]), str(shishi_url[0])))
                        #     connector.commit()
                        # if match_words>1:
                        #     cursor.execute('INSERT INTO Relation_with_hakodateshishi_more (webmap_id, hakodateshishi_id, word1, word2, word3, word4, word5, \
                        #     webmap_url, shishi_url) \
                        #         VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        #         (webmap_record[0], shishi_record[0], r_word[0],r_word[1],r_word[2],r_word[3],r_word[4],str(webmap_url[0]), str(shishi_url[0])))
                        #     print(webmap_record[0], shishi_record[0], r_word[0],r_word[1],r_word[2],r_word[3],r_word[4],str(webmap_url[0]), str(shishi_url[0]))
                        #     connector.commit()
                        #     break
#
#人物伝のtfidf
sql_jinbutsu_tfidf = "select jinbutuden_id, tfidf1, tfidf2, tfidf3, tfidf4, tfidf5 from jinbutsuden_tfidf"
cursor.execute(sql_jinbutsu_tfidf)
jinbutsu_tfidf_records = cursor.fetchall()

id = 0
for webmap_record in webmap_tfidf_records:
    for jinbutsu_record in jinbutsu_tfidf_records:
        id_flag = 0
        r_word = ["","","","",""]
        for i in range(1,6):
            for j in range(1,6):
                if webmap_record[i] and jinbutsu_record[j]:
                    synonym = synonymMatch(webmap_record[i], jinbutsu_record[j])
                    if webmap_record[i] == jinbutsu_record[j] or synonym:
                        if id_flag==0:
                            id+=1
                            id_flag=1
                        if webmap_record[i] == jinbutsu_record[j]:
                            r_word[i-1] = webmap_record[i]
                        else:
                            r_word[i-1] = synonym
                        match_words = 0
                        for w in r_word:
                            if w:
                                match_words += 1
                        sql_webmap_url = "select url from webmap where id=%s"
                        sql_jinbutsu_url = "select url from jinbutsuden where id=%s"
                        cursor.execute(sql_webmap_url, (webmap_record[0],))
                        webmap_url = cursor.fetchall()
                        cursor.execute(sql_jinbutsu_url, (jinbutsu_record[0],))
                        jinbutsu_url = cursor.fetchall()
                        cursor.execute('INSERT INTO Relation_with_jinbutsu (id, webmap_id, jinbutsu_id, word1, word2, word3, word4, word5, match_words, \
                            webmap_url, jinbutsu_url) \
                            VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE \
                            webmap_id=%s, jinbutsu_id=%s, word1=%s, word2=%s, word3=%s, word4=%s, word5=%s, match_words=%s,webmap_url=%s, jinbutsu_url=%s',
                            (id, webmap_record[0], jinbutsu_record[0], r_word[0],r_word[1],r_word[2],r_word[3],r_word[4], match_words, str(webmap_url[0]), str(jinbutsu_url[0]),
                            webmap_record[0], jinbutsu_record[0], r_word[0],r_word[1],r_word[2],r_word[3],r_word[4], match_words, str(webmap_url[0]), str(jinbutsu_url[0])))
                        print(id, webmap_record[0], jinbutsu_record[0], r_word[0],r_word[1],r_word[2],r_word[3],r_word[4], match_words, str(webmap_url[0]), str(jinbutsu_url[0]))
                        connector.commit()
                        # if webmap_record[i] == jinbutsu_record[j]:
                        #     cursor.execute('INSERT INTO Relation_with_jinbutsuden (webmap_id, jinbutsuden_id, relate_word, webmap_url, jinbutsuden_url)\
                        #     VALUES( %s, %s, %s, %s, %s)', (webmap_record[0], jinbutsu_record[0], webmap_record[i], str(webmap_url[0]), str(jinbutsu_url[0])))
                        #     connector.commit()
                        # if word_len>1:
                        #     print(word_len)
                        #     cursor.execute('INSERT INTO Relation_with_jinbutsuden_more (webmap_id, jinbutsuden_id, word1, word2, word3, word4, word5, \
                        #     webmap_url, jinbutsuden_url) \
                        #         VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        #         (webmap_record[0], jinbutsu_record[0], r_word[0],r_word[1],r_word[2],r_word[3],r_word[4],str(webmap_url[0]), str(jinbutsu_url[0])))
                        #     connector.commit()
                        #     break

connector.close()
