from command import Command
import string
import discord

# Every module has to have a command list
commandList = []

# List of channels to remove links from, stores only text channel ids
removeLinksChannels = []

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
commandList.append(Command("!createtc", "createTextChannel", "Creates a new text channel.\nUsage: !createtc <TEXT-CHANNEL-NAME> <CATEGORY-NAME> (id) (The user can include spaces in their category name, user can also specify the id of a particular category if there are multiple categories with same name)"))
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
commandList.append(Command("!deletetc", "deleteTextChannel", "Deletes a new text channel on command.\nUsage: !deletetc <TEXT-CHANNEL-NAME> (id) (id is optional, text-channel-name should be text-channel-id)"))
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
commandList.append(Command("!createvc", "createVoiceChannel", "Creates a new voice channel.\nUsage: !createvc <CHANNLE_NAME> <*CATEGORY_NAME>"))
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
commandList.append(Command("!removelinks", "updateRemoveLinksList", "Interact with the remove links list.\nUsage: !removelinks <ADD/REMOVE/VIEW> <CHANNEL-NAME> (id) (adds or removes a channel for monitoring links)"))
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
commandList.append(Command("!roles", "listRoles"))
async def listRoles(client, message):
    guild = message.guild
    response = ">>> Listing All Server Roles:\n"
    response += ", ".join([str(r.name) for r in guild.roles])
    await message.channel.send(response)
    return

# Create a role
commandList.append(Command("!createRole", "createRole"))
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
commandList.append(Command("!dRole", "dRole"))
async def dRole(client, message):
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
commandList.append(Command("!giveRole", "giveRole"))
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

commandList.append(Command("!banMember", "banMember", "Bans member from server"))
async def banMember(client, message):
    await message.channel.send("IN BAN MEMBER")
    member = message.author
    guild = message.guild
    response=""
    if len(message.content.split(" ")) != 3:
        await message.channel.send(">>> Please use format:\n !banMember \"user\" \"reason\"")
        return
    await message.channel.send("PASSED FORMAT CHECK")
    user_found = False
    member_to_ban = 0
    userList = message.guild.members
    for user in userList:
        if str(user) == message.content.split(" ")[1]:
            user_found = True
            member_to_ban = user
    if user_found == False:
        await message.channel.send("USER NOT FOUND")
        return
    #for i in range(3, len(message.content.split(" "))):
        #response+=message.content.split(" ")[i]
    #await message.channel.send(response)
    await guild.ban(member_to_ban)
    #guild.ban(member, reason=message)  
    await message.channel.send("User has been kicked")

# Display a list of all banned words
commandList.append(Command("!bannedWords", "displayBannedWords", "Can display, add, or remove words from banned words list.\nUsage: !bannedWords (optional) <ADD/REMOVE> <WORD>"))
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
    for i in range(2, len(message.content.split(" "))):
        word = words[i]
        bannedWords.append(word)
        # Write them to the file
        file = open("bannedWords.txt", "a")
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
        if (word in words):
            bannedWords.remove(word)
        else:
            await message.channel.send(word + " not found in banned words list, try again.")
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
    allowBannedWords = len(messageWords) > 1 and messageWords[0] == "!bannedWords" and messageWords[1] == "remove"
    if (allowBannedWords):
        return False
    reformattedMessageWords= []
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


# For testing ONLY
commandList.append(Command("!stop", "logoutBot"))
async def logoutBot(client, message):
    await client.logout()
