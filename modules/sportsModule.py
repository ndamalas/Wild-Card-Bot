from os import link
from bs4 import BeautifulSoup
from command import Command
import requests
import discord
from googlesearch import search


# Every module has to have a command list
commandList = []

commandList.append(Command("!score", "score", "Used to see the score of live games or the betting odds of an upcoming game.\nNote: if trying to use this command on a team that is not in season it will not give their most recent final score.\nUsage: `!score <team>`\nThe bot will then give either an upcoming game or a live game."))
async def score(client, message):
    contents = message.content.split(" ")
    if len(contents) < 2:
        await message.channel.send("Please give an argument.")

    # Live score handler
    team = ""
    for i in range(1, len(contents)-1):
        team += contents[i] + "+"
    team += contents[len(contents)-1]

    searchURL = "https://www.google.com/search?q=espn+" + team
    html = requests.get(searchURL)
    soup = BeautifulSoup(html.content, 'html.parser')


    links = soup.find_all('a')

    # Now do a new soup with the espn team page
    searchURL = links[16].get('href')[7:]
    if (searchURL.find("team") == -1):
        await message.channel.send("Invalid team, could not be found on ESPN.")
        return

    html = requests.get(searchURL)
    soup = BeautifulSoup(html.content, 'html.parser')

    # Now get the latest game page
    for p in soup.find_all("section", class_="club-schedule"):
        textList = p.find_all("a")
        searchURL = "https://www.espn.com" + textList[1].get('href')
    html = requests.get(searchURL)
    soup = BeautifulSoup(html.content, 'html.parser')





    scores = soup.find_all('div', class_='score-container')
    teamStr = []
    time = ""
    for t in soup.find_all('div', class_='team-container'):
        teams = t.find_all('span')
        teamStr.append(teams[0].text + " " + teams[1].text)
    line = ""
    for s in soup.find_all('div', class_='game-status'):
        span = s.find_all('span', class_='line')
        if len(span) != 0:
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
    else:
        for t in soup.find_all('div', class_='team-container'):
            r = t.find_all('div', class_='record')
            teamRecords.append(r[0].text)
    for s in soup.find_all('div', class_='game-status'):
        span = s.find_all('span', class_='game-time')
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
        
        # time = span[0].text
    # Handling baseball
    if (time.find("outs") != -1):
        time = time[:-6] + " " + time[-6:]
    elif (time.find("out") != -1):
        time = time[:-5] + " " + time[-5:]


    """result = ""
    result += "**" + time + "**\n"
    result += "_" + teamStr[0] + "_  " + scores[0].text + "\n"
    result += "_" + teamStr[1] + "_  " + scores[1].text + ""
    """
    # print("\n")
    # print(result)
    embed = discord.Embed(title = "Gamecast", description=time, colour = discord.Colour.red(), url = searchURL)
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    if line == "": # This means game is live
        embed.add_field(name="**" + teamStr[0] + " " + scores[0].text + "**", value=teamRecords[0], inline=True)
        embed.add_field(name="**" + teamStr[1] + " " + scores[1].text + "**", value=teamRecords[1], inline=True)
    else:
        embed.add_field(name="**" + teamStr[0] + "**", value=teamRecords[0] + "\nSpread:      " + teamLines[0] + "\nMoney Line: " + teamMoneyLines[0], inline=True)
        embed.add_field(name="**" + teamStr[1] + "**", value=teamRecords[1] + "\n" + teamLines[1] + "\n" + teamMoneyLines[1], inline=True)
        embed.add_field(name="Over/Under", value=over, inline=False)
    await message.channel.send(embed=embed)

commandList.append(Command("!player", "player", "TODO"))
async def player(client, message):
    contents = message.content.split(" ")
    if len(contents) < 2:
        await message.channel.send("Please give an argument.")

    # Live score handler
    player = ""
    for i in range(1, len(contents)):
        player += contents[i] + "+"
    # player += contents[len(contents)-1]
    player += "stats"

    searchURL = "https://www.google.com/search?q=espn+" + player
    html = requests.get(searchURL)
    soup = BeautifulSoup(html.content, 'html.parser')


    links = soup.find_all('a')
    # Now do a new soup with the espn player page
    # TODO might be an error here
    searchURL = links[16].get('href')
    if (searchURL[:5] != "https"):
        searchURL = searchURL[7:]
    # searchURL = links[16].get('href')[7:]
    index = searchURL.find("player")
    if (index == -1):
        await message.channel.send("Invalid player, could not be found on ESPN.")
        return
    if (searchURL.find("stats") == -1):
        searchURL = searchURL[:index+6] + "/stats/" + searchURL[index+7:]
    html = requests.get(searchURL)
    soup = BeautifulSoup(html.content, 'html.parser')
    # playerName = " ".join(contents[1:])



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
    # recent += "**" + recentSeason[0].text + " " + recentSeason[1].text + ":**\n"
    # print(statNames)
    for i in range(len(statNames)):
        recent += "" + statNames[i].text + ": " + recentRow[i].text + "\n"
    if (len(careerRow) != 0):
        career = ""
        # career += "Career:\n| "
        for i in range(len(statNames)):
            career += "" + statNames[i].text + ": " + careerRow[i].text + "\n"

    playerName = ""
    for s in soup.find_all('h1', class_='PlayerHeader__Name flex flex-column ttu fw-bold pr4 h2'):
        spans = s.find_all('span')
        playerName += spans[0].text + " " + spans[1].text
    
    embed = discord.Embed(title = playerName, description="Shows most recent or current season stats and career stats for pro athletes.", colour = discord.Colour.purple(), url = searchURL)
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    embed.add_field(name=recentSeason[0].text + " " + recentSeason[1].text, value = recent, inline = True)
    if (len(careerRow) != 0):
        embed.add_field(name="Career", value = career, inline = True)
    await message.channel.send(embed=embed)