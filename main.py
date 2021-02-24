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

#Dictionary to hold prefixes (commands) and the function file
externalFunctions = {}

#Load functions from functions folder:
for filename in os.listdir("functions"):
	#grab all .py files except for the init file
    if filename.endswith(".py") and not filename.startswith("__init__"):      
        #get module name
        filename = filename.replace(".py", "")
        #import files as a module
        externalFunc = importlib.import_module("functions."+filename)
        #if command already exists in dict, don't load the file and warn the console
        if externalFunc.prefix in externalFunctions:
        	print("Error: Command collision on {} when loading {}\nModule not loaded".format(externalFunc.prefix, "functions." + filename))
        else:
        	#add modules to dict with the command as the key
        	externalFunctions[externalFunc.prefix] = externalFunc

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

	#basic test command
	if message.content == '!test':
		response = "Test successful!"
		await message.channel.send(response)
		return

	#make sure it is a command:
	if message.content.startswith('!'):
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
    

#Run the bot
client.run(TOKEN)
