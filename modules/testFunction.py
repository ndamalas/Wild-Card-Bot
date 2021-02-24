from command import Command

#function to test calling external commands

#create variable with keyphrase
prefix = '!external'

# Every module has to have a command list
commandList = []
# Set the module to None, because it will be changed when added to the main
# bot's command list
testCommand = Command("test", "func", None)
commandList.append(testCommand)
#function accepts the client and message
#needs to be async
#Since we can pass client and message we can have these functions do anything
async def func(client, message):
	response = 'This was executed in an external function!'
	await message.channel.send(response)


