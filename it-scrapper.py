# Changelist
# Creado - Agosto 2018
# Anadido descarga masiva y descarga de terminos - 28/08/2018
# Anadido listado de archivos y categorias - 23/09/2018
#
# Ramon Vila Ferreres - 2018
# Licencia MIT

from bs4 import BeautifulSoup
import requests
import os, sys
from Tkinter import *
import Tkinter,Tkconstants,tkFileDialog

global book_page_num
book_page_num = 0

page_max = 136
download_links = []
categories = {
				1:"web-development",
				2:"programming",
				3:"databases",
				4:"game-programming",
				5:"graphics-design",
				6:"operating-systems",
				7:"networking-cloud-computing",
				8:"administration",
				9:"computers-technology",
				10:"certification",
				11:"enterprise",
				12:"marketing-seo",
				13:"hardware",
				14:"security",
				15:"software"
			}

def get_save_dir():
	root = Tk()
	save_dir = tkFileDialog.askdirectory()
	root.destroy()
	return save_dir

def list_categories():
	print "                    CATEGORIES                     "
	print "    ---------------------------------------------"
	print "     N  |  Categories                             "
	print "    ---------------------------------------------"

	for k,v in categories.iteritems():
		print "    [{}] | {}".format(k,v)

	selected_category = categories.get(input("#> "))
	return selected_category

def download_everything():
	try:
		for page_num in range(1, page_max + 1):
			url = 'http://www.allitebooks.com/page/{}'.format(str(page_num))
			soup = get_page_content(url)
			books_in_page = get_books_in_page(soup)
			for book_url in books_in_page:
				splitted_url = book_url.split("/")
				book_file_name = splitted_url[len(splitted_url) -1]
				print " "
				print "Downloading file {} at page {}".format(book_file_name, str(page_num))
				try:
					save_dir = get_save_dir()
					download_file(book_url, save_dir)
				except Exception as exc:
					print "An error ocurred, continuing ..."
					print str(exc)

	except Exception as exc:
					print "An error ocurred, continuing ..."
					print str(exc)


def get_page_content(url):
	page = requests.get(url)
	page_content = page.content
	#soup = BeautifulSoup(page_content, "html.parser")
	soup = BeautifulSoup(page_content)
	return soup

def get_books_in_page(page_soup):

	books_in_page = {}
	books = page_soup.findAll("article", {"class": "post"})

	for book in books:
		try:
			title = book.find("h2",{"class":"entry-title"}).getText()
			book_url = book.find("a")["href"]
			file_url = get_file_link(book_url)

			book_entry = {
				"entry-title": title,
				"url": book_url,
				"file_url": file_url,
			}

			books_in_page[books.index(book)] = book_entry

		except Exception as exc:
			print "An error ocurred, continuing ..."
			print str(exc)
			continue

	return books_in_page


def download_file(url, save_dir):
	local_filename = save_dir + "/" + url.split("/")[len(url.split("/")) -1]
	# NOTE the stream=True parameter
	r = requests.get(url, stream=True)
	with open(local_filename, 'wb') as f:
		for chunk in r.iter_content(chunk_size=1024):
			if chunk: # filter out keep-alive new chunks
				f.write(chunk)

	return local_filename

def get_file_link(book_url):
	download_page_soup = get_page_content(book_url)
	download_element = download_page_soup.findAll("span", {"class" : "download-links"})[0]
	download_link = download_element.find("a")["href"]

	return download_link

def download_search(term):
	try:
		save_dir = get_save_dir()
		for page_num in range(1, page_max + 1):
			url = 'http://www.allitebooks.com/page/{}/?s={}'.format(str(page_num), term)
			soup = get_page_content(url)
			print url
			books_in_page = get_books_in_page(soup)
			print books_in_page
			for booknum, bookdata in books_in_page.iteritems(): #Adaptar a dict
				book_url = books_in_page[booknum]["file_url"]
				splitted_url = book_url.split("/")
				book_file_name = splitted_url[len(splitted_url) -1]
				print "[D] Downloading file {} at page {}".format(book_file_name, str(page_num))
				try:
					download_file(book_url, save_dir)

				except Exception as exc:
					print "An error ocurred, continuing ..."
					print str(exc)

	except Exception as exc:
		print "An error ocurred, continuing ..."
		print str(exc)

def main():
	print "Welcome to Allitebooks Books downloader"
	main_options()

def list_book_in_page(page_url):

	base_url = "http://www.allitebooks.com/"
	extended_url = base_url + page_url
	actual_page_num = page_url.split("/")[len(page_url.split("/")) -1 ]
	books_in_current_page = get_books_in_page(get_page_content(extended_url)) # Pasar soup, no string

	print "                Books -- Page [{}]             ".format(actual_page_num)
	print "    ---------------------------------------------"
	print "     N  |  Categories                             "
	print "    ---------------------------------------------"

	for booknum, bookdata in books_in_current_page.iteritems():
		print "    [{}] | {}".format(booknum, bookdata["entry-title"])

	print ""
	print "    ---------------------------------------------"
	print "    <---- (B)ack       |      (F)orward ----->"
	print "    ---------------------------------------------"

	selected_book = raw_input("#> ")
	return selected_book


def book_selector(chosen_cat, current_num):

	local_num = current_num
	os.system("cls")

	sub_url = "/{}/page/{}".format(chosen_cat, current_num)
	selected_book = list_book_in_page(sub_url)

	if (selected_book == "b" or selected_book == "B"): # Go back

		if (book_page_num > 0):
			local_num -= 1
			book_selector(chosen_cat, local_num)

		elif book_page_num == 0:
			print "You can't go back"
			book_selector(chosen_cat, local_num)

	elif (selected_book == "f" or selected_book == "F"): # Go forward
		local_num += 1
		book_selector(chosen_cat,local_num)

	elif (selected_book not in "abcdefghijklmnopqrstuvwxyz"):
		base_url = "http://www.allitebooks.com"
		extended_url = (base_url + sub_url).replace(" ","-")
		books_in_current_page = get_books_in_page(get_page_content(extended_url)) 
		book_download_url = books_in_current_page[int(selected_book)]["file"]
		save_dir = get_save_dir()
		print "Downloading..."
		download_file(book_download_url, save_dir)
		print "Done"

		book_selector(chosen_cat,local_num)

def main_options():
	print "Select an option: "
	print "[1] Download everything"
	print "[2] Search an specific term"
	print "[3] Navigate categories and books"
	print ""

	option = raw_input("#>")

	if option == "1":
		download_everything()

	elif option == "2":
		term = raw_input("Enter the term you want to search: ")
		print "Searching and downloading books {}".format(term)
		download_search(term)

	elif option == "3":
		category = list_categories()
		book_selector(category, book_page_num)

	else:
		main_options()

main()
