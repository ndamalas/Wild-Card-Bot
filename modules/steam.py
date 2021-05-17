import string
import discord
import asyncio
import aiohttp
import pandas as pd
from command import Command
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup

commandList = []

steam_api_key = "54964BFA9E709E047EB70CC7A6F2BA1C"

commandList.append(Command("!steam", "steam_profile", "Displays a user's steam profile\nUsage: !steam profile <USERNAME>\nCan also display trending games\nUsage: !steam trending\nCan also show recently released games\nUsage: !steam recent\nCan also show the top played games in the last 2 weeks\nUsage: !steam top\n"))
async def steam_profile(ctx, message):
    msg = await message.channel.send("Gathering Information")
    if message.content.split(" ")[1] == "profile":
        name = message.content.split(" ")[2]

        # Get steamID from name
        session = aiohttp.ClientSession()
        output = await session.get(f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={steam_api_key}&vanityurl={name}")
        out = await output.json()
        await session.close()
        myDf = pd.DataFrame.from_dict(out)
        if myDf['response'][myDf.index == "success"].item() != 1:
            await msg.edit(content="Not a valid username")
            return
        steamid = myDf['response'][myDf.index == "steamid"].item()

        #Get user infos
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
        # await message.channel.send(persona + " is currently: " + state)

        # Output current game playing
        if 'gameextrainfo' in userDf:
            current_game = userDf['gameextrainfo']
        else:
            current_game = "None"
        # await message.channel.send(persona + " is playing: " + current_game)

        # Output location of user
        if 'loccountrycode' in userDf:
            location = userDf['loccountrycode']
        else:
            location = "N/A"
        # await message.channel.send(persona + " location: " + location)

        # Output groups
        session = aiohttp.ClientSession()
        output = await session.get(f"https://api.steampowered.com/ISteamUser/GetUserGroupList/v1/?key={steam_api_key}&steamid={steamid}")
        out = await output.json()
        await session.close()
        groupDf = pd.DataFrame.from_dict(out)
        groupDf = groupDf['response'][groupDf.index == "groups"][0]
        # await message.channel.send(persona + "\'s Groups: ")
        text = ""
        for group in groupDf:
            gid = group['gid']
            session = aiohttp.ClientSession()
            output = await session.get(f"https://steamcommunity.com/gid/{gid}/memberslistxml/?xml=1")
            out = await output.read()
            await session.close()
            soup = BeautifulSoup(out, 'xml')
            # await message.channel.send(soup.groupName.get_text())
            # await message.channel.send("https://steamcommunity.com/groups/" + soup.groupURL.get_text())
            txt = soup.groupName.get_text()
            link = "https://steamcommunity.com/groups/" + soup.groupURL.get_text()
            text += f"[{txt}]({link})\n"
        if not groupDf:
            text += "None"
            # await message.channel.send("None")

        # Set privacy state
        privacy = userDf["communityvisibilitystate"]
        if privacy == 3:
            privacy_state = "Public"
            # await message.channel.send(persona + "\'s profile is public")
        else:
            privacy_state = "Private"
            # await message.channel.send(persona + "\'s profile is private")

        embed=discord.Embed(title=persona, url=userDf['profileurl'], color=0x2a475e)
        embed.set_thumbnail(url=userDf['avatarfull'])
        embed.add_field(name="User Info", value=f"**Status:** {state}\n**Playing:** {current_game}\n**Profile privacy:** {privacy_state}\n**Location:** {location}\n**SteamID:** {steamid}", inline=True)
        embed.add_field(name="Groups", value=text, inline=True)

        await msg.edit(content="", embed=embed)
    elif message.content.split(" ")[1] == "groups":
        name = message.content.split(" ")[2]

        # Get steamID from name
        session = aiohttp.ClientSession()
        output = await session.get(f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={steam_api_key}&vanityurl={name}")
        out = await output.json()
        await session.close()
        myDf = pd.DataFrame.from_dict(out)
        if myDf['response'][myDf.index == "success"].item() != 1:
            await msg.edit(content="Not a valid username")
            return
        steamid = myDf['response'][myDf.index == "steamid"].item()

        #Get user infos
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
        # await message.channel.send(persona + " is currently: " + state)

        # Output current game playing
        if 'gameextrainfo' in userDf:
            current_game = userDf['gameextrainfo']
        else:
            current_game = "None"
        # await message.channel.send(persona + " is playing: " + current_game)

        # Output location of user
        if 'loccountrycode' in userDf:
            location = userDf['loccountrycode']
        else:
            location = "N/A"
        # await message.channel.send(persona + " location: " + location)

        # Output groups
        session = aiohttp.ClientSession()
        output = await session.get(f"https://api.steampowered.com/ISteamUser/GetUserGroupList/v1/?key={steam_api_key}&steamid={steamid}")
        out = await output.json()
        await session.close()
        groupDf = pd.DataFrame.from_dict(out)
        groupDf = groupDf['response'][groupDf.index == "groups"][0]
        # await message.channel.send(persona + "\'s Groups: ")
        text = ""
        for group in groupDf:
            gid = group['gid']
            session = aiohttp.ClientSession()
            output = await session.get(f"https://steamcommunity.com/gid/{gid}/memberslistxml/?xml=1")
            out = await output.read()
            await session.close()
            soup = BeautifulSoup(out, 'xml')
            # await message.channel.send(soup.groupName.get_text())
            # await message.channel.send("https://steamcommunity.com/groups/" + soup.groupURL.get_text())
            txt = soup.groupName.get_text()
            link = "https://steamcommunity.com/groups/" + soup.groupURL.get_text()
            text += f"[{txt}]({link})\n"
        if not groupDf:
            text += "None"
            # await message.channel.send("None")

        # Set privacy state
        privacy = userDf["communityvisibilitystate"]
        if privacy == 3:
            privacy_state = "Public"
            # await message.channel.send(persona + "\'s profile is public")
        else:
            privacy_state = "Private"
            # await message.channel.send(persona + "\'s profile is private")

        embed=discord.Embed(title=persona, url=userDf['profileurl'], color=0x2a475e)
        embed.set_thumbnail(url=userDf['avatarfull'])
        embed.add_field(name="Groups", value=text, inline=True)

        await msg.edit(content="", embed=embed)
    elif message.content.split(" ")[1] == "status":
        name = message.content.split(" ")[2]

        # Get steamID from name
        session = aiohttp.ClientSession()
        output = await session.get(f"https://api.steampowered.com/ISteamUser/ResolveVanityURL/v1/?key={steam_api_key}&vanityurl={name}")
        out = await output.json()
        await session.close()
        myDf = pd.DataFrame.from_dict(out)
        if myDf['response'][myDf.index == "success"].item() != 1:
            await msg.edit(content="Not a valid username")
            return
        steamid = myDf['response'][myDf.index == "steamid"].item()

        #Get user infos
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
        await msg.edit(content=state)
    elif message.content.split(" ")[1] == "trending":
        #Gets the website and uses beautifulSoup to parse html website
        #the request is so that it doesn't deny access thinking we are bots
        URL = 'https://steamspy.com'
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(URL,headers=hdr)
        page= urlopen(req)
        soup = BeautifulSoup(page)
        #Finds the trending games table tab
        table = soup.find('table', id="trendinggames")
        #print(table)
        #Finds the table itself
        body = table.find('tbody')
        #print(body)

        #Finds the rows in the table
        rows = body.find_all('tr')
        #print(rows)

        #Array of game names we wish to output
        game_name_array = []

        #Go through the rows and add 10 games to the array
        counter = 0
        for row in rows:
            if(counter == 10):
                break
            names = row.find_all('td')
            #print(names)
            for name in names:
                #print(name)
                if(name == names[1]):
                    print(name)
                    game_name_array.append(name.get_text())
            counter += 1

        #print(game_name_array)

        #Print the array in an embed and output the embed to the user
        text=""
        for i in range(len(game_name_array)):
            text+=str(i+1) + " " + game_name_array[i] + "\n"
        embed=discord.Embed(title="Top 10 Trending Games", description=text)
        await msg.edit(content="", embed=embed)
    elif message.content.split(" ")[1] == "recent":
        #Gets the website and uses beautifulSoup to parse html website
        #the request is so that it doesn't deny access thinking we are bots
        URL = 'https://steamspy.com'
        hdr = {'User-Agent': 'Mozilla/5.0'}
        req = Request(URL,headers=hdr)
        page= urlopen(req)
        soup = BeautifulSoup(page)
        #Finds the recently released games table tab
        table = soup.find('table', id="recentgames")
        #print(table)
        #Finds the table itself
        body = table.find('tbody')
        #print(body)

        #Finds the rows in the table
        rows = body.find_all('tr')
        #print(rows)

        #Array of game names we wish to output
        game_name_array = []

        #Go through the rows and add 10 games to the array
        counter = 0
        for row in rows:
            if(counter == 10):
                break
            names = row.find_all('td')
            #print(names)
            for name in names:
                #print(name)
                if(name == names[1]):
                    print(name)
                    game_name_array.append(name.get_text())
            counter += 1

        #print(game_name_array)

        #Print the array in an embed and output the embed to the user
        text=""
        for i in range(len(game_name_array)):
            text+=str(i+1) + " " + game_name_array[i] + "\n"
        embed=discord.Embed(title="Top 10 Recently Released Games on Steam", description=text)
        await msg.edit(content="", embed=embed)
    elif message.content.split(" ")[1] == "top":

        session = aiohttp.ClientSession()
        output = await session.get("https://steamspy.com/api.php?request=top100in2weeks")
        out = await output.json()
        topDf = pd.DataFrame.from_dict(out)
        await session.close()
        print(topDf)
        #print(topDf.iloc[1][0])
        #print(topDf.iloc[1][1])

        text=""
        for i in range(10):
            text += (str(i+1) + " " + topDf.iloc[1][i] + '\n')
        embed = discord.Embed(title="Top 10 Most Played Games in the Last 2 Weeks", description=text)
        await msg.edit(content="", embed=embed)
    elif message.content.split(" ")[1] == "game":
        if len(message.content.split(" ")) <= 2:
            await message.channel.send(">>> Not enough parameters")
            return
        #if message.content.split(" ")[1] != "game":
        #return
        msg = await message.channel.send("Gathering Game Information")
        game_name = message.content[12:]
        #game_name = "Valheim"
        #await message.channel.send("Game: "+game_name)

        session = aiohttp.ClientSession()
        output = await session.get(f"http://api.steampowered.com/ISteamApps/GetAppList/v0002/")
        out = await output.json()
        await session.close()
        pd.set_option("display.max_columns", None)
        gameDf = pd.DataFrame.from_dict(out)
        #print(gameDf)
        gameDf = gameDf['applist'][gameDf.index == "apps"][0]
        #print(gameDf)
        for game in gameDf:
            current_game_name = game['name']
            if current_game_name == game_name:
                game_appid = game['appid']
                #await message.channel.send(game_appid)
                session = aiohttp.ClientSession()
                output = await session.get(f"https://store.steampowered.com/api/appdetails?appids={game_appid}")
                out = await output.json()
                await session.close()
                pd.set_option("display.max_columns", None)
                gameidDf = pd.DataFrame.from_dict(out)
                #print(gameidDf)
                gameidDf = gameidDf[gameidDf.index == 'data'][gameidDf.columns[0]][0]
                #print(gameidDf)
                #game_type = gameidDf['type']
                #print(game_type)
                title = "Game Description"
                header_image = gameidDf['header_image']
                game_info = "Name: " + gameidDf['name'] + "\n" + "Game ID: " + str(gameidDf['steam_appid']) + "\n" +  "Type: " + gameidDf['type'] + "\n" +  "Free: "  + str(gameidDf['is_free']) + "\n"
                embed=discord.Embed(title=title, description=game_info, color=0x2a475e)
                embed.set_image(url=header_image)
                await message.channel.send(embed=embed)
                #for attribute in gameidDf:
                    #print(attribute)
                    #print(gameidDf[attribute])
                    #print()
                    #await message.channel.send(attribute+":")
                    #await message.channel.send(gameidDf[attribute])
                    #await message.channel.send()
    else:
        embed=discord.Embed(title="Sorry that tag does not exist.")
        await msg.edit(content="", embed=embed)

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
