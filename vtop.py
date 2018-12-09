# import selenium for scraping website
# import BeautifulSoup to parse the source code of page
# import urllib.request to save captcha from webpage
# import selenium.common.exceptions to catch exceptions
# import Image from PIL to manipulate and process the Captcha image
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import selenium.common.exceptions as selExc
import urllib.request
import time
import os
import json
from PIL import Image


# This function checks if the page has successfully loaded
def page_loading():
	# It finds a particular element on the page
	try:
		driver.find_element_by_id("uname")
		return False
		print("Page Loaded")
	# If the page has not loaded it will raise an error
	except selExc.NoSuchElementException:
		print("loading", end="\r")
		return True


# This function converts all non black pixels to white
def refine():
	for col in range(0, image.height):
		for row in range(0, image.width):
			if pixel_matrix[row, col] != 0:
				pixel_matrix[row, col] = 255


# This function reduces noise by checking adjacent pixels of a black pixel
def noise_red():
	for col in range(1, image.height - 1):
		for row in range(1, image.width - 1):
			if pixel_matrix[row, col] == 0 and pixel_matrix[row, col - 1] != 0 and pixel_matrix[row, col + 1] != 0:
				pixel_matrix[row, col] = 255
			if pixel_matrix[row, col] == 0 and pixel_matrix[row - 1, col] != 0 and pixel_matrix[row + 1, col] != 0:
				pixel_matrix[row, col] = 255


# configuring the headless browser
options = Options()
options.add_argument('--disable-gpu')
options.add_argument('--window-size=1080,720')
# options.add_argument('--headless')

path = os.path.dirname(__file__)
driver = webdriver.Chrome(executable_path= path + r'\chromedriver.exe', chrome_options = options)
print("Process Started")

driver.get("https://vtop10.vit.ac.in/")
driver.find_element_by_class_name("btn-primary").click()
time.sleep(2)

# Switching to new window
driver.switch_to.window(driver.window_handles[1])
# If the page hasn't loaded, wait for 3 sec
while page_loading():
	time.sleep(3)

reg_no = driver.find_element_by_id("uname")
reg_no.send_keys(input("Enter Username: "))
password = driver.find_element_by_id("passwd")
password.send_keys(input("Enter Password: "))
login_btn = driver.find_element_by_class_name("btn-primary")

html_doc = driver.page_source
# Parsing the page source using lxml compiler
soup = BeautifulSoup(html_doc, 'lxml')
imgs = soup.find_all('img')
# Locating and downloading img tag which contains captcha
src = imgs[1]["src"]
urllib.request.urlretrieve(src, "img.png")
# opening and converting image to Grayscale
image = Image.open(path + "img.png").convert("L")
pixel_matrix = image.load()

refine()
noise_red()

# This part of code (to break Captcha) is work of @Presto412
# -------------------------------------------------------------------
characters = "123456789abcdefghijklmnpqrstuvwxyz"
captcha = ""
with open("bitmaps.json", "r") as fin:
	bitmap = json.load(fin)

	# parses every character, 6 is number of characters
	for j in range(int(image.width / 6), image.width + 1, int(image.width / 6)):
		char_img = image.crop((j - 30, 12, j, 44))
		char_matrix = char_img.load()
		matches = {}
		for char in characters:
			match = 0
			black = 0
			bitmap_matrix = bitmap[char]
			for col in range(0, 32):
				for row in range(0, 30):
					if char_matrix[row, col] == bitmap_matrix[col][row] \
						and bitmap_matrix[col][row] == 0:
						match += 1
					if bitmap_matrix[col][row] == 0:
						black += 1
			perc = float(match) / float(black)
			matches.update({perc: char[0].upper()})
		try:
			captcha += matches[max(matches.keys())]
		except ValueError:
			print("failed captcha")
			captcha += "0"
# -------------------------------------------------------------------
	os.remove(path + "img.png")

	driver.find_element_by_id("captchaCheck").send_keys(captcha)

login_btn.click()
driver.quit()