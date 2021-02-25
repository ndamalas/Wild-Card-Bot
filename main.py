# from command import Command
import os
import importlib
import discord
import serverAdministration
from dotenv import load_dotenv

#loads in Discord API token
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Connect to discord client
intents = discord.Intents.all()
client = discord.Client(intents=intents)


# Command List will hold Command objects
commandList = {}

# Function to print out all commands to the user
def printCommandList():
    response = '!commands\n'
    for command in commandList:
        response += command + '\n'
    return response


# Load commands from the serverAdministration.py file
def loadAdminCommands():
	for c in serverAdministration.commandList:
		# Check for command collisions
		if c.name in commandList:
			print("Error: Command collision on {} when loading {}".format(c.name, serverAdministration))
			break
		# If no collisions, load the module
		c.module = serverAdministration
		commandList[c.name] = c

# Call to load the admin commands using the function above
loadAdminCommands()

#Function to load in commands
def loadCommands():
	# Load modules from functions folder:
	for filename in os.listdir("modules"):
		# grab all .py files except for the init file
		if (filename.endswith(".py") and not filename.startswith("__init__")):
			# get module name
			filename = filename.replace(".py", "")
			# import files as a module using importlib
			module = importlib.import_module("modules." + filename)
			# for each command in the module commandList, if not a collision, add it to the main commandList dictionary with the command as they key and module as the value
			for c in module.commandList:
				if c.name in commandList:
					print("Error: Command collision on {} when loading {}".format(c.name, "modules." + filename))
					break
				c.module = module
				commandList[c.name] = c
#Call function above to load the commands
loadCommands()

#Now refresh function (when we make it) is just clearing commandList and calling loadAdminCommands and loadCommands()
			
# When the bot is ready it will print to console
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

# When a user sends a message, checks the contents and responds if containing the command
@client.event
async def on_message(message):
	#if message sender is the bot, don't check it
	if message.author == client.user:
		return

	# Check if it is a command:
	if message.content.startswith('!'):
		#command to print out the command list
		if (message.content == '!commands'):
			await message.channel.send(printCommandList())
			return
		
		# Get the first word in the message, which would be the command
		name = message.content.split(' ')[0]
		# If it exists, call the command, otherwise warn user it was not recognized
		if name in commandList:
			await commandList[name].callCommand(client, message)
			return
		await message.channel.send("Sorry that command was not recognized!")

	# Else, should be send to the chat moderation function to check for banned words, etc.
			


#Run the bot
client.run(TOKEN)
