from command import Command

import discord

# Module that displays information for developers

# Every module has to have a command list
commandList = []

# This function is for developers to learn about the bot
# Currently unfinished
commandList.append(Command("!developer", "developerInfo", "Command that displays useful information for Discord developers."))
async def developerInfo(client, message):
    if len(message.content.split(" ")) >= 2:
        section = message.content.split(" ")[1]
        if section == "format" or section == "python":
            response = 'The format for your python module is as follows:\n'
            response += 'Required:\n'
            response += '```from command import Command\n'
            response += 'commandList = []\n```'
            response += 'commandList will hold all the Command objects that you create in your module.\n\n'
            response += 'Once you have the required syntax, here is how to add a command:\n'
            response += '```commandList.append(Command(<command_name>, <command_function>))```\n'
            response += '<command_name> refers to the name of your command such as !example and\n'
            response += '<command_function> refers to the name of the function that implements your command.\n\n'
            response += 'This function will need to have two parameters, client and message.\n'
            response += 'message: the message sent by the user with your command'
            embed = discord.Embed(title='Developer: Python Format', description=response, colour=discord.Colour.purple())
            await message.channel.send(embed=embed)
        elif section == "languages":
            response = 'Currently Wild Card Bot fully supports the following languages:\n'
            response += 'Python\n\n'
            response += 'Wild Card Bot also supports the following languages with limited functionality:\n'
            response += 'C++ (Only message based commands, no role or channel manipulations)\n\n'
            response += 'To learn more about the format of modules in a language, use the command !developer <language-name>\n'
            response += 'Note: For C++ please use cpp.'
            embed = discord.Embed(title='Developer: Compatible Languages', description=response, colour=discord.Colour.purple())
            await message.channel.send(embed=embed)
        elif section == "cpp":
            response = 'The format for your c++ module is as follows:\n'
            response += 'Your module must accept command line arguments. Compiled C++ modules are invoked by '
            response += 'cppModuleRunner.py. Use the !cpp command to run your C++ commands.\n\n'
            response += 'Command Line Arguments:\n'
            response += 'argv[1] will be the command name ("!example") and any additional arguments will be '
            response += 'after argv[1] ("!example test" results in argv[1] = "!example" and argv[2] = "test")\n\n'
            response += 'Currently, only message based commands are supported for C++. cppModuleRunner.py will '
            response += 'take the stdout from your program and generate a message with the contents of stdout.\n'
            response += 'Once you have finished coding your module, you must compile it to be used with this bot.\n'
            response += 'More detailed information can be found in the comments of cppModuleRunner.py.'
            embed = discord.Embed(title='Developer: C++ Format', description=response, colour=discord.Colour.purple())
            await message.channel.send(embed=embed)
        else:
            response = 'That section was not found in the manual!\n\n'
            response += 'This manual consists of the following sections:\n'
            response += '1. Module Format\n'
            response += 'Use !developer format to learn more.\n'
            response += '2. Language Support\n'
            response += 'Use !developer languages to learn more.\n'
            embed = discord.Embed(title='Section Not Found', description=response, colour=discord.Colour.purple())
            await message.channel.send(embed=embed)
    else:
        response = 'Welcome to the developer manual!\n'
        response += 'Wild Card Bot is a Discord bot that uses a modular function system.\n'
        response += 'This means that you can add your own commands using external modules!\n\n'
        response += 'This manual consists of the following sections:\n'
        response += '1. Module Format\n'
        response += 'Use !developer format to learn more.\n'
        response += '2. Language Support\n'
        response += 'Use !developer languages to learn more.\n'
        embed = discord.Embed(title='Developer Manual', description=response, colour=discord.Colour.purple())
        await message.channel.send(embed=embed)