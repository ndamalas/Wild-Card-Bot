import string
import discord
import asyncio
import os
import pandas as pd
import random
from command import Command

commandList = []
playerlist = []
classes = ["Enchanter", "Fighter", "Mage", "Marksman", "Assassin", "Tank"]
monsterlist = []
attack = 100
defense = 50
hp = 300
enemiesdf = pd.read_excel('./CS307_RPG_Mobs.xlsx')
itemDf = pd.read_csv('./modules/Items.csv')

index = enemiesdf.index
a_list = list(index)

class character:
    def __init__(self, userID, char_name, classtype):
        self.id = userID
        self.name = char_name
        self.character_class = classtype
        '''if(classtype == "Enchanter"):
            attack = 35
            defense = 10
            hp = 300
        elif(classtype == "Fighter"):
            attack = 55
            defense = 30
            hp = 480
        elif(classtype == "Mage"):
            attack = 50
            defense = 35
            hp = 450
        elif(classtype == "Marksman"):
            attack = 45
            defense = 25
            hp = 350
        elif(classtype == "Tank"):
            attack = 30
            defense = 40
            hp = 550'''
        self.ad = attack
        self.armor = defense
        self.hp = hp
        balance = 50
        self.balance = balance
        self.inventory = []
        self.primary = "None"
        self.secondary = "None"
    def subtract_balance(self, amount):
        self.balance -= amount

#Install this: pip install xlrd
#Install this: pip install openpyxl
class enemy:
    def __init__(self, type):
        temp = enemiesdf.loc[enemiesdf['Monster Name'] == type]
        self.name = temp['Monster Name'].item()
        self.hp = temp['Health Points'].item()
        self.ad = temp['Attack Damage'].item()
        self.armor = temp['Armor'].item()

commandList.append(Command("!rpg", "rpg", "rpg game\nUsage: !rpg help"))
async def rpg(ctx, message):
    global playerlist

    if (len(playerlist) > 0):
        mycharacter = playerlist[0]
    else:
        mycharacter = "True"

    if message.content.split(" ")[1] == "help":
        await help_rpg(ctx, message)

    if message.content.split(" ")[1] == "start":
        await start_rpg(ctx, message)
        await help_rpg(ctx, message)

    if message.content.split(" ")[1] == "myinfo":
        await myinfo_rpg(ctx, message, mycharacter)

    if message.content.split(" ")[1] == "shop":
        await shop_rpg(ctx, message)

    if message.content.split(" ")[1] == "item":
        await item_rpg(ctx, message)

    if message.content.split(" ")[1] == "inventory":
        await inventory_rpg(ctx, message, mycharacter)

    if message.content.split(" ")[1] == "enemies":
        await enemies_rpg(ctx, message)

    if message.content.split(" ")[1] == "buy":
        await buy_rpg(ctx, message, mycharacter)

    if message.content.split(" ")[1] == "sell":
        await sell_rpg(ctx, message, mycharacter)
    if message.content.split(" ")[1] == "dungeonlist":
        await dungeonlist_rpg(ctx, message)

    if message.content.split(" ")[1] == "dungeon":
        if message.content.split(" ")[2] == "Tutorial":
            await tutorial_rpg(ctx, message)
        else:
            await message.channel.send("Sorry that dungeon is not one that is available.")
    # if message.content.split(" ")[1] == "exit":

async def help_rpg(ctx, message):
    embed=discord.Embed(title="RPG Command List and Help\nUsage: !rpg <COMMAND>")
    embed.add_field(name="start", value="Starts a new game. Prompts user for class type and name of character", inline=False)
    embed.add_field(name="myinfo", value="Displays basic user info including character class, user ID, name", inline=False)
    embed.add_field(name="dungeonlist", value="Displays a list of current available dungeons.", inline=False)
    await message.channel.send(embed=embed)

async def myinfo_rpg(ctx, message, mycharacter):
    embed=discord.Embed(title=message.author.display_name)
    mystr = "**Name: **\t" + str(mycharacter.name) + "\n**Class: **\t" + str(mycharacter.character_class) + "\n**User ID: **\t" + str(mycharacter.id) + "\n**Health Points: **\t" + str(mycharacter.hp) + "\n**Attack Damage: **\t" + str(mycharacter.ad) + "\n**Armor: **\t" + str(mycharacter.armor) + "\n**Balance: **\t" + str(mycharacter.balance)
    embed.add_field(name="**Info**", value=mystr, inline=False)
    await message.channel.send(embed=embed)

async def start_rpg(ctx, message):
    await message.channel.send("Starting RPG game")
    embed=discord.Embed(title="Choose your class", color=0xFF99CC)
    embed.add_field(name=":knife: Assassin", value="Assassins specialize in infiltrating enemy lines with their unrivaled mobility to quickly dispatch high-priority targets. Due to their mostly melee nature, Assassins must put them themselves into dangerous positions in order to execute their targets. Luckily, they often have defensive tricks up their sleeves that, if used cleverly, allow them to effectively avoid incoming damage.", inline=False)
    embed.add_field(name=":magic_wand: Enchanter", value="Enchanters focus on amplifying their allies' effectiveness by directly augmenting them and defending them from incoming threats. Enchanters themselves are often quite fragile and bring relatively low damage to the table, meaning they really only shine when grouped together with others.", inline=False)
    embed.add_field(name=":crossed_swords: Fighter", value="Fighters are a diverse group of short-ranged combatants who excel at both dealing and surviving damage. With easy access to heavy, continuous damage and a host of innate defenses, fighters thrive in extended fights as they seek out enemies to take down, but their limited range puts them at constant risk of being kept at bay by their opponents via crowd control, range and mobility.", inline=False)
    embed.add_field(name=":mage: Mage", value="Mages typically possess great reach, ability-based area of effect damage and crowd control, and who use all of these strengths in tandem with each other to trap and destroy enemies from a distance. Specializing in magic damage, often burst damage, and therefore investing heavily in items that allow them to cast stronger and faster spells, mages excel at chaining their abilities together in powerful combos in order to win fights.", inline=False)
    embed.add_field(name=":bow_and_arrow: Marksman", value="Marksmen are ranged fighters whose power almost exclusively revolves around their base attack stats. Using their reach to land massive continuous damage from a distance, marksmen are capable of taking down even the toughest of opponents when positioned behind the safety of their team.", inline=False)
    embed.add_field(name=":shield: Tank", value="Tanks are tough melee champions who sacrifice damage in exchange for powerful crowd control. While able to engage enemies in combat, a tank's purpose isn't usually to kill opponents; rather, tanks excel at disrupting enemies and diverting focus to themselves, allowing them to lock down specific targets, as well as remove threats from their allies.", inline=False)
    msg = await message.channel.send(content="", embed=embed)
    await msg.add_reaction(u"\U0001F52A")
    await msg.add_reaction(u"\U0001FA84")
    await msg.add_reaction(u"\u2694")
    await msg.add_reaction(u"\U0001F9D9")
    await msg.add_reaction(u"\U0001F3F9")
    await msg.add_reaction(u"\U0001F6E1")
    await asyncio.sleep(4)
    for reaction in ctx.cached_messages[len(ctx.cached_messages) - 1].reactions:
        if reaction.count > 1:
            tempstr1 = "You have chosen the "
            tempstr2 = " class!"
            if reaction.emoji == u"\U0001F52A":
                await message.channel.send(tempstr1 + "Assassin" + tempstr2)
                character_class = "Assassin"
            if reaction.emoji == u"\U0001FA84":
                await message.channel.send(tempstr1 + "Enchanter" + tempstr2)
                character_class = "Enchanter"
            if reaction.emoji == u"\u2694":
                await message.channel.send(tempstr1 + "Fighter" + tempstr2)
                character_class = "Fighter"
            if reaction.emoji == u"\U0001F9D9":
                await message.channel.send(tempstr1 + "Mage" + tempstr2)
                character_class = "Mage"
            if reaction.emoji == u"\U0001F3F9":
                await message.channel.send(tempstr1 + "Marksman" + tempstr2)
                character_class = "Marksman"
            if reaction.emoji == u"\U0001F6E1":
                await message.channel.send(tempstr1 + "Tank" + tempstr2)
                character_class = "Tank"
    await message.channel.send("**Enter a name for your character:**")
    await asyncio.sleep(4)
    charname = ctx.cached_messages[len(ctx.cached_messages) - 1].content
    await message.channel.send("**Character name: **" + charname)
    userID = message.author.id
    new_character = character(userID, charname, character_class)
    playerlist.append(new_character)

async def shop_rpg(ctx, message):
    output_name = ""
    output_class = ""
    output_cost = ""
    embed=discord.Embed(title="Shop")
    if (len(message.content.split(" ")) == 2):
        for idx, item in itemDf.iterrows():
            # output += "{:<40}{:^30}{:>20}".format(item['Item'], item['Recommended'], item['Cost']) + "\n"
            # output += f"{item['Item']:<40}{item['Recommended']:^30}{item['Cost']:>20}"
            output_name += item['Item'] + '\n'
            output_class += item['Recommended'] + '\n'
            output_cost += str(item['Cost']) + '\n'
    else:
        for idx, item in itemDf.iterrows():
            if item['Recommended'] == message.content.split(" ")[2]:
                output_name += item['Item'] + '\n'
                output_class += item['Recommended'] + '\n'
                output_cost += str(item['Cost']) + '\n'
    embed.add_field(name="Name", value=output_name, inline=True)
    embed.add_field(name="Class", value=output_class, inline=True)
    embed.add_field(name="Cost", value=output_cost, inline=True)
    await message.channel.send(embed=embed)

async def item_rpg(ctx, message):
    name = ""
    if len(message.content.split(" ")) < 3:
        await message.channel.send("Enter a valid item name\nUsage: !rpg item <NAME>")
    else:
        for i in range(2, len(message.content.split(" "))):
            name += message.content.split(" ")[i] + " "
        name = name.strip()
        description = ""
        temp_col = ""
        temp_val = ""
        i = 0
        for col in itemDf.columns:
            if i != 0 and i != 10:
                temp_col += col + '\n'
            i += 1
        for idx, item in itemDf.iterrows():
            if item['Item'] == name:
                j = 0
                for col in item:
                    if j == 0:
                        pass
                    elif j == 10:
                        description = col
                    else:
                        temp_val += str(col) + '\n'
                    j += 1
        embed=discord.Embed(title=name, description=description)
        embed.add_field(name="Stat", value=temp_col, inline=True)
        embed.add_field(name="Value", value=temp_val, inline=True)
        await message.channel.send(embed=embed)

async def inventory_rpg(ctx, message, mycharacter):
    title = str(mycharacter.name) + "\'s Inventory"
    output = ""
    if not mycharacter.inventory:
        embed=discord.Embed(title=title, description="Empty")
        await message.channel.send(embed=embed)
        return
    else:
        for item in mycharacter.inventory:
            output += str(item) + "\n"
    embed=discord.Embed(title=title)
    embed.add_field(name="Items", value=output)
    await message.channel.send(embed=embed)

async def enemies_rpg(ctx, message):
    title = "Enemies:"
    embed=discord.Embed(title=title)
    output = ""
    zombie_string = ""
    skeleton_string = ""
    goblin_string = ""
    spider_string = ""
    golem_string = ""
    hellhound_string = ""
    ogre_string = ""
    guardian_string = ""
    dragon_string = ""
    king_string = ""
    Zombie = enemy("Zombie")
    Skeleton = enemy("Skeleton")
    Goblin = enemy("Goblin")
    Spider = enemy("Spiders")
    Golem = enemy("Golem")
    Hellhound = enemy("Hellhounds")
    Ogre = enemy("Ogre")
    Guardian = enemy("Guardian")
    Dragon = enemy("Dragon")
    King = enemy("The Ruined King")
    if len(message.content.split(" ")) == 2:
        #print("Length is 2")
        zombie_string += "Name: " + Zombie.name + "\nHealth Points: " + str(Zombie.hp) + "\nAttack Damage: " + str(Zombie.ad) + "\nArmor: " + str(Zombie.armor)
        embed.add_field(name="Zombie", value=zombie_string, inline=False)
        skeleton_string += "Name: " + Skeleton.name + "\nHealth Points: " + str(Skeleton.hp) + "\nAttack Damage: " + str(Skeleton.ad) + "\nArmor: " + str(Skeleton.armor)
        embed.add_field(name="Skeleton", value=skeleton_string, inline=False)
        goblin_string += "Name: " + Goblin.name + "\nHealth Points: " + str(Goblin.hp) + "\nAttack Damage: " + str(Goblin.ad) + "\nArmor: " + str(Goblin.armor)
        embed.add_field(name="Goblin", value=goblin_string, inline=False)
        spider_string += "Name: " + Spider.name + "\nHealth Points: " + str(Spider.hp) + "\nAttack Damage: " + str(Spider.ad) + "\nArmor: " + str(Spider.armor)
        embed.add_field(name="Spider", value=spider_string, inline=False)
        golem_string += "Name: " + Golem.name + "\nHealth Points: " + str(Golem.hp) + "\nAttack Damage: " + str(Golem.ad) + "\nArmor: " + str(Golem.armor)
        embed.add_field(name="Golem", value=golem_string, inline=False)
        hellhound_string += "Name: " + Hellhound.name + "\nHealth Points: " + str(Hellhound.hp) + "\nAttack Damage: " + str(Hellhound.ad) + "\nArmor: " + str(Hellhound.armor)
        embed.add_field(name="Hellhound", value=hellhound_string, inline=False)
        ogre_string += "Name: " + Ogre.name + "\nHealth Points: " + str(Ogre.hp) + "\nAttack Damage: " + str(Ogre.ad) + "\nArmor: " + str(Ogre.armor)
        embed.add_field(name="Ogre", value=ogre_string, inline=False)
        guardian_string += "Name: " + Guardian.name + "\nHealth Points: " + str(Guardian.hp) + "\nAttack Damage: " + str(Guardian.ad) + "\nArmor: " + str(Guardian.armor)
        embed.add_field(name="Guardian", value=guardian_string, inline=False)
        dragon_string += "Name: " + Dragon.name + "\nHealth Points: " + str(Dragon.hp) + "\nAttack Damage: " + str(Dragon.ad) + "\nArmor: " + str(Dragon.armor)
        embed.add_field(name="Dragon", value=ogre_string, inline=False)
        king_string += "Name: " + King.name + "\nHealth Points: " + str(King.hp) + "\nAttack Damage: " + str(King.ad) + "\nArmor: " + str(King.armor)
        embed.add_field(name="The Ruined King", value=king_string, inline=False)
    elif len(message.content.split(" ")) == 3:
        #("Length is 3")
        if message.content.split(" ")[2] == "Zombie":
            zombie_string += "Name: " + Zombie.name + "\nHealth Points: " + str(Zombie.hp) + "\nAttack Damage: " + str(Zombie.ad) + "\nArmor: " + str(Zombie.armor)
            embed.add_field(name="Zombie", value=zombie_string, inline=False)
        elif message.content.split(" ")[2] == "Skeleton":
            skeleton_string += "Name: " + Skeleton.name + "\nHealth Points: " + str(Skeleton.hp) + "\nAttack Damage: " + str(Skeleton.ad) + "\nArmor: " + str(Skeleton.armor)
            embed.add_field(name="Skeleton", value=skeleton_string, inline=False)
        elif message.content.split(" ")[2] == "Goblin":
            goblin_string += "Name: " + Goblin.name + "\nHealth Points: " + str(Goblin.hp) + "\nAttack Damage: " + str(Goblin.ad) + "\nArmor: " + str(Goblin.armor)
            embed.add_field(name="Goblin", value=goblin_string, inline=False)
        elif message.content.split(" ")[2] == "Spider":
            spider_string += "Name: " + Spider.name + "\nHealth Points: " + str(Spider.hp) + "\nAttack Damage: " + str(Spider.ad) + "\nArmor: " + str(Spider.armor)
            embed.add_field(name="Spider", value=spider_string, inline=False)
        elif message.content.split(" ")[2] == "Golem":
            golem_string += "Name: " + Golem.name + "\nHealth Points: " + str(Golem.hp) + "\nAttack Damage: " + str(Golem.ad) + "\nArmor: " + str(Golem.armor)
            embed.add_field(name="Golem", value=golem_string, inline=False)
        elif message.content.split(" ")[2] == "Hellhound":
            hellhound_string += "Name: " + Hellhound.name + "\nHealth Points: " + str(Hellhound.hp) + "\nAttack Damage: " + str(Hellhound.ad) + "\nArmor: " + str(Hellhound.armor)
            embed.add_field(name="Hellhound", value=hellhound_string, inline=False)
        elif message.content.split(" ")[2] == "Ogre":
            ogre_string += "Name: " + Ogre.name + "\nHealth Points: " + str(Ogre.hp) + "\nAttack Damage: " + str(Ogre.ad) + "\nArmor: " + str(Ogre.armor)
            embed.add_field(name="Ogre", value=ogre_string, inline=False)
        elif message.content.split(" ")[2] == "Guardian":
            guardian_string += "Name: " + Guardian.name + "\nHealth Points: " + str(Guardian.hp) + "\nAttack Damage: " + str(Guardian.ad) + "\nArmor: " + str(Guardian.armor)
            embed.add_field(name="Guardian", value=guardian_string, inline=False)
        elif message.content.split(" ")[2] == "Dragon":
            dragon_string += "Name: " + Dragon.name + "\nHealth Points: " + str(Dragon.hp) + "\nAttack Damage: " + str(Dragon.ad) + "\nArmor: " + str(Dragon.armor)
            embed.add_field(name="Dragon", value=dragon_string, inline=False)
        elif message.content.split(" ")[2] == "TheRuinedKing":
            king_string += "Name: " + King.name + "\nHealth Points: " + str(King.hp) + "\nAttack Damage: " + str(King.ad) + "\nArmor: " + str(King.armor)
            embed.add_field(name="The Ruined King", value=king_string, inline=False)
        elif message.content.split(" ")[2] == "Common":
            zombie_string += "Name: " + Zombie.name + "\nHealth Points: " + str(Zombie.hp) + "\nAttack Damage: " + str(Zombie.ad) + "\nArmor: " + str(Zombie.armor)
            embed.add_field(name="Zombie", value=zombie_string, inline=False)
            skeleton_string += "Name: " + Skeleton.name + "\nHealth Points: " + str(Skeleton.hp) + "\nAttack Damage: " + str(Skeleton.ad) + "\nArmor: " + str(Skeleton.armor)
            embed.add_field(name="Skeleton", value=skeleton_string, inline=False)
            goblin_string += "Name: " + Goblin.name + "\nHealth Points: " + str(Goblin.hp) + "\nAttack Damage: " + str(Goblin.ad) + "\nArmor: " + str(Goblin.armor)
            embed.add_field(name="Goblin", value=goblin_string, inline=False)
            spider_string += "Name: " + Spider.name + "\nHealth Points: " + str(Spider.hp) + "\nAttack Damage: " + str(Spider.ad) + "\nArmor: " + str(Spider.armor)
            embed.add_field(name="Spider", value=spider_string, inline=False)
        elif message.content.split(" ")[2] == "Rare":
            golem_string += "Name: " + Golem.name + "\nHealth Points: " + str(Golem.hp) + "\nAttack Damage: " + str(Golem.ad) + "\nArmor: " + str(Golem.armor)
            embed.add_field(name="Golem", value=golem_string, inline=False)
            hellhound_string += "Name: " + Hellhound.name + "\nHealth Points: " + str(Hellhound.hp) + "\nAttack Damage: " + str(Hellhound.ad) + "\nArmor: " + str(Hellhound.armor)
            embed.add_field(name="Hellhound", value=hellhound_string, inline=False)
            ogre_string += "Name: " + Ogre.name + "\nHealth Points: " + str(Ogre.hp) + "\nAttack Damage: " + str(Ogre.ad) + "\nArmor: " + str(Ogre.armor)
            embed.add_field(name="Ogre", value=ogre_string, inline=False)
        elif message.content.split(" ")[2] == "Epic":
            guardian_string += "Name: " + Guardian.name + "\nHealth Points: " + str(Guardian.hp) + "\nAttack Damage: " + str(Guardian.ad) + "\nArmor: " + str(Guardian.armor)
            embed.add_field(name="Guardian", value=guardian_string, inline=False)
            dragon_string += "Name: " + Dragon.name + "\nHealth Points: " + str(Dragon.hp) + "\nAttack Damage: " + str(Dragon.ad) + "\nArmor: " + str(Dragon.armor)
            embed.add_field(name="Dragon", value=dragon_string, inline=False)
        elif message.content.split(" ")[2] == "Legendary":
            king_string += "Name: " + King.name + "\nHealth Points: " + str(King.hp) + "\nAttack Damage: " + str(King.ad) + "\nArmor: " + str(King.armor)
            embed.add_field(name="The Ruined King", value=king_string, inline=False)
        else:
            await message.channel.send(">>> Arguments invalid")
            return
    else:
        await message.channel.send(">>> Arguments invalid")
        return
    await message.channel.send(embed=embed)
async def buy_rpg(ctx, message, mycharacter):
    item = ""
    for i in range(2, len(message.content.split(" "))):
        item += message.content.split(" ")[i] + " "
    item_name = item.strip()
    cost = 0
    for idx, item in itemDf.iterrows():
        if item['Item'] == item_name:
            cost = item['Cost']
    if playerlist[0].balance < cost:
        embed=discord.Embed(title="Purchase fail", description="You do not have enough to buy this item")
        await message.channel.send(embed=embed)
    else:
        playerlist[0].subtract_balance(cost)
        mycharacter.inventory.append(item_name)
        temp_str = item_name + " has been added to your inventory"
        embed=discord.Embed(title="Purchase success", description=temp_str)
        await message.channel.send(embed=embed)
async def sell_rpg(ctx, message, mycharacter):
    item = ""
    for i in range(2, len(message.content.split(" "))):
        item += message.content.split(" ")[i] + " "
    item_name = item.strip()
    if not mycharacter.inventory:
        embed=discord.Embed(title="Cannot sell item", description="Your inventory is empty")
        await message.channel.send(embed=embed)
        return
    i = 0
    for item in mycharacter.inventory:
        if item == item_name:
            cost = 0
            for idx, item in itemDf.iterrows():
                if item['Item'] == item_name:
                    cost = item['Cost']
            title = "Sold " + item_name
            mycharacter.balance += cost
            del mycharacter.inventory[i]
            #try:
            #    mycharacter.inventory.remove(item)
            #except ValueError as e:
            #    pass
            description = str(cost) + " has been added to your balance"
            embed=discord.Embed(title=title, description=description)
            await message.channel.send(embed=embed)
            return
        i += 1
    embed=discord.Embed(title="Cannot sell item", description="You don't own this item")
    await message.channel.send(embed=embed)
async def dungeonlist_rpg(ctx, message):
    embed=discord.Embed(title="Dungeon List", description = "Tutorial")
    await message.channel.send(embed=embed)
async def tutorial_rpg(ctx, message):
    #Introduction
    await message.channel.send("Welcome " + playerlist[0].name + " to the RPG Tutorial!\n")
    await message.channel.send("This is the tutorial dungeon. Each dungeon is divided into 3 floors in which players will fight monsters to earn gold and glory.\n")
    await message.channel.send("The monster on the floors will increase in difficulty and strength as you progress. Once all 3 floors of the dungeon have been cleared you will have cleared the dungeon and can move on to other dungeons.\n")
    await message.channel.send("Good luck!\n")
    #For loop for each floor
    for i in range(3):
        #List of monsters on that floor
        floormonsterlist = []
        if (i == 0):
            #Randomize one monster for the first floor (weak, common monsters)
            await message.channel.send("Floor 1")
            r1 = random.randint(0,3)
            if(r1 == 0):
                enemy0 = enemy("Zombie")
                floormonsterlist.append(enemy0)
            elif(r1 == 1):
                enemy1 = enemy("Skeleton")
                floormonsterlist.append(enemy1)
            elif(r1 == 2):
                enemy2 = enemy("Goblin")
                floormonsterlist.append(enemy2)
            elif(r1 == 3):
                enemy3 = enemy("Spiders")
                floormonsterlist.append(enemy3)
            #Dungeon message
            await message.channel.send("\nYou enter the dungeon and are approached by a " + floormonsterlist[0].name + ".")
            #Show enemy stats
            await enemy_stats_rpg(ctx, message, floormonsterlist)
            #Show your stats
            await player_stats_rpg(ctx, message)
        elif (i == 1):
            #Randomize multiple monsters for the second floor (weaker, common monsters)
            await message.channel.send("Floor 2")
            for i in range(2):
                r2 = random.randint(0,3)
                if(r2 == 0):
                    enemy0 = enemy("Zombie")
                    floormonsterlist.append(enemy0)
                elif(r2 == 1):
                    enemy1 = enemy("Skeleton")
                    floormonsterlist.append(enemy1)
                elif(r2 == 2):
                    enemy2 = enemy("Goblin")
                    floormonsterlist.append(enemy2)
                elif(r2 == 3):
                    enemy3 = enemy("Spiders")
                    floormonsterlist.append(enemy3)
            await message.channel.send("\nOn the second floor of the dungeon you encounter a " + floormonsterlist[0].name + " and " + floormonsterlist[1].name + ".")
            #Show enemy stats
            await enemy_stats_rpg(ctx, message, floormonsterlist)
            #Show your stats
            await player_stats_rpg(ctx, message)
        elif (i == 2):
            #Randomize multiple monsters for the second floor (weaker, common monsters)
            await message.channel.send("Floor 3: Boss Battle!")
            r3 = random.randint(0,2)
            if(r3 == 0):
                enemy0 = enemy("Golem")
                floormonsterlist.append(enemy0)
            elif(r2 == 1):
                enemy1 = enemy("Hellhounds")
                floormonsterlist.append(enemy1)
            elif(r2 == 2):
                enemy2 = enemy("Ogre")
                floormonsterlist.append(enemy2)
            await message.channel.send("\nYou approach the final floor the boss battle is with a huge " + floormonsterlist[0].name + "!")
            #Show enemy stats
            await enemy_stats_rpg(ctx, message, floormonsterlist)
            #Show your stats
            await player_stats_rpg(ctx, message)
        #This is for temporary defense
        choseDefense = False
        #While you are still fighting enemies
        while(len(floormonsterlist) > 0):
            #Shows the combat options
            await combat_options_rpg(ctx, message)
            #Waits for user to enter an option
            def check(m):
                messageval = ""
                if (m.content == "!rpg combat Attack"):
                    messageval = "!rpg combat Attack"
                elif (m.content == "!rpg combat Defend"):
                    messageval = "!rpg combat Defend"
                elif (m.content == "!rpg combat Heal"):
                    messageval = "!rpg combat UseItem"
                elif (m.content == "!rpg combat UseItem"):
                    messageval = "!rpg combat UseItem"
                elif (m.content == "!rpg combat Flee"):
                    messageval = "!rpg combat Flee"
                else:
                    messageval = "!rpg combat invalid"
                return m.content == messageval and m.channel == message.channel
            #Passes the option to the combat_choice option
            msg = await ctx.wait_for("message", check=check)
            await combat_choice_rpg(ctx, msg, floormonsterlist, choseDefense)
            if (len(floormonsterlist) > 0 and (playerlist[0].hp > 0)):
                #Shows the embed of the monster's stats
                await enemy_stats_rpg(ctx, message, floormonsterlist)
                #Show embed of your stats
                await player_stats_rpg(ctx, message)
                #Monster attack phase
                await monsterphase_rpg(ctx, message, floormonsterlist, choseDefense)
                #Shows the embed of the monster's stats
                await enemy_stats_rpg(ctx, message, floormonsterlist)
                #Show embed of your stats
                await player_stats_rpg(ctx, message)
            elif (playerlist[0].hp == 0):
                await message.channel.send("You have died trying to clear the first floor of the Tutorial.")
                await message.channel.send("All of the gold earned on this floor will be lost, but your progress will be saved.")
                await message.channel.send("Better luck next time.")
                return
        if (i == 0):
            await message.channel.send("Congratulations you have cleared the first floor!")
        if (i == 1):
            await message.channel.send("Congratulations you have cleared the second floor!")
        if (i == 2):
            await message.channel.send("Congratulations you have cleared the third floor and completed the tutorial!")
            await message.channel.send("Your character will return to full Hp and Armor upon leaving.")
            playerlist[0].armor = defense
            playerlist[0].hp = hp
            await message.channel.send("Here are your rewards: +350 gold")
            playerlist[0].balance += 350


async def enemy_stats_rpg(ctx, message, floormonsterlist):
    #Shows the embed of the monster's stats
    description = ""
    for i in range(len(floormonsterlist)):
        description += "Monster Name: " + floormonsterlist[i].name + "\nHealth Points: " + str(floormonsterlist[i].hp) + "\nAttack Damage: " + str(floormonsterlist[i].ad) + "\nArmor: " + str(floormonsterlist[i].armor) + "\n"
    whileembed=discord.Embed(title="Enemies", description=description)
    await message.channel.send(embed=whileembed)
async def player_stats_rpg(ctx, message):
    #Show your stats
    player_description = "Player Name: " + playerlist[0].name + "\nHealth Points: " + str(playerlist[0].hp) + "\nAttack Damage: " + str(playerlist[0].ad) + "\nArmor: " + str(playerlist[0].armor) + "\n"
    player_embed=discord.Embed(title="Your Stats", description=player_description)
    await message.channel.send(embed=player_embed)
async def combat_options_rpg(ctx, message):
    embed=discord.Embed(title="Combat Options")
    embed.add_field(name="Attack", value="Deal " + str(playerlist[0].ad) + " to one monster.", inline=False)
    embed.add_field(name="Defend", value="Increase your defense stats by 10 for one turn which would make your defense: " + str(playerlist[0].armor + 10) + ".", inline=False)
    if (playerlist[0].character_class == "Enchanter"):
        embed.add_field(name="Heal", value="Heal yourself for 100 Health", inline=False)
    else:
        embed.add_field(name="UseItem", value="Use an item from your inventory to grant you stats.", inline=False)
    embed.add_field(name="Flee", value="Save your progress and leave the dungeon to return for another time")
    embed.add_field(name="How to Use", value="In order to use these commands options please type: !rpg combat <OPTION>", inline=False)
    await message.channel.send(embed=embed)
async def combat_choice_rpg(ctx, message, floormonsterlist, choseDefense):
    if(message.content.split(" ")[2] == "Attack"):
        #Targets the first monster
        await message.channel.send("You chose to attack.")
        await message.channel.send("The player attacks " + floormonsterlist[0].name)
        if(playerlist[0].ad >= floormonsterlist[0].armor):
            difference = floormonsterlist[0].armor - playerlist[0].ad
            if (floormonsterlist[0].armor != 0):
                await message.channel.send(floormonsterlist[0].name + "'s armor has been reduced to 0!")
            floormonsterlist[0].armor = 0
            floormonsterlist[0].hp += difference
            if (difference != 0):
                await message.channel.send(floormonsterlist[0].name + " took " + str(-difference) + " damage!")

        else:
            floormonsterlist[0].armor -= playerlist[0].ad
            await message.channel.send(floormonsterlist[0].name + "'s armor has been reduced by " + str(playerlist[0].ad) + "!")

        if(floormonsterlist[0].hp <= 0):
            await message.channel.send("You killed: " + floormonsterlist[0].name)
            floormonsterlist.remove(floormonsterlist[0])
            await message.channel.send("Floormonsterlist length: " + (str(len(floormonsterlist))))
    elif(message.content.split(" ")[2] == "Defend"):
        #Raises your Armor by 10 for one turn
        await message.channel.send("You choose to defend.")
        playerlist[0].armor += 10
        await message.channel.send("You take a defensive stance. Your armor is raised by 10. You now have " + str(playerlist[0].armor) + "armor.")
        choseDefense = True
    else:
        await message.channel.send("Work in progress.")
async def monsterphase_rpg(ctx, message, floormonsterlist, choseDefense):
    #Right now all monsters do is attack the player
    #You could implement options to defend, heal, apply cc or like make it more complicated for the boss monster/s
    for i in range(len(floormonsterlist)):
        await message.channel.send(floormonsterlist[i].name + " chooses to attack the player!")
        await message.channel.send(floormonsterlist[i].name + " does " + str(floormonsterlist[i].ad) + " to the player!")
        if(floormonsterlist[i].ad >= playerlist[0].armor):
            difference = playerlist[0].armor - floormonsterlist[i].ad
            if (floormonsterlist[0].armor != 0):
                await message.channel.send(playerlist[0].name + "'s armor has been reduced to 0!")
            playerlist[0].armor = 0
            playerlist[0].hp += difference
            if (difference != 0):
                await message.channel.send(playerlist[0].name + " took " + str(-difference) + "damage!")
            if (playerlist[0].hp <= 0):
                await message.channel.send("You have been killed by: " + floormonsterlist[i])
                playerlist[0].hp = 0

        else:
            playerlist[0].armor -= floormonsterlist[i].ad
            if(choseDefense == True):
                if (floormonsterlist[i].ad < 10):
                    difference = 10 - floormonsterlist[i].ad
                    playerlist[0].armor -= difference
                choseDefense = False
            await message.channel.send(playerlist[0].name + "'s armor has been reduced by " + str(floormonsterlist[i].ad) + "!")
