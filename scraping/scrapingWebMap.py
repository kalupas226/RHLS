# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import re
import mysql.connector
import mechanize

DESCRIPTION = 0
INSCRIPTION = 1
REFERENCE = 2
TOURIST_SIGN = 3
ENGLISH = 4

def removeRecord(cursor):
    cursor.execute("TRUNCATE TABLE WebMap")
    cursor.execute("TRUNCATE TABLE WebMapTag")
    cursor.execute("TRUNCATE TABLE WebMap_Image")
    connector.commit()

def checkNextPage(soup):
    NextPage = soup.find_all("div")
    NextPageURL = "" #次のページがあるかを判定する
    for nextpage in NextPage:
        if nextpage.text.strip() == u"過去の投稿 →" or nextpage.text.strip() == u"全ての記事を読む →":
            NextPageURL = nextpage.a.get("href")
    return NextPageURL

def getDateFromString(detailpage):
    string = detailpage.find("h3", {"class": "vcard"}).text[4:] #「作成日：」を削除
    year = string[:string.find(u"年")]
    month_str = string[string.find(u"年") + 1 : string.find(u"月")]
    month = month_str if len(month_str) == 2 else "0" + month_str
    day_str = string[string.find(u"月") + 1 : string.find(u"日")]
    day = day_str if len(day_str) == 2 else "0" + day_str
    date = year + "-" + month + "-" + day
    return date

def getDataFromTable(detailpage, pos):
    table = detailpage.find("table")
    columnList = table.find_all("th")
    return columnList[pos].text.strip()

def getImage(detailpage):
    image = DetailPage.find_all("img")
    img_list = []
    for img in image:
        if img.get("src").find("http://donan-museums.jp/wp-content/uploads/") != -1:
            img_list.append(img.get("src"))
    return img_list

def extractContext(text, regexp_idx, cate_flag):
    context = ""
    joined_txt = "\n".join(text)

    if regexp_idx is DESCRIPTION:
        regexp_flag = True # 「■解説」で抽出させるため，何もない場合はTrue
    else:
        regexp_flag = False # それ以外は，False
    regexp = [
        "■解説|■解　　説|■追加解説|^■説明$|■(?!(碑文|刻文|参考文献|説明板|観光説明板|観光説明版|観光案内板|坂名説明標柱|坂名説明板|案内版|案内板))", \
        "■碑文|■刻文|^碑文$", \
        "■参考文献|^参考文献：", \
        "■説明板|■観光説明板|■観光説明版|■観光案内板|■坂名説明標柱|■坂名説明板|■案内版|■案内板"
    ]
    other_regexp = regexp[:]
    other_regexp.remove(regexp[regexp_idx])
    joined_regexp = "|".join(other_regexp)

    # 「■」がない場合，returnする
    # しかし，「■解説」の場合のみ本文をそのまま返す
    if not u"■" in joined_txt:
        if cate_flag is True:
            return joined_txt
        else:
            return ""

    for line in text:
        # 抽出したいものと一致したい場合
        if re.compile(regexp[regexp_idx]).search(line.encode("utf-8")):
            regexp_flag = True
        # 抽出したくないものと一致した場合
        elif re.compile(joined_regexp).search(line.encode("utf-8")):
            regexp_flag = False
        # 観光案内板（日本語）で英語を抽出しない
        elif regexp_idx is TOURIST_SIGN and re.compile("[a-zA-z]{3}").search(line.encode("utf-8")):
                regexp_flag = False

        if regexp_flag is True:
            if not re.compile(regexp[regexp_idx]).search(line.encode("utf-8")): #「■」がある行は抽出しない
                context += line + "\n"

    return context[:-1] # 最後の改行を削除

def extractEnglish(text):
    context = ""

    regexp_flag = False
    regexp = "■説明板|■観光説明板|■観光説明版|■観光案内板|■坂名説明標柱|■坂名説明板|■案内版|■案内板"
    for line in text:
        if re.compile(regexp).search(line.encode("utf-8")):
            regexp_flag = True

        if regexp_flag is True and re.compile("[a-zA-z]{3}").search(line.encode("utf-8")):
            context += line + "\n"

    return context[:-1]

def show_newline(context, page):
    tag_dic = { \
        "description": "■解説", \
        "inscription": "■碑文", \
        "sign_ja": "■観光説明板", \
        "sign_en": "■Description", \
        "kantaiji": "■描述", \
        "hantaiji": "■描述", \
        "russian": "■Oписание", \
        "hangul": "■설명", \
        "thai": "■คำอธิบาย", \
        "reference": "■参考文献" \
    }

    keys = tag_dic.keys()
    for key in keys:
        if page.find("div", {"id": key}):
            context = context.replace(tag_dic[key].decode("utf-8"), tag_dic[key].decode("utf-8") + "\n")

    return context


if __name__ == "__main__":
    hostname = "localhost" #IPアドレス
    dbname = "Research_System" #データベース名
    username = "root" #ユーザ名
    password = "" #パスワード
    connector = mysql.connector.connect(host=hostname, db=dbname, user=username, passwd=password, charset="utf8")
    cursor = connector.cursor()
    removeRecord(cursor)
    #Login Form
    url = 'http://donan-museums.jp/list'
    ListPage = BeautifulSoup(urllib2.urlopen(url), "html5lib")
    NextPageURL = checkNextPage(ListPage)
    sub = 0;
    while NextPageURL:
        Title = ListPage.find_all("h2")
        titleList = []
        urlList = []
        for title in Title:
            if title.a:
                urlList.append(title.a.get("href"))
                titleList.append(title.text.strip())
        if len(titleList) == len(urlList):
             for i in range(0, len(titleList)):
                 sub += 1
                 DetailURL = urlList[i]
                 detail_page = urllib2.urlopen(DetailURL)
                 DetailPage = BeautifulSoup(detail_page, "html5lib")
                 page_id = sub
                 title = titleList[i]
                 yomi = DetailPage.find("p", {"style": "font-size:18pt"}).text
                 author = DetailPage.find("span", {"class": "fn"}).text
                 date = getDateFromString(DetailPage)
                 tagList = getDataFromTable(DetailPage, 11).split(", ")
                 for tag in tagList:
                     cursor.execute('INSERT INTO WebMapTag (id, title, tag) VALUES (%s, %s, %s)' , (str(page_id), title, tag))
                     connector.commit()
                 image_list = getImage(DetailPage)
                 if not image_list: # 画像がない場合
                      cursor.execute('INSERT INTO WebMap_Image (id, title, image) VALUES (%s, %s, %s)' , (str(page_id), title, ""))
                      connector.commit()
                 for image in image_list:
                      cursor.execute('INSERT INTO WebMap_Image (id, title, image) VALUES (%s, %s, %s)' , (str(page_id), title, image))
                      connector.commit()
                 text = DetailPage.find("div", {"class": "entry-content"}).text.strip()
                 text = show_newline(text, DetailPage)
                 context = DetailPage.find("div", {"class": "entry-content"}).text.strip().split("\n")
                 if DetailPage.find("div", {"id": "description"}):
                     description = DetailPage.find("div", {"id": "description"}).text
                     description = description.replace(u"■解説\n", "")
                 else:
                     description = extractContext(context, DESCRIPTION, True)

                 if DetailPage.find("div", {"id": "inscription"}):
                     inscription = DetailPage.find("div", {"id": "inscription"}).text
                     inscription = inscription.replace(u"■碑文\n", "")
                 else:
                     inscription = extractContext(context, INSCRIPTION, False)

                 if DetailPage.find("div", {"id": "reference"}):
                     reference = DetailPage.find("div", {"id": "reference"}).text
                     reference = reference.replace(u"■参考文献\n", "")
                 else:
                     reference = extractContext(context, REFERENCE, False)

                 if DetailPage.find("div", {"id": "sign_ja"}):
                     tourist_sign = DetailPage.find("div", {"id": "sign_ja"}).text
                 else:
                     tourist_sign = extractContext(context, TOURIST_SIGN, False)

                 if DetailPage.find("div", {"id": "sign_en"}):
                     english = DetailPage.find("div", {"id": "sign_en"}).text
                 else:
                     english = extractEnglish(context)

                 hantaiji = ""
                 if DetailPage.find("div", {"id": "hantaiji"}):
                     hantaiji = DetailPage.find("div", {"id": "hantaiji"}).text

                 kantaiji = ""
                 if DetailPage.find("div", {"id": "kantaiji"}):
                     kantaiji = DetailPage.find("div", {"id": "kantaiji"}).text

                 russian = ""
                 if DetailPage.find("div", {"id": "russian"}):
                     russian = DetailPage.find("div", {"id": "russian"}).text

                 hangul = ""
                 if DetailPage.find("div", {"id": "hangul"}):
                     hangul = DetailPage.find("div", {"id": "hangul"}).text

                 thai = ""
                 if DetailPage.find("div", {"id": "thai"}):
                     thai = DetailPage.find("div", {"id": "thai"}).text

                 large_area = getDataFromTable(DetailPage, 1)
                 small_area = getDataFromTable(DetailPage, 3)
                 location = getDataFromTable(DetailPage, 5)
                 age_production = getDataFromTable(DetailPage, 7)
                 age_subject = getDataFromTable(DetailPage, 9)
                 cursor.execute('INSERT INTO WebMap (title, title_yomi, author, date, context, description, inscription, reference, tourist_sign, english, hantaiji, kantaiji, russian, hangul, thai, large_area, small_area, location, age_production, age_subject, url) \
                   VALUES( %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (title, yomi, author, date, text, description, inscription, reference, tourist_sign, english, hantaiji, kantaiji, russian, hangul, thai, large_area, small_area, location, age_production, age_subject, DetailURL))
                 connector.commit()
                 print (sub, title)
        NextPageURL = checkNextPage(ListPage)
        if NextPageURL:
            nextpage = urllib2.urlopen(NextPageURL)
            ListPage = BeautifulSoup(nextpage, "html5lib")
    connector.close()
