from command import Command

import discord
import random

# Module that displays information for developers

# Every module has to have a command list
commandList = []
usage = "Command that helps makes decisions. "
usage += "If you want a random number, use !decide (numbers) number (low bound) (high bound). "
usage += "If you want to choose from custom options, use !decide (numbers) custom (option1) (option2). "
usage += "If you want your options to have spaces, please use quotes around your options."

# Format: !decide (number of decisions) <number/custom> (low bound) (high bound) (options)
commandList.append(Command("!decide", "decisionMaker", usage))
async def decisionMaker(client, message):
    action = 0 # Specifies whether to use numbers or custom options

    if len(message.content.split(" ")) >= 2:
        # Check if the user wants to generate a number between 0 and 9
        action = message.content.split(" ")[1]
        if action == "number":
            randomNumber = generateRandNumber(0, 9)
            await sendNumberResults(message, randomNumber, 0, 9, 1)
    else:
        response = "Incorrect usage of the command !decide. Please use **!commands !decide** to see the syntax of this command."
        embed = discord.Embed(title='Incorrect Usage of !decide', description=response, colour=discord.Colour.purple())
        await message.channel.send(embed=embed)
        action = "error"

# Generates a random integer or float between lowBound and highBound
def generateRandNumber(lowBound, highBound):
    # Check if any of the bounds are floats
    numberType = 0 # Float or integer
    if type(lowBound) == type(1.5) or type(highBound) == type(1.5):
        numberType = "float"
    # Depending on the number type generate the random integer or float
    if numberType == "float":
        return 1.0
    else:
        return random.randint(lowBound, highBound)

# Sends a message to the user with the random number choices
async def sendNumberResults(message, result, lowBound, highBound, count):
    response = "Hello " + message.author.mention + "!\n"
    response += "I have generated **" + str(count) + "** random number(s) between **" + str(lowBound) + "** "
    response += "and **" + str(highBound) + "**.\n\n"
    embed = discord.Embed(title='Decision Results', description=response, colour=discord.Colour.random())
    embed.add_field(name="Chosen Number(s):", value=str(result), inline=False)
    await message.channel.send(embed=embed)
