from modules.clockModule import timezone
import time
import pytz
from datetime import datetime
from bs4 import BeautifulSoup
import requests
from timezonefinder import TimezoneFinder


# First webscrape coordinates
searchURL = "https://www.google.com/search?q=Hawaii" + "+coordinates"
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')

description = soup.find_all('div', class_="BNeawe iBp4i AP7Wnd")
if len(description) == 0:
    description = soup.find_all('div', class_="BNeawe s3v9rd AP7Wnd")
result = description[0].text
print(result)
contents = result.split(" ")

# Next plug coordinates into api
tf = TimezoneFinder()
latitude, longitude = float(contents[0][:-1]), float(contents[2][:-1])
if contents[1] == "S,":
    latitude = -latitude
if contents[3] == "W":
    longitude = -longitude
location = tf.timezone_at(lng=longitude, lat=latitude)

print(location)

# Get local time
t = pytz.timezone(location)

newTime = datetime.now(t)

curr_clock = newTime.strftime("%a, %d %b %Y %H:%M:%S")

  
print(curr_clock)
