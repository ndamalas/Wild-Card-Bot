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
    session = aiohttp.ClientSession()
    name = message.content.split(" ")[1]
    output = await session.get(f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={steam_api_key}&vanityurl={name}")
    out = await output.json()
    await session.close()
    myDf = pd.DataFrame.from_dict(out)
    print(myDf['response'][myDf.index == "steamid"].item())
    
