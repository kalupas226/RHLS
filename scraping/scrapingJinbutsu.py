# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import urllib2
import re
import mysql.connector
import mechanize

if __name__ == "__main__":
    hostname = "localhost"
    dbname = "Research_System"
    username = "root"
    password = "tyogyakuten226"
    connector = mysql.connector.connect(host=hostname, db=dbname, user=username, passwd=password, charset="utf8")
    cursor = connector.cursor()

    cursor.execute("TRUNCATE TABLE Jinbutsuden")
    connector.commit()

    url = 'http://www.zaidan-hakodate.com/jimbutsu/'
    listPage = BeautifulSoup(urllib2.urlopen(url), "html.parser")
    sub = 0;
    linkUrl = listPage.find_all("a")
    personLinks = []
    pattern = r"\w*\/[\w-]*.html"

    for li in linkUrl:
        if li.get("href") is not None and re.match(pattern, li.get("href")):
            personLinks.append(li.get("href"))

    for personLink in personLinks:
        detailPage = urllib2.urlopen(url + personLink)
        DetailPage = BeautifulSoup(detailPage, "html.parser")
        titleList = DetailPage.find_all("h2", {"class": "ttl_name"})
        nameReg = u"(?<=[(（]).*?(?=[)）])"
        name = "" #人物名
        stopWord = ["（", "）", "～", "代","年","?","？","(",")"] #取り除きたい語
        nameYomiReg = u'（+.*）+'
        nameYomi = "" #人物名のふりがな
        dateReg = r'(\d{4})' #生没年の抽出
        date = []
        dateBorn = "" #生年
        dateDeath = "" #没年
        image = DetailPage.find_all("img", {"class": "photo"})
        imgList = []
        for img in image:
            imgList.append(url + img.get("src").encode("utf-8")[3:]) #画像のurlの最初３文字を削る
        JinbutsuImage = ""
        for im in imgList:
            JinbutsuImage += im
            print(JinbutsuImage)
        catchWord = ""
        try:
            catchWord = DetailPage.find("h3").text
            print(catchWord)
        except:
            print(url + personLink)
            print("h3がありません")
        description = DetailPage.find("p", {"class": "line"}).text
        print(description)
        for title in titleList:
            sub += 1
            print(title.text)
            name = re.sub(nameReg, "", title.text)
            name = re.sub(r"\d","",name)
            for stop in stopWord:
                name = name.replace(stop,"")
            name = name.encode("utf-8")
            print(name)
            if len(re.findall(nameYomiReg,title.text)) != 0:
                name_yomi = re.findall(nameYomiReg,title.text)
                nameYomi = name_yomi[0].encode("utf-8")
                for stop in stopWord:
                    nameYomi = nameYomi.replace(stop, "")
                nameYomi = re.sub(r"\d","",nameYomi)
                nameYomi = re.sub(u"[一-龥]","",nameYomi)
                print(nameYomi)
            try:
                date = re.findall(dateReg,title.text)
                dateBorn = date[0]
                dateDeath = date[1]
                print(dateBorn)
                print(dateDeath)
            except:
                dateBorn = "生年不明"
                dateDeath = "没年不明"
                print("生没年不明")
            cursor.execute('INSERT INTO Jinbutsuden (name, nameYomi, dateBorn, dateDeath ,catchWord, description, url, imgUrl) \
                VALUES( %s, %s, %s, %s, %s, %s, %s, %s)', (name.lstrip(), nameYomi, dateBorn, dateDeath, catchWord, description, url+personLink, JinbutsuImage.rstrip()))
            connector.commit()
            # 重複する行の削除
            cursor.execute('DELETE FROM Jinbutsuden WHERE id NOT IN (SELECT min_id from (SELECT MIN(id) min_id FROM Jinbutsuden GROUP BY name) tmp);')
            connector.commit()
            cursor.execute('SET @i := 0;')
            cursor.execute('update `Jinbutsuden` set id = (@i := @i + 1);')
            connector.commit()
            print(sub,name)
    connector.close()
