from command import Command
#Importing discord for the embedded model 
import discord
#Google search API imported
#from googleapiclient.discovery import build
#import pprint


# Every module has to have a command list
commandList = []

# List of channels to remove links from, stores only text channel ids
removeLinksChannels = []

# Example function:
# Just make sure that the function name in a command is the same
# Make sure every function is async and has both client, message as parameters, and that await is used when sending your response
commandList.append(Command("!example", "exampleFunction"))
async def exampleFunction(client, message):
    response = "This is an example of a function setup."
    await message.channel.send(response)

# Display a list of either all command functionality
commandList.append(Command("!help", "help"))
async def help(client, message):
    # This will display a response that will hold descriptions of all of the commands
    response = """`!help` : Displays a page of all commands and their descriptions.\n
`!commands` : This command will display all of the available comamnds\n
`!users` <optional_arg> : Will display a list of all users and their roles with no argument,
but when given a role it will display all users with the given role.\n"""
    await message.channel.send(response)


# Display a list of either all Users or only Users with a certain role
commandList.append(Command("!users", "displayAllUsers"))
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
commandList.append(Command("!createtc", "createTextChannel"))
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
            await createTextChannelWithCategoryID(client, message, guild, channelName, categoryId)
            # Obtain the category name
            for category in guild.categories:
                if category.id == categoryId:
                    categoryName = category.name
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
                response = ">>> Multiple matches found for category with name **" + categoryName + "**. "
                response += "Please specify using category ID.\n"
                responseCount = 1
                for category in guild.categories:
                    if category.name == categoryName:
                        response += str(responseCount) + ". " + str(category.id) + "\n"
                        responseCount += 1
                response += "Command format: **!createtc text-channel-name category-id id**"
                await message.channel.send(response)
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
        response = ">>> Please specify a text channel name! Category name is optional.\n"
        response += "Command format: **!createtc text-channel-name category-name**"
        await message.channel.send(response)
    # Generate response with text channel added
    if channelName != 0:
        response = ">>> Successfully created the new text channel **" + channelName
        if categoryName != 0:
            response += "** in category **" + categoryName
        response += "**!"
        await message.channel.send(response)

# Helper function for createTextChannel that creates a text channel in the category specified by the ID
async def createTextChannelWithCategoryID(client, message, guild, channelName, categoryId):
    categoryFound = False
    for category in guild.categories:
        if category.id == categoryId:
            # Mark the category was found and create the text channel in the category
            categoryFound = True
            await guild.create_text_channel(channelName, category=category)
            break
    # Notify user if the channel was not found
    if categoryFound == False:
        await message.channel.send(">>> Category with id **" + str(categoryId) + "** was not found!")

# Command that deletes a new text channel on command
# Format: !deletetc text-channel-name (id) (id is optional, text-channel-name should be text-channel-id)
commandList.append(Command("!deletetc", "deleteTextChannel"))
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
                    await message.channel.send(">>> Successfully deleted the **" + tc.name + "** text channel!")
                    break
            # Notify user if the channel was not found
            if channelFound == False:
                await message.channel.send(">>> Text channel with id **" + str(channelId) + "** was not found!")
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
        await message.channel.send(">>> Please specify a text channel name!\nCommand format: **!deletetc text-channel-name**")

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
            response = ">>> Multiple matches found for **" + channelName + "**. Please delete using channel ID.\n"
            responseCount = 1
            for tc in guild.text_channels:
                if tc.name == channelName:
                    response += str(responseCount) + ". " + str(tc.id) + "\n"
                    responseCount += 1
            response += "Command format: **!deletetc text-channel-id id**"
            await message.channel.send(response)
        elif nameMatchCount == 1:
            # Delete the text channel with the given name
            for tc in guild.text_channels:
                if tc.name == channelName:
                    await tc.delete()
                    await message.channel.send(">>> Successfully deleted the **" + channelName + "** text channel!")
                    break
        else:
            # No text channel with the given name was found
            await message.channel.send(">>> Text channel with name **" + channelName + "** was not found!")


# Command that deletes a new text channel on command
# Format: !removelinks (add/remove/view) channel-name (id) (adds or removes a channel for monitoring links)
commandList.append(Command("!removelinks", "updateRemoveLinksList"))
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
        response = ">>> Please provide a text channel name and whether to add or remove link monitoring!\n"
        response += "Command format: **!removelinks add/remove channel-name**\n\n"
        response += "You may also view the list of text channels current being monitored.\n"
        response += "Command format: **!removelinks view**"
        await message.channel.send(response)
        action = "error" # Prevent the prompt from being printed twice
    # If an action was not specified or incorrectly specified, notify the user
    if action == 0:
        response = ">>> Please specify whether you want to add or remove a channel from being monitored for links!\n"
        response += "Command format: **!removelinks add/remove channel-name**\n\n"
        response += "If you wanted to view the list of text channels current being monitored, use the command below.\n"
        response += "Command format: **!removelinks view**"
        await message.channel.send(response)

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
                    response = ">>> The text channel **" + tc.name + "** has been added to the list to be monitored for links!"
                else:
                    response = ">>> The text channel **" + tc.name + "** has already been added to the list!"
                await message.channel.send(response)
                break
         # if the channel was not found, notify user
        if channelFound == False:
            await message.channel.send(">>> Text channel with id **" + str(channelId) + "** was not found!")
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
            response = ">>> Multiple matches found for **" + channelName + "**. Please add to the list using channel ID.\n"
            responseCount = 1
            for tc in guild.text_channels:
                if tc.name == channelName and tc.id not in removeLinksChannels:
                    response += str(responseCount) + ". " + str(tc.id) + "\n"
                    responseCount += 1
            response += "Command format: **!removelinks add channel-id id**"
            await message.channel.send(response)
        elif nameMatchCount == 1:
            # Add the text channel with the given name to removeLinksList
            for tc in guild.text_channels:
                if tc.name == channelName and tc.id not in removeLinksChannels:
                    removeLinksChannels.append(tc.id)
                    response = ">>> The text channel **" + tc.name + "** has been added to the list to be monitored for links!"
                    await message.channel.send(response)
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
                response = ">>> The text channel **" + channelName + "** has already been added to the list!"
            else:
                response = ">>> Text channel with name **" + channelName + "** was not found!"
            await message.channel.send(response)

# Helper function to updateRemoveLinksList that removes a text channel id to the list
async def removeFromRemoveLinksList(client, message, guild, action, channelInfo):
    # If id is passed in, find the channel by id and remove it from the list
    if action == "id":
        channelId = channelInfo
        if channelId in removeLinksChannels:
            removeLinksChannels.remove(channelId)
            response = ">>> The text channel **" + guild.get_channel(channelId).name 
            response += "** has been removed from the list for monitoring links."
            await message.channel.send(response)
        else:
            # Check if the channel actually exists on the server
            channelExists = False
            for tc in guild.text_channels:
                if tc.id == channelId:
                    channelExists = True
                    break
            if channelExists == True:
                response = ">>> The text channel **" + guild.get_channel(channelId).name + "** was not found in the list!"
            else:
                response = ">>> Text channel with id **" + str(channelId) + "** was not found!"
            await message.channel.send(response)
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
            response = ">>> Multiple matches found for **" + channelName + "**. Please remove from the list using channel ID.\n"
            responseCount = 1
            for tcId in removeLinksChannels:
                tc = guild.get_channel(tcId)
                if tc.name == channelName:
                    response += str(responseCount) + ". " + str(tc.id) + "\n"
                    responseCount += 1
            response += "Command format: **!removelinks remove channel-id id**"
            await message.channel.send(response)
        elif nameMatchCount == 1:
            # Remove the text channel with the given name from removeLinksList
            for tcId in removeLinksChannels:
                tc = guild.get_channel(tcId)
                if tc.name == channelName:
                    removeLinksChannels.remove(tc.id)
                    response = ">>> The text channel **" + tc.name + "** has been removed from the list for monitoring links."
                    await message.channel.send(response)
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
                response = ">>> The text channel **" + channelName + "** was not found in the list!"
            else:
                response = ">>> Text channel with name **" + channelName + "** was not found!"
            await message.channel.send(response)

# Helper function to updateRemoveLinksList that prints the list to the user
async def viewRemoveLinksList(client, message, guild):
    if len(removeLinksChannels) == 0:
        await message.channel.send(">>> There are currently no text channels being monitored for links.")
    response = ">>> Here are all the text channels currently being monitored for links:\n" # Message to the user
    responseCount = 1 # Used for numbers
    for tcId in removeLinksChannels:        
        tc = guild.get_channel(tcId)
        response += str(responseCount) + ". " + tc.name + "\n"
        response += "ID: " + str(tc.id) + "\n"
        responseCount += 1
    if len(removeLinksChannels) != 0:
        await message.channel.send(response)

# This function is used by main.py to check if the associated message has a link
# If the message has a link and the channel is monitored, we return True to indicate deletion
# If the message does not satify conditions False should be returned
def checkMessageForLinks(message):
    if message.channel.id in removeLinksChannels:
        if "https://" in message.content or "http://" in message.content:
            return True
    return False
# Additional module command
commandList.append(Command("!downloadModules", "downloadAdditionalModules"))
# Function for additional module download command
async def downloadAdditionalModules(ctx, message):
    #Check the number of arguments typed including the command
    args = len(message.content.split(" "))
    # If the user just types the command give them the link to the GitHub modules that we have
    # Otherwise given them the google search as well
    if(args == 1):
        #Embedded is the nice block that also gives the embedded link
        embed = discord.Embed(
        title='More Discord Modules',
        description='[GitHub](https://github.com/ndamalas/Wild-Card-Bot/tree/main/modules)',
        color = 0xffffff
        )
    await message.channel.send(embed=embed)
    #else:
        #Need to run: "pip install google-api-python-client" before this works
        #googleKey = "AIzaSyDMod0KR7Boab6HJm4hY1lpgR-kBZb97uA"
        #cse_ID = "d867b72f0fa01663e"
        #results = googleSearch(
            #args, googleKey, cse_ID, num=5)
        #for result in results:
            #pprint.pprint(result)
    #await message.channel.send(results)
#def googleSearch(args, googleKey, cse_ID, **kwargs):
    #service = build("customsearch", "v1", developerKey=googleKey)
    #res = service.cse().list(q=args, cx=cse_ID, **kwargs).execute()
    #return res['items']
# For testing ONLY
commandList.append(Command("!stop", "logoutBot"))
async def logoutBot(client, message):
    await client.logout()