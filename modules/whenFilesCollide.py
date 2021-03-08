from command import Command

#File to have colliding command to show what happens when collisions happen

# Every module has to have a command list


commandList = []
commandList.append(Command("!collide1", "func"))
async def func(client, message):
    response = 'In collide'
    await message.channel.send(response)

commandList.append(Command("!collide2", "func"))
    