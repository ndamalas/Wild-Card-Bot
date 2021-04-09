import string
import discord
import asyncio
import aiohttp
import pandas as pd
from command import Command

commandList = []

steam_api_key = "54964BFA9E709E047EB70CC7A6F2BA1C"

commandList.append(Command("!steam", "get_status", ""))
async def get_status(ctx, message):
    name = message.content.split(" ")[1]

    # Get steamID from name
    session = aiohttp.ClientSession()
    output = await session.get(f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={steam_api_key}&vanityurl={name}")
    out = await output.json()
    await session.close()
    myDf = pd.DataFrame.from_dict(out)
    steamid = myDf['response'][myDf.index == "steamid"].item()

    # Get user infos
    session = aiohttp.ClientSession()
    output = await session.get(f"https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/?key={steam_api_key}&steamids={steamid}")
    out = await output.json()
    await session.close()
    pd.set_option("display.max_columns", None)
    userDf = pd.DataFrame.from_dict(out)
    userDf = userDf['response'][userDf.index == "players"][0][0]

    persona = userDf['personaname']

    # Output user status
    state = status(userDf['personastate'])
    await message.channel.send(persona + " is currently: " + state)

    # Output current game playing
    if 'gameextrainfo' in userDf:
        current_game = userDf['gameextrainfo']
    else:
        current_game = "None"
    await message.channel.send(persona + " is playing: " + current_game)


def status(state):
    s = {
        0: "Offline",
        1: "Online",
        2: "Busy",
        3: "Away",
        4: "Snooze",
        5: "Looking to trade",
        6: "Looking to play",
    }
    return s.get(state)

def unnest(myDf: pd.DataFrame, columns: list) -> pd.DataFrame:
  tempDf = pd.DataFrame()
  for i in columns:
    if i in myDf:
      if isinstance(myDf.loc[:, i].iloc[0], dict):
        x = myDf[i].apply(pd.Series)
        tempDf = pd.concat([tempDf, x], axis = 1)
  return tempDf
