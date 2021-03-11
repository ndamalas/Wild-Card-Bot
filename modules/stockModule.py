from command import Command
import discord
import os
import requests
import random
import yfinance as yf


# Every module has to have a command list
commandList = []

usage = "Returns basic stock info given a ticker. Usage: '!stock TICKER'\nAdd the following if you want more information: 'all', volume', 'day' 'short', 'longTerm', 'business', and 'more'"
commandList.append(Command("!stock", "getStock", usage))
async def getStock(client, message):
	#Grab ticker data and pull from API
	tickerName = message.content.split(' ')[1]
	ticker = yf.Ticker(tickerName)
	td = ticker.info

	#grab logo
	logo = td["logo_url"]

	#start response
	response = "```\n"
	longSum = ''
	link = ''
	#grab basic stock data
	currentPrice = td["regularMarketPrice"]
	name = td["shortName"]
	response = response + "{}\nCurrent Price: {}\n".format(name, currentPrice)

	#if there are extra tags, append the desired data
	input_data = message.content.split(' ')
	#allow users to grab all data at once
	allData = "all" in input_data

	if(len(input_data) > 2):

		if("vol" in input_data or "volume" in input_data or allData):
			#Volumes
			volume = td["volume"]
			mktCap = td["marketCap"]
			response = response + "Volume: {}\nMarket Cap: {}\n".format(volume, mktCap)

		if("day" in input_data or "daily" in input_data or allData):
			#Daily info
			dayHigh = td["dayHigh"]
			dayLow = td["dayLow"]
			lastOpen = td["open"]
			lastClose = td["previousClose"]
			response = response + "Daily Info:\n\tHigh: {}\n\tLow: {}\n\tOpen: {}\n\tPrevious Close: {}\n".format(dayHigh, dayLow, lastOpen, lastClose)
		
		if("longTerm" in input_data or allData):
			#LongTerm Data
			yearHigh = td["fiftyTwoWeekHigh"]
			yearLow = td["fiftyTwoWeekLow"]
			fiftyDay = td["fiftyDayAverage"]
			twohundredDay = td["twoHundredDayAverage"]
			response = response + "Long Term Data:\n\t52 Week High: {}\n\t52 Week Low: {}\n\t50 Day Average: {}\n\t200 Day Average: {}\n".format(yearHigh, yearLow, fiftyDay, twohundredDay)

		#greeks
		beta=td["beta"]

		if("short" in input_data or allData):
			#shorts
			shortPerc = td["shortPercentOfFloat"]
			shortPerMonth = td["sharesShortPriorMonth"]
			shortRatio = td["shortRatio"]
			outstanding = td["sharesOutstanding"]
			response = response + "Short Data:\n\tShort Ratio: {}\n\tShort % of Float: {}\n\tShares Outstanding: {}\n\tShares Short Last Month: {}\n".format(shortRatio, shortPerc, outstanding, shortPerMonth)
		
		if("business" in input_data or "company" in input_data or allData):
			#business info
			numEmployees = td["fullTimeEmployees"]
			industry = td["industry"]
			sector = td["sector"]
			address = td["address1"]
			city = td["city"]
			state = td["state"]
			zipCode = td["zip"]
			country = td["country"]
			longSum = td["longBusinessSummary"]
			phone = td["phone"]
			website = td["website"]
			longName = td["longName"]

			response = response +  "Business Information:\n\tName: {}\n\tIndustry and Sector: {}, {}\n\tNumber of Employees: {}\n\tAddress: {}, {} {}, {}, {}\n\tPhone: {}\n\tWebsite: {}\n".format(longName, industry, sector, numEmployees, address, city, state, zipCode, country, phone, website)

			Summary = "```\nBusiness Summary: \n\t{}\n```".format(longSum)

		if("more" in input_data or allData):
			link = "Link for more information: https://www.finance.yahoo.com/quote/{}\n".format(tickerName.upper())

	#Return the logo and data to the user
	await message.channel.send(logo)
	await message.channel.send(response+"\n```")
	#add summary and link as extra so we don't exceed data limits and so link is clickable
	if len(longSum) > 1:
		if len(Summary) > 2000:
			await message.channel.send("Summary is too long to send here, please use 'more' to get the link to view the summary.\n")
		else:
			await message.channel.send(Summary)
	if len(link) > 1:
		await message.channel.send(link)