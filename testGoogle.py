from bs4 import BeautifulSoup
from command import Command
import requests
import discord
from googlesearch import search 

from youtubesearchpython import VideosSearch

videosSearch = VideosSearch('juice wrld', limit = 5)
results = videosSearch.result()['result']
for i in range(5):
    print(results[i]['link'])
# print(videosSearch.result())
# print(videosSearch.result()['result'][0]['link'])


#Function to test sending data to external commands

# Every module has to have a command list

# contents = message.split(" ")

# to search 
query = 'music'




"""searchURL = "https://www.bing.com/images/search?q=" + query
print(searchURL)
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')"""

#searchURL = "https://www.youtube.com/results?search_query=" + query
searchURL = "https://www.google.com/search?q=" + query + "&rlz=1C1CHBF_enUS858US858&sxsrf=ALeKk036sAuCPyhYiGbr6amekvOH93cFDg:1616160790513&source=lnms&tbm=vid&sa=X&ved=2ahUKEwiJ0MWOvLzvAhWTQc0KHd--BOcQ_AUoA3oECA8QBQ&biw=1266&bih=557"
print(searchURL)
"""html = requests.get(searchURL).text
soup = BeautifulSoup(html, 'html.parser')
"""

"""for i in search(query.replace("+", " "), tld="co.in", num=10, stop=10, pause=2):
    print(i)
"""

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
"""
content = soup.find_all('a')
# print(content)
src = content[25].get('href')
print(src)
"""



