# -*- coding: utf-8 -*-

import MeCab                    # 形態素解析器MeCab
import os
import math
import mysql.connector
import codecs

text = []
#mysql connection
connector = mysql.connector.connect(host="localhost", db="Research_System", user="root", passwd="tyogyakuten226", charset="utf8")
cursor = connector.cursor()

cursor.execute("TRUNCATE TABLE Jinbutsuden_tfidf")
connector.commit()

sql = "select name, description, id from Jinbutsuden;"
cursor.execute(sql)
records = cursor.fetchall()
for record in records:
    print(record[0])
    print(record[1])
    allText = ""
    if record[0]:
        allText += record[0].encode("utf-8")
    if record[1]:
        allText += record[1].encode("utf-8")
    text.append(allText)

# for record in records:
#     print record[0]
#     print record[1]
#     allText = ""
#     if record[0]:
#         allText += record[0].encode("utf-8")
#     if record[1]:
#         allText += record[1].encode("utf-8")
#     if record[2]:
#         allText += record[2].encode("utf-8")
#     text.append(allText)

txt_num = len(text)
print('total texts:%d' % txt_num)

fv_tf = []                      # ある文書中の単語の出現回数を格納するための配列
fv_df = {}                      # 単語の出現文書数を格納するためのディクショナリ
word_count = []                 # 単語の総出現回数を格納するための配列

fv_tf_idf = []                  # ある文書中の単語の特徴量を格納するための配列

count_flag = {}                 # fv_dfを計算する上で必要なフラグを格納するためのディクショナリ

# 各文書の形態素解析と、単語の出現回数の計算
for txt_id, txt in enumerate(text):
    # MeCabを使うための初期化
    tagger = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
    node = tagger.parseToNode(txt)


    fv = {}                     # 単語の出現回数を格納するためのディクショナリ
    words = 0                   # ある文書の単語の総出現回数

    for word in fv_df.keys():
        count_flag[word] = False
    while node.next:
        meta = node.feature.split(",")
        if meta[0] == '名詞':
            surface = node.surface # 形態素解析により得られた単語
        else:
            surface = ""

        node = node.next
        #surface = node.surface # 形態素解析により得られた単語

        words += 1

        fv[surface] = fv.get(surface, 0) + 1 # fvにキー値がsurfaceの要素があれば、それに1を加え、なければ新しくキー値がsurfaceの要素をディクショナリに加え、値を1にする

        if surface in fv_df.keys(): # fv_dfにキー値がsurfaceの要素があれば
            if count_flag[surface] == False: # フラグを確認し，Falseであれば
                fv_df[surface] += 1 # 出現文書数を1増やす
                count_flag[surface] = True # フラグをTrueにする
        else:                 # fv_dfにキー値がsurfaceの要素がなければ
            fv_df[surface] = 1 # 新たにキー値がsurfaceの要素を作り，値として1を代入する
            count_flag[surface] = True # フラグをTrueにする

    fv_tf.append(fv)
    word_count.append(words)

# tf, idf, tf-idfなどの計算
for txt_id, fv in enumerate(fv_tf):
    tf = {}
    idf = {}
    tf_idf = {}
    for key in fv.keys():
        tf[key] = float(fv[key]) / word_count[txt_id] # tfの計算
        idf[key] = math.log(float(txt_num) / fv_df[key]) # idfの計算
        tf_idf[key] = (tf[key] * idf[key], tf[key], idf[key], fv[key], fv_df[key]) # tf-idfその他の計算
    tf_idf = sorted(tf_idf.items(), key=lambda x:x[1][0], reverse=True) # 得られたディクショナリtf-idfを、tf[key]*idf[key](tf-idf値)で降順ソート(処理後にはtf-idfはリストオブジェクトになっている)
    fv_tf_idf.append(tf_idf)


# 出力
f = open("tfidf_jinbutsuden.txt", "w")
i = 0
for fv,record in zip(fv_tf_idf,records):
    print('This is the tf-idf of text %d' % i)
    print(txt_id)
    print('total words:%d' % word_count[i])
    #f.write(word_count[txt_id])
    print(record[0])
    id = record[2]
    title = record[0].encode("utf-8")
    f.write('\n')
    f.write(str(id) + " " +title)
    f.write('\n')
    j=0
    count = 0
    top_tfidf = []
    for word, tf_idf in fv:
        print('%s\ttf-idf:%lf\ttf:%lf\tidf:%lf\tterm_count:%d\tdocument_count:%d' % (word, tf_idf[0], tf_idf[1], tf_idf[2], tf_idf[3], tf_idf[4])) # 左から順に、単語、tf-idf値、tf値、idf値、その文書中の単語の出現回数、その単語の出現文書数(これは単語ごとに同じ値をとる)
        if count < 5:
            top_tfidf.append(word)
        count += 1
        f.write(word)
        f.write('\ttfidf:')
        f.write(str(tf_idf[0]))
        f.write('\n')

    f.write('\n')

    for i in range(5):
        if not top_tfidf[i]:
            top_tfidf.append("")

    cursor.execute('INSERT INTO Jinbutsuden_tfidf (jinbutuden_id, tfidf1, tfidf2, tfidf3, tfidf4, tfidf5)\
      VALUES( %s, %s, %s, %s, %s, %s)', (id, top_tfidf[0], top_tfidf[1], top_tfidf[2], top_tfidf[3], top_tfidf[4]))
    connector.commit()

f.close()
connector.close()
