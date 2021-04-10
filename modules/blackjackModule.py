try:
    from command import Command
except:
    pass

import discord
import random
import asyncio

# Module for the blackjack game

# Classes
# Class representing a card
class Card:
    suits = [u"\u2664", u"\u2667", u"\u2661", u"\u2662"]
    numbers = ["A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K"]
    def __init__(self, suit, number):
        self.suit = suit      # The suit of the card
        self.number = number  # The number of the card where A is ace and J, Q, K are jack, queen, king respectively
    # Used for displaying the card
    def __str__(self):
        cardStr =  "**" + str(self.number) + "** of " + str(self.suit)
        return cardStr

# Class representing a player
class Player:
    betAmounts = [100, 200, 500, 1000]
    betReactions = [u"1\ufe0f\u20e3", u"2\ufe0f\u20e3", u"5\ufe0f\u20e3", u"\U0001F51F"]
    def __init__(self, userid, money = 100000, bet = 500):
        self.userid = userid  # User ID of the player
        self.money = money    # Money the player owns
        self.done = False     # Determines if the player is done with the current round
        self.hand = []        # List of Card objects that represent the player's hand
        self.value = 0        # The value of the player's hand
        self.bet = bet        # The amount of money the player is currently betting
    # Prepares the player for another round
    def reset(self):
        self.done = False
        self.hand = []
        self.value = 0
    # Calculate the hand value of the player
    def calculateValue(self):
        value = 0
        for card in self.hand:
            if card.number == 'J' or card.number == 'Q' or card.number == 'K':
                value += 10
            elif card.number == 'A':
                value += 11
            else:
                value += card.number
        # Recalulate if there is ace as it can have a value of 1 and 11
        # Only do this if it would cause the player to bust
        if len([c for c in self.hand if c.number == 'A']) > 0 and value > 21:
            value = 0
            for card in self.hand:
                if card.number == 'J' or card.number == 'Q' or card.number == 'K':
                    value += 10
                elif card.number == 'A':
                    value += 1
                else:
                    value += card.number
        self.value = value
    # Ends the turn for the player
    def end(self):
        self.done = True
    # Edit the amount of money the player has
    def updateBalance(self, change):
        self.money += change
    # Draw card
    def drawCard(self):
        self.hand.append(randomCard())

# Class representing a game
class Game:
    actions = ["Hit", "Stand", "Fold"]
    actionReactions = [u"\u2705",  	u"\u274E", u"\U0001F6AB"]
    def __init__(self, guild, tc):
        self.guild = guild  # The server of the game
        self.players = []   # List of Player objects that represent the players in the game
        self.round = 0      # The current round of the game
        self.dealer = []    # List of Card objects that represent the dealer's hand
        self.gm = None      # The Message object of the game
        self.embed = None   # The embed used for displaying the game
        self.tc = tc        # The channel ID that the game will continue to send to
    # Initiate round
    async def initializeRound(self):
        await self.newPlayers()
        if len(self.players) == 0:
            self.end()
            return
        self.round += 1
        self.dealer = []
        self.dealer.append(randomCard())
        self.dealer.append(randomCard())
        await self.setEmbed()
    # Ends the game
    async def end(self):
        response = "There are no more players in the game! The game will be removed."
        embed = discord.Embed(title="No More Players", description=response, colour=discord.Colour.blue())
        await self.guild.get_channel(self.tc).send(embed=embed)
        del self
    # Adds a player
    def addPlayer(self, player):
        self.players.append(player)
    # Sets the embed of the game
    async def setEmbed(self):
        roundStr = "**Round " + str(self.round) + "**\n"
        roundStr += "**Dealer's Cards:**"
        embed = discord.Embed(title="Blackjack", description=roundStr, colour=discord.Colour.darker_gray())
        embed.add_field(name="Card 1", value=str(self.dealer[0]), inline=True)
        embed.add_field(name="Card 2", value="**Hidden**", inline=True)
        playerStr = ""
        for player in self.players:
            playerObj = await self.guild.fetch_member(player.userid)
            playerStr += playerObj.display_name
            playerStr += "\nMoney: $" + str(player.money) + "\n\n"
        embed.add_field(name="Players", value=playerStr, inline=False)
        embed.add_field(name="Round Starting", value="Check your DMs! The round is starting!", inline=False)
        self.embed = embed
    # Check for additional players
    async def newPlayers(self):
        pass


# Every module has to have a command list
commandList = []

# Dictionary that keeps track of all the Player objects
# Key: user ID
# Value: Player object for the user
players = {}

# Dictionary that keeps track of all the Game Objects
# Key: server ID
# Value: Game object for the server
games = {}

# Description for !blackjack
usage = "Command used to initialize or redisplay the blackjack game. There will be one game per server."
usage += "You will be direct messaged to make decisions in the game. To view the rules, use **!blackjack rules <section>**."
usage += "To view your balance, use **!blackjack balance**. You will recieve a DM in both cases."

# Format: !blackjack <rules/balance> <section>
try:
    commandList.append(Command("!blackjack", "runBlackjack", usage))
except:
    print("Command Module correctly not imported.")
    print("The Main Module is required for this to work.")
    print("")

# Runs the blackjack game and parses all commands from users
async def runBlackjack(client, message):
    if len(message.content.split(" ")) >= 2 and message.content.split(" ")[1] == "rules":
        pass
    elif len(message.content.split(" ")) >= 2 and message.content.split(" ")[1] == "balance":
        pass
    else:
        # Check if the current guild has a game
        if message.guild.id in games:
            # Reprompt game
            game = games[message.guild.id]
            game.tc = message.channel.id
            await game.gm.delete()
            game.gm = await game.guild.get_channel(game.tc).send(embed=game.embed)
        else:
            # Create the game
            game = Game(message.guild, message.channel.id)
            games[message.guild.id] = game
            # Add the user as a player
            if message.author.id not in players:
                players[message.author.id] = Player(message.author.id)
            game.addPlayer(players[message.author.id])
            # Initialize the first round
            await game.initializeRound()
            game.gm = await game.guild.get_channel(game.tc).send(embed=game.embed)
            # Start running the rounds
            await runRounds(client, game)

# Helper function that randomly generates a Card object
def randomCard():
    suit = Card.suits[random.randrange(len(Card.suits))]
    number = Card.numbers[random.randrange(len(Card.numbers))]
    return Card(suit, number)

# Helper function that runs the rounds
async def runRounds(client, game):
    while game != None:
        # Send each player a chance to change bets
        for player in game.players:
            await sendBetChanger(client, game, player)
        # Wait for all players to finish
        while len([p for p in game.players if p.done == True]) < len(game.players):
            pass
        # Reset all players
        for player in game.players:
            player.reset()
        # Draw two cards for each player
        for player in game.players:
            player.drawCard()
            player.drawCard()
        # Send each player the prompt for hit, stand, or fold
        for player in game.players:
            await sendHand(client, game, player)
        break

# Direct messages the bet changing message to the player
async def sendBetChanger(client, game, player):
    response = "The round is about to begin!\n"
    response += "Current Bet: **$" + str(player.bet) + "**\n"
    response += "To change your bet amount, react to this message.\n"
    response += "You have 15 seconds to make a decision.\n"
    embed = discord.Embed(title="Round Starting", description=response, colour=discord.Colour.blurple())
    # Only bet amounts allowed: 100, 200, 500, 1000
    betStr = ""
    for i in range(len(Player.betAmounts)):
        betStr += Player.betReactions[i] + " for $" + str(Player.betAmounts[i]) + "\n"
    embed.add_field(name="Bets", value=betStr, inline=False)
    playerObj = await game.guild.fetch_member(player.userid)
    betMsg = await playerObj.send(embed=embed)
    # React with all the bet amounts
    for betReaction in Player.betReactions:
        await betMsg.add_reaction(betReaction)
    # Helper function that checks if the user has reacted with a emote of interest
    def betChangerCheck(reaction, user):
        return user == playerObj and str(reaction.emoji) in Player.betReactions
    # Check for bet amount from the user
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=15.0, check=betChangerCheck)
    except asyncio.TimeoutError:
        reaction = None
        user = None
    # Change the bet amount
    if reaction != None and user != None:
        for i in range(len(Player.betAmounts)):
            if str(reaction.emoji) == Player.betReactions[i]:
                player.bet = Player.betAmounts[i]
                break
    await betMsg.delete()
    response = "Your bet amount: **$" + str(player.bet) + "**\n"
    embed = discord.Embed(title="Your Bet", description=response, colour=discord.Colour.blurple())
    await playerObj.send(embed=embed)
    # Notify player is done
    player.done = True

# Direct messages the player's hand
async def sendHand(client, game, player):
    response = "**Round " + str(game.round) + "**\n"
    response += "Here are your cards. React to hit, stand, or fold.\n"
    response += "You have 30 seconds to make a decision.\n"
    response += "**Your Cards:**"
    embed = discord.Embed(title="Your Hand", description=response, colour=discord.Colour.dark_gray())
    # Display the cards
    cardNum = 1
    for card in player.hand:
        embed.add_field(name="Card " + str(cardNum), value=str(card), inline=True)
        cardNum += 1
    # Calculate the hand value
    player.calculateValue()
    embed.add_field(name="Hand Value", value=str(player.value), inline=False)
    # Display the actions
    actionStr = ""
    for i in range(len(Game.actions)):
        actionStr += Game.actionReactions[i] + " for " + Game.actions[i] + "\n"
    embed.add_field(name="Actions", value=actionStr, inline=False)
    playerObj = await game.guild.fetch_member(player.userid)
    handMsg = await playerObj.send(embed=embed)
    # React with all the actions
    for actionReaction in Game.actionReactions:
        await handMsg.add_reaction(actionReaction)