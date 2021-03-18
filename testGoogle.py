from bs4 import BeautifulSoup
from command import Command
import requests
import discord
from googlesearch import search 


#Function to test sending data to external commands

# Every module has to have a command list

# contents = message.split(" ")

# to search 
query = "How+large+is+earth"

searchURL = "https://www.google.com/search?q=" + query
print(searchURL)
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')

for i in search(query.replace("+", " "), tld="co.in", num=10, stop=10, pause=2):
    print(i)
    index = i.find("www.")
    name = i[index:]
    print(name)


## This may be used for ones with no description
description = soup.find_all('div', class_="BNeawe s3v9rd AP7Wnd")
#, class_='PZPZlf hb8SAc'
print(description[0].text)
# if description:
#     print(description)
# else:
#     print("No description")
