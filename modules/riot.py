import string
import discord
import os
import pandas as pd
from command import Command
from riotwatcher import LolWatcher, ApiError, RiotWatcher, LorWatcher, TftWatcher

commandList = []


riot_api_key = "RGAPI-699f4344-49e5-4e99-8a76-362b6a39c1ad"
lol_watcher = LolWatcher(riot_api_key)
riot_watcher = RiotWatcher(riot_api_key)
lor_watcher = LorWatcher(riot_api_key)
tft_watcher = TftWatcher(riot_api_key)

pd.set_option('display.max_columns', 5)
myDf = pd.read_json('./leaguedata/11.6.1/data/en_US/champion.json')

commandList.append(Command("!regions", "get_regions", "Displays all regions"))
async def get_regions(ctx, message):
    response = "BR1\nEUN1\nEUW1\nJP1\nKR\nLA1\nLA2\nNA1\nOC1\nRU\nTR1"
    embed = discord.Embed(title='Riot regions', description=response, colour=discord.Colour.dark_red())
    await message.channel.send(embed=embed)


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
        output += player['summonerName'] + " " + search_champion_by_id(str(player['championId'])) + " " + str(player['spell1Id']) + " " + str(player['spell2Id']) + " "
        output += str(player['perks']['perkStyle']) + " " + str(player['perks']['perkIds'][0]) + " " + str(player['perks']['perkIds'][1]) + " " + str(player['perks']['perkIds'][2]) + " "
        output += str(player['perks']['perkSubStyle']) + " " + str(player['perks']['perkIds'][3]) + " " + str(player['perks']['perkIds'][4]) + " " + str(player['perks']['perkIds'][5]) + " "
        output += str(player['perks']['perkIds'][6]) + " " + str(player['perks']['perkIds'][7]) + " " + str(player['perks']['perkIds'][8])
        output += "\n"
        i += 1
    output += "Red Side\n"
    while i < 10:
        player = spectator['participants'][i]
        output += player['summonerName'] + " " + search_champion_by_id(str(player['championId'])) + " " + str(player['spell1Id']) + " " + str(player['spell2Id']) + " "
        output += str(player['perks']['perkStyle']) + " " + str(player['perks']['perkIds'][0]) + " " + str(player['perks']['perkIds'][1]) + " " + str(player['perks']['perkIds'][2]) + " "
        output += str(player['perks']['perkSubStyle']) + " " + str(player['perks']['perkIds'][3]) + " " + str(player['perks']['perkIds'][4]) + " " + str(player['perks']['perkIds'][5]) + " "
        output += str(player['perks']['perkIds'][6]) + " " + str(player['perks']['perkIds'][7]) + " " + str(player['perks']['perkIds'][8])
        output += "\n"
        i += 1
    await message.channel.send(output)

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

def search_champion_by_id(id: str) -> str:
    for i in myDf['data']:
        if i['key'] == id:
            return i['id']

commandList.append(Command("!league", "get_league_profile", "Displays a player's League of Legends profile\nUsage: !league <REGION> <IGN>"))
async def get_league_profile(ctx, message):
    messageArray = message.content.split(" ")
    region = message.content.split(" ")[1]
    name = ""
    for i in range(2, len(messageArray)):
      name += message.content.split(" ")[i]
    # print(name)
    version = lol_watcher.data_dragon.versions_for_region(region)
    await message.channel.send(version)
    user = lol_watcher.summoner.by_name(region, name)
    ranked_stats = lol_watcher.league.by_summoner(region, user['id'])
    await message.channel.send(user['name'] + " Lvl " + str(user['summonerLevel']))
    await message.channel.send("http://ddragon.leagueoflegends.com/cdn/" + version['n']['profileicon'] + "/img/profileicon/" + str(user['profileIconId']) + ".png")
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
    version = lol_watcher.data_dragon.versions_for_region(region)
    user = tft_watcher.summoner.by_name(region, name)
    ranked_stats = tft_watcher.league.by_summoner(region, user['id'])
    await message.channel.send(user['name'] + " Lvl " + str(user['summonerLevel']))
    await message.channel.send("http://ddragon.leagueoflegends.com/cdn/" + version['n']['profileicon'] + "/img/profileicon/" + str(user['profileIconId']) + ".png")
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
    version = lol_watcher.data_dragon.versions_for_region(region)
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
      await message.channel.send(">>> \n" + str(i + 1) + ".\nQueue: " + get_queue_type(matchlist['matches'][i]['queue']) + "\nChampion: " + search_champion_by_id(str(matchlist['matches'][i]['champion'])) + "\n")
