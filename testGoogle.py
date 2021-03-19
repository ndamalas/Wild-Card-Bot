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




"""searchURL = "https://www.bing.com/images/search?q=" + query
print(searchURL)
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')"""

#searchURL = "https://www.youtube.com/results?search_query=" + query
searchURL = "https://www.google.com/search?q=" + query + "&rlz=1C1CHBF_enUS858US858&sxsrf=ALeKk02CkZmXlqPXeG1zYfhlNWziJkRu1Q:1616111833740&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjsoZHehbvvAhXELc0KHXcKBN0Q_AUoA3oECCIQBQ&biw=1266&bih=557"
print(searchURL)
html = requests.get(searchURL).text
soup = BeautifulSoup(html, 'html.parser')


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
"""
images = soup.find_all('img', class_='mimg')
src = images[0].attrs['src']
print(src)
"""

content = soup.find_all('img')
#print(content)
src = content[2].attrs['src']
print(src)
"""src = videos[0].attrs['href']
print(src)"""


