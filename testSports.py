from bs4 import BeautifulSoup
from command import Command
import requests
import discord
# from googlesearch import search

team = "purdue+football"
searchURL = "https://www.google.com/search?q=espn+" + team
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')


links = soup.find_all('a')
print(links[16].get('href')[7:])
# Now do a new soup with the espn team page
searchURL = links[16].get('href')[7:]
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')

# Now get the latest game page
for p in soup.find_all("section", class_="club-schedule"):
    textList = p.find_all("a")
    searchURL = "https://www.espn.com" + textList[1].get('href')
    print(textList[1].get('href'))
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')





# "https://www.espn.com/nba/boxscore/_/gameId/401307560"
scores = soup.find_all('div', class_='score-container')
teams = soup.find_all('div', class_='team-container')
time = soup.find_all('div', class_='game-status')

print(scores)
print(teams)
print(time)