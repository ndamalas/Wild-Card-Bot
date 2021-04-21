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
enemiesdf = pd.read_excel('./CS307_RPG_Mobs.xlsx')
itemDf = pd.read_csv('./modules/Items.csv')

index = enemiesdf.index
a_list = list(index)

class character:
    def __init__(self, userID, char_name, classtype):
        self.id = userID
        self.name = char_name
        self.character_class = classtype
        self.balance = 0

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

    if message.content.split(" ")[1] == "help":
        await help_rpg(ctx, message)

    if message.content.split(" ")[1] == "start":
        await start_rpg(ctx, message)

    if message.content.split(" ")[1] == "myinfo":
        await myinfo_rpg(ctx, message, mycharacter)

    if message.content.split(" ")[1] == "shop":
            await shop_rpg(ctx, message)

    # if message.content.split(" ")[1] == "exit":

async def help_rpg(ctx, message):
    embed=discord.Embed(title="RPG Command List and Help\nUsage: !rpg <COMMAND>")
    embed.add_field(name="start", value="Starts a new game. Prompts user for class type and name of character", inline=False)
    embed.add_field(name="myinfo", value="Displays basic user info including character class, user ID, name", inline=False)
    await message.channel.send(embed=embed)

async def myinfo_rpg(ctx, message, mycharacter):
    embed=discord.Embed(title=message.author.display_name)
    mystr = "**Name: **\t" + str(mycharacter.id) + "\n**Class: **\t" + str(mycharacter.character_class) + "\n**User ID: **\t" + str(mycharacter.name)
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
    await asyncio.sleep(8)
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
    await asyncio.sleep(8)
    charname = ctx.cached_messages[len(ctx.cached_messages) - 1].content
    await message.channel.send("**Character name: **" + charname)
    userID = message.author.id
    new_character = character(userID, charname, character_class)

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
