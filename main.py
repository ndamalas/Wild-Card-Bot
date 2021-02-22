import os

import discord
from dotenv import load_dotenv

#loads in Discord API token
load_dotenv()
TOKEN = os.getenv('TOKEN')

#Connect to discord client
client = discord.Client()

#When the bot is ready it will print to console
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

#When a user sends a message, checks the contents and responds if containing the command
@client.event
async def on_message(message):
	if message.author == client.user:
		return
	if message.content == '!test':
		response = "Test successful!"
		await message.channel.send(response)

#Run the bot
client.run(TOKEN)