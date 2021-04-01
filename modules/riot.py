import string
import discord
import os
import pandas as pd
import requests
from command import Command
from bs4 import BeautifulSoup
from riotwatcher import LolWatcher, ApiError, RiotWatcher, LorWatcher, TftWatcher
from bs4 import BeautifulSoup
import asyncio
from urllib.request import Request, urlopen
# from PIL import Image

commandList = []


# Unnest nested columns in data frame. myDf is dataframe to unnest and columns is name of column to unnest
def unnest(myDf: pd.DataFrame, columns: list) -> pd.DataFrame:
  tempDf = pd.DataFrame()
  for i in columns:
    if i in myDf:
      if isinstance(myDf.loc[:, i].iloc[0], dict):
        x = myDf[i].apply(pd.Series)
        tempDf = pd.concat([tempDf, x], axis = 1)
  return tempDf

riot_api_key = "RGAPI-435e3d4b-27ea-4008-8984-bf28cbf2ecd5"
lol_watcher = LolWatcher(riot_api_key)
riot_watcher = RiotWatcher(riot_api_key)
lor_watcher = LorWatcher(riot_api_key)
tft_watcher = TftWatcher(riot_api_key)

dirname = "./leaguedata/"

pd.set_option('display.max_columns', 5)

championDf = unnest(pd.read_json('./leaguedata/11.6.1/data/en_US/championFull.json'), ["data"])
index = championDf.index
imgNameDf = unnest(championDf, ["image"])
passiveDf = unnest(championDf, ["passive"])
spellsDf = unnest(championDf, ["spells"])
passiveImgDf = unnest(passiveDf, ["image"])

summonerDf = pd.read_json('./leaguedata/11.6.1/data/en_US/summoner.json')
runesDf = pd.read_json('./leaguedata/11.6.1/data/en_US/runesReforged.json')


commandList.append(Command("!regions", "get_regions", "Displays all regions"))
async def get_regions(ctx, message):
    response = "BR1\nEUN1\nEUW1\nJP1\nKR\nLA1\nLA2\nNA1\nOC1\nRU\nTR1"
    embed = discord.Embed(title='Riot regions', description=response, colour=discord.Colour.dark_red())
    await message.channel.send(embed=embed)

commandList.append(Command("!tips", "champion_tips", "Display tips on playing with or against a champion\nUsage: !tips <CHAMPION-NAME>"))
async def champion_tips(ctx, message):
    name = message.content.split(" ")[1] # name
    name = name.capitalize()
    await message.channel.send("Playing with " + name)
    for tip in championDf["allytips"][index == name][0]:
        await message.channel.send(tip)
    await message.channel.send("Playing against " + name)
    for tip in championDf["enemytips"][index == name][0]:
        await message.channel.send(tip)

commandList.append(Command("!champ", "champion_info", "Displays information on a champion]\nUsage: !champ <CHAMPION-NAME>"))
async def champion_info(ctx, message):
    name = message.content.split(" ")[1] # name
    name = name.capitalize()
    output = ""
    output += "**" + name + " " + championDf[index == name]['title'].item() + "**"
    await message.channel.send(output)
    fn = dirname + "/11.6.1/img/champion/" + imgNameDf[index == name]["full"].item()
    fp = open(fn, 'rb')
    await message.channel.send(file=discord.File(fp))
    await message.channel.send("**Resource: **" + championDf[index == name]['partype'].item()) # resource
    await message.channel.send("**Class: **" + ', '.join(championDf.loc[index == name, "tags"].item())) # Class
    await message.channel.send("**Passive: **" + passiveDf[index == name]['name'].item()) # passive name
    await message.channel.send(passiveDf[index == name]['description'].item()) # passive description
    await message.channel.send("**Q Ability: **" + BeautifulSoup(championDf["spells"][index == name][0][0]["name"], "lxml").get_text('\n'))
    await message.channel.send(BeautifulSoup(championDf["spells"][index == name][0][0]["description"], "lxml").get_text('\n'))
    await message.channel.send("**W Ability: **" + BeautifulSoup(championDf["spells"][index == name][0][1]["name"], "lxml").get_text('\n'))
    await message.channel.send(BeautifulSoup(championDf["spells"][index == name][0][1]["description"], "lxml").get_text('\n'))
    await message.channel.send("**E Ability: **" + BeautifulSoup(championDf["spells"][index == name][0][2]["name"], "lxml").get_text('\n'))
    await message.channel.send(BeautifulSoup(championDf["spells"][index == name][0][2]["description"], "lxml").get_text('\n'))
    await message.channel.send("**R Ability: **" + BeautifulSoup(championDf["spells"][index == name][0][3]["name"], "lxml").get_text('\n'))
    await message.channel.send(BeautifulSoup(championDf["spells"][index == name][0][3]["description"], "lxml").get_text('\n'))



commandList.append(Command("!live", "live_game", "Displays live game stats\nUsage: !live <REGION> <IGN>"))
async def live_game(ctx, message):
    messageArray = message.content.split(" ")
    region = message.content.split(" ")[1]
    name = ""
    for i in range(2, len(messageArray)):
      name += message.content.split(" ")[i]
    user = lol_watcher.summoner.by_name(region, name)
    spectator = lol_watcher.spectator.by_summoner(region, user['id'])
    output = ""
    output += get_queue_type(spectator['gameQueueConfigId']) + "\n"
    output += "Blue Side\n"
    i = 0
    while i < 5:
        player = spectator['participants'][i]
        output += search_champion_by_id(str(player['championId']), "name") + " **" + player['summonerName'] + "** " + search_summoner_spell_by_id(str(player['spell1Id'])) + " " + search_summoner_spell_by_id(str(player['spell2Id'])) + " "
        output += search_runes_by_id(player['perks']['perkStyle']) + " " + search_runes_by_id(player['perks']['perkIds'][0]) + " " + search_runes_by_id(player['perks']['perkIds'][1]) + " " + search_runes_by_id(player['perks']['perkIds'][2]) + " " + search_runes_by_id(player['perks']['perkIds'][3]) + " "
        output += search_runes_by_id(player['perks']['perkSubStyle']) + " " + search_runes_by_id(player['perks']['perkIds'][4]) + " " + search_runes_by_id(player['perks']['perkIds'][5]) + " "
        output += search_runes_by_id(player['perks']['perkIds'][6]) + " " + search_runes_by_id(player['perks']['perkIds'][7]) + " " + search_runes_by_id(player['perks']['perkIds'][8])
        output += "\n"
        i += 1
    output += "Red Side\n"
    while i < 10:
        player = spectator['participants'][i]
        output += search_champion_by_id(str(player['championId']), "name") + " **" + player['summonerName'] + "** " + search_summoner_spell_by_id(str(player['spell1Id'])) + " " + search_summoner_spell_by_id(str(player['spell2Id'])) + " "
        output += search_runes_by_id(player['perks']['perkStyle']) + " " + search_runes_by_id(player['perks']['perkIds'][0]) + " " + search_runes_by_id(player['perks']['perkIds'][1]) + " " + search_runes_by_id(player['perks']['perkIds'][2]) + " " + search_runes_by_id(player['perks']['perkIds'][3]) + " "
        output += search_runes_by_id(player['perks']['perkSubStyle']) + " " + search_runes_by_id(player['perks']['perkIds'][4]) + " " + search_runes_by_id(player['perks']['perkIds'][5]) + " "
        output += search_runes_by_id(player['perks']['perkIds'][6]) + " " + search_runes_by_id(player['perks']['perkIds'][7]) + " " + search_runes_by_id(player['perks']['perkIds'][8])
        output += "\n"
        i += 1
    await message.channel.send(output)

commandList.append(Command("!league", "get_league_profile", "Displays a player's League of Legends profile\nUsage: !league <REGION> <IGN>"))
async def get_league_profile(ctx, message):
    messageArray = message.content.split(" ")
    region = message.content.split(" ")[1]
    name = ""
    for i in range(2, len(messageArray)):
      name += message.content.split(" ")[i]
    # print(name)
    user = lol_watcher.summoner.by_name(region, name)
    ranked_stats = lol_watcher.league.by_summoner(region, user['id'])
    await message.channel.send(user['name'] + " Lvl " + str(user['summonerLevel']))
    if len(ranked_stats) > 1:
        await message.channel.send("Ranked Flex: " + ranked_stats[0]['tier'] + " " + ranked_stats[0]['rank'] + " " + str(ranked_stats[0]['leaguePoints']) + "LP " + str(ranked_stats[0]['wins']) + "W/" + str(ranked_stats[0]['losses']) + "L")
        await message.channel.send("Ranked Solo: " + ranked_stats[1]['tier'] + " " + ranked_stats[1]['rank'] + " " + str(ranked_stats[1]['leaguePoints']) + "LP " + str(ranked_stats[1]['wins']) + "W/" + str(ranked_stats[1]['losses']) + "L")
    elif len(ranked_stats) == 1:
        await message.channel.send("Ranked Solo: " + ranked_stats[0]['tier'] + " " + ranked_stats[0]['rank'] + " " + str(ranked_stats[0]['leaguePoints']) + "LP " + str(ranked_stats[0]['wins']) + "W/" + str(ranked_stats[0]['losses']) + "L")

commandList.append(Command("!tft", "get_tft_profile", "Displays a player's TFT profile\nUsage: !tft <REGION> <IGN>"))
async def get_tft_profile(ctx, message):
    messageArray = message.content.split(" ")
    region = message.content.split(" ")[1]
    name = ""
    for i in range(2, len(messageArray)):
      name += message.content.split(" ")[i]
    user = tft_watcher.summoner.by_name(region, name)
    ranked_stats = tft_watcher.league.by_summoner(region, user['id'])
    await message.channel.send(user['name'] + " Lvl " + str(user['summonerLevel']))
    if len(ranked_stats) == 1:
        await message.channel.send("Ranked TFT: " + ranked_stats[0]['tier'] + " " + ranked_stats[0]['rank'] + " " + str(ranked_stats[0]['leaguePoints']) + "LP " + str(ranked_stats[0]['wins']) + "W/" + str(ranked_stats[0]['losses']) + "L")

commandList.append(Command("!mastery", "get_champion_mastery", "Displays the specified player's top 3 champion masteries.\nUsage: !mastery <REGION> <IGN>"))
async def get_champion_mastery(ctx, message):
    #Splits string into !command region username
    messageArray = message.content.split(" ")
    region = message.content.split(" ")[1]
    #print(region)
    name = ""
    for i in range(2, len(messageArray)):
      name += message.content.split(" ")[i]
    #Get the version (what patch league is on)
    version = "11.6.1"
    #print(version)
    #Gets the user data using the region and username
    user = lol_watcher.summoner.by_name(region, name)
    #Gets the champion mastery
    championmastery = lol_watcher.champion_mastery.by_summoner(region, user['id'])
    #Gets the total mastery score like returns as an int (i.e. 577)
    totalmastery = lol_watcher.champion_mastery.scores_by_summoner(region, user['id'])
    #Gets the list of all champions/abilites/descriptions
    championdata = lol_watcher.data_dragon.champions(version ['n']['champion'], False, None)
    championList = []
    for champion in championdata['data']:
      championList.append(championdata['data'][champion])
    print(championList[0]['id'])
    #Array of top 3 champions
    championArray = []
    #For loop goes through all the champions matching the champion by championID to get names
    for j in range(3):
      for i in range(len(championList)):
        if (str(championdata['data'][championList[i]['id']]['key']) == str(championmastery[j]['championId'])):
          #print("hi")
          #print(championmastery[j]['championId'])
          championArray.append(championdata['data'][championList[i]['id']]['id'])
    #Prints out username, total mastery score, top 3 champion names each with total mastery points + level of mastery
    await message.channel.send(user['name'])
    await message.channel.send("Total Mastery Score: " + str(totalmastery))
    for i in range(3):
      await message.channel.send("Champion: " + championArray[i] +
      #await message.channel.send(championdata['data'][championArray[i]]['image']['sprite'])
      "\nTotal Mastery Points: " + str(championmastery[i]['championPoints']) + "\nMastery Level: " + str(championmastery[i]['championLevel']))

commandList.append(Command("!matchhistory", "get_match_history", "Displays a player's League of Legends match history\nUsage: !matchhistory <REGION> <IGN>"))
async def get_match_history(ctx, message):
    messageArray = message.content.split(" ")
    region = message.content.split(" ")[1]
    name = ""
    for i in range(2, len(messageArray)):
      name += message.content.split(" ")[i]
    # print(name)
    user = lol_watcher.summoner.by_name(region, name)
    # print(user)
    matchlist = lol_watcher.match.matchlist_by_account(region, user['accountId'])
    await message.channel.send(">>> MATCH HISTORY: \n")
    for i in range(5):
      await message.channel.send(">>> \n" + str(i + 1) + ".\nQueue: " + get_queue_type(matchlist['matches'][i]['queue']) + "\nChampion: " + search_champion_by_id(str(matchlist['matches'][i]['champion']), "name") + "\n")


commandList.append(Command("!clearpm", "clear_path_pm", "PMS user with the appropriate jungle path for that champion\nUsage: !clearpm <champion> <side>"))
async def clear_path_pm(ctx, message):
    guild = message.guild
    if len(message.content.split(" ")) != 3:
        await message.channel.send(">>> Please use format: \n !clearpm <Champion> <Side>")
    await message.channel.send("Sending Jungling tips to user now")
    if message.content.split(" ")[1] == "Kayn":
        if message.content.split(" ")[2] == "Blue":
            await message.author.send("Kayn Jungling tips for Blue side:\n")
            await asyncio.sleep(1)
            await message.author.send("Go to Red Buff and watch out for invade")
            await asyncio.sleep(1)
            await message.author.send("Ping bot lane to help leash Red Buff")
            await asyncio.sleep(7)
            await message.author.send("Take Red buff with leash")
            await asyncio.sleep(7)
            await message.author.send("Level e and shadow step through wall and clear Krugs")
            await asyncio.sleep(1)
            await message.author.send("Use wall to cancel q animation")
            await asyncio.sleep(7)
            await message.author.send("Shadow step through red buff walls and go to raptors")
            await asyncio.sleep(1)
            await message.author.send("use q animation cancel into wall and kite camp towards wolves")
            await asyncio.sleep(7)
            await message.author.send("Level q up again and make way to wolves")
            await asyncio.sleep(1)
            await message.author.send("Smite wolves and take using q")
            await asyncio.sleep(7)
            await message.author.send("Shadow step to blue buff and take")
            await asyncio.sleep(1)
            await message.author.send("Take gromp and blue buff together and level w")
            await asyncio.sleep(7)
            await message.author.send("Take scuttle or gank")
            await asyncio.sleep(1)
            await message.author.send("CONGRATS YOU DID FIRST CLEAR")



commandList.append(Command("!skillorder", "get_skill_order", "Displays the skill order of specified League of Legends champion.\nUsage: !skillorder <CHAMPION_NAME>"))
async def get_skill_order(ctx, message):
    #Gets the desired champion name
    champion_name = message.content.split(" ")[1]

    #List of skillorder and the counter for that list 1 = First skill to be leveled
    skillOrderList = []
    counter = 1

    #Data is obtained from u.gg which uses Riot API
    URL = 'https://u.gg/lol/champions/' + champion_name + '/build'
    #page is the way to access the webpage
    page = requests.get(URL)

    #Soup parses the page into html sections
    soup = BeautifulSoup(page.content, 'html.parser')

    #Searches for the skill order tab on u.gg
    results = soup.find_all('div', class_= 'skill-order-row')
    #Gets the skills from the skilltable
    for i in range(18):
        for result in results:
            skillups = result.find_all('div', class_='skill-up')
            if (None in skillups):
                continue
            skillname = result.find('div', class_='skill-label bottom-right')
            print(skillname)
            for skillup in skillups:
                print(skillup)
                if str(skillup) == '<div class="skill-up"><div>' + str(counter) + '</div></div>' or str(skillup) == '<div class="skill-up rec"><div>' + str(counter) + '</div></div>':
                    skillOrderList.append(str(skillname)[38:39])
                    counter += 1
    print(skillOrderList)

    #Final formatted string
    skillOrderString = ""

    #Makes the string Q->E->W->R as an example
    for i in range(len(skillOrderList)):
        if i == len(skillOrderList) - 1:
            skillOrderString += skillOrderList[i]
        else:
            skillOrderString += skillOrderList[i] + "->"

    await message.channel.send(skillOrderString)

commandList.append(Command("!items", "get_recommended_items", "Displays the recommended items for a champion given the champion name.\nUsage: !recommendeditems <CHAMPION_NAME>"))
async def get_recommended_items(ctx, message):
    #Gets the desired champion name
    champion_name = message.content.split(" ")[1]

    #Data is obtained from op.gg which uses Riot API
    URL = 'https://na.op.gg/champion/' + champion_name + '/statistics'
    hdr = {'User-Agent': 'Mozilla/5.0'}
    req = Request(URL,headers=hdr)
    page=urlopen(req)
    soup = BeautifulSoup(page)
    print(URL)
    #page is the way to access the webpage
    
    print(page)

    #Soup parses the page into html sections
    
    print(soup)

    #Searches for the first row item builds (they display the most popular builds)
    results = soup.find_all('tr', class_= 'champion-overview__row champion-overview__row--first')

    #Store the images file in the itemImages list as num.png (i.e. 3045.png)
    starterItemspng = []
    coreItemspng = []
    bootspng = []
    counter = 1

    #Finds the build images from op.gg
    #For all instances looks for the num.png and puts them into the list
    for result in results:
        images = result.find_all('img')
        print(images)
        for image in images:
            if str(image)[5] == 's':
                if counter == 1:
                    starterItemspng.append(str(image)[54:62])
                elif counter == 2:
                    coreItemspng.append(str(image)[54:62])
                else:
                    bootspng.append(str(image)[54:62])
        counter += 1
    #print(starterItemspng)
    #print(coreItemspng)
    #print(bootspng)
    #Stores the images as discord Files in 3 separate lists so we can print them separately
    starterItems = []
    coreItems = []
    boots = []
    #Converts the png file names to full path names as discord files and adds them to appropriate lists
    for i in range(len(starterItemspng)):
        #Path name to the image folder
        await message.channel.send(dirname+ "/11.6.1/img/item/" + starterItemspng[i])
        temp_img = discord.File(fp=dirname + "/11.6.1/img/item/" + starterItemspng[i])
        starterItems.append(temp_img)
    for i in range(len(coreItemspng)):
        temp_img = discord.File(fp=dirname + "/11.6.1/img/item/" + coreItemspng[i])
        coreItems.append(temp_img)
    for i in range(len(bootspng)):
        #print(i)
        temp_img = discord.File(fp=dirname + "/11.6.1/img/item/" + bootspng[i])
        boots.append(temp_img)

    '''embed = discord.Embed(title="Recommended Build")
    embed.add_field(name='Starting Items:', value=(file=discord.File(imageFiles[0]) + discord.File(imageFiles[1]) + discord.File(imageFiles[2])))
    embed.add_field(name='Core Items:', value=(discord.File(imageFiles[3]) + discord.File(imageFiles[4]) + discord.File(imageFiles[5])))
    embed.add_field(name='Boots:', value=(discord.File(imageFiles[6])))'''
    #Prints out all of the lists with dividers
    await message.channel.send('Starting Items:', files=starterItems)
    #await message.channel.send(files=starterItems)
    await message.channel.send('Core Items:', files=coreItems)
    #await message.channel.send(files=coreItems)
    await message.channel.send('Boots:', files=boots)
    #await message.channel.send(file=boots[0])
    #temp_img = discord.File("C:/Users/liehr/OneDrive/Wild-Card-Bot/leaguedata/dragontail-11.6.1/11.6.1/img/item/" + bootspng[0])

commandList.append(Command("!database", "get_database", "Displays a link to the jungle paths database.\nUsage: !database"))
async def get_database(ctx, message):
    embed = discord.Embed(
        title='Jungle Paths Database',
        description='[Google Spreadsheet](https://docs.google.com/spreadsheets/d/1keK1QUeOLVvaMug5PoAm4oHb3npUaIIRL6tSb2M5cCI/edit?usp=sharing)',
        color=0x000000)
    embed.set_image(url="https://raw.communitydragon.org/latest/plugins/rcp-fe-lol-clash/global/default/assets/images/position-selector/positions/icon-position-jungle.png")
    await message.channel.send(embed=embed)


# Helper function to get queue type by id
def get_queue_type(id: int) -> str:
    mode = ""
    if id == 0:
        mode += "Custom"
    elif id == 400:
        mode += "Normal Draft"
    elif id == 420:
        mode += "Ranked Solo/Duo"
    elif id == 430:
        mode += "Normal Blind"
    elif id == 440:
        mode += "Ranked Flex"
    elif id == 450:
        mode += "ARAM"
    elif id == 700:
        mode += "Clash"
    elif id == 900:
        mode += "URF"
    else:
        mode += "Other"
    return mode

# Helper function to get champion by id
def search_champion_by_id(id: str, value: str):
    champ = championDf.loc[championDf['key'] == id, value].item()
    return champ

# Helper function to get summoner spells by id
def search_summoner_spell_by_id(id: str) -> str:
    for i in summonerDf['data']:
        if i['key'] == id:
            return i['name']

# Helper function to get runes by id
def search_runes_by_id(id: int) -> str:
    if id == 8100:
        return "Domination"
    elif id == 8300:
        return "Inspiration"
    elif id == 8000:
        return "Precision"
    elif id == 8400:
        return "Resolve"
    elif id == 8200:
        return "Sorcery"
    elif id == 5008:
        return "AF"
    elif id == 5003:
        return "MR"
    elif id == 5002:
        return "Armor"
    elif id == 5005:
        return "AS"
    elif id == 5007:
        return "Haste"
    elif id == 5001:
        return "HP"
    for i in runesDf['slots']:
        for j in i:
            for k in j['runes']:
                if k['id'] == id:
                    return k['key']
