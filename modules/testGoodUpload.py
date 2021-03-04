from command import Command
import string
import discord

#this file does have a command list
commandList = []

commandList.append(Command("!good", "goodFunction", "This is an example of a good function."))
async def goodFunction(client, message):
    response = "Good file works."
    await message.channel.send(response)

if(commandList):
	print("yes")