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
    exitReaction = u"\u274c"
    def __init__(self, userid, money = 100000, bet = 500):
        self.userid = userid  # User ID of the player
        self.money = money    # Money the player owns
        self.done = False     # Determines if the player is done with the current round
        self.hand = []        # List of Card objects that represent the player's hand
        self.value = 0        # The value of the player's hand
        self.bet = bet        # The amount of money the player is currently betting
        self.result = None    # Determines if the player won, push, or lost
        self.ingame = False   # Keeps track of whether the player is currently in a game
        self.blackjacks = 0   # Number of blackjacks player has obtained
        self.wonrounds = 0    # Number of rounds player has won
        self.moneywon = 0     # Total money won by player
    # Prepares the player for another round
    def reset(self):
        self.done = False
        self.hand = []
        self.value = 0
        self.result = None
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
    addReaction = u"\U0001F0CF"
    def __init__(self, guild, tc):
        self.guild = guild  # The server of the game
        self.players = []   # List of Player objects that represent the players in the game
        self.round = 0      # The current round of the game
        self.dealer = []    # List of Card objects that represent the dealer's hand
        self.dealerVal = 0  # Value of the dealer's cards
        self.gm = None      # The Message object of the game
        self.embed = None   # The embed used for displaying the game
        self.tc = tc        # The channel ID that the game will continue to send to
    # Initiate round
    async def initializeRound(self):
        await self.newPlayers()
        self.round += 1
        self.dealer = []
        self.dealer.append(randomCard())
        self.dealer.append(randomCard())
        await self.setEmbed()
    # Ends the game
    async def end(self):
        response = "There are no more players in the game! The game has be removed."
        embed = discord.Embed(title="No More Players", description=response, colour=discord.Colour.red())
        await self.gm.edit(embed=embed)
        await self.gm.clear_reactions()
        # Remove the game from the dictionary
        del games[self.guild.id]
    # Adds a player
    def addPlayer(self, player):
        self.players.append(player)
        player.ingame = True
    # Removes a player
    def removePlayer(self, player):
        self.players.remove(player)
        player.ingame = False
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
        # Send none if there are no players in the game
        if playerStr == "":
            playerStr = "None"
        embed.add_field(name="Players:", value=playerStr, inline=False)
        response = "Check your DMs! The round is starting!\n"
        response += "React with " + Game.addReaction + " to join the next round."
        embed.add_field(name="Round Starting", value=response, inline=False)
        self.embed = embed
    # Sets the embed to the round results
    async def setResultEmbed(self):
        roundStr = "**Round " + str(self.round) + " Results**\n"
        roundStr += "**Dealer's Cards:**"
        embed = discord.Embed(title="Blackjack", description=roundStr, colour=discord.Colour.darker_gray())
        # Display dealer's cards
        cardNum = 1
        for card in self.dealer:
            embed.add_field(name="Card " + str(cardNum), value=str(card), inline=True)
            cardNum += 1
        # Display dealer's value
        dealerVal = str(self.dealerVal)
        if self.dealerVal > 21:
            dealerVal += " (Bust)"
        embed.add_field(name="Dealer's Value:", value=str(dealerVal), inline=False)
        winStr = ""
        loseStr = ""
        pushStr = ""
        foldStr = ""
        for player in self.players:
            playerObj = await self.guild.fetch_member(player.userid)
            # If concat to string depending on result
            if player.result == "W":
                winStr += playerObj.display_name
                winStr += "\nMoney: $" + str(player.money) + " (+" + str((player.bet // 2) + player.bet) + ")\n"
                winStr += "Final Value: **" + str(player.value) + "**\n\n"
            elif player.result == "L":
                loseStr += playerObj.display_name
                loseStr += "\nMoney: $" + str(player.money) + " (-" + str(player.bet) + ")\n"
                if player.value > 21:
                    loseStr += "Final Value: **" + str(player.value) + "** (Bust)\n\n"
                else:
                    loseStr += "Final Value: **" + str(player.value) + "**\n\n"
            elif player.result == "P":
                pushStr += playerObj.display_name
                pushStr += "\nMoney: $" + str(player.money) + "\n"
                pushStr += "Final Value: **" + str(player.value) + "**\n\n"
            else:
                foldStr += playerObj.display_name
                foldStr += "\nMoney: $" + str(player.money) + " (-" + str(player.bet // 2) + ")\n"
        # Only add fields if there are players corresponding to the section
        if winStr != "":
            embed.add_field(name="Players That Won:", value=winStr, inline=False)
        if loseStr != "":
            embed.add_field(name="Players That Lost:", value=loseStr, inline=False)
        if pushStr != "":
            embed.add_field(name="Players That Tied:", value=pushStr, inline=False)
        if foldStr != "":
            embed.add_field(name="Players That Folded:", value=foldStr, inline=False)
        response = "The current round has ended. Prepare for the next round!\n"
        response += "React with " + Game.addReaction + " to join the next round."
        embed.add_field(name="Round Ended", value=response, inline=False)
        self.embed = embed
    # Check for additional players
    async def newPlayers(self):
        # Do not check for new players if the game message doesn't exist
        if self.gm == None:
            return
        self.gm = await self.gm.channel.fetch_message(self.gm.id)
        # Obtain all users who have reacted with the add reaction
        reaction = [r for r in self.gm.reactions if str(r.emoji) == Game.addReaction][0]
        users = await reaction.users().flatten()
        for user in users:
            # Don't consider bots
            if user.bot == True:
                continue
            # Check if user is not current in the game
            if len([p for p in self.players if p.userid == user.id]) == 0:
                if user.id not in players:
                    players[user.id] = Player(user.id)
                self.addPlayer(players[user.id])
    # Update the status of the game
    def updateStatus(self, title, status):
        status += "\nReact with " + Game.addReaction + " to join the next round."
        self.embed.remove_field(len(self.embed.fields) - 1)
        self.embed.add_field(name=title, value=status, inline=False)
    # Calculate the hand value of the dealer
    def calculateDealerValue(self):
        value = 0
        for card in self.dealer:
            if card.number == 'J' or card.number == 'Q' or card.number == 'K':
                value += 10
            elif card.number == 'A':
                value += 11
            else:
                value += card.number
        # Recalulate if there is ace as it can have a value of 1 and 11
        # Only do this if it would cause the player to bust
        if len([c for c in self.dealer if c.number == 'A']) > 0 and value > 21:
            value = 0
            for card in self.dealer:
                if card.number == 'J' or card.number == 'Q' or card.number == 'K':
                    value += 10
                elif card.number == 'A':
                    value += 1
                else:
                    value += card.number
        self.dealerVal = value
    # Runs the dealer's turn
    def dealerTurn(self):
        # Keep hitting until dealer reaches a value of 17
        self.calculateDealerValue()
        while self.dealerVal < 17:
            self.dealer.append(randomCard())
            self.calculateDealerValue()

# Class representing a slot machine
class Slot:
    betAmounts = [100, 200, 500, 1000]
    betReactions = [u"1\ufe0f\u20e3", u"2\ufe0f\u20e3", u"5\ufe0f\u20e3", u"\U0001F51F"]
    exitReaction = u"\u274c"
    def __init__(self, player):
        self.player = player         # Player object currently playing the slot machine
        self.sm = None               # Message corresponding to the slot machine
        self.numbers = [7, 7, 7]     # The three numbers displayed on the slot machine
        self.embed = None            # The embed for the slot machine message
    # Obtain three random numbers
    def rollNumbers(self):
        self.numbers = []
        for _ in range(3):
            self.numbers.append(random.randint(0, 9))
    # Initialize the display
    def setEmbed(self):
        response = "Welcome to the Slot Machine!\n"
        embed = discord.Embed(title="Slots", description=response, colour=discord.Colour.greyple())
        embed.add_field(name="Current Balance", value="$" + str(self.player.money), inline=False)
        count = 1
        for num in self.numbers:
            embed.add_field(name="Slot " + str(count), value=str(num), inline=True)
            count += 1
        betStr = ""
        for i in range(len(Slot.betReactions)):
            betStr += Slot.betReactions[i] + " to bet $" + str(Slot.betAmounts[i]) + "\n"
        embed.add_field(name="React To Play", value=betStr, inline=False)
        winStr = ""
        winStr += "Two of a kind:   2x bet\n"
        winStr += "Three of a kind: 8x bet\n"
        winStr += "Two 7s:          5x bet\n"
        winStr += "Three 7s:        50x bet\n"
        embed.add_field(name="Winnings", value=winStr, inline=False)
        self.embed = embed
    # Update the number fields of the embed
    def updateNumbers(self):
        for _ in range(3):
            self.embed.remove_field(1)
        self.rollNumbers()
        count = 1
        for num in self.numbers:
            self.embed.insert_field_at(count, name="Slot " + str(count), value=str(num), inline=True)
            count += 1
    # Update the winnings display
    def updateWinnings(self, bet):
        for _ in range(2):
            self.embed.remove_field(len(self.embed.fields) - 1)
        winStr = ""
        winStr += "Two of a kind:  $" + str(2 * bet) + "\n"
        winStr += "Three of a kind: $" + str(8 * bet) + "\n"
        winStr += "Two 7s:         $" + str(5 * bet) + " \n"
        winStr += "Three 7s:       $" + str(50 * bet) + "\n"
        self.embed.add_field(name="Winnings", value=winStr, inline=False)
    # Update balance
    def updateBalance(self):
        self.embed.remove_field(0)
        self.embed.insert_field_at(0, name="Current Balance", value="$" + str(self.player.money), inline=False)
    # Calculate winnings
    def calculateWinnings(self, bet):
        if self.numbers[0] == self.numbers[1] or self.numbers[1] == self.numbers[2] or self.numbers[0] == self.numbers[2]:
            return 2 * bet
        if self.numbers[0] == self.numbers[1] and self.numbers[1] == self.numbers[2]:
            return 8 * bet
        if len([n for n in self.numbers if n == 7]) == 2:
            return 5 * bet
        if len([n for n in self.numbers if n == 7]) == 3:
            return 50 * bet
        return 0
    # End the slot machine
    async def end(self):
        await self.sm.delete()
        del slots[self.player.userid]

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

# Dictionary that keeps track of all the Slot Objects
# Key: user ID
# Value: Slot object for the user
slots = {}

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
    if len(message.content.split(" ")) >= 2 and message.content.split(" ")[1] == "leaderboard":
        await displayLeaderboard(client, message.guild, message.channel)
    elif len(message.content.split(" ")) >= 2 and message.content.split(" ")[1] == "rules":
        sent = False
        if len(message.content.split(" ")) == 2:
            section = "all"
            title = "Blackjack Rules"
        else:
            section = message.content.split(" ")[2].lower()
            title = "Blackjack Rules: Section " + section
        if section == "all" or section == "game":
            sent = True
            response = "**Section 1: Game**\n"
            response += "Blackjack is one of the most popular card games. In blackjack, "
            response += "you will always be competing against the dealer regardless of the number "
            response += "of players currently in the game. The goal of the game is to obtain "
            response += "a hand value larger than the dealer's without exceeding 21. Your hand "
            response += "value is the sum of the card values, given in the next section. Just for fun, "
            response += "each player will be given a balance for which they can alter by playing blackjack.\n"
            response += "Important terminology:\n"
            response += "Round: Each round consists of a bet, player's turn, and result. These are explained "
            response += "in the following sections.\n"
            response += "Bust: This is when your hand value exceeds 21.\n"
            response += "Dealer: Who are playing against. The dealer's turn occurs after all players have had a turn."
            embed = discord.Embed(title=title, description=response, colour=discord.Colour.dark_gray())
            await message.author.send(embed=embed)
        if section == "all" or section == "cards":
            sent = True
            response = "**Section 2: Cards**\n"
            response += "In blackjack, the value of each card is as follows:\n"
            response += "All face cards have a value of 10.\n"
            response += "Face Cards: J, Q, K\n"
            response += "All cards between 2 and 10 have their respective value.\n"
            response += "Ace, represented by A, can be valued at 1 or 11.\n"
            response += "Aces are valued at 11 by default. However, if drawing another card "
            response += "would cause the player to bust, Aces will change value to 1 to prevent "
            response += "the player from busting."
            embed = discord.Embed(title=title, description=response, colour=discord.Colour.dark_gray())
            await message.author.send(embed=embed)
        if section == "all" or section == "turn":
            sent = True
            response = "**Section 3: Turn**\n"
            response += "At the start of your turn for the current round, you will have a chance to change your bet amount.\n"
            response += "Bet Amounts: $100, $200, $500, $1000\n"
            response += "After declaring your bet amount, you will be given two cards. You then have three options.\n"
            response += "Hit: Draw another card, adding additional value to your hand.\n"
            response += "Stand: Declare your final value. This will determine if you win or not.\n"
            response += "Fold: Give up the round. Cannot be done if you have hit already. Half your bet is returned to you.\n"
            response += "If at any point your hand value exceeds 21, you will bust and lose the round.\n"
            embed = discord.Embed(title=title, description=response, colour=discord.Colour.dark_gray())
            await message.author.send(embed=embed)
        if section == "all" or section == "outcomes":
            sent = True
            response = "**Section 4: Outcomes**\n"
            response += "At the end of a round, there are three possible outcomes.\n"
            response += "Win: You win the round if your hand value exceeds the dealer's or the dealer busts "
            response += "and you do not. You cannot have busted during the round.\n"
            response += "Lose: You lose the round if your hand value is less than "
            response += "the dealer's or you busted during the round\n"
            response += "Push: If you and the dealer have the same hand value, a push occurs.\n"
            response += "Depending on the outcome, your balance will be affect as follows:\n"
            response += "Win: You gain $3 for every $2 in your bet.\n"
            response += "Lose: You lose your bet.\n"
            response += "Push: Your balance is unchanged.\n"
            embed = discord.Embed(title=title, description=response, colour=discord.Colour.dark_gray())
            await message.author.send(embed=embed)
        if section == "all" or section == "play":
            sent = True
            response = "**Section 5: Play**\n"
            response += "There are two ways to join and play the blackjack game.\n"
            response += "If there is no game going on in your current server, create a game with the **!blackjack** command.\n"
            response += "If there is a game running, react with the black joker reaction to the game message. "
            response += "You will join the game in the next round. If you can't see the game message, use the **!blackjack** "
            response += "command to redisplay the game message.\n"
            response += "You may leave the game at the very beginning of a round when you are changing your bet. Simply "
            response += "react with the red cross mark reaction to exit the game.\n"
            embed = discord.Embed(title=title, description=response, colour=discord.Colour.dark_gray())
            await message.author.send(embed=embed)
        if sent == False:
            response = "The section given was not found.\n"
            response += "Sections:\n"
            response += "**Section 1: Game**\n"
            response += "**Section 2: Cards**\n"
            response += "**Section 3: Turn**\n"
            response += "**Section 4: Outcomes**\n"
            response += "**Section 5: Play**\n"
            embed = discord.Embed(title='No Section', description=response, colour=discord.Colour.red())
            await message.author.send(embed=embed)
        # Send message to the channel indicating rules sent
        response = "The requested game rules has been direct messaged to you."
        embed = discord.Embed(title='Game Rules', description=response, colour=discord.Colour.dark_gray())
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)
    elif len(message.content.split(" ")) >= 2 and message.content.split(" ")[1] == "balance":
        if message.author.id not in players:
            players[message.author.id] = Player(message.author.id)
        # Direct message the player the balance
        player = players[message.author.id]
        response = "Current Balance: **$" + str(player.money) + "**"
        embed = discord.Embed(title='Your Balance', description=response, colour=discord.Colour.blurple())
        await message.author.send(embed=embed)
        # Send message to the channel indicating balance sent
        response = "Your balance has been direct messaged to you."
        embed = discord.Embed(title='Balance', description=response, colour=discord.Colour.blurple())
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)
    else:
        # Check if the current guild has a game
        if message.guild.id in games:
            # Reprompt game
            game = games[message.guild.id]
            game.tc = message.channel.id
            await game.gm.delete()
            game.gm = await game.guild.get_channel(game.tc).send(embed=game.embed)
            await game.gm.add_reaction(game.addReaction)
        else:
            # Create the game
            game = Game(message.guild, message.channel.id)
            games[message.guild.id] = game
            # Add the user as a player if they are not currently in a game
            if message.author.id not in players:
                players[message.author.id] = Player(message.author.id)
            if players[message.author.id].ingame == False:
                game.addPlayer(players[message.author.id])
            # Initialize the first round
            await game.initializeRound()
            game.gm = await game.guild.get_channel(game.tc).send(embed=game.embed)
            await game.gm.add_reaction(game.addReaction)
            # Wait 15 seconds for people to join
            await asyncio.sleep(15)
            # Check for new players and update game display
            await game.newPlayers()
            await game.setEmbed()
            await game.gm.edit(embed=game.embed)
            # Start running the rounds
            await runRounds(client, game)

# Helper function that randomly generates a Card object
def randomCard():
    suit = Card.suits[random.randrange(len(Card.suits))]
    number = Card.numbers[random.randrange(len(Card.numbers))]
    return Card(suit, number)

# Helper function that runs the rounds
async def runRounds(client, game):
    firstRound = True  # Keeps track if this is the first round played
    while game != None:
        # If not first round, initialize round
        if firstRound == False:
            await game.initializeRound()
            await game.gm.edit(embed=game.embed)
        # Send each player a chance to change bets
        for player in game.players:
            await sendBetChanger(client, game, player)
        # Check if there are any players in the game
        if len(game.players) == 0:
            await game.end()
            break
        # Wait for all players to finish
        while len([p for p in game.players if p.done == True]) < len(game.players):
            pass
        # Reset all players
        for player in game.players:
            player.reset()
        # Notify round in progress
        await game.setEmbed()
        game.updateStatus("Round In Progress", "The round is currently in progress.")
        await game.gm.edit(embed=game.embed)
        # Draw two cards for each player
        for player in game.players:
            player.drawCard()
            player.drawCard()
        # Send each player the prompt for hit, stand, or fold
        for player in game.players:
            await sendHand(client, game, player)
        # Wait for all players to finish
        while len([p for p in game.players if p.done == True]) < len(game.players):
            pass
        # Dealer's turn
        game.dealerTurn()
        for player in game.players:
            # Check to see if the player busted or folded
            if player.value <= 21 and player.value >= 0:
                await compareToDealer(game, player)
        # Send round results
        await game.setResultEmbed()
        await game.gm.edit(embed=game.embed)
        # Reset all players
        for player in game.players:
            player.reset()
        # Wait for the players to view the round results
        await asyncio.sleep(15)
        # Set first round to false to notify first round finished
        firstRound = False

# Direct messages the bet changing message to the player
async def sendBetChanger(client, game, player):
    response = "The round is about to begin!\n"
    response += "Current Bet: **$" + str(player.bet) + "**\n"
    response += "Current Balance: **$" + str(player.money) + "**\n"
    response += "To change your bet amount, react to this message.\n"
    response += "You have 15 seconds to make a decision.\n"
    embed = discord.Embed(title="Round Starting", description=response, colour=discord.Colour.blurple())
    # Only bet amounts allowed: 100, 200, 500, 1000
    betStr = ""
    for i in range(len(Player.betAmounts)):
        betStr += Player.betReactions[i] + " for $" + str(Player.betAmounts[i]) + "\n"
    betStr += Player.exitReaction + " to leave the game\n"
    embed.add_field(name="Bets", value=betStr, inline=False)
    playerObj = await game.guild.fetch_member(player.userid)
    betMsg = await playerObj.send(embed=embed)
    # React with all the bet amounts
    for betReaction in Player.betReactions:
        await betMsg.add_reaction(betReaction)
    # React with the exit reaction
    await betMsg.add_reaction(Player.exitReaction)
    # Helper function that checks if the user has reacted with a emote of interest
    def betChangerCheck(reaction, user):
        return user == playerObj and (str(reaction.emoji) in Player.betReactions or str(reaction.emoji) == Player.exitReaction)
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
        # Check if player reacted to exit the game
        if str(reaction.emoji) == Player.exitReaction:
            game.removePlayer(player)
            await betMsg.delete()
            response = "You have left the game!\n"
            embed = discord.Embed(title="Left The Game", description=response, colour=discord.Colour.red())
            await playerObj.send(embed=embed)
            return
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
    embed.add_field(name="Hand Value", value=str(player.value) + "\n\n**Dealer's Cards:**", inline=False)
    # Display the dealer's cards
    embed.add_field(name="Card 1", value=str(game.dealer[0]), inline=True)
    embed.add_field(name="Card 2", value="**Hidden**", inline=True)
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
    # Helper function that checks if the user has reacted with a emote of interest
    def actionCheck(reaction, user):
        return user == playerObj and str(reaction.emoji) in Game.actionReactions
    # Check for bet amount from the user
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=actionCheck)
    except asyncio.TimeoutError:
        # if there is no response immediately fold
        await handMsg.delete()
        await fold(game, player)
        return
    # Delete the message
    await handMsg.delete()
    # Check if user is valid
    if user != None:
        if str(reaction.emoji) == Game.actionReactions[0]:
            # Check for hit
            await hit(client, game, player)
        if str(reaction.emoji) == Game.actionReactions[1]:
            # Check for stand
            await stand(game, player)
        elif str(reaction.emoji) == Game.actionReactions[2]:
            # Check for fold
            await fold(game, player)

# The player has folded for the round, end player's round and adjust balance
async def fold(game, player):
    # If a player folds, they lose half of their bet
    player.updateBalance(-1 * (player.bet // 2))
    response = "**Round " + str(game.round) + "**\n"
    response += "You have folded. You recieved half your bet back.\n"
    response += "You lost **$" + str(player.bet // 2) + "**.\n"
    response += "Current Balance: **$" + str(player.money) + "**\n"
    response += "Waiting on others to finish the round."
    embed = discord.Embed(title="You Folded", description=response, colour=discord.Colour.dark_gray())
    playerObj = await game.guild.fetch_member(player.userid)
    await playerObj.send(embed=embed)
    # Set value to -1 to indicate fold
    player.value = -1
    # Notify that the player is done
    player.done = True

# The player has stand for the round, so end round and wait for comparison
async def stand(game, player):
    response = "**Round " + str(game.round) + "**\n"
    response += "You stood. Waiting for the dealer's turn.\n"
    response += "Final Value: **" + str(player.value) + "**\n"
    if player.value == 21:
        response += "You got a blackjack!\n"
        player.blackjacks += 1
    response += "Waiting on others to finish the round.\n"
    response += "**Your Cards:**"
    embed = discord.Embed(title="You Stood", description=response, colour=discord.Colour.dark_gray())
    # Display the cards
    cardNum = 1
    for card in player.hand:
        embed.add_field(name="Card " + str(cardNum), value=str(card), inline=True)
        cardNum += 1
    embed.add_field(name="Your Value:", value=str(player.value), inline=False)
    playerObj = await game.guild.fetch_member(player.userid)
    await playerObj.send(embed=embed)
    # Notify that the player is done
    player.done = True

# Reprompt the player's hand without the ability to fold
async def hit(client, game, player):
    # Add new card to players hand and recalculate hand
    player.drawCard()
    player.calculateValue()
    # Check for bust
    if player.value > 21:
        await bust(game, player)
        return
    response = "**Round " + str(game.round) + "**\n"
    response += "You have hit. A new card has been given to you.\n"
    response += "Here are your cards. React to hit or stand.\n"
    response += "You have 30 seconds to make a decision.\n"
    response += "**Your Cards:**"
    embed = discord.Embed(title="Your Hand", description=response, colour=discord.Colour.dark_gray())
    # Display the cards
    cardNum = 1
    for card in player.hand:
        embed.add_field(name="Card " + str(cardNum), value=str(card), inline=True)
        cardNum += 1
    # Display the hand value
    embed.add_field(name="Hand Value", value=str(player.value) + "\n\n**Dealer's Cards:**", inline=False)
    # Display the dealer's cards
    embed.add_field(name="Card 1", value=str(game.dealer[0]), inline=True)
    embed.add_field(name="Card 2", value="**Hidden**", inline=True)
    # Display the actions
    actionStr = ""
    for i in range(len(Game.actions) - 1):
        actionStr += Game.actionReactions[i] + " for " + Game.actions[i] + "\n"
    embed.add_field(name="Actions", value=actionStr, inline=False)
    playerObj = await game.guild.fetch_member(player.userid)
    handMsg = await playerObj.send(embed=embed)
    # React with all the actions
    for actionReaction in Game.actionReactions:
        # Do not react with fold
        if actionReaction != Game.actionReactions[2]:
            await handMsg.add_reaction(actionReaction)
    # Helper function that checks if the user has reacted with a emote of interest
    def actionCheck(reaction, user):
        return user == playerObj and str(reaction.emoji) in Game.actionReactions and str(reaction.emoji) != Game.actionReactions[2]
    # Check for bet amount from the user
    try:
        reaction, user = await client.wait_for('reaction_add', timeout=30.0, check=actionCheck)
    except asyncio.TimeoutError:
        # if there is no response immediately stand
        await handMsg.delete()
        await stand(game, player)
        return
    # Delete the message
    await handMsg.delete()
    # Check if user is valid
    if user != None:
        if str(reaction.emoji) == Game.actionReactions[0]:
            # Check for hit
            await hit(client, game, player)
        if str(reaction.emoji) == Game.actionReactions[1]:
            # Check for stand
            await stand(game, player)

# The player has busted so they lose the round regardless of the dealer's cards
async def bust(game, player):
    # Player loses bet
    player.updateBalance(-1 * player.bet)
    response = "**Round " + str(game.round) + "**\n"
    response += "You busted! You have lost the round.\n"
    response += "Final Value: **" + str(player.value) + "**\n"
    response += "You lost **$" + str(player.bet) + "**.\n"
    response += "Current Balance: **$" + str(player.money) + "**\n"
    response += "Waiting on others to finish the round.\n"
    response += "**Your Cards:**"
    embed = discord.Embed(title="You Busted", description=response, colour=discord.Colour.red())
    # Display the cards
    cardNum = 1
    for card in player.hand:
        embed.add_field(name="Card " + str(cardNum), value=str(card), inline=True)
        cardNum += 1
    embed.add_field(name="Your Value:", value=str(player.value), inline=False)
    playerObj = await game.guild.fetch_member(player.userid)
    await playerObj.send(embed=embed)
    # Notify that the player is done and lost
    player.done = True
    player.result = "L"

# Compares the player's value to the dealer's value
async def compareToDealer(game, player):
    # If dealer busts and the player has not, then the player wins
    if game.dealerVal > 21:
        await win(game, player)
    else:
        # Determine win, loss, push based on values
        if player.value > game.dealerVal:
            await win(game, player)
        elif player.value == game.dealerVal:
            await push(game, player)
        else:
            await loss(game, player)

# Send message to player that they won the round
async def win(game, player):
    # $3 to $2 for bet upon winning
    player.updateBalance((player.bet // 2) + player.bet)
    player.wonrounds += 1
    player.moneywon += (player.bet // 2) + player.bet
    response = "**Round " + str(game.round) + "**\n"
    response += "You won the round! You have been given $3 for every $2 you bet.\n"
    response += "Final Value: **" + str(player.value) + "**\n"
    response += "You won **$" + str((player.bet // 2) + player.bet) + "**!\n"
    response += "Current Balance: **$" + str(player.money) + "**\n"
    response += "Waiting on others to finish the round.\n"
    response += "**Your Cards:**"
    embed = discord.Embed(title="You Won", description=response, colour=discord.Colour.green())
    # Display the cards
    cardNum = 1
    for card in player.hand:
        embed.add_field(name="Card " + str(cardNum), value=str(card), inline=True)
        cardNum += 1
    embed.add_field(name="Your Value:", value=str(player.value) + "\n\n**Dealer's Cards:**", inline=False)
    # Display the dealer's cards
    cardNum = 1
    for card in game.dealer:
        embed.add_field(name="Card " + str(cardNum), value=str(card), inline=True)
        cardNum += 1
    # Display dealer's value
    dealerVal = str(game.dealerVal)
    if game.dealerVal > 21:
        dealerVal += " (Bust)"
    embed.add_field(name="Dealer's Value:", value=str(dealerVal), inline=False)
    playerObj = await game.guild.fetch_member(player.userid)
    await playerObj.send(embed=embed)
    # Notify player has won
    player.result = "W"

# Send message to player that they tied the round
async def push(game, player):
    response = "**Round " + str(game.round) + "**\n"
    response += "The dealer had the same value. Your balance remains unchanged.\n"
    response += "Final Value: **" + str(player.value) + "**\n"
    response += "Current Balance: **$" + str(player.money) + "**\n"
    response += "Waiting on others to finish the round.\n"
    response += "**Your Cards:**"
    embed = discord.Embed(title="Push", description=response, colour=discord.Colour.dark_gray())
    # Display the cards
    cardNum = 1
    for card in player.hand:
        embed.add_field(name="Card " + str(cardNum), value=str(card), inline=True)
        cardNum += 1
    embed.add_field(name="Your Value:", value=str(player.value) + "\n\n**Dealer's Cards:**", inline=False)
    # Display the dealer's cards
    cardNum = 1
    for card in game.dealer:
        embed.add_field(name="Card " + str(cardNum), value=str(card), inline=True)
        cardNum += 1
    # Display dealer's value
    dealerVal = str(game.dealerVal)
    if game.dealerVal > 21:
        dealerVal += " (Bust)"
    embed.add_field(name="Dealer's Value:", value=str(dealerVal), inline=False)
    playerObj = await game.guild.fetch_member(player.userid)
    await playerObj.send(embed=embed)
    # Notify the player has push
    player.result = "P"

# Send message to player that they lost the round
async def loss(game, player):
    # lose the entire bet
    player.updateBalance(-1 * player.bet)
    response = "**Round " + str(game.round) + "**\n"
    response += "You lost the round. Your bet has been taken away.\n"
    response += "Final Value: **" + str(player.value) + "**\n"
    response += "You lost **$" + str(player.bet) + "**.\n"
    response += "Current Balance: **$" + str(player.money) + "**\n"
    response += "Waiting on others to finish the round.\n"
    response += "**Your Cards:**"
    embed = discord.Embed(title="You Lost", description=response, colour=discord.Colour.red())
    # Display the cards
    cardNum = 1
    for card in player.hand:
        embed.add_field(name="Card " + str(cardNum), value=str(card), inline=True)
        cardNum += 1
    embed.add_field(name="Your Value:", value=str(player.value) + "\n\n**Dealer's Cards:**", inline=False)
    # Display the dealer's cards
    cardNum = 1
    for card in game.dealer:
        embed.add_field(name="Card " + str(cardNum), value=str(card), inline=True)
        cardNum += 1
    # Display dealer's value
    dealerVal = str(game.dealerVal)
    if game.dealerVal > 21:
        dealerVal += " (Bust)"
    embed.add_field(name="Dealer's Value:", value=str(dealerVal), inline=False)
    playerObj = await game.guild.fetch_member(player.userid)
    await playerObj.send(embed=embed)
    # Notify the player has lost
    player.result = "L"

# Displays the leaderboard
async def displayLeaderboard(client, guild, channel):
    changeReactions = [u"\U0001F1FC", u"\U0001F1E7", u"\U0001F1F2"]
    first = True
    while guild != None:
        if first == True:
            embed = await setEmbedRoundsWon(guild, changeReactions)
            msg = await channel.send(embed=embed)
            await msg.add_reaction(changeReactions[1])
            await msg.add_reaction(changeReactions[2])
        # Wait for reaction
        def actionCheck(reaction, user):
            return user.bot == False and str(reaction.emoji) in changeReactions
        # Check for display change
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=actionCheck)
        except asyncio.TimeoutError:
            # if there is no response remove the msg
            await msg.delete()
            return
        # Take the reaction and adjust display
        if user != None:
            if str(reaction.emoji) == changeReactions[0]:
                embed = await setEmbedRoundsWon(guild, changeReactions)
                await msg.edit(embed=embed)
                await msg.clear_reactions()
                await msg.add_reaction(changeReactions[1])
                await msg.add_reaction(changeReactions[2])
            elif str(reaction.emoji) == changeReactions[1]:
                embed = await setEmbedBlackjacks(guild, changeReactions)
                await msg.edit(embed=embed) 
                await msg.clear_reactions()
                await msg.add_reaction(changeReactions[0])
                await msg.add_reaction(changeReactions[2])
            elif str(reaction.emoji) == changeReactions[2]:
                embed = await setEmbedMoneyWon(guild, changeReactions)
                await msg.edit(embed=embed) 
                await msg.clear_reactions()
                await msg.add_reaction(changeReactions[0])
                await msg.add_reaction(changeReactions[1])
        # Set first to false
        first = False

# Set embed for most rounds won
async def setEmbedRoundsWon(guild, changeReactions):
    # Set embed to rounds won
    response = "Players Who Have Won The Most Rounds"
    embed = discord.Embed(title='Blackjack Leaderboard', description=response, colour=discord.Colour.dark_gray())
    # Obtain all players on the server
    playersInServer = []
    for member in guild.members:
        if member.id in players:
            playersInServer.append(players[member.id])
    # Sort the players according to most rounds won
    playersInServer = sorted(playersInServer, key=(lambda x: x.wonrounds), reverse=True)
    count = 1
    # Display the players
    for player in playersInServer:
        position = ""
        if count == 1:
            position += "1st"
        elif count == 2:
            position += "2nd"
        elif count == 3:
            position += "3rd"
        else:
            position += str(count) + "th"
        title = position + " Place"
        playerObj = await guild.fetch_member(player.userid)
        response = playerObj.display_name + "\n"
        response += "Rounds Won: " + str(player.wonrounds) + "\n"
        response += "Balance: $" + str(player.money)
        embed.add_field(name=title, value=response, inline=False)
        count += 1
    # Check if count has ever been incremented
    if count == 1:
        response = "There are currently no registered players. Play a blackjack game or slot machine to register. "
        response += "You may also register by calling **!blackjack balance**."
        embed.add_field(name="No Players", value=response, inline=False)
    # Display change info
    response = changeReactions[1] + " for most blackjacks\n"
    response += changeReactions[2] + " for most money won"
    embed.add_field(name="Change Display", value=response, inline=False)
    return embed

# Set embed for most rounds won
async def setEmbedBlackjacks(guild, changeReactions):
    # Set embed to blackjacks
    response = "Players Who Have Gotten The Most Blackjacks"
    embed = discord.Embed(title='Blackjack Leaderboard', description=response, colour=discord.Colour.dark_gray())
    # Obtain all players on the server
    playersInServer = []
    for member in guild.members:
        if member.id in players:
            playersInServer.append(players[member.id])
    # Sort the players according to most rounds won
    playersInServer = sorted(playersInServer, key=(lambda x: x.blackjacks), reverse=True)
    count = 1
    # Display the players
    for player in playersInServer:
        position = ""
        if count == 1:
            position += "1st"
        elif count == 2:
            position += "2nd"
        elif count == 3:
            position += "3rd"
        else:
            position += str(count) + "th"
        title = position + " Place"
        playerObj = await guild.fetch_member(player.userid)
        response = playerObj.display_name + "\n"
        response += "Blackjacks: " + str(player.blackjacks) + "\n"
        response += "Balance: $" + str(player.money)
        embed.add_field(name=title, value=response, inline=False)
        count += 1
    # Check if count has ever been incremented
    if count == 1:
        response = "There are currently no registered players. Play a blackjack game or slot machine to register. "
        response += "You may also register by calling **!blackjack balance**."
        embed.add_field(name="No Players", value=response, inline=False)
    # Display change info
    response = changeReactions[0] + " for most rounds won\n"
    response += changeReactions[2] + " for most money won"
    embed.add_field(name="Change Display", value=response, inline=False)
    return embed

# Set embed for most money won
async def setEmbedMoneyWon(guild, changeReactions):
    # Set embed to money
    response = "Players Who Have Gained the Most Money from Wins"
    embed = discord.Embed(title='Blackjack Leaderboard', description=response, colour=discord.Colour.dark_gray())
    # Obtain all players on the server
    playersInServer = []
    for member in guild.members:
        if member.id in players:
            playersInServer.append(players[member.id])
    # Sort the players according to most rounds won
    playersInServer = sorted(playersInServer, key=(lambda x: x.moneywon), reverse=True)
    count = 1
    # Display the players
    for player in playersInServer:
        position = ""
        if count == 1:
            position += "1st"
        elif count == 2:
            position += "2nd"
        elif count == 3:
            position += "3rd"
        else:
            position += str(count) + "th"
        title = position + " Place"
        playerObj = await guild.fetch_member(player.userid)
        response = playerObj.display_name + "\n"
        response += "Money Won: $" + str(player.moneywon) + "\n"
        response += "Balance: $" + str(player.money)
        embed.add_field(name=title, value=response, inline=False)
        count += 1
    # Check if count has ever been incremented
    if count == 1:
        response = "There are currently no registered players. Play a blackjack game or slot machine to register. "
        response += "You may also register by calling **!blackjack balance**."
        embed.add_field(name="No Players", value=response, inline=False)
    # Display change info
    response = changeReactions[0] + " for most rounds won\n"
    response += changeReactions[1] + " for most blackjacks"
    embed.add_field(name="Change Display", value=response, inline=False)
    return embed

# Command for playing slots
usage = "Command used to display the slot machine. It is direct messaged to you."
# Format: !slots
try:
    commandList.append(Command("!slots", "runSlots", usage))
except:
    pass

# Runs the slot machine
async def runSlots(client, message):
    # Check if user is already playing slots
    if message.author.id in slots:
        # Notify user that slot machine is already running
        response = "The slot machine is already running!"
        embed = discord.Embed(title='Slots Running', description=response, colour=discord.Colour.red())
        embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
        await message.channel.send(embed=embed)
    else:
        # Check to see if Player object exists for user
        if message.author.id not in players:
            players[message.author.id] = Player(message.author.id)
        # Create new slot machine for the user
        if players[message.author.id].ingame == False:
            slots[message.author.id] = Slot(players[message.author.id])
            slot = slots[message.author.id]
            # Send notification to check dms
            response = "The slot machine has been created. Please check your dms!"
            embed = discord.Embed(title='Slots', description=response, colour=discord.Colour.greyple())
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)
            # Notify that the player is currently in game
            slot.player.ingame = True
            await slotMachine(client, slot, message.author)
            # Once slots is over, notify user is no longer in a game
            slot.player.ingame = False
        else:
            # Notify that the user is currently in a game
            response = "You are currently in a game! Slot machine not created."
            embed = discord.Embed(title='In Game', description=response, colour=discord.Colour.red())
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar_url)
            await message.channel.send(embed=embed)

# Runs the slot machine
async def slotMachine(client, slot, playerObj):
    while slot != None:
        slot.setEmbed()
        slot.sm = await playerObj.send(embed=slot.embed)
        for reaction in Slot.betReactions:
            await slot.sm.add_reaction(reaction)
        await slot.sm.add_reaction(Slot.exitReaction)
        # Wait for response
        def reactionCheck(reaction, user):
            return user == playerObj and (str(reaction.emoji) in Slot.betReactions or str(reaction.emoji) == Slot.exitReaction)
        # Check for bet amount from the user
        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=reactionCheck)
        except asyncio.TimeoutError:
            # if there is no response, end the slot machine
            await slot.end()
            response = "Due to inactivity, the slot machine has been removed."
            embed = discord.Embed(title='Slots Ended', description=response, colour=discord.Colour.red())
            await playerObj.send(embed=embed)
            return
        # Parse the reaction and bet
        if user != None and reaction != None:
            for i in range(len(Slot.betAmounts)):
                if str(reaction.emoji) == Slot.betReactions[i]:
                    bet = Slot.betAmounts[i]
                    slot.player.updateBalance(-1 * bet)
                    slot.updateBalance()
                    await slot.sm.edit(embed=slot.embed) 
                    break
            # Check if player reacted to end the slot machine
            if str(reaction.emoji) == Player.exitReaction:
                await slot.end()
                response = "Thanks for playing! The slot machine has been removed."
                embed = discord.Embed(title='Slots Ended', description=response, colour=discord.Colour.blurple())
                await playerObj.send(embed=embed)
                return
            # Update the bet
            slot.updateWinnings(bet)
            await slot.sm.edit(embed=slot.embed) 
            # Run the slots
            for _ in range(6):
                slot.updateNumbers()
                await slot.sm.edit(embed=slot.embed)
                await asyncio.sleep(0.8)
            # Check winnings
            winnings = slot.calculateWinnings(bet)
            slot.player.updateBalance(winnings)
            slot.updateBalance()
            await slot.sm.edit(embed=slot.embed) 
            # Update winnings and balance
            slot.embed.remove_field(len(slot.embed.fields) - 1)
            if winnings == 0:
                response = "You didn't win anything. Better luck next time!"
                slot.embed.add_field(name="Winnings", value=response, inline=False)
            else:
                response = "You won $" + str(winnings) + "!"
                slot.embed.add_field(name="Winnings", value=response, inline=False)
            await slot.sm.edit(embed=slot.embed)
            # Wait for the next round
            await asyncio.sleep(5)
            await slot.sm.delete()