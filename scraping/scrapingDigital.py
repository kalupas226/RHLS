from bs4 import BeautifulSoup
from urllib import request

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
        for thumbnail in thumbnails:
            detail_url = root_url + thumbnail.select('a')[0]['href']
            print(detail_url)
            if 'thumbnailChild' in detail_url:
                child_soup = get_soup(detail_url)
                child_next_url = check_next_page(child_soup)
                child_thumbnails = child_soup.find('ul', class_='thumbnails')
                child_thumbnails = child_thumbnails.select('div.thumbnail')
                while child_next_url:
                    for child_thumbnail in child_thumbnails:
                        child_detail_url = root_url + child_thumbnail.select('a')[0]['href']
                        print(child_detail_url)
                    child_soup = get_soup(child_next_url)
                    child_next_url = check_next_page(child_soup)
                    child_thumbnails = child_soup.find('ul', class_='thumbnails')
                    child_thumbnails = child_thumbnails.select('div.thumbnail')
        thumbnail_soup = get_soup(next_page_url)
        next_page_url = check_next_page(thumbnail_soup)
        thumbnails = thumbnail_soup.find('ul', class_='thumbnails')
        thumbnails = thumbnails.select('div.thumbnail')



