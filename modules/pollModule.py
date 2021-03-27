try:
    from command import Command
except:
    pass

import discord
import random
import asyncio

# Module that creates and monitors polls

# Poll class that represents a poll
class Poll:
    # In each situation, None indicates that the user has not specified it yet
    def __init__(self):
        self.complete = False # Whether the poll is complete or not
        self.title = None     # The title of the poll
        self.question = None  # The question associated with the poll
        self.options = None   # List of all possible options
        self.reactions = None # List of reactions that the people will use to vote
        self.time = None      # The time limit of the poll, -1 indicates no time limit
        self.channel = None   # The id of the text channel that the poll is sent to

# Every module has to have a command list
commandList = []

# Description for !commands
usage = "Command used to initiate the process of creating a poll. The creation process is redirected to your DMs."

# Dictionary that keeps tracks of the polls currently being created or voted on corresponding to each user 
# Key: user id
# Value: list of Poll objects
userPolls = {}

# Format: !createpoll
try:
    commandList.append(Command("!createpoll", "createPoll", usage, permissions=["direct_message"]))
except:
    print("Command Module correctly not imported.")
    print("The Main Module is required for this to work.")
    print("")

# Creates a poll with info specified by the user
async def createPoll(client, message):
    user = message.author
    # Create the poll and message the user if recieved !createpoll from a channel
    if checkCreationConditions(message, user) == True:
        if user.id in userPolls:
            userPolls[user.id].append(Poll())
        else:
            userPolls[user.id] = []
            userPolls[user.id].append(Poll())
        response = "Hello " + user.mention + "!\n\n"
        response += "To initiate the poll creation process, please give your poll a title.\n\n"
        response += "If at any point you want to cancel poll creation, message **cancel**.\n"
        response += "If you call another command while creating a poll, call !createpoll again to resume poll creation."
        await directMessageUser(user, "Poll Creation", response)
        # Notify the user to check their dms
        response = ""
        response += "Hello " + user.mention + "!\n\n"
        response += "Please check your DMs to continue the poll creation process."
        embed = discord.Embed(title="Poll Creation", description=response, colour=discord.Colour.blue())
        embed.set_author(name=user.display_name, icon_url=user.avatar_url)
        await message.channel.send(embed=embed)
    elif checkForUnfinishedPoll(message, user) == True:
        await completePoll(client, message, user)

# Direct messages the given user with an embed created from the title and response arguments
async def directMessageUser(user, title, response):
    embed = discord.Embed(title=title, description=response, colour=discord.Colour.blue())
    embed.set_author(name=user.display_name, icon_url=user.avatar_url)
    await user.send(embed=embed)

# Checks if the user matches the conditions necessary for poll creation
def checkCreationConditions(message, user):
    if user.id in userPolls:
        notAlreadyCreatingPoll = len([p for p in userPolls[user.id] if p.complete == False]) == 0
    else:
        notAlreadyCreatingPoll = True
    return message.guild != None and message.content.split(" ")[0] == "!createpoll" and notAlreadyCreatingPoll

# Checks if the user is currently creating a poll
def checkForUnfinishedPoll(message, user):
    if user.id in userPolls:
        return len([p for p in userPolls[user.id] if p.complete == False]) > 0 and message.guild == None
    return False

# Completes the next incremental step in the poll
async def completePoll(client, message, user):
    poll = [p for p in userPolls[user.id] if p.complete == False][0]
    # Order in which the poll info should be completed
    # title->question->options->reactions->time->channel
    if message.content == 'cancel':
        userPolls[user.id].remove(poll)
        response = "Poll creation successfully canceled."
        await directMessageUser(user, "Poll Creation Cancelled", response)
    elif poll.title == None:
        poll.title = message.content
        response = "The title for your poll is **" + poll.title + "**.\n"
        response += "Please enter the question to be asked in your poll."
        await directMessageUser(user, "Title Added", response)
    elif poll.question == None:
        poll.question = message.content
        response = "The question for your poll is **" + poll.question + "**.\n"
        response += "Please enter the answer options for your poll.\n"
        response += "Seperate options with spaces. If an option has spaces in it, surround it with quotes."
        await directMessageUser(user, "Question Added", response)
    elif poll.options == None:
        poll.options = parseOptions(message.content)
        optionStr = ""
        for option in poll.options:
            optionStr += str(option) + "\n"
        response = "Here are the options to be included in your poll:\n"
        response += optionStr
        await directMessageUser(user, "Options Added", response)
        await setReactions(client, user, poll)

# Parses the options from the message content
def parseOptions(content):
    # Check if quotes are used to specify inputs, making sure the number of quotes is even
    if content.count('"') > 0 and content.count('"') % 2 == 0:
        options = []
        inQuotes = False
        currentOption = ""
        for char in content:
            if inQuotes == False and char == '"':
                inQuotes = True
            elif inQuotes == False:
                if char != " ":
                    currentOption += char
                else:
                    if currentOption != "":
                        options.append(currentOption)
                        currentOption = ""
            elif inQuotes == True and char == '"':
                inQuotes = False
                if currentOption != "":
                    options.append(currentOption)
                    currentOption = ""
            elif inQuotes == True:
                currentOption += char
        # Check if currentOption contains an option
        if currentOption != "":
            options.append(currentOption)
        return options
    else:
        # Since there are no quotes, parse using spaces
        options = []
        messageArgs = content.split(" ")
        for arg in messageArgs:
            if arg != "":
                options.append(arg)
        return options

# Sends a dm to the user and asks them to react to it
# The reactions are then parsed for use by the poll
async def setReactions(client, user, poll):
    # Create message for the user to react to
    response = "Please react to this message with the reactions you would like to use for your poll.\n"
    response += "You have specified **" + str(len(poll.options)) + "** options. Please react with **" 
    response += str(len(poll.options)) + "** reactions.\n"
    response += "If you want the bot to choose for you,  message **auto**."
    embed = discord.Embed(title="Set Reactions", description=response, colour=discord.Colour.blue())
    embed.set_author(name=user.display_name, icon_url=user.avatar_url)
    await user.send(embed=embed)
    # Continuously check the message to see if the user has added a reaction
    poll.reactions = []
    while poll != None and len(poll.reactions) < len(poll.options):
        reaction, user = await client.wait_for('reaction_add')
        poll.reactions.append(reaction)
    # Notify user that the reactions have been successfully added
    response = ""
    response = "Reactions successfully added to your poll!\n"
    await directMessageUser(user, "Reactions Added", response)