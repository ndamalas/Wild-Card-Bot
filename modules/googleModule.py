from bs4 import BeautifulSoup
from command import Command
import requests
import discord
from googlesearch import search
from youtubesearchpython import VideosSearch



#Function to test sending data to external commands

# Every module has to have a command list
commandList = []

commandList.append(Command("!google", "googleSearch", "TODO"))
async def googleSearch(client, message):
    contents = message.content.split(" ")
    if len(contents) == 1:
        await message.channel.send("Please give an argument to be searched on google.")
    
    start = 1
    if (contents[1].isnumeric() or contents[1] == "images" or contents[1] == "videos"):
        start = 2
    # to search 
    query = ""
    for i in range(start, len(contents)-1):
        query += contents[i] + "+"
    query += contents[len(contents)-1]
    searchURL = "https://www.google.com/search?q=" + query
    html = requests.get(searchURL)
    soup = BeautifulSoup(html.content, 'html.parser')
    embed = discord.Embed(title = query, colour = discord.Colour.blue())
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    if (contents[1].isnumeric()):
        numResults = int(contents[1])
        for i in search(query.replace("+", " "), tld="co.in", num=numResults, stop=numResults, pause=2):
            embed.add_field(name='\u200b', value=i, inline=False)
    elif (contents[1] == "images"):
        searchURL = "https://www.google.com/search?q=" + query + "&rlz=1C1CHBF_enUS858US858&sxsrf=ALeKk02CkZmXlqPXeG1zYfhlNWziJkRu1Q:1616111833740&source=lnms&tbm=isch&sa=X&ved=2ahUKEwjsoZHehbvvAhXELc0KHXcKBN0Q_AUoA3oECCIQBQ&biw=1266&bih=557"
        html = requests.get(searchURL)
        soup = BeautifulSoup(html.text, 'html.parser')
        # Show first 5 images
        images = soup.find_all('img')
        for i in range(2, 10):
            src = images[i].attrs['src']
            #embed.add_field(name='\u200b', value=src, inline=False)
            await message.channel.send(src)
        return
    elif (contents[1] == "videos"):
        videosSearch = VideosSearch(query.replace("+", " "), limit = 5)
        results = videosSearch.result()['result']
        for i in range(5):
            await message.channel.send(results[i]['link'])
        return
    else:
        description = soup.find_all('div', class_="BNeawe s3v9rd AP7Wnd")
        result = description[0].text
        embed = discord.Embed(title = "Google", description=result, colour = discord.Colour.green())
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
        
    await message.channel.send(embed=embed)
# Search command to give hyperlinks
