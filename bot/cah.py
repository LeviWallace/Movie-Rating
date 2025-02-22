import discord
from discord.ext import commands

import json
import random

import lobby
import util


"""
FUNCTIONS NEEDED

|cah -> if first user, cza

Start lobby - 
Join lobby - waits until start of a round
Start game - Begins first round
Draw cards - make sure to draw to 7
Select card to play
Discard 
Kick
Leave


JSON FILE PSEUDO
{deckInfo:{blackCards:{id:{text:text, picks:picks}}, whiteCards:{id:{text:text}}},
 gameInfo:{users:{userID:{points: points, hand:[cardIDs]}}, lobby:[userID], tsar:userID, cards:[cardIDs], discard:[cardIDs], cardsRound: {cardID: userID}}}

"""
   

class CAH(commands.Cog, name="cah"):
    def __init__(self, bot):
        self.bot = bot
        #self.gameChannel = None
        self.lobby = self.bot.get_cog("Lobby")
        self.cah = {"state": 0, "users": {}, "czar": 0, "blackCard": 0 , "whiteCardPile": [], "blackCardPile": [], "discard": [], "cardsRound": {}, "phase": "draw"}


    async def start(self):
        print("Test")
        
        # TEMP NUM 
        #self.gameChannel = ctx.guild.get_channel(704835784703737957)
        if len(await self.lobby.getLobby()) > 0:
            with open("cah.json", "r") as f:
                cah = json.load(f)
            userIDs = self.lobby.getLobby()
            for userID in userIDs:
                self.cah["users"][userID] = {}
                self.cah["users"][userID]["points"] = []
                self.cah["users"][userID]["hand"] = []
            #TODO: Put here a reset to stats in game (discard, points, ect.)
            self.cah["whiteCardPile"] = list(range(len(cah["whiteCards"])))
            self.cah["blackCardPile"] = list(range(len(cah["blackCards"])))
            random.shuffle(self.cah["whiteCardPile"])
            random.shuffle(self.cah["blackCardPile"])
            self.cah["discard"] = []
            self.cah["czar"] = 0
            await self.checkPhase()
        else:
            await ctx.send("There aren't enough people in the lobby!")

    
    async def removeUser(self, userID):
        if userID in list(self.cah["users"]):
            if len(list(self.cah["users"])) <= 2:
                await self.sendAllUsers("There aren't enough players after {} left! The game is now closing".format(await util.getName(userID)))
                self.cah["phase"] = "end"
            elif list(self.cah["users"]).index(userID) == self.cah["czar"]:
                self.cah["phase"] = "draw"
                self.cah["cardsRound"] = {}
                await self.sendAllUsers("The czar has left! New round is going to begin")
            del self.cah["users"][userID]
            await self.checkPhase()


    async def checkPhase(self):
        while True:
            if self.cah["phase"] == "draw":
                #   Black card stuff 
                self.cah["blackCard"] = self.cah["blackCardPile"].pop(0)
                await self.sendAllUsers("{} is the czar! They will be selecting the best answer for:\n{}".format(
                    await util.getName(list(self.cah["users"])[self.cah["czar"]]), await CAH.getCardName(self.cah["blackCard"], False)))
                #   Making sure everyone has enough cards
                userIDs = list(self.cah["users"])
                for userID in userIDs:
                    for i in range(7 - len(self.cah["users"][userID]["hand"])):
                        self.cah["users"][userID]["hand"].append(self.cah["whiteCardPile"].pop(0))
                    user = self.bot.get_user(int(userID))
                    if user.dm_channel is None:
                         await user.create_dm()
                    if userIDs.index(userID) == self.cah["czar"]:  
                        await user.dm_channel.send("You are the czar. Wait for the players to choose their cards.")
                    else:  
                        await user.dm_channel.send("Your points: {}\nYour Hand:\n{}".format(
                        len(self.cah["users"][userID]["points"]), 
                        await self.getPlayerHand(userID)))
                #   Sending everyone their information
                # await self.sendAllUsers("Please choose your card by using |select <Card number (the number to the left)>",
                #     userLambda=lambda i: "Your points: {}\nYour Hand:{}".format(
                #         len(self.cah["users"][i]["points"]), 
                #         self.getPlayerHand(i)),
                #     czar="You are the czar. Wait for the players to choose their cards.",
                #     czarSkip=True)
                #   Ending the phase. This makes the waiting begin
                self.cah["phase"] = "playersSelect"
                
            #   If both of these are true, this means that everyone has submitted a card
            if self.cah["phase"] == "playersSelect" and len(list(self.cah["cardsRound"])) == len(list(self.cah["users"])) - 1:
                random.shuffle(self.cah["cardsRound"])
                cardNames = [await CAH.getCardName(x, True) for x in list(self.cah["cardsRound"])]
                await self.sendAllUsers("Here are the cards selected to answer {}:\n {}\n Czar {} will now be choosing the winning card!".format(
                    await self.getCardName(self.cah["blackCard"], False),
                    await util.genList(cardNames, dashed=False, numbered=True),
                    await util.getName(list(self.cah["users"])[self.cah["czar"]])),
                    czar = "Please choose the winning card by using |select <Card number (the number to the left)>")
                self.cah["phase"] = "czarSelect"
            if self.cah["phase"] == "checkWinner":
                self.cah["cardsRound"] = {}
                userIDs = list(self.cah["users"])
                for userID in userIDs:
                    if len(self.cah["users"][userID]["points"]) > 1:
                        user = await util.getName(userID)
                        await self.sendAllUsers("{} has won!".format(user))
                        # await self.sendAllUsers("{} has won by winning the following rounds!\n {}".format(
                        #     user,
                        #     await util.genList(self.cah["users"][userID]["points"], keyWordLam=lambda i:CAH.getCardName(i, False), dashed=False, numbered=False)))
                        await self.sendAllUser("\n\nThe game has finished! Sending players back to lobby!\n")
                        await self.lobby.finish()
                        return
                # newUsers = await lobby.Lobby.pullLobby()
                # for userID in newUsers:
                #     self.cah["users"][userID] = {}
                #     self.cah["users"][userID]["points"] = []
                #     self.cah["users"][userID]["hand"] = []
                self.cah["czar"] = (self.cah["czar"] + 1) % len(list(self.cah["users"]))
                self.cah["phase"] = "draw"
                continue
            return


    async def sendAllUsers(self, message = " ", userLambda=lambda i:" ", czar="", czarSkip = False):
        userIDs = list(self.cah["users"])
        for userID in userIDs:
            user = self.bot.get_user(int(userID))
            if user.dm_channel is None:
                await user.create_dm()
            if userIDs.index(userID) == self.cah["czar"]:
                if czar:
                    await user.dm_channel.send(czar)
                if czarSkip:
                    continue
            await user.dm_channel.send("{}{}".format(userLambda(userID),message))
            

    
    @staticmethod    
    async def getCardName(id, isWhite):
        with open("cah.json", "r") as f:
            cah = json.load(f)
        if isWhite:
            return "*" + cah["whiteCards"][id] + "*"
        return "**" + cah["blackCards"][id]["text"] + "**"


    async def getPlayerHand(self, id):
        cardNames = [await CAH.getCardName(i, True) for i in self.cah["users"][id]["hand"]]
        return await util.genList(cardNames, dashed=False, numbered=True)
        

    @commands.command()
    async def select(self, ctx, *, message=None):
        author = str(ctx.author.id)
        if self.cah["phase"] == "playersSelect":
            if author == list(self.cah["users"])[self.cah["czar"]]:
                await ctx.send("You are the czar, you do not select until all of the players have chosen their cards")
                return
            else:
                maxNum = 7
        elif self.cah["phase"] == "czarSelect":
            if author == list(self.cah["users"])[self.cah["czar"]]:
                maxNum = len(list(self.cah["cardsRound"])) + 1
            else:
                await ctx.send("You are not the czar, you do not select the winning card")
                return
        else:
            return
        if message is None:
            await ctx.send("Please type in a number between 1 and {}".format(maxNum))
            return
        try:
            num = int(message) - 1
        except ValueError:
            await ctx.send("The input you have given is not an integer (whole number)")
            return 
        if not 0 <= num < maxNum:
            await ctx.send("The input you have given is not between 1 and {}".format(maxNum))
            return
        
        if author == list(self.cah["users"])[self.cah["czar"]]:
            selectedCard = list(self.cah["cardsRound"])[num]
            winner = self.cah["cardsRound"][selectedCard]
            self.cah["users"][winner]["points"].append(self.cah["blackCard"])
            await ctx.send("{} has selected {}, which was played by {}!".format(await util.getName(author), await CAH.getCardName(selectedCard, True), await util.getName(winner)))
            self.cah["phase"] = "checkWinner"
        else:
            selectedCard = self.cah["users"][author]["hand"].pop(num)
            self.cah["cardsRound"][selectedCard] = author
            user = self.bot.get_user(int(author))
            await user.dm_channel.send("{} has been played!".format(await CAH.getCardName(selectedCard, True)))
            await self.sendAllUsers("{} has selected their card!".format(await util.getName(author)))
        await self.checkPhase()
                

    @commands.command()
    async def addCard(self, ctx, *, message = None):
        if message is None:
            await ctx.send("Please type in the type of card you want to add, followed by its text\nExample of what to type>>> |addCard white Ethan's Big Dick")
            return
        message = message.split()
        print(message)
        if not message[0].lower() == "white" and not message[0].lower() == "black":
            await ctx.send("Please start by specifying what type of card you want to add, then follow it with the text\nExample of what to type>>> |addCard white Ethan's Big Dick")
            return
        with open("cah.json", "r") as f:
            cah = json.load(f)
        if message[0].lower() == "white":
            txt = " ".join(message[1:])
            if txt in cah["whiteCards"]:
                await ctx.send("That White Card is already in the deck")
                return
            cah["whiteCards"].append(txt)
            await ctx.send("The White Card: *{}* has been added!".format(txt))
        else:
            txt = " ".join(message[1:])
            if txt in [i["text"] for i in list(cah["blackCards"])]:
                await ctx.send("That Black Card is already in the deck")
                return
            cah["blackCards"].append({"text":txt,"pick":1})
            await ctx.send("The Black Card: **{}** has been added!".format(txt))
            
        with open("cah.json", "w") as f:
            json.dump(cah, f)
    
            
            
            # await user.dm_channel.send("Card played")
        # for userID in userIDs:
        #     if userID == cah["gameInfo"]["czar"]:
        #         continue
        #     user = self.bot.get_user(int(userID))
        #     if user.dm_channel == None:
        #         await user.create_dm()

        #     # is the message valid.
        #     #await user.dm_channel.send(await util.genList(cardNames, dictLam=lambda i: " ", dashed=False, numbered=True))
            #await user.dm_channel.send("Please select the card by type the number")


        
    # async def getInput(self):
    #     userIDs = list(self.cah["gameInfo"]["users"])
    #     def check(m):
    #         #TODO: Add a check to make sure this is not the czar
    #         try:
    #             num = int(m.content)
    #             return 1 <= num <= 7 
    #         except ValueError:
    #             return False
        
    #     answer = await self.bot.wait_for('message', check = check, timeout=10)
    #     author = answer.author
    #     if author.dm_channel == None:
    #         await author.create_dm()
    #     userID = str(author.id)
    #     selectedCard = list(self.cah["gameInfo"]["users"][userID]["hand"]).pop(int(answer.content) - 1)
    #     self.cah["gameInfo"]["cardsRound"][selectedCard] = userID
    #     await author.dm_channel.send("{} has been played!".format(await self.getCardName(selectedCard, True)))
        


