from command import Command
import discord
import os
import subprocess

# Module that runs complied c++ programs

# Every module has to have a command list
commandList = []

# IMPORTANT FORMATTING
# Note: Modules written in languages other than Python have very limited functionality. 
# Your cpp file must follow the following format:
# It must accept command line arguments. When this module calls your program,
# argv[1] will be the command name ("!example") and any additional arguments will be
# after argv[1] (for example, "!example test" results in argv[1] = "!example" and argv[2] = "test")

# HOW THIS WORKS
# Upon the user passing the command name and arguments, those strings will be the corresponding command
# line arguments used to run your program.
# This module runner will take the stdout from your program and parse it according.
# If you want to simply send a message consisting of some text, all that is needed is the following:
# std::cout << "text" << std::endl; (where "text" is any text you want)

# DO NOT FORGET TO RECOMPILE YOUR CPP FILE EVERY TIME YOU MAKE MODIFICATIONS!

# Command format: !cpp file-name command-name (any arguments)
# How to use this module runner:
# First compile the .cpp code into a .exe file
# Add the .exe file to the modules folder
# Use the above command format to the cpp module (Example: !cpp cppTest !cppTest)
commandList.append(Command("!cpp", "cppRunner", "Runs a module that uses cpp. Format: !cpp file-name command-name (any arguments)"))
async def cppRunner(client, message):
    if len(message.content.split(" ")) < 3:
        response = "Incorrect usage! Check !help for usage info."
        embed = discord.Embed(title='!cpp Incorrect Usage', description=response, colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return
    # Extract file name and command name
    fileName = message.content.split(" ")[1]
    if fileName.endswith(".exe") == False:
        fileName += ".exe"
    commandName = message.content.split(" ")[2]
    for nativeFile in os.listdir("modules"):
        if nativeFile == fileName:
            # Important security consideration: Always use run with parameter shell=False, which is done
            # by default. Not doing so allows for shell injection.
            result = subprocess.run(["./modules/" + fileName, commandName], capture_output=True, text=True)
            output = result.stdout

            # Send the output recieved from the program via a message
            embed = discord.Embed(title= commandName + " Output", description=output, colour=discord.Colour.gold())
            await message.channel.send(embed=embed)   