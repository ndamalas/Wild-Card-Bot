from command import Command
import os
import os.path
import sys
import importlib
import asyncio
import discord
import serverAdministration
import time
from dotenv import load_dotenv

#import requests for file download
import requests
#used to check for time vs time of modified dir
import time
import threading

#loads in Discord API token
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Connect to discord client
intents = discord.Intents.all()
client = discord.Client(intents=intents)

# Command List will hold Command objects
commandList = {}
lastmodified = ""

# List of Commands a Role cannot use
bannedCommandsByRole = {}

# List of Modules that are available
moduleList = []

# Function to get out all commands to the user
def getCommandList():
	response = "```"
	for command in commandList:
		response += "" + command + "\n"
	response += "```"
	return response

# Load the commands in the main module
def loadMainCommands():
	commandList["!help"] = Command("!help", "help", "Will display all of the commands and descriptions if given no arguments.\nTo view only a specific command's description and usage: Use !help <COMMAND>.\nTo view specific modules' commands' descriptions and usages: Use !help <MODULENAME (without .py)>.", sys.modules[__name__])
	commandList["!commands"] = Command("!commands", "getCommands", "Will display a list of all available comamnds.\nAn alias for this command is to just type \"!\".", sys.modules[__name__])
	commandList["!add"] = Command("!add", "downloadFile", "Place as a comment on an uploaded function file to add it to the modules folder", sys.modules[__name__], permissions=["administrator"])
	commandList["!del"] = Command("!del", "removeFile", "Use with the name of a module to remove it from the modules folder. !del <filename>", sys.modules[__name__], permissions=["administrator"])
	commandList["!rolecommands"] = Command("!rolecommands", "roleCommands", "Allows and blocks certain roles from specific commands.\nAlso lists the commands a role can use.\nUsage: !rolecommands <allow/block/perms> role-name (id) command", sys.modules[__name__], permissions=["manage_permissions"])
	commandList["!modules"] = Command("!modules", "getModules", "Lists all of the current modules that the user has on their bot.\nUsage: !modules", sys.modules[__name__], permissions=["administrator"])
	commandList["!rename"] = Command("!rename", "rename", "Used to rename commands.\nUsage: !rename <OLDNAME> <NEWNAME>.", sys.modules[__name__], permissions=["administrator"])



# Call function above to load the main module commands
loadMainCommands()

# Function to handle collisions with command names when being loaded from files
def handleCollision(command, module):
	newName = input("Command collision on {} when loading {}.\nPlease enter a new name for {}.\nWarning: this name will be changed in the internal python file.\n".format(command.name, module.__name__, command.name))
	oldName = command.name
	command.name = newName
	commandList[newName] = command
	# Change name in the python file
	filename = command.module.__name__
	filename = filename.replace('.', '/')
	filename += ".py"
	lines = []
	with open(filename) as f:
		lines = f.readlines()
	for i in range(len(lines)):
		# Goes line by line
		if "Command(" in lines[i] and oldName in lines[i]:
			newLine = lines[i]
			newLine = newLine.replace(oldName, newName)
			lines[i] = newLine
	file = open(filename, "w")
	for line in lines:
		file.write(line)

# Load commands from the serverAdministration.py file
def loadAdminCommands():
	for c in serverAdministration.commandList:
		c.module = serverAdministration
		# If no collisions, load the module
		commandList[c.name] = c

# Call to load the admin commands using the function above
loadAdminCommands()

#Now refresh function (when we make it) is just clearing commandList and calling loadAdminCommands and loadCommands()
#Reload: clear command list and reload in commands
def reload():
	#error, accessing before assignment?
	commandList.clear()
	loadMainCommands()
	loadAdminCommands()
	loadCommands()

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
				c.module = module
				if c.name in commandList:
					handleCollision(c, module)
					reload()
					return
				commandList[c.name] = c
#Call function above to load the commands
loadCommands()

# Get Renames
def getRenames():
	data = []
	with open("commandRenames.txt") as f:
		data = f.readlines()
	for i in range(len(data)):
		# Goes line by line
		contents = data[i].split(" ")
		command = commandList[contents[0]]
		contents[1] = contents[1].rstrip()
		command.name = contents[1]
		commandList[contents[1]] = commandList.pop(contents[0])
#Call function
getRenames()


#collect last modified for modules dir now that it is loaded
lastmodified = time.ctime(max(os.stat(root).st_mtime for root,_,_ in os.walk("modules")))
moduleLen = len(os.listdir("modules"))

#print("Len {}\nTime {}\n".format(moduleLen, lastmodified))
#Now refresh function (when we make it) is just clearing commandList and calling loadAdminCommands and loadCommands()
#Reload: clear command list and reload in commands
def reload():
	#error, accessing before assignment?
	commandList.clear()
	loadMainCommands()
	loadAdminCommands()
	loadCommands()


#Check for changes in modules directory
def checkForChanges(f_stop):
	global moduleLen
	global lastmodified
	if not f_stop.is_set():
		#check for changes
		newLen = len(os.listdir("modules"))
		newmod = time.ctime(max(os.stat(root).st_mtime for root,_,_ in os.walk("modules")))
		if(newLen != moduleLen or lastmodified != newmod):
			print("Change detected in module file!")
			moduleLen = newLen
			lastmodified = newmod
			#print("Len {}\nTime {}\n".format(moduleLen, lastmodified))
			reload()
		#every 60 seconds
		threading.Timer(60, checkForChanges, [f_stop]).start()
#have alternative threading event running to check for changes
f_stop = threading.Event()
checkForChanges(f_stop)


#Downloading function
async def downloadFile(client, message):
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
async def removeFile(client, message):
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

async def getModules(client, message):
	reponse = listModules()
	await message.channel.send(reponse)

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

# Format: !rolecommands <allow/block/perms> role-name id command
# Command used for banning certain roles from using certain commands
async def roleCommands(client, message):
    action = 0 # 0 indicates incorrect arguments and prints error
	# Set the message arguments correctly
	# Since roles can have spaces in the name, we need to account for it
    if len(message.content.split(" ")) > 1:
        messageArguments = []
        messageArguments.append(message.content.split(" ")[0]) # Command Name
        messageArguments.append(message.content.split(" ")[1]) # Action
        if message.content.split(" ")[1] == "perms" and "id" not in message.content.split(" "):
            if len(messageArguments[0]) + len(messageArguments[1]) + 2 < len(message.content):
                roleName = message.content[len(messageArguments[0]) + len(messageArguments[1]) + 2:]
                messageArguments.append(roleName)
        if message.content.split(" ")[1] == "allow" or message.content.split(" ")[1] == "block" and "id" not in message.content.split(" "):
            if len(messageArguments[0]) + len(messageArguments[1]) + 2 < len(message.content):
                roleName = message.content[len(messageArguments[0]) + len(messageArguments[1]) + 2:]
                commandName = None
                if roleName.split(" ")[-1].startswith("!") and roleName.rfind(" ") != -1:
                    commandName = roleName[roleName.rfind(" ") + 1:]
                    roleName = roleName[:roleName.rfind(" ")]
                messageArguments.append(roleName)
                if commandName != None:
                    messageArguments.append(commandName)
        if "id" in message.content.split(" "):
            messageArguments = message.content.split(" ")
    else:
        messageArguments = message.content.split(" ")

    # Determine if admin wants to allow a command, block a command, or see which commands the role can use
    if len(messageArguments) >= 5:
        # Find role by ID if specified, or else find role by name
        if messageArguments[3] == "id":
            command = messageArguments[4]
            roleId = int(messageArguments[2])
            exists = await determineRoleExists(message, command, roleId, "id")
            if exists == False:
                return
			# determine action based on second argument
            if messageArguments[1] == "allow":
                action = "allow"
                await allowCommandForRole(message, command, roleId, "id")
            if messageArguments[1] == "block":
                action = "block"
                await blockCommandFromRole(message, command, roleId, "id")
            if messageArguments[1] == "perms":
                action = "perms"
                await listPermissionsForRole(message, roleId, "id")
        else:
            command = messageArguments[3]
            roleName = messageArguments[2]
            exists = await determineRoleExists(message, command, roleName, "name")
            if exists == False:
                return
			# If multiple roles have the same name, ask user to use ID
            if await sameNameRolesCheck(message, roleName) == True:
                return
			# determine action based on second argument
            if messageArguments[1] == "allow":
                action = "allow"
                await allowCommandForRole(message, command, roleName, "name")
            if messageArguments[1] == "block":
                action = "block"
                await blockCommandFromRole(message, command, roleName, "name")
            if messageArguments[1] == "perms":
                action = "perms"
                await listPermissionsForRole(message, roleName, "name")
    elif len(messageArguments) >= 4:
        # Find role by name, or if id is specified display commands the role with id can use
        if messageArguments[3] == "id":
            command = None # Indicate that command is not needed
            roleId = int(messageArguments[2])
            exists = await determineRoleExists(message, command, roleId, "id")
            if exists == False:
                return
			# determine action based on second argument
            if messageArguments[1] == "perms":
                action = "perms"
                await listPermissionsForRole(message, roleId, "id")
        else:
            command = messageArguments[3]
            roleName = messageArguments[2]
            exists = await determineRoleExists(message, command, roleName, "name")
            if exists == False:
                return
			# If multiple roles have the same name, ask user to use ID
            if await sameNameRolesCheck(message, roleName) == True:
                return
			# determine action based on second argument
            if messageArguments[1] == "allow":
                action = "allow"
                await allowCommandForRole(message, command, roleName, "name")
            if messageArguments[1] == "block":
                action = "block"
                await blockCommandFromRole(message, command, roleName, "name")
            if messageArguments[1] == "perms":
                action = "perms"
                await listPermissionsForRole(message, roleName, "name")
    elif len(messageArguments) >= 3:
        # List all available commands to a specific role
        command = None # Indicate that command is not needed
        roleName = messageArguments[2]
        exists = await determineRoleExists(message, command, roleName, "name")
        if exists == False:
                return
		# If multiple roles have the same name, ask user to use ID
        if await sameNameRolesCheck(message, roleName) == True:
            return
        if messageArguments[1] == "perms":
            action = "perms"
            await listPermissionsForRole(message, roleName, "name")
    else:
        response = "Please provide a role name, a command, and whether to allow or block the command!\n"
        response += "Command format: **!rolecommands allow/block role-name command**\n\n"
        response += "You may also view the commands the current role can call.\n"
        response += "Command format: **!rolecommands perms role-name**"
        embed = discord.Embed(title='!rolecommands Usage', description=response, colour=discord.Colour.blue())
        await message.channel.send(embed=embed)
        action = "error" # Prevent the prompt from being printed twice
	# If an action was not specified or incorrectly specified, notify the user
    if action == 0:
        response = "Please specify whether you want to allow or block a role from a command!\n"
        response += "Command format: **!rolecommands allow/block role-name command**\n\n"
        response += "If you wanted to view the permissions of a role, use the command below.\n"
        response += "Command format: **!rolecommands perms role-name**"
        embed = discord.Embed(title='!rolecommands Usage', description=response, colour=discord.Colour.blue())
        await message.channel.send(embed=embed)

# Helper function for roleCommands
async def determineRoleExists(message, command, role, nameOrId):
    # Check to see if command actually exists on the server
    if command != None and command not in commandList:
        response = "The command " + command + " was not found in the command list!"
        embed = discord.Embed(title='Not In Command List', description=response, colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return False
    # Check to see if the role exists on the server
    if nameOrId == "name":
        roleName = role
        roleExists = False
        for role in message.guild.roles:
            if role.name == roleName:
                roleExists = True
                break
    else:
        roleId = role
        roleExists = False
        for role in message.guild.roles:
            if role.id == roleId:
                roleExists = True
                break
    # Throw error if role does not exists
    if roleExists == False:
        response = "That role was not found on the server!"
        embed = discord.Embed(title='No Such Role', description=response, colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return False
    return True

# Helper function for roleCommands that checks if multiple roles have the same name
# Returns True if there are same name roles, False if there are not
async def sameNameRolesCheck(message, roleName):
	roleCount = 0
	for role in message.guild.roles:
		if role.name == roleName:
			roleCount += 1
	# If there are more than one role named roleName, tell user
	if roleCount > 1:
		response = "Multiple matches found for the role **" + roleName + "**. Please specify using role ID.\n"
		responseCount = 1
		for role in message.guild.roles:
			if role.name == roleName:
				response += str(responseCount) + ". " + str(role.id) + "\n"
				responseCount += 1
		response += "\nIf you want to allow or block the role **" + roleName + "** from a command, use the following command:\n"
		response += "**!rolecommands allow/block role-id id command**\n\n"
		response += "If you want to view the permissions of the role **" + roleName + "**, use the following command:\n"
		response += "**!rolecommands perms role-id id**"
		embed = discord.Embed(title='Multiple Roles Found', description=response, colour=discord.Colour.blue())
		await message.channel.send(embed=embed)
		return True
	return False

# Helper function for roleCommands that allows a command for a certain role
async def allowCommandForRole(message, command, role, nameOrId):
	if nameOrId == "name":
		roleName = role
		# Find the role with the given name
		for role in message.guild.roles:
			if role.name == roleName:
				roleFound = role
				break
	else:
		# Find the role with the given id
		roleId = role
		roleFound = message.guild.get_role(roleId)
	# Remove the command from the corresponding role list
	if roleFound.id in bannedCommandsByRole:
		if command in bannedCommandsByRole[roleFound.id]:
			bannedCommandsByRole[roleFound.id].remove(command)
			response = command + " has been allowed for " + roleFound.name + "!"
			embed = discord.Embed(title='Command Allowed', description=response, colour=discord.Colour.blue())
			await message.channel.send(embed=embed)
		else:
			response = command + " for " + roleFound.name + " is already allowed!"
			embed = discord.Embed(title='Command Already Allowed', description=response, colour=discord.Colour.blue())
			await message.channel.send(embed=embed)
	else:
		response = command + " for " + roleFound.name + " is already allowed!"
		embed = discord.Embed(title='Command Already Allowed', description=response, colour=discord.Colour.blue())
		await message.channel.send(embed=embed)

# Helper function for roleCommands that allows a command for a certain role
async def blockCommandFromRole(message, command, role, nameOrId):
	if nameOrId == "name":
		roleName = role
		# Find the role with the given name
		for role in message.guild.roles:
			if role.name == roleName:
				roleFound = role
				break
	else:
		# Find the role with the given id
		roleId = role
		roleFound = message.guild.get_role(roleId)
	# Add the command to the corresponding role list
	if roleFound.id in bannedCommandsByRole:
		if command in bannedCommandsByRole[roleFound.id]:
			response = command + " for " + roleFound.name + " is already blocked!"
			embed = discord.Embed(title='Command Already Blocked', description=response, colour=discord.Colour.blue())
			await message.channel.send(embed=embed)
		else:
			bannedCommandsByRole[roleFound.id].append(command)
			response = command + " has been blocked for " + roleFound.name + "!"
			embed = discord.Embed(title='Command Blocked', description=response, colour=discord.Colour.blue())
			await message.channel.send(embed=embed)
	else:
		bannedCommandsByRole[roleFound.id] = []
		bannedCommandsByRole[roleFound.id].append(roleFound.permissions)
		bannedCommandsByRole[roleFound.id].append(command)
		response = command + " has been blocked for " + roleFound.name + "!"
		embed = discord.Embed(title='Command Blocked', description=response, colour=discord.Colour.blue())
		await message.channel.send(embed=embed)

# Helper function for roleCommands that lists all the permissions of a given role
async def listPermissionsForRole(message, role, nameOrId):
	if nameOrId == "name":
		roleName = role
		# Find the role with the given name
		for role in message.guild.roles:
			if role.name == roleName:
				roleFound = role
				break
	else:
		# Find the role with the given id
		roleId = role
		roleFound = message.guild.get_role(roleId)
	# Build the list of commands allowed
	response = "The following commands are allowed for the role " + roleFound.name + ":\n"
	if roleFound.id in bannedCommandsByRole and len(bannedCommandsByRole[roleFound.id]) > 1:
		for command in commandList:
			if command not in bannedCommandsByRole[roleFound.id]:
				response += command + "\n"
		response += "\nThe following commands are blocked for the role " + roleFound.name + ":\n"
		for command in bannedCommandsByRole[roleFound.id]:
			if type(command) == type("str"):
				response += command + "\n"
	else:
		for command in commandList:
			response += command + "\n"
	embed = discord.Embed(title='Commands Role Can Use', description=response, colour=discord.Colour.blue())
	await message.channel.send(embed=embed)

# Checks if the role given is blocked from using the given command
# Returns True if the command is allowed, False if the command is blocked
def checkCommandAllowedForRole(role, command):
	if role.id in bannedCommandsByRole:
		if command in bannedCommandsByRole[role.id]:
			return False
	return True

# Checks if the roles in the server are in bannedCommandsByRole
# If not, update bannedCommandsByRole with the new roles and automatically set permissions
def autoSetPermissionsForRoles(message):
	for role in message.guild.roles:
		if role.id not in bannedCommandsByRole:
			# If the role is currently not in the dict, then add it
			bannedCommandsByRole[role.id] = []
			# Append the permissions object to detect if there are any changes to the permissions
			bannedCommandsByRole[role.id].append(role.permissions)
			# If the role does not have admin permissions, block all commands that require admin permissions
			# Since admin is granted every permission, if the user is an admin they will have access to all commands
			if role.permissions.administrator == False:
				for command in commandList:
					commandObj = commandList[command]
					if "administrator" in commandObj.permissions:
						bannedCommandsByRole[role.id].append(command)
				# If role does not have permissions to manage channels, block all such commands
				if role.permissions.manage_channels == False:
					for command in commandList:
						commandObj = commandList[command]
						if "manage_channels" in commandObj.permissions:
							bannedCommandsByRole[role.id].append(command)
				# If role does not have permissions to manage permissions, block all such commands
				if role.permissions.manage_permissions == False:
					for command in commandList:
						commandObj = commandList[command]
						if "manage_permissions" in commandObj.permissions or "manage_roles" in commandObj.permissions:
							bannedCommandsByRole[role.id].append(command)
				# Add more permissions check here
		else:
			if role.permissions != bannedCommandsByRole[role.id][0]:
				# Since permissions have changed, remove the entry for this role and rebuild it
				del bannedCommandsByRole[role.id]
				autoSetPermissionsForRoles(message)


#Todo: File upload command:


# Command to rename a command
async def rename(client, message):
	contents = message.content.split(" ")
	if (len(contents) != 3):
		response = "Incorrect usage of command !rename!\nUsage: !rename <OLDNAME> <NEWNAME>"
	elif (contents[1] not in commandList):
		response = "Error, no command with the name {}".format(contents[1])
	else:
		renameCommand(contents[1], contents[2])
		response = "Successfully renamed {} to {}!".format(contents[1], contents[2])
	await message.channel.send(response)

# Helper function to actually rename the command and change it in the commandList
def renameCommand(oldName, newName):
	command = commandList[oldName]
	command.name = newName
	commandList[newName] = commandList.pop(oldName)
	writeToRename(oldName, newName)

# Function used to write to the renameCommands.txt
def writeToRename(oldName, newName):
	# Names will be stored like <NAME IN CODE> <ALIAS>
	# Find the line number to edit
	data = []
	with open("commandRenames.txt") as f:
		data = f.readlines()
	found = False
	for i in range(len(data)):
		# Goes line by line
		if oldName in data[i]:
			found = True
			contents = data[i].split(" ")
			newLine = contents[0] + " " + newName + "\n"
			if contents[0] == newName:
				newLine = ""
			data[i] = newLine
	if found:
		file = open("commandRenames.txt", "w")
		for line in data:
			file.write(line)
	else:
		file = open("commandRenames.txt", "a")
		file.write(oldName + " " + newName + "\n")

# Makes a list of modules without ".py" at the end and stores them in moduleList
def makeModuleList():
	for filename in os.listdir("modules"):
		# grab all .py files except for the init file
		if (filename.endswith(".py") and not filename.startswith("__init__")):
			fileAdded = filename[:-3]
			moduleList.append(fileAdded)

def rolesThatCanUseEachCommand(message, command):
	response = ""
	for roleFound in message.guild.roles:
		if roleFound.id in bannedCommandsByRole and len(bannedCommandsByRole[roleFound.id]) > 1:
			if command not in bannedCommandsByRole[roleFound.id]:
				if (roleFound.name == "@everyone"):
					response = roleFound.name
					return response
				response += roleFound.name + " "
	return response

# Display a list of either all command functionality
async def help(client, message):
	messageArray = message.content.split(' ')
	# For when users only want help on specific commands or specific modules
	makeModuleList()
	if (len(messageArray) > 1):
		embed = discord.Embed(title = "Help", colour = discord.Colour.green())
		embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
		for i in range(1, len(messageArray)):
			if messageArray[i] in commandList:
				command = messageArray[i]
				rolesAllowed = "\n**Roles:**" + rolesThatCanUseEachCommand(message, command)
				if commandList[command].description == None:
					commandList[command].description = rolesAllowed
				else:
					commandList[command].description = commandList[command].description + rolesAllowed
				embed.add_field(name='`'+command+'`', value=commandList[command].description, inline=False)
				#embed.add_field(name="Roles than can use this command:")
			elif messageArray[i] in moduleList:
				module = importlib.import_module("modules." + messageArray[i])
				for c in module.commandList:
					embed.add_field(name='`'+c.name+'`', value=c.description, inline=False)
			else :
				await message.channel.send('*'+ '__' + messageArray[i] + '__' + '*' + " not found in commands list or module list, try again.")
				return
	else:
		# This will display a response that will hold descriptions of all of the commands
		count = 0
		embed = discord.Embed(title = "Help", description = "**How to use all of the commands.**", colour = discord.Colour.green())
		embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
		for command in commandList:
			rolesAllowed = "\n**Roles:**" + rolesThatCanUseEachCommand(message, command)
			if commandList[command].description == None:
				commandList[command].description = rolesAllowed
			else:
				commandList[command].description = commandList[command].description + rolesAllowed
			embed.add_field(name='`'+command+'`', value=commandList[command].description, inline=False)
			count += 1
			if count > 24:
				await message.channel.send(embed=embed)
				embed = discord.Embed(title = "Help cont.", colour = discord.Colour.green())
				count = 0
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

	# Check if user is muted
	# True is returned if the author is currently muted
	if serverAdministration.checkAuthorIsMuted(message) == True:
		user = message.author.mention
		response = user + " You are currently muted!\n"
		response += "You may not send messages while muted. Please wait until your penalty is over."
		embed = discord.Embed(title='You Are Muted', description=response, colour=discord.Colour.red())
		embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
		await message.channel.send(embed=embed)
		await message.delete()
		return

	# Remove messages with banned words
	# True is returned if the message should be deleted for having a banned word
	if serverAdministration.checkMessageForBannedWords(message) == True:
		# Ping the user and warn them about the banned word
		user = message.author.mention
		response = user + " You have used a banned word. Your message has been deleted.\n"
		response += "If you are unsure about the banned word you used, please contact server administrator(s).\n\n"
		response += "You are muted for the next 10 seconds."
		embed = discord.Embed(title='Banned Word Used', description=response, colour=discord.Colour.red())
		embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
		await message.channel.send(embed=embed)
		await message.delete()
		await serverAdministration.addUserToMutedList(message)
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
		# Check the server for any new roles and automatically set permissions
		autoSetPermissionsForRoles(message)

		# Prevent commands that are blocked for a specific role from executing
		# If the user has multiple roles, all roles will be checked
		commandAllowed = True
		for role in message.author.roles:
			command = message.content.split(" ")[0]
			# True means that the command is allowed for that particular role
			# If user has one role that allows usage, stop searching as user is allowed
			if checkCommandAllowedForRole(role, command) == True:
				commandAllowed = True
				break
			else:
				commandAllowed = False
		# If command is not allowed, prevent user from using command unless it is the server owner
		if commandAllowed == False and message.guild.owner_id != message.author.id:
			user = message.author.mention
			response = user + " You do not have the permissions to use this command!"
			embed = discord.Embed(title='No Permissions To Use Command', description=response, colour=discord.Colour.red())
			embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
			await message.channel.send(embed=embed)
			return

		if (len(message.content) == 1):
			await getCommands(client, message)
			return

		# Get the first word in the message, which would be the command
		name = message.content.split(' ')[0]
		# If it exists, call the command, otherwise warn user it was not recognized
		if name in commandList:
			await commandList[name].callCommand(client, message)
			return
		await message.channel.send("Sorry that command was not recognized!")

#Run the bot
client.run(TOKEN)
