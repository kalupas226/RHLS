# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import time
import tqdm
import mysql.connector

def coordinate(address):
    """
    addressに住所を指定すると緯度経度を返す。

    >>> coordinate('東京都文京区本郷7-3-1')
    ['35.712056', '139.762775']
    """
    payload = {'q': address}
    html = requests.get(URL, params=payload)
    soup = BeautifulSoup(html.content, "html.parser")
    if soup.find('error'):
        # raise ValueError(f"Invalid address submitted. {address}")
        print("error")
        latitude = ""
        longitude = ""
    else:
        latitude = soup.find('lat').string
        longitude = soup.find('lng').string
    return [latitude, longitude]

def coordinates(addresses, interval=10, progress=True):
    """
    addressesに住所リストを指定すると、緯度経度リストを返す。

    >>> coordinates(['東京都文京区本郷7-3-1', '東京都文京区湯島３丁目３０−１'], progress=False)
    [['35.712056', '139.762775'], ['35.707771', '139.768205']]
    """
    coordinates = []
    for address in progress and tqdm(addresses) or addresses:
        coordinates.append(coordinate(address))
        time.sleep(interval)
    return coordinates

#mysql connection
connector = mysql.connector.connect(host="localhost", db="Research_System", user="root", passwd="tyogyakuten226", charset="utf8")
cursor = connector.cursor()

cursor.execute("TRUNCATE TABLE WebMap_Location")
connector.commit()

sql = "select id, large_area, small_area, location from WebMap;"
cursor.execute(sql)
records = cursor.fetchall()

URL = 'http://www.geocoding.jp/api/'

for record in records:
    print(record[0])
    print(record[1])
    print(record[2])
    print(record[3])
    id = record[0]
    lat = ""
    lng = ""
    if record[3] != "":
        if '北海道' in record[3]:
            latlng = coordinate(record[3])
        else:
            latlng = coordinate("北海道" + record[3])
        lat = str(latlng[0])
        lng = str(latlng[1])
        print("lat: " + lat)
        print("lng: " + lng)
    elif record[1] != "":
        latlng = coordinate("北海道" + record[1])
        lat = str(latlng[0])
        lng = str(latlng[1])
        print("lat: " + lat)
        print("lng: " + lng)
    cursor.execute('INSERT INTO WebMap_Location (id, lat, lng)\
      VALUES( %s, %s, %s)', (id, lat, lng))
    connector.commit()
    time.sleep(6)
    
connector.close()