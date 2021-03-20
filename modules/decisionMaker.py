try:
    from command import Command
except:
    print("Initiating Unit Tests for decisionMaker Module.")
    print("")

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
try:
    commandList.append(Command("!decide", "decisionMaker", usage))
except:
    print("Command Module correctly not imported.")
    print("The Main Module is required for this to work.")
    print("")

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

# Unit tests
if __name__=="__main__":
    print("Begin Unit Testing.")
    print("")
    # Unit Tests for function generateRandNumber()
    print("Testing random number generation:")
    print("")
    passed = 0
    # Test 1: sanity check to see if random module is working
    result = generateRandNumber(0, 0)
    if result == 0 and type(result) == type(3):
        passed += 1
    else:
        print("-x- Test 1 Failed")    
    # Test 2: random number generated for two int args
    result = generateRandNumber(0, 9)
    if result >= 0 and result <= 9 and type(result) == type(3):
        passed += 1
    else:
        print("-x- Test 2 Failed")    
    # Test 3: random float generated for two float args
    result = generateRandNumber(1.2, 2.4)
    if result >= 1.2 and result <= 2.4 and type(result) == type(3.5):
        passed += 1
    else:
        print("-x- Test 3 Failed")
    # Test 4: random float generated for one float arg and one int arg
    result = generateRandNumber(1.2, 3)
    if result >= 1.2 and result <= 3.0 and type(result) == type(3.5):
        passed += 1
    else:
        print("-x- Test 4 Failed")
    # Test 5: random float generated for one int arg and one float arg
    result = generateRandNumber(1, 3.4)
    if result >= 1 and result <= 3.4 and type(result) == type(3.5):
        passed += 1
    else:
        print("-x- Test 5 Failed")
    
    print("    Tests Complete for generateRandNumber()")
    print("    Passed " + str(passed) + "/" + str(5) + " Tests")
    print("")
    # End tests for function generateRandNumber()

    # Unit Tests for function assignBounds()
    print("Testing bound assignment:")
    print("")
    passed = 0
    # Test 1: check bound assignment when no bounds are given
    input = ["!decide", "number"]
    result = assignBounds(input)
    if result == [0, 9]:
        passed += 1
    else:
        print("-x- Test 1 Failed")
    # Test 2: check bound assignment when one postive int bound given
    input = ["!decide", "number", "5"]
    result = assignBounds(input)
    if result == [0, 5]:
        passed += 1
    else:
        print("-x- Test 2 Failed")
    # Test 3: check bound assignment when one negative int bound given
    input = ["!decide", "number", "-2"]
    result = assignBounds(input)
    if result == [-2, 0]:
        passed += 1
    else:
        print("-x- Test 3 Failed")
    # Test 4: check bound assignment when one positive float bound given
    input = ["!decide", "number", "3.5"]
    result = assignBounds(input)
    if result == [0, 3.5]:
        passed += 1
    else:
        print("-x- Test 4 Failed")
    # Test 5: check bound assignment when one negative float bound given
    input = ["!decide", "number", "-3.5"]
    result = assignBounds(input)
    if result == [-3.5, 0]:
        passed += 1
    else:
        print("-x- Test 5 Failed")
    # Test 6: check bound assignment when two int bounds given in ascending order
    input = ["!decide", "number", "-3", "2"]
    result = assignBounds(input)
    if result == [-3, 2]:
        passed += 1
    else:
        print("-x- Test 6 Failed")
    # Test 7: check bound assignment when two int bounds given in descending order
    input = ["!decide", "number", "5", "-4"]
    result = assignBounds(input)
    if result == [-4, 5]:
        passed += 1
    else:
        print("-x- Test 7 Failed")
    # Test 8: check bound assignment when two float bounds given in ascending order
    input = ["!decide", "number", "-3.5", "3.5"]
    result = assignBounds(input)
    if result == [-3.5, 3.5]:
        passed += 1
    else:
        print("-x- Test 8 Failed")
    # Test 9: check bound assignment when two float bounds given in descending order
    input = ["!decide", "number", "3.5", "-3.5"]
    result = assignBounds(input)
    if result == [-3.5, 3.5]:
        passed += 1
    else:
        print("-x- Test 9 Failed")
    # Test 10: check bound assignment when one int bound given and one float bound given
    input = ["!decide", "number", "-3", "3.5"]
    result = assignBounds(input)
    if result == [-3.0, 3.5]:
        passed += 1
    else:
        print("-x- Test 10 Failed")
    # Test 11: check bound assignment when one float bound given and int bound given
    input = ["!decide", "number", "-3.5", "3"]
    result = assignBounds(input)
    if result == [-3.5, 3.0]:
        passed += 1
    else:
        print("-x- Test 11 Failed")
    # Test 12: check proper error handling for one invalid bound given
    input = ["!decide", "number", "error"]
    result = assignBounds(input)
    if result == None:
        passed += 1
    else:
        print("-x- Test 12 Failed")
    # Test 13: check proper error handling for one invalid bound given and one valid bound given
    input = ["!decide", "number", "error", "0"]
    result = assignBounds(input)
    if result == None:
        passed += 1
    else:
        print("-x- Test 13 Failed")
    # Test 14: check proper error handling for two invalid bounds given
    input = ["!decide", "number", "error", "error2"]
    result = assignBounds(input)
    if result == None:
        passed += 1
    else:
        print("-x- Test 14 Failed")
    
    print("    Tests Complete for assignBounds()")
    print("    Passed " + str(passed) + "/" + str(14) + " Tests")
    print("")
    # End tests for function assignBounds()