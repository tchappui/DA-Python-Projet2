# -*-coding:UTF-8 -*
import requests
from bs4 import BeautifulSoup
import urllib.parse
import csv
import re
import os.path
import pandas as pd
import wget
from slugify import slugify

def set_the_url():
	"""
	This function is only here to check if the input url is correct.
	:return: the input url after regex check.
	"""
	regex_ok = False
	while regex_ok == False:	#try to set the url
		input_url = input("Veuillez saisir l'URL : ")
		pattern = '^https?://books[.]toscrape[.]com/'
		result = re.match(pattern, input_url)	#regex check
		if result:		
			regex_ok = True
			return input_url
		else:
			print("L'URL n'est pas valide.")

def download_image(the_url):
	"""
	Extract:\n
	:param the_url: list.\n
	This function create a directory whose name is the category name.\n
	Then the function extract all images in the current page in this directory.\n
	:return: the category name.
	"""
	for link in the_url:
		response = requests.get(link)
		if response.ok:
			soup = BeautifulSoup(response.content, 'html.parser')
			title_slug = slugify(soup.h1.text)
			image_url = urllib.parse.urljoin("http://books.toscrape.com/", soup.img['src'])
			category_slug = slugify(soup.find('ul')('li')[2].text.strip())
			os.makedirs("Books-To-Scrape/" + category_slug, exist_ok=True)	#creat a directory 
			wget.download(image_url, "Books-To-Scrape/" + category_slug + "/" + title_slug + '.jpg', bar = None)	#download the image

	return category_slug


def scrap_one_book(url = ''):
	"""
	This function is in two part.\n
	Extract:\n
	:param url: string.\n
	The first part extract all the informations of a book.\n	
	First, request the URL parameter. 
	Then extract all the infos of a book.\n
	The second part transform all informations in a DataFrame with Pandas.\n
	:return: DataFrame.
	"""
	book_info = pd.DataFrame()		
	response = requests.get(url)	#set the response resquests
	if response.ok:
		soup = BeautifulSoup(response.content, 'html.parser')
		product_page_url = url
		title = soup.h1.text
		image_url = urllib.parse.urljoin("http://books.toscrape.com/", soup.img['src'])    #scrap of URL image
		category = soup.find('ul')('li')[2].text.strip()	#scrap gategory			
		all_p = soup.find_all('p')    #find all paragraph			
		product_description = all_p[3].text    #in all paragraph, index[3] is the description
		
		for p in all_p:    #find each paragraph in all paragraph
			rewiev_p = p['class']	#find all paragraph with argument class
			if rewiev_p[0] == 'star-rating':	#condition to find the paragraph with class == star rating
				review_rating = rewiev_p[1]    #select the number rating	
				break
			
		tds = soup.find_all('td')    #find all td
		universal_product_code = tds[0].text
		price_excluding_tax = tds[2].text
		price_including_tax = tds[3].text
		number_available_list = re.findall(r'\d', tds[5].text)    #make a list of number
		number_available = ''.join(number_available_list)    #join the number
	"""
	Transform: 
	"""
	try:
		book_info = pd.DataFrame({
			'product_page_url': [product_page_url],
			'universal_product_code(upc)': [universal_product_code],
			'title': [title],
			'price_including_tax': [price_including_tax],
			'price_excluding_tax': [price_excluding_tax],
			'number_available': [number_available],
			'product_description': [product_description],
			'category': [category],
			'review_rating': [review_rating],
			'image_url': ['=HYPERLINK("' + image_url + '")'],
			'image_local': ['=HYPERLINK("' + slugify(title) +'.jpg")']
			})								
		
	except NameError:
		print("ERREUR : Le livre est introuvable, l'URL n'est pas valide. Relancer le programme avec une URL valide.")

	return book_info

if __name__ == '__main__':	
	url_list = []
	the_url = set_the_url()
	url_list.append(the_url) # put the url in a list because the function download_image need a list as parameter
	category_name = download_image(url_list)
	path = "Books-To-Scrape/" + category_name + '/' + category_name + '.csv'
	"""
	Load :
	Push the DataFrame to a csv file.
	"""
	scrap_one_book(the_url).to_csv(path, sep=';', index=False, encoding="utf-8-sig")