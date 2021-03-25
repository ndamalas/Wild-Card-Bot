from command import Command
import string
import discord
import asyncio
import youtube_dl
import os
from googlesearch import search
from discord.voice_client import VoiceClient
from discord import FFmpegPCMAudio
import re
import threading
#double linked list for music
from node import Node
# Every module has to have a command list
commandList = []

# List of channels to remove links from, stores only text channel ids
removeLinksChannels = []

# Muted members list, stores member ids
mutedMembers = []

# Example function:
# Just make sure that the function name in a command is the same
# Make sure every function is async and has both client, message as parameters, and that await is used when sending your response
commandList.append(Command("!example", "exampleFunction", "This is an example function."))
async def exampleFunction(client, message):
    response = "This is an example of a function setup."
    await message.channel.send(response)

# List of banned words
bannedWords = []
# Will read in words into the bannedWords list
def readBannedWords():
    file = open("bannedWords.txt", "r")
    line = file.readline()
    while (line):
        bannedWords.append(line[:len(line)-1])
        line = file.readline()
    file.close()
readBannedWords()

# List of banned users
bannedUsers = []
# Will read in words into the bannedUsers list
def readBannedUsers():
    file = open("bannedUsers.txt", "r")
    line = file.readline()
    while (line):
        bannedUsers.append(line[:len(line)-1])
        line = file.readline()
    file.close()
readBannedUsers()

# Display a list of either all Users or only Users with a certain role
commandList.append(Command("!users", "displayAllUsers", "Will display all of the users if just given !users.\nUse !users <ROLE> to list users of a specific role."))
async def displayAllUsers(client, message):
    # User List to hold all members in the server
    userList = message.guild.members
    response = ""
    if len(message.content.split(" ")) > 1:
        response = getUsersFromRole(userList, message.content.split(" ")[1])
    else:
        response = getAllUsers(userList)
    await message.channel.send(response)

# Get a string response with all users and their roles
def getAllUsers(userList):
    response = ""
    for user in userList:
        if user.display_name == "Wild Card Bot":
            continue
        response += "**" + user.display_name + "**\n__Roles:__ "
        for role in user.roles:
            response += role.name + " "
        response += "\n"
    return response
# Get a string response of a list of all users with a given role
def getUsersFromRole(userList, role):
    response = ""
    for user in userList:
        if user.display_name == "Wild Card Bot":
            continue
        for userRole in user.roles:
            if userRole.name == role:
                response += "**" + user.display_name + "**"
                response += "\n"
                break
    return response


# Command that creates a new text channel on command
# Format: !createtc text-channel-name category-name (id) (The user can include spaces in their category name,
# user can also specify the id of a particular category if there are multiple categories with same name)
commandList.append(Command("!createtc", "createTextChannel", "Creates a new text channel.\nUsage: !createtc <TEXT-CHANNEL-NAME> <CATEGORY-NAME> (id) (The user can include spaces in their category name, user can also specify the id of a particular category if there are multiple categories with same name)", permissions=["manage_channels"]))
# Creates a text channel with the name specified by the user
async def createTextChannel(client, message):
    guild = message.guild # Get the server from the message sent
    channelName = 0 # Holds the channel name. 0 indicates no channel created
    categoryName = 0 # Holds the category name if specified. If not specified, 0 indicates no category

    # Create the text channel, considering if the user specified a category or name
    if len(message.content.split(" ")) > 2:
        # Check if ID was specified, special procedure if there is ID specified
        if len(message.content.split(" ")) > 3 and message.content.split(" ")[3] == "id":
            channelName = message.content.split(" ")[1]
            categoryId = int(message.content.split(" ")[2])
            returnedChannel = await createTextChannelWithCategoryID(client, message, guild, channelName, categoryId)
            # Obtain the category name
            for category in guild.categories:
                if category.id == categoryId:
                    categoryName = category.name
            # If no channel was created from createTextChannelWithCategoryID, set channelName to 0
            if returnedChannel == None:
                channelName = 0
        else:
            # If no ID specified, use the name
            channelName = message.content.split(" ")[1] # The channel name cannot have any spaces
            categoryName = message.content[len("!createtc ") + len(channelName) + 1:] # Category names can have spaces
            # Scans to see if the category already exists, adds channel to category if it does
            # Count how many times the category appears
            categoryCount = 0
            for category in guild.categories:
                if category.name == categoryName:
                    categoryCount += 1
            if categoryCount > 1:
                # If multiple matches, notify user and print all matches of categories
                response = "Multiple matches found for category with name **" + categoryName + "**. "
                response += "Please specify using category ID.\n"
                responseCount = 1
                for category in guild.categories:
                    if category.name == categoryName:
                        response += str(responseCount) + ". " + str(category.id) + "\n"
                        responseCount += 1
                response += "Command format: **!createtc text-channel-name category-id id**"
                embed = discord.Embed(title='Multiple Categories Found', description=response, colour=discord.Colour.blue())
                await message.channel.send(embed=embed)
                channelName = 0 # Notify that channel was not created
            elif categoryCount == 1:
                for category in guild.categories:
                    if category.name == categoryName:
                        # Create the text channel in the existing category
                        await guild.create_text_channel(channelName, category=category)
                        break
            else:
                # If the category does not exist, create the category and add channel to it
                await guild.create_category_channel(categoryName)
                # Find the category just created
                for category in guild.categories:
                    if category.name == categoryName:
                        # Create the text channel in the new category
                        await guild.create_text_channel(channelName, category=category)
                        break
    elif len(message.content.split(" ")) > 1:
        # Create text channel with just a given name
        channelName = message.content.split(" ")[1]
        await guild.create_text_channel(channelName)
    else:
        # If no name is specified, notify user
        response = "Please specify a text channel name! Category name is optional.\n"
        response += "Command format: **!createtc text-channel-name category-name**"
        embed = discord.Embed(title='!createtc Usage', description=response, colour=discord.Colour.blue())
        await message.channel.send(embed=embed)
    # Generate response with text channel added
    if channelName != 0:
        response = "Successfully created the new text channel **" + channelName
        if categoryName != 0:
            response += "** in category **" + categoryName
        response += "**!"
        embed = discord.Embed(title='Text Channel Created', description=response, colour=discord.Colour.blue())
        await message.channel.send(embed=embed)

# Helper function for createTextChannel that creates a text channel in the category specified by the ID
async def createTextChannelWithCategoryID(client, message, guild, channelName, categoryId):
    categoryFound = False
    for category in guild.categories:
        if category.id == categoryId:
            # Mark the category was found and create the text channel in the category
            categoryFound = True
            return await guild.create_text_channel(channelName, category=category)
    # Notify user if the channel was not found
    if categoryFound == False:
        response = "Category with id **" + str(categoryId) + "** was not found!"
        embed = discord.Embed(title='!createtc Usage', description=response, colour=discord.Colour.blue())
        await message.channel.send(embed=embed)
    return None

# Command that deletes a new text channel on command
# Format: !deletetc text-channel-name (id) (id is optional, text-channel-name should be text-channel-id)
commandList.append(Command("!deletetc", "deleteTextChannel", "Deletes a new text channel on command.\nUsage: !deletetc <TEXT-CHANNEL-NAME> (id) (id is optional, text-channel-name should be text-channel-id)", permissions=["manage_channels"]))
# Deletes a text channel with the name or id specified by the user
async def deleteTextChannel(client, message):
    guild = message.guild
    # Check if multiple channels have the same name
    if len(message.content.split(" ")) > 2:
        # Delete a text channel via channel id
        if message.content.split(" ")[2] == "id":
            channelId = int(message.content.split(" ")[1]) # Channel ID is an int, so must cast
            channelFound = False
            for tc in guild.text_channels:
                if tc.id == channelId:
                    channelFound = True
                    await tc.delete()
                    response = "Successfully deleted the **" + tc.name + "** text channel!"
                    embed = discord.Embed(title='Text Channel Deleted', description=response, colour=discord.Colour.blue())
                    await message.channel.send(embed=embed)
                    break
            # Notify user if the channel was not found
            if channelFound == False:
                response = "Text channel with id **" + str(channelId) + "** was not found!"
                embed = discord.Embed(title='Text Channel Not Found', description=response, colour=discord.Colour.blue())
                await message.channel.send(embed=embed)
        else:
            # Delete a text channel by name
            channelName = message.content.split(" ")[1]
            await deleteTextChannelByName(client, message, guild, channelName)
    elif len(message.content.split(" ")) > 1:
        # Delete a text channel by name
        channelName = message.content.split(" ")[1]
        await deleteTextChannelByName(client, message, guild, channelName)
    else:
        # If no arguments provided, notify user
        response = "Please specify a text channel name!\nCommand format: **!deletetc text-channel-name**"
        embed = discord.Embed(title='!deletetc Usage', description=response, colour=discord.Colour.blue())
        await message.channel.send(embed=embed)

# Helper function for deleteTextChannel that deletes a text channel via specifed name
async def deleteTextChannelByName(client, message, guild, channelName):
     # Check how many channels match that name
        nameMatchCount = 0
        for tc in guild.text_channels:
            if tc.name == channelName:
                nameMatchCount += 1
        # Determine action based on how many name matches
        if nameMatchCount > 1:
            # If multiple matches, notify user and print all matches
            response = "Multiple matches found for **" + channelName + "**. Please delete using channel ID.\n"
            responseCount = 1
            for tc in guild.text_channels:
                if tc.name == channelName:
                    response += str(responseCount) + ". " + str(tc.id) + "\n"
                    responseCount += 1
            response += "Command format: **!deletetc text-channel-id id**"
            embed = discord.Embed(title='Multiple Channels Found', description=response, colour=discord.Colour.blue())
            await message.channel.send(embed=embed)
        elif nameMatchCount == 1:
            # Delete the text channel with the given name
            for tc in guild.text_channels:
                if tc.name == channelName:
                    await tc.delete()
                    response = "Successfully deleted the **" + channelName + "** text channel!"
                    embed = discord.Embed(title='Text Channel Deleted', description=response, colour=discord.Colour.blue())
                    await message.channel.send(embed=embed)
                    break
        else:
            # No text channel with the given name was found
            response = "Text channel with name **" + channelName + "** was not found!"
            embed = discord.Embed(title='Text Channel Not Found', description=response, colour=discord.Colour.blue())
            await message.channel.send(embed=embed)

# Syntax: !createvc channel_name *category_name
commandList.append(Command("!createvc", "createVoiceChannel", "Creates a new voice channel.\nUsage: !createvc <CHANNEL_NAME> <*CATEGORY_NAME>", permissions=["manage_channels"]))
async def createVoiceChannel(client, message):
    guild = message.guild
    channelName = 0
    categoryName = 0

    if len(message.content.split(" ")) > 2:
            channelName = message.content.split(" ")[1]
            categoryName = message.content[len("!createvc ") + len(channelName) + 1:]
            exists = 0
            for category in guild.categories:
                if category.name == categoryName:
                    await guild.create_voice_channel(channelName, overwrites=None, category=category, reason=None)
                    exists = 1
                    break
            if exists == 0:
                await guild.create_category_channel(categoryName)
                for category in guild.categories:
                    if category.name == categoryName:
                        await guild.create_voice_channel(channelName, overwrites=None, category=category, reason=None)
                        break
    elif len(message.content.split(" ")) > 1:
        channelName = message.content.split(" ")[1]
        await guild.create_voice_channel(channelName, overwrites=None, category=None, reason=None)
    else:
        await message.channel.send("Error")
    if channelName != 0:
        await message.channel.send("Success")

# Command that can show removeLinks
# Format: !removelinks (add/remove/view) channel-name (id) (adds or removes a channel for monitoring links)
commandList.append(Command("!removelinks", "updateRemoveLinksList", "Interact with the remove links list.\nUsage: !removelinks <ADD/REMOVE/VIEW> <CHANNEL-NAME> (id) (adds or removes a channel for monitoring links)", permissions=["manage_channels"]))
# Deletes a text channel with the name or id specified by the user
async def updateRemoveLinksList(client, message):
    guild = message.guild
    action = 0 # Check what action (add/remove/view) user wants, 0 indicates no action specified
    # Check if necessary arguments are passed in
    if len(message.content.split(" ")) >= 3:
        # Check if add or remove was specified
        if message.content.split(" ")[1] == "add":
            action = "add"
        elif message.content.split(" ")[1] == "remove":
            action = "remove"
        # Check if id was passed in
        if len(message.content.split(" ")) >= 4 and message.content.split(" ")[3] == "id":
            # Add or remove to list by id
            channelId = int(message.content.split(" ")[2]) # Channel ID is an int
            if action == "add":
                await addToRemoveLinksList(client, message, guild, "id", channelId)
            if action == "remove":
                await removeFromRemoveLinksList(client, message, guild, "id", channelId)
        else:
            # Add or remove to list by name
            channelName = message.content.split(" ")[2]
            if action == "add":
                await addToRemoveLinksList(client, message, guild, "name", channelName)
            if action == "remove":
                await removeFromRemoveLinksList(client, message, guild, "name", channelName)
    elif len(message.content.split(" ")) >= 2:
        # View the contents of the list
        if message.content.split(" ")[1] == "view":
            action = "view"
            await viewRemoveLinksList(client, message, guild)
    else:
        response = "Please provide a text channel name and whether to add or remove link monitoring!\n"
        response += "Command format: **!removelinks add/remove channel-name**\n\n"
        response += "You may also view the list of text channels current being monitored.\n"
        response += "Command format: **!removelinks view**"
        embed = discord.Embed(title='!removelinks Usage', description=response, colour=discord.Colour.blue())
        await message.channel.send(embed=embed)
        action = "error" # Prevent the prompt from being printed twice
    # If an action was not specified or incorrectly specified, notify the user
    if action == 0:
        response = "Please specify whether you want to add or remove a channel from being monitored for links!\n"
        response += "Command format: **!removelinks add/remove channel-name**\n\n"
        response += "If you wanted to view the list of text channels current being monitored, use the command below.\n"
        response += "Command format: **!removelinks view**"
        embed = discord.Embed(title='!removelinks Usage', description=response, colour=discord.Colour.blue())
        await message.channel.send(embed=embed)

# Helper function to updateRemoveLinksList that adds another text channel id to the list
async def addToRemoveLinksList(client, message, guild, action, channelInfo):
    # If id is passed in, find the channel by id and add it into the list
    if action == "id":
        channelId = channelInfo
        channelFound = False
        for tc in guild.text_channels:
            if tc.id == channelId:
                channelFound = True
                if tc.id not in removeLinksChannels:
                    removeLinksChannels.append(tc.id)
                    response = "The text channel **" + tc.name + "** has been added to the list to be monitored for links!"
                    embed = discord.Embed(title='Added Channel For Link Monitoring', description=response, colour=discord.Colour.blue())
                else:
                    response = "The text channel **" + tc.name + "** has already been added to the list!"
                    embed = discord.Embed(title='Channel Already Added', description=response, colour=discord.Colour.blue())
                await message.channel.send(embed=embed)
                break
         # if the channel was not found, notify user
        if channelFound == False:
            response = "Text channel with id **" + str(channelId) + "** was not found!"
            embed = discord.Embed(title='Channel Not Found', description=response, colour=discord.Colour.blue())
            await message.channel.send(embed=embed)
    else:
        # if name is passed in, check first to see how many channels have such a name that are not in the list
        channelName = channelInfo
        nameMatchCount = 0
        for tc in guild.text_channels:
            if tc.name == channelName and tc.id not in removeLinksChannels:
                nameMatchCount += 1
        # Determine action based on how many matches
        if nameMatchCount > 1:
            # If multiple matches, notify user and print all matches
            response = "Multiple matches found for **" + channelName + "**. Please add to the list using channel ID.\n"
            responseCount = 1
            for tc in guild.text_channels:
                if tc.name == channelName and tc.id not in removeLinksChannels:
                    response += str(responseCount) + ". " + str(tc.id) + "\n"
                    responseCount += 1
            response += "Command format: **!removelinks add channel-id id**"
            embed = discord.Embed(title='Multiple Channels Found', description=response, colour=discord.Colour.blue())
            await message.channel.send(embed=embed)
        elif nameMatchCount == 1:
            # Add the text channel with the given name to removeLinksList
            for tc in guild.text_channels:
                if tc.name == channelName and tc.id not in removeLinksChannels:
                    removeLinksChannels.append(tc.id)
                    response = "The text channel **" + tc.name + "** has been added to the list to be monitored for links!"
                    embed = discord.Embed(title='Added Channel For Link Monitoring', description=response, colour=discord.Colour.blue())
                    await message.channel.send(embed=embed)
                    break
        else:
            # No text channel with the given name was found outside of the list
            # Check if name actually exists in the list
            channelExists = False
            for tcId in removeLinksChannels:
                tc = guild.get_channel(tcId)
                if tc.name == channelName:
                    channelExists = True
            # Print corresponding message depending if channel exists
            if channelExists == True:
                response = "The text channel **" + channelName + "** has already been added to the list!"
                embed = discord.Embed(title='Channel Already Added', description=response, colour=discord.Colour.blue())
            else:
                response = "Text channel with name **" + channelName + "** was not found!"
                embed = discord.Embed(title='Channel Not Found', description=response, colour=discord.Colour.blue())
            await message.channel.send(embed=embed)

# Helper function to updateRemoveLinksList that removes a text channel id to the list
async def removeFromRemoveLinksList(client, message, guild, action, channelInfo):
    # If id is passed in, find the channel by id and remove it from the list
    if action == "id":
        channelId = channelInfo
        if channelId in removeLinksChannels:
            removeLinksChannels.remove(channelId)
            response = "The text channel **" + guild.get_channel(channelId).name
            response += "** has been removed from the list for monitoring links."
            embed = discord.Embed(title='Channel Removed from List Monitoring', description=response, colour=discord.Colour.blue())
            await message.channel.send(embed=embed)
        else:
            # Check if the channel actually exists on the server
            channelExists = False
            for tc in guild.text_channels:
                if tc.id == channelId:
                    channelExists = True
                    break
            if channelExists == True:
                response = "The text channel **" + guild.get_channel(channelId).name + "** was not found in the list!"
                embed = discord.Embed(title='Channel Not In List', description=response, colour=discord.Colour.blue())
            else:
                response = "Text channel with id **" + str(channelId) + "** was not found!"
                embed = discord.Embed(title='Channel Not Found', description=response, colour=discord.Colour.blue())
            await message.channel.send(embed=embed)
    else:
        # if name is passed in, check first to see how many channels have such a name in the list
        channelName = channelInfo
        nameMatchCount = 0
        for tcId in removeLinksChannels:
            tc = guild.get_channel(tcId)
            if tc.name == channelName:
                nameMatchCount += 1
        # Determine action based on how many matches
        if nameMatchCount > 1:
            # If multiple matches, notify user and print all matches
            response = "Multiple matches found for **" + channelName + "**. Please remove from the list using channel ID.\n"
            responseCount = 1
            for tcId in removeLinksChannels:
                tc = guild.get_channel(tcId)
                if tc.name == channelName:
                    response += str(responseCount) + ". " + str(tc.id) + "\n"
                    responseCount += 1
            response += "Command format: **!removelinks remove channel-id id**"
            embed = discord.Embed(title='Multiple Channels Found', description=response, colour=discord.Colour.blue())
            await message.channel.send(embed=embed)
        elif nameMatchCount == 1:
            # Remove the text channel with the given name from removeLinksList
            for tcId in removeLinksChannels:
                tc = guild.get_channel(tcId)
                if tc.name == channelName:
                    removeLinksChannels.remove(tc.id)
                    response = "The text channel **" + tc.name + "** has been removed from the list for monitoring links."
                    embed = discord.Embed(title='Channel Removed From Link Monitoring', description=response, colour=discord.Colour.blue())
                    await message.channel.send(embed=embed)
                    break
        else:
            # No text channel with the given name was found
            # First check if the name of the channel exists in the server
            channelExists = False
            for tc in guild.text_channels:
                if tc.name == channelName:
                    channelExists = True
                    break
            if channelExists == True:
                response = "The text channel **" + channelName + "** was not found in the list!"
                embed = discord.Embed(title='Channel Not In List', description=response, colour=discord.Colour.blue())
            else:
                response = "Text channel with name **" + channelName + "** was not found!"
                embed = discord.Embed(title='Channel Not Found', description=response, colour=discord.Colour.blue())
            await message.channel.send(embed=embed)

# Helper function to updateRemoveLinksList that prints the list to the user
async def viewRemoveLinksList(client, message, guild):
    if len(removeLinksChannels) == 0:
        response = "There are currently no text channels being monitored for links."
        embed = discord.Embed(title='No Channels in List', description=response, colour=discord.Colour.blue())
        await message.channel.send(embed=embed)
    response = "Here are all the text channels currently being monitored for links:\n" # Message to the user
    responseCount = 1 # Used for numbers
    for tcId in removeLinksChannels:
        tc = guild.get_channel(tcId)
        response += str(responseCount) + ". " + tc.name + "\n"
        response += "ID: " + str(tc.id) + "\n"
        responseCount += 1
    if len(removeLinksChannels) != 0:
        embed = discord.Embed(title='Channel List For Link Monitoring', description=response, colour=discord.Colour.blue())
        await message.channel.send(embed=embed)

# This function is used by main.py to check if the associated message has a link
# If the message has a link and the channel is monitored, we return True to indicate deletion
# If the message does not satify conditions False should be returned
def checkMessageForLinks(message):
    if message.channel.id in removeLinksChannels:
        if "https://" in message.content or "http://" in message.content:
            return True
    return False

# Displays a list of all roles in the server
commandList.append(Command("!roles", "listRoles", "Lists all roles in server\nUsage: !roles"))
async def listRoles(client, message):
    guild = message.guild
    response = ">>> Listing All Server Roles:\n"
    response += ", ".join([str(r.name) for r in guild.roles])
    await message.channel.send(response)
    return

# Create a role
commandList.append(Command("!createRole", "createRole", "Creates a new Role in the server\nUsage: !createRole \"role name\""))
async def createRole(client, message):
    guild = message.guild
    #member = message.author
    if len(message.content.split(" ")) != 2:
        await message.channel.send(">>> Please use format:\n !createRole \"role name\"")
        return
    await guild.create_role(name=message.content.split(" ")[1])
    response = ">>> NEW ROLE CREATED!"
    await message.channel.send(response)
    return

# Delete a role
commandList.append(Command("!delRole", "delRole", "Deletes a Role from the server\nUsage: !delRole \"role name\""))
async def delRole(client, message):
    guild = message.guild
    #member = message.author
    if len(message.content.split(" ")) != 2:
        await message.channel.send(">>> Please use format:\n !dRole \"role name\"")
        return
    response = ">>> Role not found"
    for current_role in guild.roles:
        if str(current_role.name) == message.content.split(" ")[1]:
            role_to_delete=discord.utils.get(message.guild.roles, name=str(current_role.name))
            await role_to_delete.delete()
            response = "ROLE DELETED!"
    await message.channel.send(response)
    return

#Gives a role to a user
commandList.append(Command("!giveRole", "giveRole", "Gives user a role\nUsage: !giveRole \"User#0000\" \"Role Name\""))
async def giveRole(client, message):
    guild = message.guild
    await message.channel.send("IN GIVE ROLE FUNCTION")
    if len(message.content.split(" ")) != 3:
        await message.channel.send(">>> Please use format: \n !giveRole \"User#0000\" \"Role Name\"")
    user_found = False
    member=0
    userList = message.guild.members
    #await message.channel.send(userList[0])
    for user in userList:
        if str(user) == message.content.split(" ")[1]:
            user_found = True
            member = user
    if user_found == False:
        await message.channel.send("USER NOT FOUND")
        return
    #role_found = False
    #role=0
    #for curr_role in guild.roles():
    #    if str(curr_role.name) == message.content.split(" ")[2]:
    #        await message.channel.send("Role found dw")
    #        role_found = True
    #        role = curr_role
    #await message.channel.send("OUT OF LOOP")
    #if role_found == False:
    #    await message.channel.send("ROLE NOT FOUND")
    #    return
    role=discord.utils.get(message.guild.roles, name="role name")
    await member.add_role(role)
    await message.channel.send("ROLE GIVEN")
    return

#Removes a role from a user
commandList.append(Command("!removeRole", "removeRole", "Removes a role from user\nUsage: !removeRole <USER-NAME> <ROLE-NAME>"))
async def removeRole(client, message):
    guild = message.guild
    if len(message.content.split(" ")) != 3:
        await message.channel.send(">>> Please use format: \n !removeRole \"User#0000\" \"Role Name\"")
    user_found = False
    member=0
    userList = message.guild.members
    #await message.channel.send(userList[0])
    for user in userList:
        if str(user) == message.content.split(" ")[1]:
            user_found = True
            member = user
    if user_found == False:
        await message.channel.send("User not found")
        return
    for role in guild.roles:
        if role.name == message.content.split(" ")[2]:
            await member.remove_roles(role)
            await message.channel.send("Role removed")
            return
    await message.channel.send("User does not have specified role")

commandList.append(Command("!banMember", "banMember", "Bans member from server\nUsage: !banMember \"user\" \"reason\""))
async def banMember(client, message):
    #await message.channel.send("IN BAN MEMBER")
    member = message.author
    guild = message.guild
    response=""
    if len(message.content.split(" ")) != 3:
        await message.channel.send(">>> Please use format:\n !banMember \"user\" \"reason\"")
        return
    #await message.channel.send("PASSED FORMAT CHECK")
    user_found = False
    member_to_ban = 0
    userList = message.guild.members
    for user in userList:
        if str(user) == message.content.split(" ")[1]:
            user_found = True
            member_to_ban = user
            bannedUsers.append(str(user.id))
            file = open("bannedUsers.txt", "a")
            file.write(str(user.id) + "\n")
            file.close()
    if user_found == False:
        await message.channel.send("USER NOT FOUND")
        return
    #for i in range(3, len(message.content.split(" "))):
        #response+=message.content.split(" ")[i]
    #await message.channel.send(response)
    await guild.ban(member_to_ban)
    #guild.ban(member, reason=message)
    await message.channel.send("User has been banned")

commandList.append(Command("!kickMember", "kickMember", "Kicks member from server\nUsage: !kickMember \"user\" \"reason\""))
async def kickMember(client, message):
    await message.channel.send("In Kick MEMBER")
    member = message.author
    guild = message.guild
    #response=""
    if len(message.content.split(" ")) != 3:
        await message.channel.send(">>> Please use format:\n !kickMember \"user\" \"reason\"")
        return
    await message.channel.send("PASSED FORMAT CHECK")
    user_found = False
    member_to_kick = 0
    userList = message.guild.members
    for user in userList:
        if str(user) == message.content.split(" ")[1]:
            user_found = True
            member_to_kick = user
    if user_found == False:
        await message.channel.send("USER NOT FOUND")
        return
    #for i in range(3, len(message.content.split(" "))):
        #response+=message.content.split(" ")[i]
    #await message.channel.send(response)
    await guild.kick(member_to_kick)
    # member.kick(member_to_kick)
    # client.Kick(member_to_kick)
    # guild.ban(member_to_kick)
    #guild.ban(member, reason=message)
    await message.channel.send("User has been kicked")

commandList.append(Command("!bannedMembers", "displayBannedMembers", "Shows list of banned users."))
async def displayBannedMembers(client, message):
    response = ""
    for users in bannedUsers:
        response += users + "\n"
    if response == "":
        response = "The banned users list is currently empty."
    await message.channel.send(response)

# Display a list of all banned words
commandList.append(Command("!bannedWords", "displayBannedWords", "Can display, add, or remove words from banned words list.\nUsage: !bannedWords (optional) <ADD/REMOVE/CLEAR> <WORD>"))
async def displayBannedWords(client, message):
    if (len(message.content.split(" ")) <= 1):
        response = ""
        for word in bannedWords:
            response += word + "\n"
        if response == "":
            response = "The banned words list is currently empty."
        await message.channel.send(response)
        return
    elif (message.content.split(" ")[1] == "add"):
        await addBannedWord(message)
        return
    elif (message.content.split(" ")[1] == "remove"):
        await removeBannedWord(message)
        return
    elif (message.content.split(" ")[1] == "clear"):
        await clearBannedWords(message)
        return
    await message.channel.send("Error: incorrect usage!")


# Helper to add a word to the banned word list
async def addBannedWord(message):
    if (len(message.content.split(" ")) <= 2):
        await message.channel.send("Please enter one or more words to add to the banned words list.\nUsage: !bannedWords add <WORD>")
        return
    words = message.content.split(" ")
    file = open("bannedWords.txt", "a")
    for i in range(2, len(message.content.split(" "))):
        word = words[i]
        if word in bannedWords:
            continue
        bannedWords.append(word)
        # Write them to the file
        file.write(word + "\n")
    file.close()

    await message.channel.send("Successfully added to the banned words list!")

# Helper to remove a word to the banned word list
async def removeBannedWord(message):
    if (len(message.content.split(" ")) <= 2):
        await message.channel.send("Please enter one or more words to remove from the banned words list.\nUsage: !bannedWords remove <WORD>")
        return
    words = message.content.split(" ")
    for i in range(2, len(message.content.split(" "))):
        word = words[i]
        if (word in bannedWords):
            bannedWords.remove(word)
        else:
            await message.channel.send(word + " not found in banned words list, try again.")
            return
    file = open("bannedWords.txt", "w")
    for word in bannedWords:
        file.write(word + "\n")
    file.close()
    await message.channel.send("Successfully removed from the banned words list!")

# Clears out banned words list
async def clearBannedWords(message):
    file = open("bannedWords.txt", "w")
    bannedWords.clear()
    file.close()
    await message.channel.send("Successfully cleared the banned words list!")


# This function is used by main.py to check if the associated message has a link
# If the message has a link and the channel is monitored, we return True to indicate deletion
# If the message does not satify conditions False should be returned
def checkMessageForBannedWords(message):
    messageWords = message.content.split(" ")
    allowCommands = len(messageWords) >= 1 and messageWords[0].startswith("!")
    if allowCommands:
        return False
    reformattedMessageWords = []
    # Strip the message of all punctuation and make all lowercase
    for word in messageWords:
        reformattedWord = word.translate(str.maketrans("", "", string.punctuation))
        reformattedWord = reformattedWord.lower()
        reformattedMessageWords.append(reformattedWord)

    # Check if the banned word is one of the words
    for word in bannedWords:
        bannedWord = word.lower()
        if bannedWord in reformattedMessageWords:
            return True
    return False

# Temporarily adds the user to the muted list
async def addUserToMutedList(message):
    mutedMembers.append(message.author.id)
    await asyncio.sleep(10)
    mutedMembers.remove(message.author.id)

# Checks if the author of the message is muted
def checkAuthorIsMuted(message):
    return message.author.id in mutedMembers

commandList.append(Command("!downloadModules", "downloadAdditionalModules", "Gives the user links to where new modules for the bot can be downloaded or the user can specify modules they would like to search for and links are provided.\nUsage: !downloadModules <SPECIFIC-MODULE>"))
# Function for additional module download command
async def downloadAdditionalModules(ctx, message):
    #Check the number of arguments typed including the command
    args = len(message.content.split(" "))
    # If the user just types the command give them the link to the GitHub modules that we have
    # Otherwise given them the google search as well
    embed = discord.Embed(
        title='WildCard Bot Discord Modules',
        description='[GitHub](https://github.com/ndamalas/Wild-Card-Bot/tree/main/modules)',
        color = 0xffffff
    )
    if(args == 1):
        #Embedded is the nice block that also gives the embedded link
        await message.channel.send("You can find and download more discord modules for WildCard Bot made by our team here:\n")
        await message.channel.send(embed=embed)
    else:
        #Need to install "pip install beautifulsoup4"
        #and also "pip install google"
        query = "download " + message.content[17:] + " modules for WildCard Discord Bot"
        await message.channel.send(embed=embed)
        for j in search(query, tld="com", lang = 'en', num=5, stop=5, pause=2):
            await message.channel.send(j)

commandList.append(Command("!mute", "muteUser", "Timeout specified user for amount of time.\nUsage: !timeout USER-NAME SECONDS"))
async def muteUser(ctx, message):
    guild = message.guild
    # Check if input has valid number of args
    if len(message.content.split(" ")) == 3:
        # Check if member exists in server
        user = guild.get_member_named(message.content.split(" ")[1])
        if user != None:
            mutedMembers.append(user.id)
            await message.channel.send(message.content.split(" ")[1] + " is now muted for " + message.content.split(" ")[2] + " seconds.")
            await asyncio.sleep(int(message.content.split(" ")[2]))
            mutedMembers.remove(user.id)
        else:
            await message.channel.send("User not found")
    else:
        await message.channel.send("Invalid input\nUsage: !timeout USER#0000 <SECONDS>")


commandList.append(Command("!join", "joinvc", "Bot joins specified voice channel.\nUsage: !join <VOICE-CHANNEL>"))
async def joinvc(ctx, message):
    guild = message.guild
    channel = None
    for vc in guild.voice_channels:
        if vc.name == message.content.split(" ")[1]:
            channel = vc
            break
    if guild.voice_client is not None:
        return await guild.voice_client.move_to(channel)

    await channel.connect()

commandList.append(Command("!leave", "leavevc", "Bot leaves voice channel.\nUsage: !leave"))
async def leavevc(ctx, message):
    guild = message.guild
    if guild.voice_client is not None:
        await guild.voice_client.disconnect()

# @asyncio.coroutine
# def playQueue(ctx, message):
#     guild = message.guild
#     vc = guild.voice_client
#     while guild.voice_client != None:
#         if not vc.is_playing():
#             if playlist.next != None:
#                 vc.play(discord.FFmpegPCMAudio("youtube/{}.mp3".format(playlist.next.title)))
#                 ctx.voice_clients[0].source = discord.PCMVolumeTransformer(ctx.voice_clients[0].source)
#                 playlist.next = playlist.next.next

# def loopMusic(loop, ctx, message):
#     asyncio.set_event_loop(loop)
#     loop.run_until_complete(playQueue(ctx, message))

def checkForMusic(f_stop, ctx, message):
    global head
    #get the voice client
    guild = message.guild
    vc = guild.voice_client
    if not f_stop.is_set():
        #check for changes
        if not vc.is_playing():
            #head points towards current node
            if head.next != None:
                head = head.next
                print("Next Item: "+ str(head.title))
                vc.play(discord.FFmpegPCMAudio("youtube/{}.mp3".format(head.title)), after=lambda e: os.remove("youtube/"+head.title+".mp3"))
                ctx.voice_clients[0].source = discord.PCMVolumeTransformer(ctx.voice_clients[0].source)
        #every second check again
        threading.Timer(1, checkForMusic, [f_stop, ctx, message]).start()



commandList.append(Command("!play", "playMusic", "Play audio from youtube links through the bot\nUsage: !play <URL>"))
async def playMusic(ctx, message):
    firstime = 0
    if(len(message.content.split(" ")) == 1):
        await message.channel.send("No video link provided!")
        return
    #get video url
    video = message.content.split(" ")[1]
    guild = message.guild

    #if not connected to voice, connect
    if guild.voice_client == None:
        firstime = 1
        #create playlist when joining
        global playlist
        playlist = Node()
        playlist.title = "playlist title"
        global head
        global tail
        head = playlist
        tail = playlist
        #connect
        voice_channel = message.author.voice.channel
        vc = await voice_channel.connect()
        #Start multithreading
        f_stop = threading.Event()
        checkForMusic(f_stop, ctx, message)

    #Set options for ytdl
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'youtube/%(title)s.%(ext)s',
        'restrictfilenames': True,
        'noplaylist': True,
        'nocheckcertificate': True,
        'ignoreerrors': False,
        'logtostderr': False,
        'quiet': True,
        'no_warnings': True,
        'default_search': 'auto',
        'source_address': '0.0.0.0',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with youtube_dl.YoutubeDL(opts) as ydl:
        #download video
        try:
            title = ydl.extract_info(video, download=False).get('title', None)
        except:
            await message.channel.send("Error in youtube link provided!")
            return

        if title == None:
            await message.channel.send("Error in youtube link provided!")
            return

        try:
            
            ydl.download([video])
        except:
            await message.channel.send("Error in youtube link provided!")
            return
       
        
        #Notify user that the video has been added
        #await msg.delete()
        await message.channel.send("{} added to queue!".format(title))
        #replace symbols
        title = title.replace('?', '')
        title = title.replace(' ', '_')
        title = title.replace(',', '')
        #make new playlist node with title
        newVid = Node(title=title)
        #update end of playlist
        tail.next = newVid
        newVid.prev = tail
        tail = newVid

commandList.append(Command("!vol", "adjustVolume", "Allows users to adjust volume\nUsage: !vol <0-100>"))
async def adjustVolume(ctx, message):
    guild = message.guild
    if guild.voice_client != None:
        volume = float(max(0.0, min(1.0, float(message.content.split(" ")[1]) / 100.0)))
        ctx.voice_clients[0].source.volume = volume
        print(volume)
        await message.channel.send("Set volume: {}%".format(message.content.split(" ")[1]))
    else:
        await message.channel.send("Bot is not connected to any voice channel")

#def helperBlockFunction(ctx, args)
# For testing ONLY
commandList.append(Command("!stop", "logoutBot"))
async def logoutBot(client, message):
    await client.logout()
