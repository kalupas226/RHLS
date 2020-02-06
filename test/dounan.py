# -*- coding: utf-8 -*-

import re
import bs4
import sys
import MeCab
import urllib.request
from pprint import pprint

BASE_URL = "http://donan-museums.jp/list/page/"
output_words = []
#指定したURLをセット
# if len(sys.argv) == 2:
#     url = sys.argv[1]
# else:
#     print("URLを指定してください")
#     exit()

#URLにアクセスし，ソースコードを取得&パース
for num in range(1,100):
    pageurl = BASE_URL + str(num)
    try:
        print(pageurl)
        html = urllib.request.urlopen(pageurl)
        soup = bs4.BeautifulSoup(html.read(), "html.parser")

        # #title,description,h1を抜き出し処理対象としてセット
        # title   = soup.title.string
        # description = soup.find(attrs={"name": re.compile(r'Description',re.I)}).attrs['content']
        # h1 = soup.h1.string
        # contents = title + description + h1
        # output_words = []

        all_link = soup.div.find_all("a")
        link_url = []
        for url in all_link:
            if "archives" in url.get("href"):
                print(url.get("href"))
                link_url.append(url.get("href"))
        print(link_url)
        for link in link_url:
            html = urllib.request.urlopen(link)
            soup = bs4.BeautifulSoup(html.read(), "html.parser")
            description = soup.find_all("p")
            contents = ""
            # output_words = []
            for des in description:
                contents += des.text

            # MeCab(辞書：mecab-ipadic-neologd)でキーワードを抽出する
            m = MeCab.Tagger(' -d /usr/local/lib/mecab/dic/mecab-ipadic-neologd')
            keywords = m.parse(contents)

            for row in keywords.split("\n"):
                word = row.split("\t")[0]
                if word == "EOS":
                    break
                else:
                    pos = row.split("\t")[1].split(",")[0]
                    if pos == "名詞":
                        output_words.append(word)
    except urllib.request.HTTPError as e:
        print(e.code)
        break
    except urllib.request.URLError as e:
        print(e.reason)
        break



#ユニークにして出力
pprint(list(set(output_words)))
