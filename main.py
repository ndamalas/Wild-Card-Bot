from command import Command
import os
import importlib
import discord
import serverAdministration
from dotenv import load_dotenv

#loads in Discord API token
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Connect to discord client
client = discord.Client()


# Command List will hold Command objects
commandList = {}

# Function to print out all commands to the user
def printCommandList():
    response = ''
    for command in commandList:
        response += command + '\n'
    return response


# Load commands from the serverAdministration.py file
def loadAdmin():
	for c in serverAdministration.commandList:
		if c.name in commandList:
			print("Error: Command collision on {} when loading {}".format(c.name, serverAdministration))
			break
		c.module = serverAdministration
		commandList[c.name] = c
loadAdmin()

# Load functions from functions folder:
for filename in os.listdir("modules"):
	#grab all .py files except for the init file
	if (filename.endswith(".py") and not filename.startswith("__init__")):
		#get module name
		filename = filename.replace(".py", "")
		#import files as a module
		module = importlib.import_module("modules." + filename)
		for c in module.commandList:
			if c.name in commandList:
				print("Error: Command collision on {} when loading {}".format(c.name, "modules." + filename))
				break
			c.module = module
			commandList[c.name] = c
			
#When the bot is ready it will print to console
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

#When a user sends a message, checks the contents and responds if containing the command
@client.event
async def on_message(message):
	#if message sender is the bot, don't check it
	if message.author == client.user:
		return

	#make sure it is a command:
	if message.content.startswith('!'):
		if (message.content == '!commands'):
			await message.channel.send(printCommandList())
			return
		
		name = message.content.split(' ')[0]
		if name in commandList:
			await commandList[name].callCommand(client, message)
			return
		await message.channel.send("Sorry that command was not recognized!")
			


#Run the bot
client.run(TOKEN)
