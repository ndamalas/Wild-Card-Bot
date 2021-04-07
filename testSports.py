from bs4 import BeautifulSoup
from command import Command
import requests
import discord
# from googlesearch import search
team = "reds"
searchURL = "https://www.google.com/search?q=espn+" + team
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')


links = soup.find_all('a')
print(links[16].get('href')[7:])

# Now do a new soup with the espn team page
searchURL = links[16].get('href')[7:]
if (searchURL.find("team") == -1):
    print("Invalid search")

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
teamStr = []
for t in soup.find_all('div', class_='team-container'):
    teams = t.find_all('span')
    # print(teams)
    teamStr.append(teams[0].text + " " + teams[1].text)
#time = soup.find_all('div', class_='game-status')
for s in soup.find_all('div', class_='game-status'):
    span = s.find_all('span')
    time = span[0].text
# Handling baseball
if (time.find("outs") != -1):
    time = time[:-6] + " " + time[-6:]

# print(scores)
print(teamStr[0])
print(teamStr[1])
#print(time)

result = ""
result += time + "\n"
result += teamStr[0] + " " + scores[0].text + " - "
result += teamStr[1] + " " + scores[1].text
print("\n")
print(result)

