# from os import link
from bs4 import BeautifulSoup
from command import Command
import requests
import discord
from sympy import *


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
    



commandList.append(Command("!calc", "math", "Will solve any given math problem. It has support for all basic operations including algebra and trigonometry.\nUsage: `!calc <EQUATION>`"))
async def math(client, message):
    contents = message.content.split(" ")
    if (len(contents) < 2):
        await message.channel.send("Please provide an equation.")
        return
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

    
commandList.append(Command("!derive", "derivative", "Will find the derivative of the equation given with respect to x.\nUsage: `!derive <EQUATION>`"))
async def derivative(client, message):
    contents = message.content.split(" ")
    if (len(contents) < 2):
        await message.channel.send("Please provide an equation.")
        return
    equation = "".join(contents[1:])
    original = equation

    i = 0
    while i < len(equation):
        if equation[i].isalpha():
            if i != 0 and equation[i-1].isnumeric():
                equation = equation[:i] + "*" + equation[i:]
                i += 1
        if equation[i] == "^":
            equation = equation[:i] + "**" + equation[i+1:]
            i += 1
        i += 1
    x = Symbol('x')
    try:
        solution = Derivative(equation, x).doit()
    except:
        await message.channel.send("Invalid Equation")
        return
    
    i = 1
    solStr = str(solution)
    if "Derivative" in solStr:
        await message.channel.send("Equation not supported, try again.")
        return
    while i < len(solStr):
        if solStr[i] == '*' and solStr[i-1] == '*':
            solStr = solStr[:i] + "^" + solStr[i+1:]
        i += 1
    solStr = solStr.replace("*", "")

    embed = discord.Embed(title =  solStr,  description = original + "\nDerivative with respect to x: " + solStr, colour = discord.Colour.blue())
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)


async def solveDefinite(message):
    contents = message.content.split(" ")
    if (len(contents) < 5):
        await message.channel.send("Please provide upper and lower bounds for the definite integral.")
        return
    a = float(contents[2])
    b = float(contents[3])
    equation = "".join(contents[4:])
    original = equation
    i = 0
    while i < len(equation):
        if equation[i].isalpha():
            if i != 0 and equation[i-1].isnumeric():
                equation = equation[:i] + "*" + equation[i:]
                i += 1
        if equation[i] == "^":
            equation = equation[:i] + "**" + equation[i+1:]
            i += 1
        i += 1
    x = Symbol('x')
    try:
        solution = integrate(equation, (x, a, b))
    except:
        await message.channel.send("Invalid Equation")
        return
    
    i = 1
    solStr = str(solution)
    if "integral" in solStr:
        await message.channel.send("Equation not supported, try again.")
        return
    while i < len(solStr):
        if solStr[i] == '*' and solStr[i-1] == '*':
            solStr = solStr[:i] + "^" + solStr[i+1:]
        i += 1
    solStr = solStr.replace("*", "")
    solStr = solStr[:5]

    embed = discord.Embed(title = solStr,  description = original + "\nDefinite integral from {} to {} with respect to x: ".format(a, b) + solStr, colour = discord.Colour.blue())
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)

async def solveIndefinite(message):
    contents = message.content.split(" ")
    equation = "".join(contents[1:])
    original = equation
    i = 0
    while i < len(equation):
        if equation[i].isalpha():
            if i != 0 and equation[i-1].isnumeric():
                equation = equation[:i] + "*" + equation[i:]
                i += 1
        if equation[i] == "^":
            equation = equation[:i] + "**" + equation[i+1:]
            i += 1
        i += 1
    x = Symbol('x')
    try:
        solution = integrate(equation, x)
    except:
        await message.channel.send("Invalid Equation")
        return
    
    i = 1
    solStr = str(solution)
    if "integral" in solStr:
        await message.channel.send("Equation not supported, try again.")
        return
    while i < len(solStr):
        if solStr[i] == '*' and solStr[i-1] == '*':
            solStr = solStr[:i] + "^" + solStr[i+1:]
        i += 1
    solStr = solStr.replace("*", "")

    embed = discord.Embed(title = solStr + "  + C",  description = original + "\nIndefinite integral with respect to x: " + solStr + "  + C", colour = discord.Colour.blue())
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)


commandList.append(Command("!integrate", "integral", "Will find the integral of the equation given with respect to x.\nYou can choose between definite and indefinite integrals.\nUsage for indefinite integrals: `!integrate <EQUATION>`\nUsage for definite integrals: `!intgrate definite <A> <B> <EQUATION>"))
async def integral(client, message):
    contents = message.content.split(" ")
    if contents[1] == "definite":
        await solveDefinite(message)
        return
    await solveIndefinite(message)
    return