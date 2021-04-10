from bs4 import BeautifulSoup
from command import Command
import requests

import discord
# import time
# from googlesearch import search
team = "lebron+stats"
searchURL = "https://www.google.com/search?q=espn+" + team
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')
print(searchURL)


links = soup.find_all('a')

# Now do a new soup with the espn player page
# print(links[16].get('href'))
searchURL = links[16].get('href')
if (searchURL[:5] != "https"):
    searchURL = searchURL[7:]
print(searchURL)
index = searchURL.find("player")
if (index == -1):
    print("Invalid")
searchURL = searchURL[:index+6] + "/stats/" + searchURL[index+7:]
print(searchURL)

html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')






"""
# Now get the latest game page
for p in soup.find_all("section", class_="club-schedule"):
    textList = p.find_all("a")
    searchURL = "https://www.espn.com" + textList[1].get('href')
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')





# "https://www.espn.com/nba/boxscore/_/gameId/401307560"
scores = soup.find_all('div', class_='score-container')
teamStr = []
time = ""
for t in soup.find_all('div', class_='team-container'):
    teams = t.find_all('span')
    # print(teams)
    teamStr.append(teams[0].text + " " + teams[1].text)
line = ""
for s in soup.find_all('div', class_='game-status'):
    span = s.find_all('span', class_='line')
    line = span[0].text
teamRecords = []
teamLines = []
teamMoneyLines = []
over = ""
if line != "":
    for s in soup.find_all('div', class_='pick-center-content'):
        records = s.find_all('p', class_='record')
        teamRecords.append(records[0].text)
        teamRecords.append(records[1].text)
        records = s.find_all('p', class_='record')
        rows = s.find_all('td', class_="score")
        teamLines.append(rows[3].text)
        teamLines.append(rows[8].text)
        teamMoneyLines.append(rows[4].text.strip())
        teamMoneyLines.append(rows[9].text.strip())
        over = rows[5].text
for s in soup.find_all('div', class_='game-status'):
    span = s.find_all('span', class_='game-time')
    print(span)
    if len(span) == 0 or span[0].text == "":
        span = s.find_all('span')
    else:
        time = span[0].text
        break
    for sp in span:
        if sp.has_attr('data-date'):
            time = sp.get('data-date')
            break
    if time != "":
        newSearch = "https://www.google.com/search?q=What+time+is+" + time[11:16] + "+utc"
        html = requests.get(newSearch)
        soup = BeautifulSoup(html.content, 'html.parser')
        temp = soup.find_all('div', class_="BNeawe iBp4i AP7Wnd")
        # Convert to more readable time
        newTime = temp[0].text.split(" ")[0] + " " + temp[0].text.split(" ")[1]
        date = time[5:10]
        time = newTime + " on " + date
        break
    time = span[0].text
# Handling baseball
if (time.find("outs") != -1):
    time = time[:-6] + " " + time[-6:]

# print(scores)
#print(time)

result = ""
result += time + "\n"
result += line + "\n"
result += teamStr[0] + " " + scores[0].text + " - "
result += teamStr[1] + " " + scores[1].text
print("\n")
print(result)
"""


