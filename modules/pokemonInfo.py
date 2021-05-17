from command import Command
import discord
import requests
import pokepy
import json

##Create command list
commandList = []

#load pokepy client to access api
pClient = pokepy.V2Client()

commandList.append(Command("!poke", "getPokemon", "Grabs basic information about a requested pokemon, just use !poke <name or number>"))
async def getPokemon(client, message):
    #get the search term (either name or number)
    searchTerm = message.content.split(' ')[1]
    #Grab the pokemon data from the api
    try:
        currPoke = pClient.get_pokemon(searchTerm)
    except:
        embed = discord.Embed(title="Pokedex Error!", description="There was an error getting the requested Pokemon. Perhaps the number is invalid or the name is misspelled!", colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return
    #Create response
    response = "```Name: {}\nType(s): {}\nAbilities: {}\nStats:\n{}\n```".format(getName(currPoke), getTypes(currPoke), getAbilities(currPoke), getStats(currPoke))
    embed = discord.Embed(title="Pokedex Entry: {}".format(getName(currPoke)), description=response, colour=discord.Colour.red())
    embed.set_thumbnail(url=getSprite(currPoke))
    await message.channel.send(embed=embed)

commandList.append(Command("!item", "getItem", "Grabs basic information about a requested pokemon item. Use '!item held <item>' to see what pokemon can hold that item naturally."))
async def getItem(client, message):
    #get the search term
    terms = message.content.split(' ')
    heldSearch = 0

    #flag for held items
    if terms[1].lower() == 'held':
        terms = terms[1:]
        heldSearch = 1

    #Check if there is input
    if len(terms) == 1:
        embed = discord.Embed(title="Input Error!", description="No search term provided!", colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return
    searchTerm = formatInput(terms[1:])

    #Grab item data from api
    try:
        currItem = pClient.get_item(searchTerm)
    except:
        embed = discord.Embed(title="Item Error!", description="Item not found!", colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return

    #Get english item name
    for itemName in currItem.names:
        if itemName.language.name == 'en':
            break

    #If looking for held item, get the pokemon, otherwise get the effect
    if not heldSearch:   
        for itemEffect in currItem.effect_entries:
            if itemEffect.language.name == 'en':
                break
        response = "```Name: {}\nEffect: {}\n```".format(itemName.name, itemEffect.short_effect)    
    else:
        holders = []
        for pHold in currItem.held_by_pokemon:
            holders.append(pHold.pokemon.name.capitalize())
        if len(holders) == 0:
            response = "No pokemon naturally hold this item!"
        else:
            response = "```Name: {}\nHeld by:\n".format(itemName.name)
            for p in sorted(holders):
                response = response + "\t{}\n".format(p)
            response = response + "```"

    embed = discord.Embed(title="Item Entry: {}".format(itemName.name), description=response, colour=discord.Colour.blue())
    embed.set_image(url=currItem.sprites.default)
    await message.channel.send(embed=embed)

commandList.append(Command("!shiny", "getShiny", "Displays a pokemon's shiny sprite. Use !shiny compare <pokemon name> to compare the normal and shiny sprites!"))
async def getShiny(client, message):
    #get the search term
    terms = message.content.split(' ')
    spriteCompare = 0

    #flag for comparing
    if terms[1].lower() == 'compare':
        spriteCompare = 1
    
    #Grab the pokemon data from the api
    try:
        currPoke = pClient.get_pokemon(terms[-1])
    except:
        embed = discord.Embed(title="Pokedex Error!", description="There was an error getting the requested Pokemon. Perhaps the number is invalid or the name is misspelled!", colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return

    if spriteCompare:
        embed = discord.Embed(title="Normal {}".format(getName(currPoke)), colour=discord.Colour.red())
        embed.set_image(url=getSprite(currPoke))
        await message.channel.send(embed=embed)

    embed = discord.Embed(title="Shiny {}".format(getName(currPoke)), colour=discord.Colour.red())
    embed.set_image(url=currPoke.sprites.front_shiny)
    await message.channel.send(embed=embed)
    return

commandList.append(Command("!move", "getMove", "Displays the effect of a requested Pokemon move. Given a Pokemon name, it will list all moves that it can learn."))
async def getMove(client, message):
    #get the search terms
    terms = message.content.split(' ')
    searchTerm = formatInput(terms[1:])

    searchMove = 0
    #Check to see if they're searching for a specific pokemon
    try:
        currentPoke = pClient.get_pokemon(searchTerm)

    except:
        searchMove = 1

    if(searchMove):
        try:
            #Get the move
            currentMove = pClient.get_move(searchTerm)
        except:
            embed = discord.Embed(title="Move Error!", description="There was an error getting the requested move. Perhaps it is misspelled?", colour=discord.Colour.red())
            await message.channel.send(embed=embed)
            return
        #Get move stats
        moveName = currentMove.name.capitalize()
        moveType = currentMove.type.name.capitalize()
        moveClass = currentMove.damage_class.name.capitalize()
        movePower = currentMove.power
        moveAccuracy = currentMove.accuracy
        movePriority = currentMove.priority

        #Get effect chance, if None, leave it, otherwise make it a string
        eChance = currentMove.effect_chance
        if eChance == None:
            eChance = ""
        else:
            eChance = str(eChance)

        #Replace effect_chance with the effect chance in the description
        moveEffect = currentMove.effect_entries[0].short_effect.replace("$effect_chance", eChance)
        
        response = "```Name: {}\nType: {}, {}\nPower: {}\nAccuracy: {}\nPriority: {}\nEffect: {}\n```".format(moveName, moveType, moveClass, movePower, moveAccuracy, movePriority, moveEffect)

        embed = discord.Embed(title="Move: {}".format(moveName), description=response, colour=discord.Colour.blue())
        await message.channel.send(embed=embed)
        return
    else:
        moveNames = []
        for moves in currentPoke.moves:
            moveNames.append(moves.move.name)
        response = "```Name: {}\nLearnable Moves:\n".format(getName(currentPoke))
        for move in sorted(moveNames):
            response = response + "\t{}\n".format(move.capitalize())
        response = response + "\n```"
        embed = discord.Embed(title="{} Moves".format(getName(currentPoke)), description=response, colour=discord.Colour.blue())
        embed.set_thumbnail(url=getSprite(currentPoke))
        await message.channel.send(embed=embed)
        return

commandList.append(Command("!ability", "getAbility", "Displays the effect of a requested Pokemon ability. Can also list all abilities of a specified Pokemon."))
async def getAbility(client, message):
    #get the search terms
    terms = message.content.split(' ')
    searchAbility = 1
    #Check to see if they're searching for all pokemon with a certain ability
    if terms[1].lower() == 'all':
        terms = terms[1:]
        searchAbility = 0
    searchTerm = formatInput(terms[1:])

    try:
        currentA = pClient.get_ability(searchTerm)
    except:
        embed = discord.Embed(title="Ability Error!", description="There was an error getting the requested ability. Perhaps it is misspelled?", colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return

    #Get english ability name
    for aName in currentA.names:
        if aName.language.name == 'en':
            break
    aName = aName.name.capitalize()

    if(searchAbility):
        #Get english ability effect   
        for aEffect in currentA.effect_entries:
            if aEffect.language.name == 'en':
                break
        aEffect = aEffect.short_effect.capitalize()
        response = "```Name: {}\nEffect: {}\n```".format(aName, aEffect)
        embed = discord.Embed(title="Ability: {}".format(aName), description=response, color=discord.Colour.blue())
        await message.channel.send(embed=embed)
    
    else:
        possibleMons = []
        for p in currentA.pokemon:
            possibleMons.append(p.pokemon.name.capitalize())
        response = "```Name: {}\nPossible Pokemon:\n".format(aName)
        for p in sorted(possibleMons):
            response = response + "\t{}\n".format(p)
        response = response + "\n```"
        embed = discord.Embed(title="All Pokemon with {}".format(aName), description=response, color=discord.Colour.blue())
        await message.channel.send(embed=embed)
        return

commandList.append(Command("!evo", "getEvo", "Displays the evolutionary family of a requested pokemon."))
async def getEvo(client, message):
    #get the search term (either name or number)
    searchTerm = message.content.split(' ')[1]

    try:
        pSpecies = pClient.get_pokemon_species(searchTerm)
    except:
        embed = discord.Embed(title="Pokedex Error!", description="There was an error getting the requested Pokemon. Perhaps the number is invalid or the name is misspelled!", colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return
    pImage = getSprite(pClient.get_pokemon(searchTerm))
    chain = requests.get(pSpecies.evolution_chain.url)
    chainJSON = json.loads(chain.text)['chain']
    level = ""
    response = printEvo(chainJSON, level)

    embed = discord.Embed(title="{} Evolutionary Family".format(pSpecies.name.capitalize()), description=response, color=discord.Colour.green())
    embed.set_thumbnail(url=pImage)
    await message.channel.send(embed=embed)
    return

def printEvo(item, level):
    name = item['species']['name'].capitalize()
    #tag on name and depth
    if len(level) > 0:
        finalLevel = level + "> "
    else:
        finalLevel = level
    response = "\n{}{}".format(finalLevel,name)

    #Add evo methods
    if item['evolution_details']:
        evoDetail = item['evolution_details'][0]
        response = response + " (via {}) , requirements: [".format(evoDetail['trigger']['name'])
        count = 0
        for x in evoDetail:
            if evoDetail[x] and not x == 'trigger':
                if count > 0:
                    response = response + ", "
                if x == 'gender':
                    response = response + "{}: {}".format(x, pClient.get_gender(evoDetail[x]).name.capitalize())
                elif isinstance(evoDetail[x], int) or x == "time_of_day":
                    response = response + "{}: {}".format(x, evoDetail[x])
                else:
                    response = response + "{}: {}".format(x, evoDetail[x]['name'])
                count = count + 1
        response = response + "]"

    #Recurse if evolutions exist
    if item['evolves_to']:
        for x in item['evolves_to']:
            response = response + printEvo(x, level + ' - ')

    #If pokemon never evolves, let the user know
    if response.strip() == name:
        response = response + " does not evolve!"
    return response

commandList.append(Command("!type", "typeInfo", "Displays information about a Pokemon type or pair of types."))
async def typeInfo(client, message):
    #get the search terms
    terms = message.content.split(' ')

    try:
        type1 = pClient.get_type(terms[1])

    except:
        embed = discord.Embed(title="Pokemon Type Error!", description="There was an error getting the requested Pokemon type. Perhaps the name is misspelled!", colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return
    #get the damage relation object
    damageRel1 = type1.damage_relations
    #no damage to
    noTo1 = [x.name.capitalize() for x in damageRel1.no_damage_to]
    #half damage to, etc
    halfTo1 = [x.name.capitalize() for x in damageRel1.half_damage_to]
    doubleTo1 = [x.name.capitalize() for x in damageRel1.double_damage_to]

    #defense
    #no damage from
    noFrom1 = [x.name.capitalize() for x in damageRel1.no_damage_from]
    halfFrom1 = [x.name.capitalize() for x in damageRel1.half_damage_from]
    doubleFrom1 = [x.name.capitalize() for x in damageRel1.double_damage_from]

    if len(terms) == 2:
        #single type
        embed = discord.Embed(title="{} Damage Relations".format(type1.name.capitalize()), color=discord.Colour.blue())
        embed.add_field(name='No Damage To:', value=', '.join(noTo1) or "None", inline=True)
        embed.add_field(name='Half Damage To:', value=', '.join(halfTo1) or "None", inline=True)
        embed.add_field(name='Double Damage To:', value=', '.join(doubleTo1) or "None", inline=True)
        embed.add_field(name='No Damage From:', value=', '.join(noFrom1) or "None", inline=True)
        embed.add_field(name='Half Damage From:', value=', '.join(halfFrom1) or "None", inline=True)
        embed.add_field(name='Double Damage From:', value=', '.join(doubleFrom1) or "None", inline=True)
        await message.channel.send(embed=embed)
        return

    elif len(terms) == 3:
        #compare types
        #Get type 2
        try:
            type2 = pClient.get_type(terms[2])

        except:
            embed = discord.Embed(title="Pokemon Type Error!", description="There was an error getting the requested Pokemon type(s). Perhaps a name is misspelled!", colour=discord.Colour.red())
            await message.channel.send(embed=embed)
            return

        type2Name = type2.name.capitalize()
        offenseRel = "{} does ".format(type1.name.capitalize())
        if type2Name in noTo1:
            offenseRel = offenseRel + "no damage"
        elif type2Name in halfTo1:
            offenseRel = offenseRel + "half damage"
        elif type2Name in doubleTo1:
            offenseRel = offenseRel + "double damage"
        else:
            offenseRel = offenseRel + "normal damage"
        offenseRel = offenseRel + " to {}".format(type2Name)

        defenseRel = "{} recieves ".format(type1.name.capitalize())
        if type2Name in noFrom1:
            defenseRel = defenseRel + "no damage"
        elif type2Name in halfFrom1:
            defenseRel = defenseRel + "half damage"
        elif type2Name in doubleFrom1:
            defenseRel = defenseRel + "double damage"
        else:
            defenseRel = defenseRel + "normal damage"
        defenseRel = defenseRel + " from {}".format(type2Name)

        response = offenseRel + ",\n" + defenseRel

        embed = discord.Embed(title="{} vs {} Type Comparison".format(type1.name.capitalize(), type2Name), description = response, color=discord.Colour.blue())
        await message.channel.send(embed=embed)
        return

    else:
        embed = discord.Embed(title="Pokemon Type Error!", description="Incorrect number of types given. Please provide only one or two types.", colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return

#For egg groups
#Species -> egg group -> names
commandList.append(Command("!egg", "eggGroup", "Displays information about a Pokemon's egg group(s)"))
async def eggGroup(client, message):
    terms = message.content.split(' ')

    if len(terms) > 2:
        embed = discord.Embed(title="Pokemon Egg Error!", description="Too many inputs!", colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return

    try:
        species = pClient.get_pokemon_species(terms[1])
    except:
        try:
            group = pClient.get_egg_group(terms[1])
        except:
            embed = discord.Embed(title="Pokemon Error!", description="There was an error getting the requested Pokemon or Egg Group. Perhaps the name is misspelled!", colour=discord.Colour.red())
            await message.channel.send(embed=embed)
            return
        groupNames = [x.name.capitalize() for x in group.pokemon_species]
        embed = discord.Embed(title = "{} Group Pokemon".format(group.name.capitalize()), description=', '.join(groupNames), color=discord.Colour.blue())
        await message.channel.send(embed=embed)
        return
    #Otherwise get egg groups of species
    sName = species.name
    
    eggGroups = species.egg_groups
    eggNames = [x.name.capitalize() for x in eggGroups]
    embed = discord.Embed(title="{} Egg Group(s)".format(sName.capitalize()), description=', '.join(eggNames) or "None", color=discord.Colour.blue())
    embed.set_thumbnail(url=getSprite(pClient.get_pokemon(terms[1])))
    await message.channel.send(embed=embed)
    return

commandList.append(Command("!nature", "getNature", "Displays information about a Pokemon nature"))
async def getNature(client, message):
    terms = message.content.split(' ')

    plus = ''
    minus = ''
    searchNature = ''
    badStat = 0
    statList = ['attack', 'defense', 'special-attack', 'special-defense', 'speed']
    for x in terms:
        if x.startswith('+'):
            plus = x[1:]
            if plus.lower() not in statList:
                badStat = 1
        elif x.startswith('-'):
            minus = x[1:]
            if minus.lower() not in statList:
                badStat = 1
        else:
            searchNature = x

    if badStat:
        embed = discord.Embed(title="Stat Error!", description="One of the provided Pokemon stats is not valid!", color=discord.Colour.red())
        await message.channel.send(embed=embed)
        return
    #If they specify one stat, give a list
    natureList = []
    if (plus == '') != (minus == ''):
        for x in range(1,26):
            nature = pClient.get_nature(x)
            searchNature = nature.name.capitalize()
            if not nature.increased_stat == None and plus.lower() == nature.increased_stat.name.lower():
                natureList.append(searchNature)
            elif not nature.decreased_stat == None and minus.lower() == nature.decreased_stat.name.lower():
                natureList.append(searchNature)
        if not plus == '':
            title = "Natures that increase {}".format(plus.capitalize())
        else:
            title = "Natures that decrease {}".format(minus.capitalize())
        embed = discord.Embed(title=title, description=', '.join(natureList), color=discord.Colour.blue())
        await message.channel.send(embed=embed)
        return

    #If both are specified, find the specific nature
    elif not plus == '' and not minus == '':
        for x in range(1, 26):
            nature = pClient.get_nature(x)
            searchNature = nature.name
            if not plus == '' and not nature.increased_stat == None and not plus.lower() == nature.increased_stat.name.lower():
                searchNature = ''
            if not minus == '' and not nature.decreased_stat == None and not minus.lower() == nature.decreased_stat.name.lower():
                searchNature = ''
            if nature.increased_stat == None or nature.decreased_stat == None:
                searchNature = ''
            if not searchNature == '':
                break


        #Search
    if not searchNature == '':
        try:
            nature = pClient.get_nature(searchNature)
        except:
            embed = discord.Embed(title="Pokemon Nature Error!", description="Provided nature not found, perhaps it is misspelled?", colour=discord.Colour.red())
            await message.channel.send(embed=embed)
            return

        nName = nature.name.capitalize()
        if not nature.increased_stat == None:
            upStat = nature.increased_stat.name.capitalize()
        else:
            upStat = "Nothing"
        if not nature.decreased_stat == None:
            downStat = nature.decreased_stat.name.capitalize() or "None"
        else:
            downStat = "Nothing"
        if not nature.likes_flavor == None:
            likes = nature.likes_flavor.name.capitalize()
        else:
            likes = "No"
        if not nature.hates_flavor == None:
            dislikes = nature.hates_flavor.name.capitalize()
        else:
            dislikes = "No"

        response = "Increases {}, Decreases {}\nLikes: {} Flavors, Hates: {} Flavors".format(upStat, downStat, likes, dislikes)

        embed = discord.Embed(title="{} Nature".format(nName), description=response, color=discord.Colour.blue())
        await message.channel.send(embed=embed)
        return
    else:
        embed = discord.Embed(title="Pokemon Nature Error!", description="Provided nature not found", colour=discord.Colour.red())
        await message.channel.send(embed=embed)
        return



#For natures, just get nature info (decreased stat, increased stat, like and disliked flavors)


#Helper functions
def formatInput(input):
    return '-'.join(input).lower()

def getName(pokemon):
    return pokemon.name.capitalize()

def getTypes(pokemon):
    types = ""
    #if two types, show both
    if(len(pokemon.types) > 1):
        types = "{}, {}".format(pokemon.types[0].type.name.capitalize(), pokemon.types[1].type.name.capitalize())
    #else just show 1
    else:
        types = "{}".format(pokemon.types[0].type.name.capitalize())
    return types

def getAbilities(pokemon):
    abilities = pokemon.abilities
    #Load first abilility
    response = pokemon.abilities[0].ability.name.capitalize()
    #If more than 1 ability, add them all to the response
    for x in range (1, len(pokemon.abilities)):
        response = response + ", {}".format(abilities[x].ability.name.capitalize())
    return response

def getStats(pokemon):
    statData = pokemon.stats
    stats = "\tHP: {}\n\tAttack: {}\n\tDefense: {}\n\tSp. Attack: {}\n\tSp. Defense: {}\n\tSpeed: {}".format(statData[0].base_stat, statData[1].base_stat, statData[2].base_stat, statData[3].base_stat, statData[4].base_stat, statData[5].base_stat)
    return stats

#images
def getSprite(pokemon):
    return pokemon.sprites.front_default