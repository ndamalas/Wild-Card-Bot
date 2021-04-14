# from os import link
# from bs4 import BeautifulSoup
from command import Command
import requests
import discord


# Every module has to have a command list
commandList = []

commandList.append(Command("!math", "math", "TODO"))
async def math(client, message):
    contents = message.content.split(" ")
    equation = contents[1:],join()
    print(equation)