import discord
from discord.ext import commands

import json

import util


# Lobby: 
#   Stores players in the lobby, holds players that are waiting to join the game. 
#   Kick players from the game, or kick players from the lobby.
#
#
# Game:
#   should read from lobby holds players
#   Game has methods which lobby calls
#       A super class will be needed so all games have a uniform set of functions for lobby to call
#   Game doesn't know about lobby
#
#

class Lobby(commands.Cog, name="Lobby"):
    def __init__(self, bot):
        self.bot = bot
        self.game = None
        self.games = ["cah", "michelle"]

    @commands.command()
    async def join(self, ctx, *, message=None):
        with open("lobby.json", "r") as f:
            lobby = json.load(f)        
        user = await util.checkAlt(str(ctx.author.id))
        if user in list(lobby["users"]):
            await ctx.send("You, {}, are already in the lobby!".format(await util.getName(user)))
            return
        lobby["users"].append(user)
        await ctx.send("{} has joined the lobby!".format(await util.getName(user)))
        with open("lobby.json", "w") as f:
            json.dump(lobby, f)

    @commands.command()
    async def leave(self, ctx, *, message=None):
        with open("lobby.json", "r") as f:
            lobby = json.load(f)
        userID = await util.checkAlt(str(ctx.author.id))
        if userID not in list(lobby["users"]):
            await ctx.send("You, {}, are not in the lobby to begin with!".format(await util.getName(userID)))
            return
        lobby["users"].remove(userID)
        if not self.game is None:
            await self.game.removeUser(userID)
        await ctx.send("{} has left the lobby!".format(await util.getName(userID)))
        with open("lobby.json", "w") as f:
            json.dump(lobby, f)

    @commands.command()
    async def lobby(self, ctx, *, message=None):
        with open("lobby.json", "r") as f:
            lobby = json.load(f)  
        userNames = [await util.getName(id) for id in list(lobby["users"])]
        await ctx.send("Here is the list of people in the lobby:\n {}".format(await util.genList(userNames, dashed=False)))

    @commands.command()
    async def kick(self, ctx, *, message=None):
        with open("lobby.json", "r") as f:
            lobby = json.load(f)
        # Error Checking... 
        if message is None:
            await ctx.send("You need to say the name of the person you're trying to kick")
            return
        kickee = await util.getUserID(message)
        print(kickee)
        if kickee not in lobby["users"]:
            await ctx.send("The person you are trying to kick is not in the lobby!")
            return
        if not self.isInGame(kickee):
            await ctx.send("The person you are trying to kick is not in the game!")
            return
        # Adding people to the kick vote, which, once full, will kick the player
        if kickee not in lobby["kickVotes"]:
            lobby["kickVotes"][kickee] = []
        lobby["kickVotes"][kickee].append(await util.checkAlt(str(ctx.author.id)))
        # Checking if kick player is full
        if (len(lobby["kickVotes"][kickee]) > (len(lobby["users"])/2) or await util.authorize(ctx.author.id)) :
            lobby["users"].remove(kickee)
            if not self.game is None:
                await self.game.removeUser(userID)
            lobby["kickVotes"][kickee] = []
            await ctx.send("{} been has neutralized!".format(await util.getName(kickee)))
        else:
            await ctx.send("You have voted to kick, {}! You only need {} more vote{}!".format(
                await util.getName(kickee), 
                math.ceil(len(lobby["users"])/2) - len(lobby["kickVotes"][kickee], 
                "" if len(lobby["kickVotes"][kickee]) == 1 else "s")))
        with open("lobby.json", "w") as f:
            json.dump(lobby, f)

    @commands.command()
    async def start(self, ctx, *, message=None):
        print(message)
        if not message in self.games:
            await ctx.send("Please choose a game to start! Ex. |start <game>")
            return
        if not self.game is None:
            await ctx.send("A game is already running!")
            return
        message = message.lower().strip()
        self.game = self.bot.get_cog(message)
        if message == "michelle":
            await self.game.start(ctx)
            return
        await self.game.start()

    async def isInGame(self, userID) -> bool:
        if self.game is None:
            return False
        return self.game

    async def finish(user):
        await self.pushLobby(user)
        self.game = None

    async def getLobby(self):
        with open("lobby.json", "r") as f:
            lobby = json.load(f)

        users = lobby["users"]
        return users

    # take users from lobby and give to game       
    async def pullLobby(self):
        with open("lobby.json", "r") as f:
            lobby = json.load(f)

        users = lobby["users"]
        lobby = {"users": [], "kickVotes": {}}

        with open("lobby.json", "w") as f:
            json.dump(lobby, f)
        return users

    # take users from game and give to lobby
    async def pushLobby(self,users):
        with open("lobby.json", "r") as f:
            lobby = json.load(f)

        lobby = {"users": list(users), "kickVotes": {}}

        with open("lobby.json", "w") as f:
            json.dump(lobby, f)
        