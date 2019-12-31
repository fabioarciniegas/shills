import re
import time
import urllib
import requests
import sys
from bs4 import BeautifulSoup

def scrape(title = "the+love+witch",base="https://letterboxd.com",
           film_search="/search/films/",reviews_suffix = "reviews/page/"):
    film_search = requests.get(base+film_search+title).text
    results_page = BeautifulSoup(film_search,features="html.parser")
    film_page = results_page.find_all('span', class_='film-title-wrapper')[0].a["href"]
    for page_number in range(2,20):
        response = requests.get(base+film_page+reviews_suffix+str(page_number))
        if response.status_code != requests.codes.ok:
            break
        reviews_html = response.text
        reviews_page = BeautifulSoup(reviews_html,features="html.parser")
        reviews = reviews_page.find_all('li' , class_='film-detail')
        for review in reviews:
            stars = review.find('span', class_='rating')
            if stars:
                for s in stars.get_attribute_list("class"):
                    m = re.search(r'rated-(\d+)',s)
                    if(m):
                        print(int(m.group(1)))
                        text_div = review.find('div', class_='body-text')
                        url = text_div["data-full-text-url"]
                        page = requests.get(base+url).text
                        s2 = BeautifulSoup(page,features="html.parser")
                        print(s2.get_text().rstrip().strip())
                        print("----------------------------------------------")
                        time.sleep(1.2)

if __name__ == "__main__":
    print(urllib.parse.quote(sys.argv[1]))
    scrape(title=urllib.parse.quote(sys.argv[1]))
