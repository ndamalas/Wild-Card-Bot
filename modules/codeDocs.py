from command import Command
from bs4 import BeautifulSoup
import requests
import discord
from googlesearch import search

##Create command list
commandList = []

##Python stuff
commandList.append(Command("!python", "getPythonInfo", "Gets information from google about python documentation. Use !python <search term>"))
async def getPythonInfo(client, message):
	#get search term (all words after command)
	terms = message.content.split(' ')
	
	searchURL = "https://www.google.com/search?q=python+{}".format("+".join(terms[1:]))
	
	#get search results
	html = requests.get(searchURL)

	#parse results
	soup = BeautifulSoup(html.content, 'html.parser')

	#get text of first google result
	response = soup.find_all('div')[31].get_text()

	#Send info to user
	embed = discord.Embed(title='Python {}'.format(" ".join(terms[1:])), description=response, colour=discord.Colour.blue(), url=searchURL)

	await message.channel.send(embed=embed)

##python module search
commandList.append(Command("!pydoc", "getPythonDocs", "Gets information from the python documentation. Use !pydoc <module> <class or method>"))
async def getPythonDocs(client, message):
	#get module and class/method name
	mod = message.content.split(' ')[1]
	item = message.content.split(' ')[2]

	#open module page
	pySearch = "https://docs.python.org/3.9/py-modindex.html"
	pyhtml = requests.get(pySearch)

	soup = BeautifulSoup(pyhtml.content, 'html.parser')

	##Find module
	foundResult = 0
	for x in list(soup.find_all('code')):
		if x.get_text() == mod:
			moduleTag = x
			foundResult = 1
			break

	#if not found, tell user
	if not foundResult:
		embed = discord.Embed(title='Python Doc Error', description="Module Not Found!", colour=discord.Colour.red())
		await message.channel.send(embed=embed)

	#else find the item
	else:
		moduleURL = "https://docs.python.org/3.9/" + moduleTag.find_parent('a')['href']
		modSearch = requests.get(moduleURL)

		##Get function content
		soupMod = BeautifulSoup(modSearch.content, 'html.parser')

		foundResult = 0
		for x in list(soupMod.find_all('code')):
			if x.get_text() == item:
				itemTag = x
				foundResult = 1
				break

		#if not found, tell user, otherwise display the info
		if not foundResult:
			embed = discord.Embed(title='Python Doc Error', description="Class/Method Not Found!", colour=discord.Colour.red())
			await message.channel.send(embed=embed)
		else:
			parent = itemTag.find_parent('dt')
			sibling = parent.find_next('dd')
			child = sibling.findChild('p')
			embed = discord.Embed(title='Python {}.{}'.format(mod, item), description=child.get_text(), colour=discord.Colour.blue(), url=moduleURL)
			await message.channel.send(embed=embed)



##java stuff
commandList.append(Command("!java", "getJavaInfo", "Gets information from google on java documentation. Use !java <search term>"))
async def getJavaInfo(client, message):
	#get search term (all words after command)
	terms = message.content.split(' ')
	
	searchURL = "https://www.google.com/search?q=java+{}".format("+".join(terms[1:]))

	#Grab search results page
	html = requests.get(searchURL)

	
	#Parse page
	soup = BeautifulSoup(html.content, 'html.parser')

	#Get text of first google response
	response = soup.find_all('div')[31].get_text()

	#Make and send response
	embed = discord.Embed(title='Java {}'.format(" ".join(terms[1:])), description=response, colour=discord.Colour.blue(), url=searchURL)

	await message.channel.send(embed=embed)

#java doc stuff did not work as the only java docs I could find had js and bs4 does not mesh well with that.