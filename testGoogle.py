from bs4 import BeautifulSoup
from command import Command
import requests



searchURL = "https://www.google.com/search?q=how+many+rings+does+lebron+have"
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')
description = soup.find_all('div', class_="BNeawe iBp4i AP7Wnd")
#print(soup.prettify())
print(description[0].text)
#result = description[0].text



