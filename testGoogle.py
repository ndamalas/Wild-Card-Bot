from bs4 import BeautifulSoup
from command import Command
import requests
import discord
from googlesearch import search 


#Function to test sending data to external commands

# Every module has to have a command list

# contents = message.split(" ")

# to search 
query = "dogs"

# searchURL = "https://www.bing.com/images/search?q=" + query
searchURL = "https://www.bing.com/images/search?q=" + query + "&first=1&tsc=ImageHoverTitle"
print(searchURL)
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')

# for i in search(query.replace("+", " "), tld="co.in", num=10, stop=10, pause=2):
#     print(i)
#     index = i.find("www.")
#     name = i[index:]
#     print(name)


## This may be used for ones with no description
#description = soup.find_all('div', class_="BNeawe s3v9rd AP7Wnd")
#description = soup.find_all('div')
#, class_='PZPZlf hb8SAc'

#for i in description:
#    print(i.text + "\n")

# if description:
#     print(description)
# else:
#     print("No description")

# div = soup.find('div', id='vm_c')
images = soup.find_all('img', class_='mimg')
# print (images)
src = images[0].attrs['src']
print(src)

