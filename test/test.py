#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pythonでアシアルブログの単語ランキングを算出する
[前提]アシアルブログの記事詳細はhttp://blog.asial.co.jp/[0-9]{4}の形式になっている
1. TOPサイトから上記形式のhrefを全て抽出する
2. 1で取得したURLを全てクローリングし、BODYタグの全ての全角文字を抽出する
3. 2で抽出した全角文字を形態素解析に掛けて、一般名詞のみを抽出する
4. 3で取得した一般名詞をTF解析で単語頻出度を算出する
5. 最終的にmatplotlibで円グラフに上位10件を表示する

Created on Wed Apr 12 11:38:42 2017

@author: eguchi
"""
import unicodedata
import requests as req
from bs4 import BeautifulSoup as bs
import MeCab as mc
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.font_manager
import pylab
import re

# 定数(と言って良いのかは微妙ですが)
BASE_URL = 'http://blog.asial.co.jp/'
EXCLUDE_STR_LIST = ['年月日', '年月', 'アシ', 'アシアル', 'アル', '情報', '株式会社', '全国']
TTF_PATH = '/Users/hogehoge/anaconda/lib/python3.6/site-packages/matplotlib/mpl-data/fonts/ttf/ipam.ttf'

# 1. TOPサイトからhttp://blog.asial.co.jp/[0-9]{4}の形式のhrefを全て抽出する
html = req.get(BASE_URL).text
# BeautifulSoup4でHTMLを解析
soup = bs(html, 'html.parser')
for script in soup(["script", "style"]):
    script.extract()

# 記事詳細のlinkのみを取得
blogs = []
for link in soup.select('a[href]'):
    if (re.match('^/[0-9]{4}$', link.attrs['href'])):
        blogs.append(BASE_URL + link.attrs['href'])

# 2. 1で取得したURLを全てクローリングし、BODYタグの全ての全角文字を抽出する
# 全てのblogを走査
contents_lo = ''
for blog in blogs:
    html = req.get(blog).text
    # BeautifulSoupでHTMLを解析
    soup = bs(html, 'html.parser')
    for script in soup(["script", "style"]):
        script.extract()
        # bodyコンテンツ内のinner textのみを抽出
    contents = soup.find('body').get_text()
    # extractで救いきれなかったので、unicodedata.east_asian_widthで全角かどうか判定
    for uniStr in contents:
        str_width = unicodedata.east_asian_width(uniStr)
        if str_width == 'W':
            contents_lo += uniStr

# 3. 2で抽出した全角文字を形態素解析に掛けて、一般名詞のみを抽出する
# 形態素解析にかけて、一般名詞だけを抽出
m = mc.Tagger('mecabrc')
mecab_result = m.parse(contents_lo)
info_of_words = mecab_result.split('\n')
words = []
for info in info_of_words:
    if '\t' in info:
        kind = info.split('\t')[1].split(',')[0]
        category = info.split('\t')[1].split(',')[1]
        if kind == '名詞' and category == '一般' and (info.split('\t')[0] not in EXCLUDE_STR_LIST):
            words.append(info.split('\t')[0])

# 4. 3で取得した一般名詞をTF解析で単語頻出度を算出する
# TF解析で単語数を取得する
vectorizer = CountVectorizer(min_df=1)
tf_idf_result = vectorizer.fit_transform([' '.join(words)])
# スコアの配列を取得
tf_idf_result_array = tf_idf_result.toarray()

# ラベルを取得
feature_names = vectorizer.get_feature_names()

# スコアとラベルが一対になるように辞書型に変換(ついでに小数点の第3位切り捨て)
dic = {}
for k, v in enumerate(feature_names):
    dic[v] = round(tf_idf_result_array[0][k], 3)

# 辞書型をvalueで降順sortしてｌistにして返却
sorted_list = sorted(dic.items(), key=lambda x: x[1], reverse=True)
plot_value = np.zeros([10])
plot_label = [0 for i in range(10)]
i = 0
for rank in sorted_list:
    if i >= 10:
        break
    plot_value[i] = rank[1]
    plot_label[i] = rank[0] + '(' + str(rank[1]) + ')'
    i += 1

# 5. 最終的にmatplotlibで円グラフに上位10件を表示する
# マッププロット
prop = matplotlib.font_manager.FontProperties(fname=TTF_PATH, size=14)
pylab.clf()
patches, texts = plt.pie(plot_value, labels=plot_label, counterclock=False, startangle=90)
plt.axis('equal')
pylab.setp(texts, fontproperties=prop)
