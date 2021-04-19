# from os import link
from bs4 import BeautifulSoup
from command import Command
import requests
import discord
from sympy.solvers import solve
from sympy import Symbol


# Every module has to have a command list
commandList = []

async def solveNormal(equation, message):
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
    # Retrieve the google search
    searchURL = "https://www.google.com/search?q=" + equation
    html = requests.get(searchURL)
    soup = BeautifulSoup(html.content, 'html.parser')

    # Find answer in calculator

    div = soup.find_all('div', class_='BNeawe iBp4i AP7Wnd')
    if len(div) == 0:
        await message.channel.send("Invalid Equation")
        return
    answer = div[0].text
    answer = answer.replace("\xa0", ",")
    span = soup.find_all('span', class_='BNeawe tAd8D AP7Wnd')
    newEquation = span[0].text
    result = newEquation + " " + answer
    embed = discord.Embed(title = "Result: " + answer, description=result, colour = discord.Colour.blue())
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)

async def solveAlgebraic(equation, message):
    original = equation
    i = 0
    var = ""
    start = 0
    while i < len(equation):
        if equation[i].isalpha():
            if var != "":
                await message.channel.send("Invalid Equation")
                return
            var = equation[i]
            if i != 0 and equation[i-1].isnumeric() and equation[i-1] != '(':
                equation = equation[:i] + "*" + equation[i:]
                i += 1
        if equation[i] == '=':
            start = i
            if (not equation[i-1].isnumeric() and equation[i-1] != ')') or (not equation[i+1].isnumeric() and equation[i+1] != '('):
                await message.channel.send("Invalid Equation")
                return
        if equation[i] == '^':
            equation = equation[:i] + "**" + equation[i+1:]
            i += 1
        i += 1
    if not str(equation[len(equation)-1]).isnumeric():
        await message.channel.send("Invalid Equation")
        return

    afterEquals = equation[start+1:]
    equation = equation[:start]
    equation += "-(" + afterEquals + ")"
    x = Symbol(var)
    try:
        solution = solve(equation, x)
    except:
        await message.channel.send("Invalid Equation")
        return
    result = ""
    for num in solution:
        result += str(num) + ", "
    result = result[:-2]
    embed = discord.Embed(title = "Result: " + var + " = " + result, description= original + "\n" + var + " = " + result, colour = discord.Colour.blue())
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)
    



commandList.append(Command("!calc", "math", "TODO"))
async def math(client, message):
    contents = message.content.split(" ")
    equation = "".join(contents[1:])
    # Replace symbols to be used in the google calculator
    """i = 0
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
        i += 1"""
    if '=' not in equation:
        equation += '='
        await solveNormal(equation, message)
        return
    await solveAlgebraic(equation, message)
    return

    
    # await message.channel.send("**" + answer + "**")
