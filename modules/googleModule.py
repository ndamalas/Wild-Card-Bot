from command import Command
from googlesearch import search 


#Function to test sending data to external commands

# Every module has to have a command list
commandList = []

commandList.append(Command("!google", "googleSearch", "TODO"))
async def googleSearch(client, message):
    contents = message.split(" ")
    if len(contents) > 1:
        # to search 
        query = ""
        for i in range(1, len(contents)):
            query += contents[i]

        for j in search(query, tld="co.in", num=10, stop=10, pause=2): 
            print(j)
# Search command to give hyperlinks
