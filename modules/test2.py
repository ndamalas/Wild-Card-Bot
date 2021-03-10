from command import Command

#Function to test sending data to external commands

# Every module has to have a command list
commandList = []

#function accepts the client and message
#needs to be async
#Since we can pass client and message we can have these functions do anything
commandList.append(Command("!collide1", "func", "Function tests sending data to external commands."))
async def func(client, message):
	response = 'You said (Testing testing): {}'.format(' '.join(message.content.split()[1:]))
	await message.channel.send(response)

commandList.append(Command("!collide2", "func", "Function tests sending data to external commands."))
