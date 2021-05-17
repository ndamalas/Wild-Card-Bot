from command import Command
import discord
import time
import math
from bs4 import BeautifulSoup
import requests

# Every module has to have a command list
commandList = []


def getTimeString(seconds):
    if (seconds % 60 < 10):
        s = str(math.floor(seconds / 60)) + ":0" + str(seconds % 60)
    else:
        s = str(math.floor(seconds / 60)) + ":" + str(seconds % 60)
    return s

async def getLastStopwatch(message):
    hist = await message.channel.history(limit=100).flatten()
    lastStopwatch = None
    for old in hist:
        if old.embeds:
            description = old.embeds[0].description
            try:
                if description.find("elapsed.") != -1:
                    lastStopwatch = old
                    return lastStopwatch
            except:
                continue
    return lastStopwatch

commandList.append(Command("!stopwatch", "stopwatch", "Used to create and interact with a stopwatch.\nTo create and start a stopwatch use: `!stopwatch`\nTo stop a stopwatch use: `!stopwatch stop`\nTo unpause a stopwatch use: `!stopwatch unpause`\nTo reset a stopwatch use: `!stopwatch reset`.\nTo delete a stopwatch use: `!stopwatch delete`"))
async def stopwatch(client, message):
    content = message.content.split(' ')
    if len(content) < 2:
        # Delete old timer
        old = await getLastStopwatch(message)
        if old:
            await old.delete()
        msg = "Starting your stopwatch"
        embed = discord.Embed(title = "Stopwatch", description=msg, colour = discord.Colour.red())
        newMessage = await message.channel.send(embed=embed)
        start = time.time()
        while True:
            secondsElapsed = math.floor(time.time() - start)
            elapsed = getTimeString(secondsElapsed)
            msg = "{} elapsed.".format(elapsed)
            embed = discord.Embed(title = "Stopwatch", description=msg, colour = discord.Colour.red())
            try:
                await newMessage.edit(embed=embed)
            except:
                return
            time.sleep(0.9)
    else:
        if content[1] == "delete":
            lastStopwatch = await getLastStopwatch(message)
            if lastStopwatch == None:
                await message.channel.send("No stopwatch found.")
                return
            await lastStopwatch.delete()
            await message.channel.send("Stopwatch successfully deleted.")
            return
        elif content[1] == "stop":
            lastStopwatch = await getLastStopwatch(message)
            if lastStopwatch == None:
                await message.channel.send("No stopwatch found.")
                return
            description = lastStopwatch.embeds[0].description
            timeElapsed = description.split(" ")[0]
            await lastStopwatch.delete()
            msg = "{} elapsed. (Stopped)".format(timeElapsed)
            embed = discord.Embed(title = "Timer", description=msg, colour = discord.Colour.red())
            await message.channel.send(embed=embed)
            return
        elif content[1] == "unpause":
            lastStopwatch = await getLastStopwatch(message)
            if lastStopwatch == None:
                await message.channel.send("No stopwatch found.")
                return
            description = lastStopwatch.embeds[0].description
            if description.find("(Stopped)") == -1:
                await message.channel.send("Cannot unpause a running stopwatch.")
                return
            elapsedString = description.split(" ")[0]
            elapsedNum = (int(elapsedString[0]) * 60) + int(elapsedString[2] + elapsedString[3])
            start = time.time()
            while True:
                secondsElapsed = math.floor(time.time() - start) + elapsedNum
                elapsed = getTimeString(secondsElapsed)
                msg = "{} elapsed.".format(elapsed)
                embed = discord.Embed(title = "Stopwatch", description=msg, colour = discord.Colour.red())
                try:
                    await lastStopwatch.edit(embed=embed)
                except:
                    return
                time.sleep(0.9)
        elif content[1] == "reset":
            lastStopwatch = await getLastStopwatch(message)
            if lastStopwatch == None:
                await message.channel.send("No stopwatch found.")
                return
            await lastStopwatch.delete()
            msg = "Starting your stopwatch"
            embed = discord.Embed(title = "Stopwatch", description=msg, colour = discord.Colour.red())
            newMessage = await message.channel.send(embed=embed)
            start = time.time()
            while True:
                secondsElapsed = math.floor(time.time() - start)
                elapsed = getTimeString(secondsElapsed)
                msg = "{} elapsed.".format(elapsed)
                embed = discord.Embed(title = "Stopwatch", description=msg, colour = discord.Colour.red())
                try:
                    await newMessage.edit(embed=embed)
                except:
                    return
                time.sleep(0.9)
        else:
            await message.channel.send("Please enter a valid argument.")

# Helper to get the most recent timer
async def getLastTimer(message):
    hist = await message.channel.history(limit=100).flatten()
    lastTimer = None
    for old in hist:
        if old.embeds:
            description = old.embeds[0].description
            try:
                if description.find("remaining.") != -1:
                    lastTimer = old
                    break
            except:
                continue
    return lastTimer

commandList.append(Command("!timer", "timer", "Used to start, pause, unpause, or delete a timer.\nTo create a new timer, use: `!timer <TIME>`. The amount of time given is in minutes, (ex: if you want a 30 second timer use 0.5)\nTo pause the most recent timer, use: `!timer pause`.\nTo unpause the most recent timer, use: `!timer unpause`.\nTo delete the most recent timer, use: `!timer delete`."))
async def timer(client, message):
    content = message.content.split(' ')
    if len(content) < 2:
        await message.channel.send("Please specify the amount of time you want on your timer and whether it is in minutes or seconds.\nUsage: !timer <min/sec> <TIME>")
        return
    if content[1] == 'delete':
        lastTimer = await getLastTimer(message)
        if lastTimer == None:
            await message.channel.send("No timer found.")
            return
        await lastTimer.delete()
        await message.channel.send("Timer successfully deleted.")
        return
    elif content[1] == 'pause':
        lastTimer = await getLastTimer(message)
        if lastTimer == None:
            await message.channel.send("No timer found.")
            return
        description = lastTimer.embeds[0].description
        timeLeft = description.split(" ")[0]
        await lastTimer.delete()
        msg = "{} remaining. (Paused)".format(timeLeft)
        embed = discord.Embed(title = "Timer", description=msg, colour = discord.Colour.purple())
        await message.channel.send(embed=embed)
        return
    elif content[1] == 'unpause':
        lastTimer = await getLastTimer(message)
        if lastTimer == None:
            await message.channel.send("No timer found.")
            return
        description = lastTimer.embeds[0].description
        if description.find("(Paused)") == -1:
            await message.channel.send("Cannot unpause a running timer.")
            return
        left = description.split(" ")[0]
        start = time.time()
        end = float(left.split(":")[0]) + (float(left.split(":")[1]) / 60)
        while int(time.time() - start) < math.floor(float(end) * 60):
            secondsLeft = math.floor(float(end) * 60) - math.floor(time.time() - start)
            left = getTimeString(secondsLeft)
            msg = "{} remaining.".format(left)
            embed = discord.Embed(title = "Timer", description=msg, colour = discord.Colour.purple())
            try:
                await lastTimer.edit(embed=embed)
            except:
                return
            time.sleep(0.9)
        msg = "0:00 remaining."
        embed = discord.Embed(title = "Timer", description=msg, colour = discord.Colour.purple())
        await lastTimer.edit(embed=embed)
        await message.channel.send(message.author.mention + ", your timer is complete.")
        return

    end = content[1]
    def is_number(s):
        if s.isnumeric():
            return True
        try:
            float(s)
            return True
        except ValueError:
            return False
    if not is_number(end):
        await message.channel.send("Please enter an amount of time to run a timer.")
        return
    # Delete old timer
    old = await getLastTimer(message)
    if old:
        await old.delete()
    start = time.time()
    msg = "Starting your timer."
    embed = discord.Embed(title = "Timer", description=msg, colour = discord.Colour.purple())
    newMessage = await message.channel.send(embed=embed)
    while int(time.time() - start) < math.floor(float(end) * 60):
        secondsLeft = math.floor(float(end) * 60) - math.floor(time.time() - start)
        left = getTimeString(secondsLeft)
        msg = "{} remaining.".format(left)
        embed = discord.Embed(title = "Timer", description=msg, colour = discord.Colour.purple())
        try:
            await newMessage.edit(embed=embed)
        except:
            return
        time.sleep(0.9)
    msg = "0:00 remaining."
    embed = discord.Embed(title = "Timer", description=msg, colour = discord.Colour.purple())
    await newMessage.edit(embed=embed)
    await message.channel.send(message.author.mention + ", your timer is complete.")



commandList.append(Command("!timezone", "timezone", "Used to check the local time in a location.\nUsage: `!timezone <LOCATION>`"))
async def timezone(client, message):
    messageContents = message.content.split(" ")
    if len(messageContents) < 2:
        searchURL = "https://www.google.com/search?q=local+time"
        html = requests.get(searchURL)
        soup = BeautifulSoup(html.content, 'html.parser')
        description = soup.find_all('div', class_="BNeawe iBp4i AP7Wnd")
        if len(description) == 0:
            description = soup.find_all('div', class_="BNeawe s3v9rd AP7Wnd")
        result = description[0].text
        response = "Local time is: " + result
        embed = discord.Embed(title="Clock", description=response, colour=discord.Colour.orange())
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)
        return
    # First webscrape coordinates
    searchURL = "https://www.google.com/search?q=time+in+"
    for i in range(1, len(messageContents)):
        searchURL += messageContents[i] + "+"
    html = requests.get(searchURL)
    soup = BeautifulSoup(html.content, 'html.parser')

    description = soup.find_all('div', class_="BNeawe iBp4i AP7Wnd")
    if len(description) == 0:
        description = soup.find_all('div', class_="BNeawe s3v9rd AP7Wnd")
    result = description[0].text
    response = "Local time in "
    for i in range(1, len(messageContents)):
        response += messageContents[i] + " "
    response += "is: " + result
    # Now ask google the time difference
    searchURL = "https://www.google.com/search?q=time+difference+in+"
    for i in range(1, len(messageContents)):
        searchURL += messageContents[i] + "+"
    html = requests.get(searchURL)
    soup = BeautifulSoup(html.content, 'html.parser')
    description = soup.find_all('div', class_="BNeawe iBp4i AP7Wnd")
    if len(description) == 0:
        description = soup.find_all('div', class_="BNeawe s3v9rd AP7Wnd")
    result = description[0].text
    response += "\n" + result
    embed = discord.Embed(title="Clock", description=response, colour=discord.Colour.orange())
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)