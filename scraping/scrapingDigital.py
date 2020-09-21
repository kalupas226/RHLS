from bs4 import BeautifulSoup
from urllib import request
import pymysql.cursors
import time

def check_next_page(soup):
    next_page = soup.find('a', class_='next')
    if next_page:
        return root_url + next_page['href']
    else:
        return ""

def get_soup(url):
    response = request.urlopen(url)
    soup = BeautifulSoup(response, 'html.parser')
    response.close()
    return soup

def insert_sql(title, contents, url, img_url):
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO Digital (title, contents, url, img_url) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (title, contents, url, img_url))

        conn.commit()
    finally:
        print(title + " commited")

conn = pymysql.connect(host='localhost',
                       db='Research_System',
                       user='root',
                       passwd='',
                       charset='utf8',
                       cursorclass=pymysql.cursors.DictCursor)

try:
    with conn.cursor() as cursor:
        cursor.execute('TRUNCATE TABLE Digital')
    conn.commit()
finally:
    print('truncate table')

root_url = 'http://archives.c.fun.ac.jp'
urls = ['/fronts/index/reservoir',
        '/fronts/index/postcards',
        '/fronts/index/poster',
        '/fronts/index/photos',
        '/fronts/index/scrollframe',
        '/fronts/index/ukiyoe']

for url in urls:
    thumbnail_soup = get_soup(root_url + url)
    next_page_url = check_next_page(thumbnail_soup)
    thumbnails = thumbnail_soup.find('ul', class_='thumbnails')
    thumbnails = thumbnails.select('div.thumbnail')

    while next_page_url:
        # スクレイピングの感覚を空ける
        time.sleep(1)
        for thumbnail in thumbnails:
            image_url = thumbnail.select('img')[0]['src']
            detail_url = root_url + thumbnail.select('a')[0]['href']
            if 'thumbnailChild' in detail_url:
                child_soup = get_soup(detail_url)
                child_next_url = check_next_page(child_soup)
                child_thumbnails = child_soup.find('ul', class_='thumbnails')
                child_thumbnails = child_thumbnails.select('div.thumbnail')
                while child_next_url:
                    for child_thumbnail in child_thumbnails:
                        child_thumbnail_image_url = child_thumbnail.select('img')[0]['src']
                        child_detail_url = root_url + child_thumbnail.select('a')[0]['href']
                        child_detail_soup = get_soup(child_detail_url)
                        child_detail_tables = child_detail_soup.find('table', class_='table').select('td')
                        child_detail_title = child_detail_tables[1].string
                        child_detail_contents = child_detail_tables[3].string
                        insert_sql(child_detail_title,
                                   child_detail_contents,
                                   child_detail_url,
                                   child_thumbnail_image_url)
                    child_soup = get_soup(child_next_url)
                    child_next_url = check_next_page(child_soup)
                    child_thumbnails = child_soup.find('ul', class_='thumbnails')
                    child_thumbnails = child_thumbnails.select('div.thumbnail')
            else:
                detail_soup = get_soup(detail_url)
                detail_tables = detail_soup.find('table', class_='table').select('td')
                detail_title = detail_tables[1].string
                detail_contents = detail_tables[3].string
                insert_sql(detail_title, detail_contents, detail_url, image_url)
        thumbnail_soup = get_soup(next_page_url)
        next_page_url = check_next_page(thumbnail_soup)
        thumbnails = thumbnail_soup.find('ul', class_='thumbnails')
        thumbnails = thumbnails.select('div.thumbnail')
