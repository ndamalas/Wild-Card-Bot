from command import Command
import os
import importlib
import discord
from dotenv import load_dotenv

#loads in Discord API token
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Connect to discord client
client = discord.Client()


# Command List will hold Command objects
commandList = []

# Function to print out all commands to the user
def printCommandList():
    response = ''
    for command in commandList:
        response += '!' + command.name + '\n'
    return response

userList = []

def putUsersInList():
	pass

#Dictionary to hold prefixes (commands) and the function file
externalFunctions = {}

#Load functions from functions folder:
for filename in os.listdir("modules"):
	#grab all .py files except for the init file
	if (filename.endswith(".py") and not filename.startswith("__init__")):
		#get module name
		filename = filename.replace(".py", "")
		#import files as a module
		module = importlib.import_module("modules." + filename)
		for c in module.commandList:
			c.module = module
			commandList.append(c)
			

		"""
		externalFunc = importlib.import_module("functions."+filename)
        #if command already exists in dict, don't load the file and warn the console
        if externalFunc.prefix in externalFunctions:
        	print("Error: Command collision on {} when loading {}\nModule not loaded".format(externalFunc.prefix, "functions." + filename))
        else:
        	#add modules to dict with the command as the key
        	externalFunctions[externalFunc.prefix] = externalFunc
		"""
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

		name = message.content[1:]
		for command in commandList:
			if (name == command.name):
				await command.callCommand(client, message)
				return
		await message.channel.send("Sorry that command was not recognized!")
			
"""
		#first part of message will be command
		prefix = message.content.split(' ')[0]
		#if prefix is found, send to function
		if prefix in externalFunctions:
			#calls function from external file, all functions must have same name it seems
			await externalFunctions[prefix].func(client, message)
			return

		#Tell user if command was not valid
		else:
			await message.channel.send("Sorry that command was not recognized!")
"""

# Testing
# Add a command to the command list
testCommand = Command('hello', None, None)
testCommand1 = Command('test1', None, None)
testCommand2 = Command('test2', None, None)
testCommand3 = Command('test3', None, None)
testCommand4 = Command('test4', None, None)


commandList.append(testCommand)
commandList.append(testCommand1)
commandList.append(testCommand2)
commandList.append(testCommand3)
commandList.append(testCommand4)


#Run the bot
client.run(TOKEN)
