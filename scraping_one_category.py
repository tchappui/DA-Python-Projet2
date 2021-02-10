# -*-coding:UTF-8 -*
import requests
from bs4 import BeautifulSoup
import urllib.parse
import csv
import re
import os.path
import scraping_one_book
import pandas as pd

def find_next_page(url = ''):
    url_all_pages_list = []
    test_url = url.replace("index", "page-1")
    reponse = requests.get(test_url)
    if reponse.ok:
        for i in range(1, 9):
            url_page = url.replace("index", "page-" + str(i))
            reponse = requests.get(url_page)
            if reponse.ok:
                url_all_pages_list.append(url_page)
    else:
        url_all_pages_list.append(url)

    return url_all_pages_list

def scrap_one_category(urls = ''): #scrap all the urls' books in the category
    if __name__ == '__main__':
        url_category = scraping_one_book.set_the_url()
        response = requests.get(url_category) # url_category = url form set_the_url
    else:
        response = requests.get(urls)  # ulrs parameter
	# if OK, scrap the page
    if response.ok:
        soup = BeautifulSoup(response.content, 'html.parser')
        links = [] # list with all urls books in the page
        all_title = soup.find_all('h3')
        for one_title in all_title:
            a = one_title.find('a')
            link = a['href']
            links.append(link)
        return links #return a lists of urls

def scrap_all_books(): #scrap all books in the page
    links = scrap_one_category() #link = a lists of urls
    df_list = []
    try:
        for link in links:
            url = urllib.parse.urljoin("http://books.toscrape.com/catalogue/catalogue/catalogue/catalogue/", link)
            df_list.append(scraping_one_book.scrap_one_book(url))
       
        df_all_books = pd.concat(df_list)
        return df_all_books
    except:
        print("L'URL n'est pas correct, veuillez relancer le programme.")

if __name__ == '__main__':
    #scrap_all_books().to_csv(path_or_buf='books.csv', sep=';', index=False)
    print(find_next_page('http://books.toscrape.com/catalogue/category/books/music_14/index.html'))