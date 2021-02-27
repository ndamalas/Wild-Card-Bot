from command import Command

# Every module has to have a command list
commandList = []

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


# For testing ONLY
commandList.append(Command("!stop", "logoutBot"))
async def logoutBot(client, message):
    await client.logout()