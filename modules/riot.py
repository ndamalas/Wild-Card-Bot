import string
import discord
import os
from command import Command
from riotwatcher import LolWatcher, ApiError, RiotWatcher, LorWatcher, TftWatcher

commandList = []

riot_api_key = "RGAPI-654cbb73-cbb2-4bfb-9437-2b73fda6b689"
lol_watcher = LolWatcher(riot_api_key)
riot_watcher = RiotWatcher(riot_api_key)
lor_watcher = LorWatcher(riot_api_key)
tft_watcher = TftWatcher(riot_api_key)

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
        output += player['summonerName'] + " " + str(player['championId']) + " " + str(player['spell1Id']) + " " + str(player['spell2Id']) + " "
        output += str(player['perks']['perkStyle']) + " " + str(player['perks']['perkIds'][0]) + " " + str(player['perks']['perkIds'][1]) + " " + str(player['perks']['perkIds'][2]) + " "
        output += str(player['perks']['perkSubStyle']) + " " + str(player['perks']['perkIds'][3]) + " " + str(player['perks']['perkIds'][4]) + " " + str(player['perks']['perkIds'][5]) + " "
        output += str(player['perks']['perkIds'][6]) + " " + str(player['perks']['perkIds'][7]) + " " + str(player['perks']['perkIds'][8])
        output += "\n"
        i += 1
    output += "Red Side\n"
    while i < 10:
        player = spectator['participants'][i]
        output += player['summonerName'] + " " + str(player['championId']) + " " + str(player['spell1Id']) + " " + str(player['spell2Id']) + " "
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
