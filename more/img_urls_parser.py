from bs4 import BeautifulSoup
import requests

url = "https://www.imdb.com/title/tt1649443/mediaindex"

response = requests.get(url)

soup = BeautifulSoup(response.text, 'html.parser')

article_block = soup.find('div', class_='article')

image_links = [img['src'] for img in article_block.find_all('img') if 'src' in img.attrs]

for link in image_links:
    print(link)
