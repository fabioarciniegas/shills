import re
import time
import urllib
import requests
import sys
from bs4 import BeautifulSoup
from .models import Film, Review
import json
import asyncio
import websockets
from math import ceil
from langdetect import detect, detect_langs
from dynamic_preferences.registries import global_preferences_registry

global_preferences = global_preferences_registry.manager()


async def scrape(loop=None,title = "the+love+witch",base="https://letterboxd.com",
                 film_search="/search/films/",reviews_suffix = "reviews/page/"):

    num_pages = 20
    expected_reviews=6*num_pages
    received_reviews=1
    async with websockets.connect(
        'ws://localhost:8000/ws/film_scrapping/') as websocket:
        film_search = requests.get(base+film_search+title).text
        results_page = BeautifulSoup(film_search,features="html.parser")
        film_page = results_page.find_all('span', class_='film-title-wrapper')[0].a["href"]
        f = Film.objects.get(title=title)
        for page_number in range(1,num_pages):
            response = requests.get(base+film_page+reviews_suffix+str(page_number))
            if response.status_code != requests.codes.ok:
                break
            reviews_html = response.text
            reviews_page = BeautifulSoup(reviews_html,features="html.parser")
            reviews = reviews_page.find_all('li' , class_='film-detail')
            for review in reviews:
                if received_reviews >= expected_reviews:
                    continue;
                stars = review.find('span', class_='rating')
                if stars:
                    for s in stars.get_attribute_list("class"):
                        m = re.search(r'rated-(\d+)',s)
                        if(m):
                            text_div = review.find('div', class_='body-text')
                            url = text_div["data-full-text-url"]
                            page = requests.get(base+url).text
                            s2 = BeautifulSoup(page,features="html.parser")
                            r = Review(film=f,rating=int(m.group(1)),text=s2.get_text().rstrip().strip())
                            try:
                                if detect(r.text) == 'en' and len(detect_langs(r.text))==1:
                                    r.save()
                                else:
                                    print ("ignoring non-english review")
                            except:
                                print ("ignoring language unclassifiable review'%s'" % r.text)
                                
                            received_reviews += 1
                            p = str(int(100*received_reviews/expected_reviews))
                            if int(100*received_reviews/expected_reviews) < 100:
                                await websocket.send(json.dumps({'film': f.id, 'percentage':p}))
                                time.sleep(global_preferences['scraper__delay'])
        f.scraped_completion=100
        f.save()
        await websocket.send(json.dumps({'film': f.id, 'percentage':'100'}))
            
def scrape_in_thread(loop,title):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(scrape(loop,title))

