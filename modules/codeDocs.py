from command import Command
from bs4 import BeautifulSoup
import requests
import discord
from googlesearch import search

##Create command list
commandList = []

##Python stuff
commandList.append(Command("!python", "getPythonInfo", "Gets information from python documentation. Use !python <library>.<method>"))
async def getPythonInfo(client, message):
	#get search term (all words after command)
	terms = message.content.split(' ')
	
	searchURL = "https://www.google.com/search?q=python+{}".format("+".join(terms[1:]))
	html = requests.get(searchURL)

	# #Grab search results page
	# #searchPage = urllib.request.urlopen(searchURL).read()

	soup = BeautifulSoup(html.content, 'html.parser')

	response = soup.find_all('div')[31].get_text()

	embed = discord.Embed(title='Python {}'.format(" ".join(terms[1:])), description=response, colour=discord.Colour.blue())

	await message.channel.send(embed=embed)
	

##java stuff