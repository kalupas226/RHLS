# -*- coding: utf-8 -*-

from gensim.models import word2vec
import mysql.connector

#mysql connection
connector = mysql.connector.connect(host="localhost", db="Research_System", user="root", passwd="tyogyakuten226", charset="utf8")
cursor = connector.cursor()

cursor.execute("TRUNCATE TABLE Synonym")
connector.commit()

#tfidf値を取得する
sql_webmap_tfidf = "select webmap_id, tfidf1, tfidf2, tfidf3, tfidf4, tfidf5 from Webmap_tfidf;"
sql_jinbutsu_tfidf = "select jinbutuden_id, tfidf1, tfidf2, tfidf3, tfidf4, tfidf5 from Jinbutsuden_tfidf"
sql_shishi_tfidf = "select hakodateshishi_id, tfidf1, tfidf2, tfidf3 tfidf4, tfidf5 from hakodateshishi_tfidf"

sql_tfidf = [sql_webmap_tfidf, sql_jinbutsu_tfidf, sql_shishi_tfidf]
#word2vec学習モデルの読み込み
model = word2vec.Word2Vec.load("./wiki.model")

for sql in sql_tfidf:
    cursor.execute(sql)
    tfidf_records = cursor.fetchall()
    for record in tfidf_records:
        for i in range(1,5):
            results = ["",""]
            try:
                results = model.wv.most_similar(positive=[record[i]])
            except KeyError:
                print("類義語が存在しません")
            synonymWord = ["","","","",""]
            for j, result in enumerate(results):
                print("i:"+str(j))
                if j>4:
                    break
                else:
                    try:
                        if result[0]:
                            synonymWord[j] = result[0]
                    except IndexError:
                        print("類義語なし")
            try:
            	cursor.execute('INSERT INTO Synonym (original_word, synonym1, synonym2, synonym3, synonym4, synonym5)\
                    VALUES( %s, %s, %s, %s, %s, %s)', (record[i],synonymWord[0],synonymWord[1],synonymWord[2],synonymWord[3],synonymWord[4]))
                connector.commit()
                print(record[i])
            except mysql.connector.Error as err:
            	print("重複したレコードが存在しています.")#実行したSQL文の確認
connector.close()
