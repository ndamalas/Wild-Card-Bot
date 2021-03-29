from discord.message import Message
from command import Command
import discord
import time
import math
import threading
import asyncio

#Function to test sending data to external commands

# Every module has to have a command list
commandList = []

def getTimeString(seconds):
    if (seconds % 60 < 10):
        s = str(math.floor(seconds / 60)) + ":0" + str(seconds % 60)
    else:
        s = str(math.floor(seconds / 60)) + ":" + str(seconds % 60)
    return s

commandList.append(Command("!stopwatch", "stopwatch", "TODO"))
async def stopwatch(client, message):
    content = message.content.split(' ')
    if len(content) < 2:
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
            time.sleep(0.95)
    else:
        pass

# Helper to get the most recent timer
async def getLastTimer(message):
    hist = await message.channel.history(limit=100).flatten()
    lastTimer = None
    for old in hist:
        if old.embeds:
            description = old.embeds[0].description
            if description.find("remaining.") != -1:
                lastTimer = old
                break
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
        msg = "{} remaining.".format(timeLeft)
        embed = discord.Embed(title = "Timer", description=msg, colour = discord.Colour.purple())
        await message.channel.send(embed=embed)
        return
    elif content[1] == 'unpause':
        lastTimer = await getLastTimer(message)
        if lastTimer == None:
            await message.channel.send("No timer found.")
            return
        description = lastTimer.embeds[0].description
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
            time.sleep(0.95)
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
        time.sleep(0.95)
    msg = "0:00 remaining."
    embed = discord.Embed(title = "Timer", description=msg, colour = discord.Colour.purple())
    await newMessage.edit(embed=embed)
    await message.channel.send(message.author.mention + ", your timer is complete.")



commandList.append(Command("!timezone", "timezone", "TODO"))
async def timezone(client, message):
    pass