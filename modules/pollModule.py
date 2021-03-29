try:
    from command import Command
except:
    pass

import discord
import asyncio

# Module that creates and monitors polls

# Poll class that represents a poll
class Poll:
    # In each situation, None indicates that the user has not specified it yet
    def __init__(self, guild):
        self.guild = guild    # The server the poll was requested from
        self.id = None        # Used internally to identify polls
        self.complete = False # Whether the poll is complete or not
        self.title = None     # The title of the poll
        self.question = None  # The question associated with the poll
        self.options = None   # List of all possible options
        self.reactions = None # List of reactions that the people will use to vote
        self.time = None      # The time limit of the poll, 0 indicates no time limit
        self.channel = None   # The id of the text channel that the poll is sent to
        self.rm = None        # The message containing the reactions
        self.pm = None        # The message containing the poll

# Every module has to have a command list
commandList = []

# Description for !commands
usage = "Command used to initiate the process of creating a poll. The creation process is redirected to your DMs."

# Dictionary that keeps tracks of the polls currently being created or voted on corresponding to each user 
# Key: user id
# Value: list of Poll objects
userPolls = {}

# Keeps track of the currently assigned poll id
idAssignment = 0

# Default reactions to use
defaultReactions = [u"\U0001F34E", u"\U0001F350", u"\U0001F34A", u"\U0001F34B", u"\U0001F349"]

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
            userPolls[user.id].append(Poll(message.guild))
        else:
            userPolls[user.id] = []
            userPolls[user.id].append(Poll(message.guild))
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
    elif checkForDone(message, user) == True:
        # Check if the user has specified for a poll to be finished
        pollId = int(message.content.split(" ")[1])
        await concludePoll(user, pollId)
    elif checkForUnfinishedPoll(message, user) == True:
        # If there is an unfinished poll and the user has send input
        await completePoll(message, user)

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

# Checks if the user is requesting a poll to be concluded
def checkForDone(message, user):
    if len(message.content.split(" ")) >= 2:
        # done <poll-id> must be called, user must have a completed poll with no time limit
        if message.content.split(" ")[0].lower() == "done" and message.content.split(" ")[1].isnumeric():
            if user.id in userPolls:
                try:
                    pollId = int(message.content.split(" ")[1])
                except:
                    return False
                return len([r for r in userPolls[user.id] if r.id == pollId and r.complete == True and r.time == 0]) > 0
    return False

# Checks if the user is currently creating a poll
def checkForUnfinishedPoll(message, user):
    if user.id in userPolls:
        return len([p for p in userPolls[user.id] if p.complete == False]) > 0 and message.guild == None
    return False

# Completes the next incremental step in the poll
async def completePoll(message, user):
    poll = [p for p in userPolls[user.id] if p.complete == False][0]
    # Order in which the poll info should be completed
    # title->question->options->reactions->time->channel
    if message.content.lower() == 'cancel':
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
        await setReactions(message, user, poll)
    elif message.content.lower() == 'auto':
        for i in range(len(poll.options)):
            await poll.rm.add_reaction(defaultReactions[i])
    elif poll.time == None:
        # Check if reactions are actually set properly
        if len(poll.reactions) < len(poll.options):
            return
        poll.time = parseTime(message.content)
        # Check if the time limit was properly specified
        if poll.time == None:
            response = "There was an error parsing your time limit.\n"
            response += "Please reenter the time limit. It must be an integer."
            await directMessageUser(user, "Time Limit Error", response)
        else:
            if poll.time == 0:
                response = "The poll will run until you ask it to stop.\n"
            else:
                response = "The poll will run for **" + str(poll.time) + "** seconds.\n"
            response += "Please specify the name or id of the text channel that you would like to send the poll to.\n"
            response += "If you want to specify using text channel id, please message **<channel-id> id**."
            await directMessageUser(user, "Time Limit Added", response)
    elif poll.channel == None:
        poll.channel = await parseChannel(user, message.content, poll)
        if poll.channel != None:
            global idAssignment
            poll.id = idAssignment
            idAssignment += 1
            poll.complete = True
            # Send the poll
            response = "Success! The poll will be send to the text channel **" + poll.guild.get_channel(poll.channel).name
            response += "**!\n"
            if poll.time == 0:
                response += "The id of this poll is **" + str(poll.id) + "**. To end the poll, message "
                response += "**done** **" + str(poll.id) + "**."
            await directMessageUser(user, "Poll Sent", response)
            await sendPoll(poll)

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
async def setReactions(message, user, poll):
    # Build string of all options
    optionsStr = ""
    for option in poll.options:
        optionsStr += option + " -> "
    optionsStr = optionsStr[:-4] + "\n"
    # Create message for the user to react to
    response = "Please react to this message with the reactions you would like to use for your poll.\n"
    response += "You have specified **" + str(len(poll.options)) + "** options. Please react with **" 
    response += str(len(poll.options)) + "** reactions.\n"
    response += "The order in which you react matters. The first reaction corresponds with the first option.\n"
    response += "Order of options:\n"
    response += optionsStr
    response += "If you want the bot to choose for you,  message **auto**."
    embed = discord.Embed(title="Set Reactions", description=response, colour=discord.Colour.blue())
    embed.set_author(name=user.display_name, icon_url=user.avatar_url)
    msg = await user.send(embed=embed)
    poll.rm = msg
    # Continuously check the message to see if the user has added a reaction
    poll.reactions = []
    while poll != None and len(poll.reactions) < len(poll.options):
        msg = await message.channel.fetch_message(msg.id)
        poll.reactions = msg.reactions
        await asyncio.sleep(1)
    # Notify user that the reactions have been successfully added
    response = ""
    response = "Reactions successfully added to your poll!\n"
    response += "Please specify a time limit in seconds for the poll. Message **none** if you want no time limit."
    await directMessageUser(user, "Reactions Added", response)

# Parses the time limit from the message content
# None is returned if there is an error with the value specified
def parseTime(content):
    # None specifies no time limit
    if content.lower() == "none":
        return 0
    try:
        timeLimit = int(content)
    except:
        return None
    if timeLimit > 0:
        return timeLimit
    return None

# Parses the channel name or id and returns the channel id
# None is returned if there is an error or the channel is not found
async def parseChannel(user, content, poll):
    # Determine if we are parsing id or name
    if len(content.split(" ")) >= 2 and content.split(" ")[1] == "id":
        try:
            channelId = int(content.split(" ")[1])
        except:
            response = "There was an error with your channel ID! Make sure it is an integer."
            await directMessageUser(user, "Multiple Channels Found", response)
            return None
        channelFound = False
        for tc in poll.guild.text_channels:
            if tc.id == channelId:
                channelFound = True
                return tc.id
        # Notify user if the channel was not found
        if channelFound == False:
            response = "Text channel with id **" + str(channelId) + "** was not found!"
            await directMessageUser(user, "Text Channel Not Found", response)
            return None
    else:
        nameMatchCount = 0
        for tc in poll.guild.text_channels:
            if tc.name == content:
                nameMatchCount += 1
        # Determine action based on how many name matches
        if nameMatchCount > 1:
            # If multiple matches, notify user and print all matches
            response = "Multiple matches found for **" + content + "**. Please specify using channel ID.\n"
            responseCount = 1
            for tc in poll.guild.text_channels:
                if tc.name == content:
                    response += str(responseCount) + ". " + str(tc.id) + "\n"
                    responseCount += 1
            response += "The format is **<channel-id> id**."
            await directMessageUser(user, "Multiple Channels Found", response)
            return None
        elif nameMatchCount == 1:
            # Return the channel id matching the name specified
            for tc in poll.guild.text_channels:
                if tc.name == content:
                    return tc.id
        else:
            # No text channel with the given name was found
            response = "Text channel with name **" + content + "** was not found!"
            await directMessageUser(user, "Text Channel Not Found", response)
            return None
    return None

# Sends the poll to the designated channel
async def sendPoll(poll):
    # Format: Title -> Question -> Reactions and Options
    embed = discord.Embed(title="Poll", description = "\n", colour=discord.Colour.green())
    # Display title and question
    embed.add_field(name=poll.title, value=poll.question + "\n\n", inline=False)
    # Display which reaction corresponds with which option
    optionsAndReactions = ""
    for i in range(len(poll.options)):
        optionsAndReactions += str(poll.reactions[i]) + " for " + poll.options[i] + "\n"
    embed.add_field(name="Vote:", value=optionsAndReactions, inline=False)
    poll.pm = await poll.guild.get_channel(poll.channel).send(embed=embed)
    # React to the poll to make it easier for people to vote
    for i in range(len(poll.options)):
            await poll.pm.add_reaction(poll.reactions[i])
    # Consider the time limit
    await enforceTimeLimit(poll)
    
# Enforces the time limit if necessary
async def enforceTimeLimit(poll):
    # If no time limit, do not wait
    if poll.time == 0:
        return
    await asyncio.sleep(poll.time)
    await sendResults(poll)

# Sets up the poll for poll results 
async def concludePoll(user, pollId):
    poll = [r for r in userPolls[user.id] if r.id == pollId and r.complete == True and r.time == 0][0]
    await sendResults(poll)

# Sends the results of the poll after parsing the given votes
# Deletes the poll as well
async def sendResults(poll):
    await poll.pm.delete()
    await poll.guild.get_channel(poll.channel).send("Poll Finished")