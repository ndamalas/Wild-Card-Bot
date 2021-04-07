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
    


