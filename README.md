# Wild-Card-Bot
## Setting up for development
Run the following commands to make sure you have the required libraries (requires pip/pip3)
```
pip3 install -U discord.py
pip3 install -U python-dotenv
pip3 install -U importlib
```

## Making changes
**Do all testing in a branch until the changes are ready for production**

**REMEMBER: Always pull before each time you start working in case someone else has made changes!!!**

Start by checking out a new branch
```
git checkout -b newBranchName
```

Then make your changes and commit them using
```
git commit -am "Commit Message"
```
To push your branch to the github use
```
git push origin newBranchName
```

Once the changes are complete and ready to be put in the main project
```
git checkout main
git merge main newBranchName
git push origin main
```

## Writing Commands (Standard Format)
To make commands in external files, follow the following format:

Start each file with:

``` python
# import the command class
from command import Command

# instantiate the list that will hold all of the commands
commandList = []
```

Then, for each command:

```python
# Follow the following format

# Make sure every function is async and has both client, message as parameters, and that await is used when sending your response
async def exampleFunction(client, message):
    response = "This is an example of a function setup."
    await message.channel.send(response)

#Example Command and Function: command is !example, and the function name is exampleFunction
# Add the command to the command list, with the first argument being the command users will use and the second being the name of the function that will be called
commandList.append(Command("!example", "exampleFunction"))
```

Take a look at serverAdministrator.py to see another example of how it works!
