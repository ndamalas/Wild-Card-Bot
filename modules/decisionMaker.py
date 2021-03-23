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
    picks = 1 # Determines the number of picks the user wants, 1 is default
    messageArgs = message.content.split(" ")
    messageContent = message.content
    # Check if number of picks specified   
    if len(messageArgs) >= 2:
        # Attempt to convert the second argument to a int
        try:
            messageArgs[1] = int(messageArgs[1])
        except:
            pass
        # See if the second argument specifies the number of picks
        if type(messageArgs[1]) == type(0):
            # Delete the picks argument from the argument list
            picks = messageArgs[1]
            del messageArgs[1]
            # Delete the picks argument from the content
            firstSpace = messageContent.find(" ")
            messageContent = messageContent[:firstSpace] + messageContent[messageContent.find(" ", firstSpace + 1):]
    # Parse the message
    if len(messageArgs) >= 2:
        # Check if the user wants to specify custom options
        if messageArgs[1] == "custom":
            action = "custom"
            options = parseCustomOptions(messageContent)
            # Check if the options list actually has options
            if len(options) == 0:
                action = "error"
            # Check if the number of picks exceeds the number of options
            if checkPicksForCustomOptions(options, picks) == False:
                action = "error"
            if action != "error":
                picked = pickOption(options, picks)
                await sendCustomResults(message, picked, options, picks)
        # Check if the user wants to generate a number
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
            # Check if the number of picks exceeds the total possible integers
            if checkPicksForNumbers(lowBound, highBound, picks) == False:
                action = "error"
            # Only generate randomNumber if specified
            if action != "error":
                randomNumber = generateRandNumber(lowBound, highBound, picks)
                await sendNumberResults(message, randomNumber, lowBound, highBound, picks)
    else:
        response = "Incorrect usage of the command !decide. Please use **!commands !decide** to see the syntax of this command."
        embed = discord.Embed(title='Incorrect Usage of !decide', description=response, colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        action = "syntax"
    # Print error message if there is a cast error or no action specified
    if action == 0:
        response = "Incorrect usage of the command !decide. Please use **!commands !decide** to see the syntax of this command."
        embed = discord.Embed(title='Incorrect Usage of !decide', description=response, colour=discord.Colour.red())
        await message.channel.send(embed=embed)
    elif action == "error":
        response = "There was an error with the arguments given! Please double check you have followed the specified format "
        response += "specified by **!commands !decide**."
        embed = discord.Embed(title='Incorrect Usage of !decide', description=response, colour=discord.Colour.red())
        await message.channel.send(embed=embed)

# Parses the custom options from the message content
def parseCustomOptions(content):
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
        return options[2:] # Delete !decide and quotes
    else:
        # Since there are no quotes, parse using spaces
        options = []
        messageArgs = content.split(" ")
        for i in range(2, len(messageArgs)):
            options.append(messageArgs[i])
        return options

# Checks if the number of picks is appropriate for the given options
def checkPicksForCustomOptions(options, count):
    # It is not possible to pick no options a negative amount of options
    if count <= 0:
        return False
    # Cannot pick more than the number of total options
    if count > len(options):
        return False
    return True

# Picks a option from the given list of options
def pickOption(options, count):
    indices = random.sample(range(len(options)), count)
    allOptions = []
    for i in indices:
        allOptions.append(options[i])
    return allOptions

# Checks if the number of picks is appropriate for the given bounds
def checkPicksForNumbers(lowBound, highBound, count):
    # It is not possible to pick no options a negative amount of options
    if count <= 0:
        return False
    # If lowBound and highBound are the same, then only one pick is possible
    if highBound - lowBound == 0 and count > 1:
        return False
    # For integers, the number of picks cannot exceed the number of integers 
    # within the bounds (includes the bounds)
    if type(lowBound) == type(0) and type(highBound) == type(0):
        if count > highBound - lowBound + 1:
            return False
    return True

# Generates a random integer or float between lowBound and highBound
def generateRandNumber(lowBound, highBound, picks):
    # Check if any of the bounds are floats
    numberType = 0 # Float or integer
    if type(lowBound) == type(1.5) or type(highBound) == type(1.5):
        numberType = "float"
    # Depending on the number type generate the random integer or float
    if numberType == "float":
        allNumbers = []
        for _ in range(picks):
            allNumbers.append(random.uniform(lowBound, highBound))
        return allNumbers
    else:
        return random.sample(range(lowBound, highBound + 1), picks)

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
    # Generate string of picked numbers
    pickedStr = ""
    for num in result:
        pickedStr += str(num) + "\n"
    response = "Hello " + message.author.mention + "!\n"
    response += "I have generated **" + str(count) + "** random number(s) between **" + str(lowBound) + "** "
    response += "and **" + str(highBound) + "**.\n\n"
    embed = discord.Embed(title='Decision Results', description=response, colour=discord.Colour.random())
    embed.add_field(name="Chosen Number(s):", value=pickedStr, inline=False)
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
    await message.channel.send(embed=embed)

# Sends a message to the user with the custom option choices
async def sendCustomResults(message, picked, options, count):
    # Generate string of picked options
    pickedStr = ""
    for option in picked:
        pickedStr += str(option) + "\n"
    # Generate string of all options
    optionStr = ""
    for option in options:
        optionStr += str(option) + "\n"
    response = "Hello " + message.author.mention + "!\n"
    response += "I have picked **" + str(count) + "** option(s) from the given options:"
    embed = discord.Embed(title='Decision Results', description=response, colour=discord.Colour.random())
    embed.add_field(name="Chosen Option(s):", value=pickedStr, inline=False)
    embed.add_field(name="All Possible Option(s):", value=optionStr, inline=False)
    embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
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
    picks = 1
    result = generateRandNumber(0, 0, picks)
    if len(result) == 1 and result == [0]:
        passed += 1
    else:
        print("-x- Test 1 Failed")    
    # Test 2: random number generated for two int args
    picks = 1
    result = generateRandNumber(0, 9, picks)
    if len(result) == 1 and result[0] >= 0 and result[0] <= 9 and type(result[0]) == type(3):
        passed += 1
    else:
        print("-x- Test 2 Failed")    
    # Test 3: random float generated for two float args
    picks = 1
    result = generateRandNumber(1.2, 2.4, picks)
    if len(result) == 1 and result[0] >= 1.2 and result[0] <= 2.4 and type(result[0]) == type(3.5):
        passed += 1
    else:
        print("-x- Test 3 Failed")
    # Test 4: random float generated for one float arg and one int arg
    picks = 1
    result = generateRandNumber(1.2, 3, picks)
    if len(result) == 1 and result[0] >= 1.2 and result[0] <= 3.0 and type(result[0]) == type(3.5):
        passed += 1
    else:
        print("-x- Test 4 Failed")
    # Test 5: random float generated for one int arg and one float arg
    picks = 1
    result = generateRandNumber(1, 3.4, picks)
    if len(result) == 1 and result[0] >= 1 and result[0] <= 3.4 and type(result[0]) == type(3.5):
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

    # Unit Tests for function parseCustomOptions()
    print("Testing custom options parsing:")
    print("")
    passed = 0
    # Test 1: check that an message with no options is properly handled
    input = "!decide custom"
    result = parseCustomOptions(input)
    if result == []:
        passed += 1
    else:
        print("-x- Test 1 Failed")
    # Test 2: check parsing for a message containing one option without spaces
    input = "!decide custom one"
    result = parseCustomOptions(input)
    if result == ["one"]:
        passed += 1
    else:
        print("-x- Test 2 Failed")
    # Test 3: check parsing for a message containing one option with spaces
    input = '!decide custom "one option"'
    result = parseCustomOptions(input)
    if result == ["one option"]:
        passed += 1
    else:
        print("-x- Test 3 Failed")
    # Test 4: check parsing for a message containing multiple options without spaces
    input = '!decide custom one two three'
    result = parseCustomOptions(input)
    if result == ["one", "two", "three"]:
        passed += 1
    else:
        print("-x- Test 4 Failed")
    # Test 5: check parsing for a message containing multiple options with spaces
    input = '!decide custom "one option" "two option" "three option"'
    result = parseCustomOptions(input)
    if result == ["one option", "two option", "three option"]:
        passed += 1
    else:
        print("-x- Test 5 Failed")
    # Test 6: check parsing for a message containing one option without spaces and one option with spaces
    input = '!decide custom one "two option"'
    result = parseCustomOptions(input)
    if result == ["one", "two option"]:
        passed += 1
    else:
        print("-x- Test 6 Failed")
    # Test 7: check parsing for a message containing one option with spaces and one option without spaces
    input = '!decide custom "one option" two'
    result = parseCustomOptions(input)
    if result == ["one option", "two"]:
        passed += 1
    else:
        print("-x- Test 7 Failed")
    # Test 8: check parsing for a message containing one option with spaces and two options without spaces
    input = '!decide custom one "two option" three'
    result = parseCustomOptions(input)
    if result == ["one", "two option", "three"]:
        passed += 1
    else:
        print("-x- Test 8 Failed")
    # Test 9: check parsing for a message containing two options with spaces and one option without spaces
    input = '!decide custom "one option" two "three option"'
    result = parseCustomOptions(input)
    if result == ["one option", "two", "three option"]:
        passed += 1
    else:
        print("-x- Test 9 Failed")        
    # Test 10: stress test the parsing capabilities for a message with ten different options
    input = '!decide custom one two three "four option" five six seven "eight option" nine "ten option"'
    result = parseCustomOptions(input)
    if result == ["one", "two", "three", "four option", "five", "six", "seven", "eight option", "nine", "ten option"]:
        passed += 1
    else:
        print("-x- Test 10 Failed")
    # Test 11: check that empty quotes are not added into the options
    input = '!decide custom ""'
    result = parseCustomOptions(input)
    if result == []:
        passed += 1
    else:
        print("-x- Test 11 Failed")
    # Test 12: check that an odd number of quotes defaults to parsing without considering quotes
    input = '!decide custom "one option" "two'
    result = parseCustomOptions(input)
    if result == ['"one', 'option"', '"two']:
        passed += 1
    else:
        print("-x- Test 12 Failed")
    
    print("    Tests Complete for parseCustomOptions()")
    print("    Passed " + str(passed) + "/" + str(12) + " Tests")
    print("")
    # End tests for function parseCustomOptions()

    # Unit Tests for function pickOption()
    print("Testing custom options selection:")
    print("")
    passed = 0
    # Test 1: selection of one option from a set of one custom option
    picks = 1
    input = ["one"]
    result = pickOption(input, picks)
    if len(result) == 1 and result == ["one"]:
        passed += 1
    else:
        print("-x- Test 1 Failed")
    # Test 2: selection of one option from a set of multiple custom options
    picks = 1
    input = ["one", "two", "three"]
    result = pickOption(input, picks)
    possibleOptions = ["one", "two", "three"]
    if len(result) == 1 and result[0] in possibleOptions:
        passed += 1
    else:
        print("-x- Test 2 Failed")
    # Test 3: stress test the selection capabilities for selection of one option from a large set of options
    picks = 1
    input = ["one penny", "two", "three", "four", "five nickel", "six", "seven", "eight", "nine", "ten dime"]
    result = pickOption(input, picks)
    possibleOptions = ["one penny", "two", "three", "four", "five nickel", "six", "seven", "eight", "nine", "ten dime"]
    if len(result) == 1 and result[0] in possibleOptions:
        passed += 1
    else:
        print("-x- Test 3 Failed")
    
    print("    Tests Complete for pickOption()")
    print("    Passed " + str(passed) + "/" + str(3) + " Tests")
    print("")
    # End tests for function pickOption()