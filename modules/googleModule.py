from bs4 import BeautifulSoup
from command import Command
import requests
import discord
from googlesearch import search 


#Function to test sending data to external commands

# Every module has to have a command list
commandList = []

commandList.append(Command("!google", "googleSearch", "TODO"))
async def googleSearch(client, message):
    contents = message.content.split(" ")
    if len(contents) == 1:
        await message.channel.send("Please give an argument to be searched on google.")
    
    embed = discord.Embed(title = "Google", colour = discord.Colour.green())
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    # to search 
    query = ""
    for i in range(1, len(contents)-1):
        if (contents[1].isnumeric()):
            i += 1
        query += contents[i] + "+"
    query += contents[len(contents)-1]
    searchURL = "https://www.google.com/search?q=" + query
    html = requests.get(searchURL)
    soup = BeautifulSoup(html.content, 'html.parser')

    if (contents[1].isnumeric()):
        numResults = int(contents[1])
        for i in search(query.replace("+", " "), tld="co.in", num=numResults, stop=numResults, pause=2):
            s = str(i)
            embed.add_field(name="Result", value=s, inline=False)
    else:
        description = soup.find_all('div', class_="BNeawe s3v9rd AP7Wnd")
        result = description[0].text
        embed = discord.Embed(title = "Google", description=result, colour = discord.Colour.green())
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
        
    await message.channel.send(embed=embed)
# Search command to give hyperlinks
