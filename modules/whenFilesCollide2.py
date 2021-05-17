from command import Command

#File to have colliding command to show what happens when collisions happen

# Every module has to have a command list


commandList = []
commandList.append(Command("!fixcollide1", "func", "Just a useless function for testing."))
async def func(client, message):
    response = 'In collide'
    await message.channel.send(response)

commandList.append(Command("!fixcollide2", "func", "Just a useless function for testing."))
    