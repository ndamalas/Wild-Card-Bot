import string
import discord
import asyncio
import os
import pandas as pd
from command import Command

commandList = []
playerlist = []
classes = ["Enchanter", "Fighter", "Mage", "Marksman", "Assassin", "Tank"]
monsterlist = []
balance = 50
enemiesdf = pd.read_excel('./CS307_RPG_Mobs.xlsx')
itemDf = pd.read_csv('./modules/Items.csv')

index = enemiesdf.index
a_list = list(index)

class character:
    def __init__(self, userID, char_name, classtype):
        self.id = userID
        self.name = char_name
        self.character_class = classtype
        balance = 50
        self._balance = balance
        self.inventory = []
        self.primary = "None"
        self.secondary = "None"
    def subtract_balance(self, amount):
        self._balance -= amount

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
    # if message.content.split(" ")[1] == "exit":

async def help_rpg(ctx, message):
    embed=discord.Embed(title="RPG Command List and Help\nUsage: !rpg <COMMAND>")
    embed.add_field(name="start", value="Starts a new game. Prompts user for class type and name of character", inline=False)
    embed.add_field(name="myinfo", value="Displays basic user info including character class, user ID, name", inline=False)
    await message.channel.send(embed=embed)

async def myinfo_rpg(ctx, message, mycharacter):
    global balance
    embed=discord.Embed(title=message.author.display_name)
    mystr = "**Name: **\t" + str(mycharacter.id) + "\n**Class: **\t" + str(mycharacter.character_class) + "\n**User ID: **\t" + str(mycharacter.name) + "\n**Balance: **\t" + str(balance)
    embed.add_field(name="**Info**", value=mystr, inline=False)
    await message.channel.send(embed=embed)

async def start_rpg(ctx, message):
    global balance
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
    balance = 50
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
            name += message.content.split(" ")[i]
        name = name.title()
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
    embed=discord.Embed(title=title)
    output = ""
    for item in mycharacter.inventory:
        output += str(item) + "\n"
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
    global balance
    item = ""
    for i in range(2, len(message.content.split(" "))):
        item += message.content.split(" ")[i]
    item_name = item.title()
    cost = 0
    for idx, item in itemDf.iterrows():
        if item['Item'] == item_name:
            cost = item['Cost']
    if balance < cost:
        embed=discord.Embed(title="Purchase fail", description="You do not have enough to buy this item")
        await message.channel.send(embed=embed)
    else:
        playerlist[0].subtract_balance(cost)
        balance -= cost
        mycharacter.inventory.append(item_name)
        temp_str = item_name + " has been added to your inventory"
        embed=discord.Embed(title="Purchase success", description=temp_str)
        await message.channel.send(embed=embed)