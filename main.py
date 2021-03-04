from command import Command
import os
import os.path
import importlib
import discord
import serverAdministration
from dotenv import load_dotenv

#import requests for file download
import requests

#loads in Discord API token
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Connect to discord client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Command List will hold Command objects
commandList = {}

# Function to get out all commands to the user
def getCommandList():
	response = "```!help\n!commands\n"
	# response = "!commands\n"
	for command in commandList:
		response += "" + command + "\n"
	response += "```"
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
#Reload: clear command list and reload in commands
def reload():
	#error, accessing before assignment?
	commandList.clear()
	loadAdminCommands()
	loadCommands()


#Downloading function
async def downloadFile(message):
	#Check if user has administrator privleges
	if(not message.author.guild_permissions.administrator):
		await message.channel.send("You do not have permission to add files")
		return
	#if attached file exists
	if(message.attachments):
		#Check if filename already exists in modules
		if(os.path.isfile("modules/"+message.attachments[0].filename)):
			await message.channel.send("Module with that filename already exists, new file not added.")
			return
		#grab data from file
		r = requests.get(message.attachments[0].url)
		#write data to new file in modules directory
		newFile = open("modules/" + message.attachments[0].filename, "w")
		newFile.write(r.text)
		newFile.close()
		#Check formatting
		if(not checkFormat(message.attachments[0].filename)):
			os.remove("modules/" + message.attachments[0].filename)
			await message.channel.send("File missing command list! File not added.")
			return
		#Check for collisions
		if(collides(message.attachments[0].filename)):
			os.remove("modules/" + message.attachments[0].filename)
			await message.channel.send("File command collides with existing command! File not added.")
			return
		#reload commands
		reload()
		#Send success message
		await message.channel.send("File {} successfully uploaded and ready to use!".format(message.attachments[0].filename))
	else:
		await message.channel.send("No file attached!")

#used to remove files
async def removeFile(message):
	#check for admin priv
	if(not message.author.guild_permissions.administrator):
		await message.channel.send("You do not have permission to delete files")
		return
	#get filename
	filename = message.content.split(' ')[1]
	#if not .py add it
	if(not filename.endswith(".py")):
		filename = filename + ".py"
	#check if files exists
	if(not os.path.isfile("modules/"+filename)):
		await message.channel.send("File {} not found.".format(filename))
		return
	#remove file
	os.remove("modules/"+filename)
	#reload
	reload()
	await message.channel.send("File {} successfully removed.".format(filename))

def listModules():
	response = "```\n"
	for filename in os.listdir("modules"):
		# grab all .py files except for the init file
		if (filename.endswith(".py") and not filename.startswith("__init__")):
			response = response + "{}\n".format(filename)
	response = response + "```"
	return response




#Checks to make sure function is formatted correctly
def checkFormat(filename):
	#load file as module, then check if there is a command list?
	module = importlib.import_module("modules." + filename.replace(".py", ""))
	#check if there is a command list
	try:
		#try to access command list, if an exception occurs its a bad file
		len(module.commandList)
		return True
	except:
		return False

def collides(filename):
	#load module
	module = importlib.import_module("modules." + filename.replace(".py", ""))
	#Check if any commands are already used
	for c in module.commandList:
		if c.name in commandList:
			return True
	#return false if no collisions are found
	return False
			
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
	
	# Remove messages with banned words
	# True is returned if the message should be deleted for having a banned word
	if serverAdministration.checkMessageForBannedWords(message) == True:
		# Ping the user and warn them about the banned word
		# This part is not done by Matthew, currently holds a temp response
		response = ">>> You used a banned word."
		await message.channel.send(response)
		await message.delete()
		return

	# Remove links if the channel is currently being monitored
	# True is returned if the message should be deleted due to the message having a link
	if serverAdministration.checkMessageForLinks(message) == True:
		# Ping the user and warn them about links
		user = message.author.mention
		response = user + " Please do not post links in this channel.\n"
		response += "Messages with links are strictly prohibited in this channel and will be deleted."
		embed = discord.Embed(title='Links are NOT Allowed in This Channel', description=response, colour=discord.Colour.red())
		embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
		await message.channel.send(embed=embed)
		await message.delete()
		return

	# Check if it is a command:
	if message.content.startswith('!'):
		if (len(message.content) == 1 or message.content == '!commands'):
			await getCommands(client, message)
			return
		#command to download function
		if (message.content == '!add'):
			await downloadFile(message)
			return
		if (message.content.startswith('!del')):
			await removeFile(message)
			return
		if (message.content == '!modules'):
			await message.channel.send(listModules())
			return
		# Get the first word in the message, which would be the command
		name = message.content.split(' ')[0]
		if (name == '!help'):
			await help(client, message)
			return
		# If it exists, call the command, otherwise warn user it was not recognized
		if name in commandList:
			await commandList[name].callCommand(client, message)
			return
		await message.channel.send("Sorry that command was not recognized!")

	#Todo: File upload command:
			
# Display a list of either all command functionality
async def help(client, message):
	messageArray = message.content.split(' ')
	# For when users only want help on specific commands
	if (len(messageArray) > 1):
		embed = discord.Embed(title = "Help", colour = discord.Colour.green())
		embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
		for i in range(1, len(messageArray)):
			if messageArray[i] in commandList:
				command = messageArray[i]
				embed.add_field(name='`'+command+'`', value=commandList[command].description, inline=False)
			else:
				await message.channel.send(messageArray[i] + " not found in commands list, try again.")
				return
	else:
		# This will display a response that will hold descriptions of all of the commands
		embed = discord.Embed(title = "Help", description = "**How to use all of the commands.**", colour = discord.Colour.green())
		embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
		#Manually add in !help and !commands since they aren't in the commandList
		embed.add_field(name="`!help`", value="Will display all of the commands and descriptions if given no arguments.\nTo view only a specific command's diescription and usage: Use !help <COMMAND>.", inline=False)
		embed.add_field(name="`!command`", value="Will display a list of all available comamnds.\nAn alias for this command is to just type \"!\".")
		for command in commandList:
			embed.add_field(name='`'+command+'`', value=commandList[command].description, inline=False)
	await message.channel.send(embed=embed)


# Display a list of either all command functionality
async def getCommands(client, message):
    # c = commandList['!example']
	# url = (await c.callCommand(client, message))
	description = getCommandList()
	embed = discord.Embed(title = 'Commands', description = description, colour = discord.Colour.green())
	embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
	# embed.add_field(name='[hello](c.callCommand(client, message))')
	await message.channel.send(embed=embed)

#Run the bot
client.run(TOKEN)
