#create variable with keyphrase
prefix = '!external'

#function accepts the client and message
#needs to be async
#Since we can pass client and message we can have these functions do anything
async def func(client, message):
	response = 'This was executed in an external function!'
	await message.channel.send(response)


