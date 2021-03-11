from command import Command
import discord
import os
import subprocess

#Function to test sending data to external commands

# Every module has to have a command list
commandList = []

# Command uses !cpp file-name command-name (any arguments)
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
            
    