from bs4 import BeautifulSoup
from urllib import request

url = 'http://archives.c.fun.ac.jp/'
response = request.urlopen(url)
soup = BeautifulSoup(response)
response.close()

print(soup)