from command import Command

# Every module has to have a command list
commandList = []

# Example function:
# Just make sure that the function name in a command is the same
# Make sure every function is async and has both client, message as parameters
commandList.append(Command("!example", "exampleFunction"))
async def exampleFunction(client, message):
    response = "This is an example of a function setup."
    await message.channel.send(response)

# Display a list of the all the Users
commandList.append(Command("!users", "displayUsers"))
async def displayUsers(client, message):
    # User List to hold all members in the server
    userList = message.guild.members
    response = ""
    for user in userList:
        if user.display_name == "Wild Card Bot":
            continue
        response += user.display_name + "\nRoles: "
        for role in user.roles:
            response += role.name + ", "
        response += "\n\n"
    await message.channel.send(response)

# Function to fill the userList
"""def fillUserList(client):
    users = []
    for guild in client.guilds:
        for member in guild.members:
            users.append(member)
    return users
"""