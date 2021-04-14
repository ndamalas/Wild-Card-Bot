# from os import link
from bs4 import BeautifulSoup
from command import Command
import requests
import discord


# Every module has to have a command list
commandList = []

commandList.append(Command("!calc", "math", "TODO"))
async def math(client, message):
    contents = message.content.split(" ")
    equation = "".join(contents[1:])
    # Replace symbols to be used in the google calculator
    i = 0
    while i < len(equation):
        if equation[i] == '+':
            equation = equation[:i] + "%2B" + equation[i+1:]
            i += 1
        elif equation[i] == '/':
            equation = equation[:i] + "%2F" + equation[i+1:]
            i += 1
        elif equation[i] == '%':
            equation = equation[:i] + "%25" + equation[i+1:]
            i += 1
        i += 1
    if equation[len(equation)-1] != '=':
        equation += '='

    # Retrieve the google search
    searchURL = "https://www.google.com/search?q=" + equation
    html = requests.get(searchURL)
    soup = BeautifulSoup(html.content, 'html.parser')

    # Find answer in calculator

    div = soup.find_all('div', class_='BNeawe iBp4i AP7Wnd')
    answer = div[0].text
    answer = answer.replace("\xa0", ",")
    span = soup.find_all('span', class_='BNeawe tAd8D AP7Wnd')
    newEquation = span[0].text
    result = newEquation + " " + answer
    embed = discord.Embed(title = "Result: " + answer, description=result, colour = discord.Colour.blue())
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)
    # await message.channel.send("**" + answer + "**")
