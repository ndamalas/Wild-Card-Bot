from command import Command

#function to test calling external commands

#create variable with keyphrase
prefix = '!external'

# Every module has to have a command list
commandList = []
# Set the module to None, because it will be changed when added to the main
# bot's command list
commandList.append(Command("!test", "func"))
#function accepts the client and message
#needs to be async
#Since we can pass client and message we can have these functions do anything
async def func(client, message):
	response = 'This was executed in an external function!'
	await message.channel.send(response)



commandList.append(Command("!testTest", "testFunc"))
async def testFunc(client, message):
	response = 'TestTest'
	await message.channel.send(response)


