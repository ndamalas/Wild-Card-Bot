import os
import importlib
import discord
from dotenv import load_dotenv

#loads in Discord API token
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Connect to discord client
client = discord.Client()

#Dictionary to hold prefixes and the response
externalFunctions = {}

#Load functions from functions folder:
for filename in os.listdir("functions"):
    if filename.endswith(".py") and not filename.startswith("__init__"):
        #print out filepath to be sure it's working
        print(os.path.join("functions", filename))
        
        #get module name
        filename = filename.replace(".py", "")
        print("functions."+filename)
        external = importlib.import_module("functions."+filename)
        externalFunctions[external.prefix] = external

#When the bot is ready it will print to console
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

#When a user sends a message, checks the contents and responds if containing the command
@client.event
async def on_message(message):
	if message.author == client.user:
		return
	if message.content == '!test':
		response = "Test successful!"
		await message.channel.send(response)

	# #check for prefixes from external functions
	# for x in externalFunctions.keys():
	# 	if message.content.startswith(x):
	# 		#send data to external function
	# 		await externalFunctions[x].func(client, message)
	# 		break;

	#first part of message will be command
	#if prefix is found, send to function
	prefix = message.content.split(' ')[0]
	if prefix in externalFunctions:
		await externalFunctions[prefix].func(client, message)
    

#Run the bot
client.run(TOKEN)
