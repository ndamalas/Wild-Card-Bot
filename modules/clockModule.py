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

commandList.append(Command("!stopwatch", "stopwatch", "TODO"))
async def stopwatch(client, message):
    pass
# start = time.time()
# while int(time.time() - start) < int(10):
#     time.sleep(1)
#     print(math.floor(time.time() - start))
# Helper to get the most recent timer
async def getLastTimer(client, message):
    hist = await message.channel.history(limit=30).flatten()
    for old in hist:
        if old.author == client.user and (old.content.find("remaining.") != -1):
            lastTimer = old
            break
    return lastTimer

commandList.append(Command("!timer", "timer", "TODO"))
async def timer(client, message):
    content = message.content.split(' ')
    if len(content) < 2:
        await message.channel.send("Please specify the amount of time you want on your timer and whether it is in minutes or seconds.\nUsage: !timer <min/sec> <TIME>")
        return
    if content[1] == 'delete':
        lastTimer = await getLastTimer(client, message)
        await lastTimer.delete()
        await message.channel.send("Timer successfully deleted.")
        return
    elif content[1] == 'pause':
        lastTimer = await getLastTimer(client, message)
        timeLeft = lastTimer.content.split(" ")[0]
        await lastTimer.delete()
        await message.channel.send(content="{} remaining.".format(timeLeft))
        return
    elif content[1] == 'unpause':
        lastTimer = await getLastTimer(client, message)
        left = lastTimer.content.split(" ")[0]
        start = time.time()
        end = float(left.split(":")[0]) + (float(left.split(":")[1]) / 60)
        while int(time.time() - start) < math.floor(float(end) * 60):
            secondsLeft = math.floor(float(end) * 60) - math.floor(time.time() - start)
            if (secondsLeft % 60 < 10):
                left = str(math.floor(secondsLeft / 60)) + ":0" + str(secondsLeft % 60)
            else:
                left = str(math.floor(secondsLeft / 60)) + ":" + str(secondsLeft % 60)
            try:
                await lastTimer.edit(content="{} remaining.".format(left))
            except:
                return
            time.sleep(0.95)
        await lastTimer.edit(content="0:00 remaining.")
        await message.channel.send(message.author.mention + ", your timer is complete.")
        return
        
        
    # if not(content[1] == "min" or content[1] == "sec"):
    #     await message.channel.send("Please specify the amount of time you want on your timer and whether it is in minutes or seconds.\nUsage: !timer <min/sec> <TIME>")
    #     return
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
    start = time.time()
    # if content[1] == 'sec':
    #     newMessage = await message.channel.send("{} seconds remaining.".format(end))
    #     while int(time.time() - start) < math.floor(float(end)):
    #         await newMessage.edit(content="{} seconds remaining.".format(int(math.floor(float(end))) - math.floor(time.time() - start)))
    #         time.sleep(0.95)
    #     try:
    #         await newMessage.edit(content="0 seconds remaining.")
    #     except:
    #         return
    #elif content[1] == 'min':
    left = "0:00"
    newMessage = await message.channel.send("Starting your timer.")
    while int(time.time() - start) < math.floor(float(end) * 60):
        secondsLeft = math.floor(float(end) * 60) - math.floor(time.time() - start)
        if (secondsLeft % 60 < 10):
            left = str(math.floor(secondsLeft / 60)) + ":0" + str(secondsLeft % 60)
        else:
            left = str(math.floor(secondsLeft / 60)) + ":" + str(secondsLeft % 60)
        try:
            await newMessage.edit(content="{} remaining.".format(left))
        except:
            return
        time.sleep(0.95)
    await newMessage.edit(content="0:00 remaining.")
    await message.channel.send(message.author.mention + ", your timer is complete.")



commandList.append(Command("!timezone", "timezone", "TODO"))
async def timezone(client, message):
    pass