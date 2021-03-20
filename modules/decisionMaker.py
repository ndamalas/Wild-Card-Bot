from command import Command

import discord
import random

# Module that displays information for developers

# Every module has to have a command list
commandList = []
usage = "Command that helps makes decisions. "
usage += "If you want a random number, use !decide (picks) number (low bound) (high bound). "
usage += "If you want to choose from custom options, use !decide (picks) custom (option1) (option2). "
usage += "If you want your options to have spaces, please use quotes around your options."

# Format: !decide (number of decisions) <number/custom> (low bound) (high bound) (options)
commandList.append(Command("!decide", "decisionMaker", usage))
async def decisionMaker(client, message):
    action = 0 # Specifies whether to use numbers or custom options

    messageArgs = message.content.split(" ")
    if len(messageArgs) >= 2:
        # Check if the user wants to generate a number between 0 and 9
        if messageArgs[1] == "number":
            action = "number"
            # Assign the bounds
            bounds = assignBounds(messageArgs)
            # Check if error was recieved
            if bounds == None:
                action = "error"
            else:
                lowBound = bounds[0]
                highBound = bounds[1]
            # Only generate randomNumber if specified
            if action != "error":
                randomNumber = generateRandNumber(lowBound, highBound)
                await sendNumberResults(message, randomNumber, lowBound, highBound, 1)
    else:
        response = "Incorrect usage of the command !decide. Please use **!commands !decide** to see the syntax of this command."
        embed = discord.Embed(title='Incorrect Usage of !decide', description=response, colour=discord.Colour.purple())
        await message.channel.send(embed=embed)
        action = "syntax"
    # Print error message if there is a cast error or no action specified
    if action == 0:
        response = "Incorrect usage of the command !decide. Please use **!commands !decide** to see the syntax of this command."
        embed = discord.Embed(title='Incorrect Usage of !decide', description=response, colour=discord.Colour.purple())
        await message.channel.send(embed=embed)
    elif action == "error":
        response = "There was an error with the arguments given! Please double check you have followed the specified format "
        response += "specified by **!commands !decide**."
        embed = discord.Embed(title='Incorrect Usage of !decide', description=response, colour=discord.Colour.purple())
        await message.channel.send(embed=embed)

# Generates a random integer or float between lowBound and highBound
def generateRandNumber(lowBound, highBound):
    # Check if any of the bounds are floats
    numberType = 0 # Float or integer
    if type(lowBound) == type(1.5) or type(highBound) == type(1.5):
        numberType = "float"
    # Depending on the number type generate the random integer or float
    if numberType == "float":
        return random.uniform(lowBound, highBound)
    else:
        return random.randint(lowBound, highBound)

# Checks and assigns the bounds
def assignBounds(messageArgs):
    lowBound = 0 # Default values
    highBound = 9 # Default values
    if len(messageArgs) >= 4:
        # Check if bounds can be parsed to int or float
        try:
            lowBound = int(messageArgs[2])
            highBound = int(messageArgs[3])
        except:
            try:
                lowBound = float(messageArgs[2])
                highBound = float(messageArgs[3])
            except:
                return None
        # Switch bounds if the low bound is larger
        if highBound < lowBound:
            lowBound, highBound = highBound, lowBound
    elif len(messageArgs) >= 3:
        # Check if bound can be parsed to int or float
        try:
            highBound = int(messageArgs[2])
        except:
            try:
                highBound = float(messageArgs[2])
            except:
                return None
        # Switch bounds if the low bound is larger
        if highBound < lowBound:
            lowBound, highBound = highBound, lowBound
    return [lowBound, highBound]

# Sends a message to the user with the random number choices
async def sendNumberResults(message, result, lowBound, highBound, count):
    response = "Hello " + message.author.mention + "!\n"
    response += "I have generated **" + str(count) + "** random number(s) between **" + str(lowBound) + "** "
    response += "and **" + str(highBound) + "**.\n\n"
    embed = discord.Embed(title='Decision Results', description=response, colour=discord.Colour.random())
    embed.add_field(name="Chosen Number(s):", value=str(result), inline=False)
    await message.channel.send(embed=embed)
