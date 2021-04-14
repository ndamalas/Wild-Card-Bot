from bs4 import BeautifulSoup
from command import Command
import requests

import discord
# import time
# from googlesearch import search
# team = "jaden+ivey+stats"
team = "nets"
searchURL = "https://www.google.com/search?q=espn+" + team
html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')
print(searchURL)

"""
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
if (searchURL.find("stats") == -1):
    searchURL = searchURL[:index+6] + "/stats/" + searchURL[index+7:]
print(searchURL)

html = requests.get(searchURL)
soup = BeautifulSoup(html.content, 'html.parser')


count = 0
shift = 0 # Used when there is both a career and a season averages row
for t in soup.find_all('table'):
    row = t.find_all('tr')
    if count == 1:
        statNames = row[0].find_all('th')
        if shift == 1:
            careerRow = row[len(row)-2].find_all('td')
            recentRow = row[len(row)-3].find_all('td')
        else :
            careerRow = row[len(row)-1].find_all('td')
            recentRow = row[len(row)-2].find_all('td')
    elif count == 0:
        recentSeason = row[len(row)-2].find_all('td')
        if recentSeason[0].text == "Career":
            recentSeason = row[len(row)-3].find_all('td')
            shift = 1
    else:
        break
    count += 1

recent = ""
recent += recentSeason[0].text + " " + recentSeason[1].text + " | "
# print(statNames)
for i in range(len(statNames)):
    recent += statNames[i].text + ": " + recentRow[i].text + " "
print(recent)
career = ""
career += "Career | "
for i in range(len(statNames)):
    career += statNames[i].text + ": " + careerRow[i].text + " "
print(career)

playerName = ""
for s in soup.find_all('h1', class_='PlayerHeader__Name flex flex-column ttu fw-bold pr4 h2'):
    spans = s.find_all('span')
    playerName += spans[0].text + " " + spans[1].text
print(playerName)
"""


links = soup.find_all('a')

# Now do a new soup with the espn team page
# print(links)
searchURL = links[20].get('href')
print(searchURL)



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


