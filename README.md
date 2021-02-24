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
