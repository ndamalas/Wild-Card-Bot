from bs4 import BeautifulSoup
from command import Command
import requests
import discord
from googlesearch import search


# Every module has to have a command list
commandList = []

commandList.append(Command("!sports", "sports", "TODO"))
async def sports(client, message):
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
    # This means game is live
    if line == "":
        embed.add_field(name="**" + teamStr[0] + " " + scores[0].text + "**", value="\u200b", inline=True)
        embed.add_field(name="**" + teamStr[1] + " " + scores[1].text + "**", value="\u200b", inline=True)
    else:
        embed.add_field(name="**" + teamStr[0] + "**", value="Spread: " + teamLines[0] + "\nMoney Line: " + teamMoneyLines[0], inline=True)
        embed.add_field(name="**" + teamStr[1] + "**", value=teamLines[1] + "\n" + teamMoneyLines[1], inline=True)
        embed.add_field(name="Over/Under", value=over, inline=False)
    await message.channel.send(embed=embed)


