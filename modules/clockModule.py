from discord.message import Message
from command import Command
import discord
import time
import math

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

commandList.append(Command("!timer", "timer", "TODO"))
async def timer(client, message):
    content = message.content.split(' ')
    if len(content) < 2:
        await message.channel.send("Please specify the amount of time you want on your timer.")
        return
    start = time.time()
    end = content[1]
    if not end.isnumeric():
        await message.channel.send("Please enter a number of seconds to run a timer.")
        return
    newMessage = await message.channel.send("{} seconds remaining.".format(end))
    while int(time.time() - start) < int(end):
        await newMessage.edit(content="{} seconds remaining.".format(int(end) - math.floor(time.time() - start)))
        time.sleep(1)
    await newMessage.edit(content="0 seconds remaining.")


commandList.append(Command("!timezone", "timezone", "TODO"))
async def timezone(client, message):
    pass