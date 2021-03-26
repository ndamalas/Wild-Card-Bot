try:
    from command import Command
except:
    pass

import discord
import random

# Module that creates and monitors polls

# Poll class that represents a poll
class Poll:
    # In each situation, None indicates that the user has not specified it yet
    def __init__(self):
        self.complete = False # Whether the poll is complete or not
        self.title = None     # The title of the poll
        self.question = None  # The question associated with the poll
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
    commandList.append(Command("!createpoll", "createPoll", usage))
except:
    print("Command Module correctly not imported.")
    print("The Main Module is required for this to work.")
    print("")

# Creates a poll with info specified by the user
async def createPoll(client, message):
    user = message.author
    # Create the poll and message the user if recieved !createpoll from a channel
    if message.channel != None and message.content.split(" ")[0] == "!createpoll":
        userPolls[user.id] = Poll
        response = "Hello " + user.mention + "!\n\n"
        response += "To initiate the poll creation process, please give your poll a title.\n\n"
        response += "If at any point you want to cancel poll creation, message **cancel**."
        await directMessageUser(user, "Poll Creation", response)
        # Notify the user to check their dms
        response = ""
        response += "Hello " + user.mention + "!\n\n"
        response += "Please check your DMs to continue the poll creation process."
        embed = discord.Embed(title="Poll Creation", description=response, colour=discord.Colour.blue())
        embed.set_author(name=user.display_name, icon_url=user.avatar_url)
        await message.channel.send(embed=embed)

# Direct messages the given user with an embed created from the title and response arguments
async def directMessageUser(user, title, response):
    embed = discord.Embed(title=title, description=response, colour=discord.Colour.blue())
    embed.set_author(name=user.display_name, icon_url=user.avatar_url)
    await user.send(embed=embed)