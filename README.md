# Wild-Card-Bot
## Setting up for development
Run the following commands to make sure you have the required libraries (requires pip/pip3)
```
pip3 install -U discord.py
pip3 install -U python-dotenv
```

## Making changes
**Do all testing in your local branch until the changes are ready for production**

Start by checking out a new branch
```
git checkout -b newBranchName
```

Then make your changes and commit them using
```
git commit -am "Commit Message"
```


Once the changes are complete and work correctly
```
git checkout main
git merge main newBranchName
git push origin main
```