# Wild-Card-Bot
## Setting up for development
Run the following commands to make sure you have the required libraries (requires pip/pip3)
```
pip3 install -U discord.py
pip3 install -U python-dotenv
pip3 install -U importlib
pip3 install -U beautifulsoup4
pip3 install -U google
pip3 install -U youtube_dl
pip3 install -U youtube-search-python
pip3 install -U riotwatcher
pip3 install -U pandas
pip3 install -U aiohttp
pip3 install -U pokepy
```

You will also need to install ffmpeg from https://ffmpeg.org/download.html


## Making changes
**Do all testing in a branch until the changes are ready for production**

**REMEMBER: Always fetch then pull before each time you start working in case someone else has made changes!!!**

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

And then delete the branch when you're done with it using
```
git branch -d localBranchName
git push origin --delete remoteBranchName
```

## Writing Commands (Standard Format)
To make commands in external files, follow the following format:

Start each file with:

```python
# import the command class and Discord library
from command import Command
import discord

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

# Example Command and Function: command is !example, and the function name is exampleFunction
# Add the command to the command list, with the first argument being the command users will use and the second being the name of the function that will be called
commandList.append(Command("!example", "exampleFunction"))
```

Take a look at serverAdministrator.py to see another example of how it works!

## Setting up the bot
* Download all required dependencies
* Go to the discord developer portal: https://discord.com/developers/
* Create a new app with "New Application"

In the OAuth2 page:
* In the scopes box click "bot" and then select "Administrator" in bot permissions.
* copy the link provided to add the bot to your server

In the Bot page:
* Click copy to copy your bot authorization token
* Enable presence intent and server members intent

In the Wild-Card-Bot directory create a new file called ".env" and inside it put:
`TOKEN = TheTokenYouCopied`

The bot is now ready to run!



## Running the bot
After following the setup, you can run the bot by simply using `python3 main.py`
