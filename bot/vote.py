import discord
from discord.ext import commands

import json
import random

import util

class Vote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def createBallot(self, ctx, *, message=None):
        # with open("vote.json", "r") as f:
        #vote = json.load(f)
        if message is None:
            vote = {"users": {}, "items": {}, "rules": {
                "numVotes": -1, "adding": True}}
            await ctx.send("Ballot created. Default settings set.")
        else:

            message = str(message).split(",")
            for i in message:
                i.strip()

            vote = {"users": {}, "items": {message[item]: [] for item in range(
                2, len(message))}, "rules": {"numVotes": message[0], "adding": message[1]}}
            tempStr = ""
            for i in range(2, len(message)):
                tempStr += message[i] + ", "
            await ctx.send("Ballot created. Cusrom settings set: \n\
            Number of votes per person:   {}\n\
            Allow adding to the list:   {}\n\
            Beginning values:   {}".format(message[0], message[1], tempStr))

        with open("vote.json", "w") as f:
            json.dump(vote, f)

        print("Ballot Cleared")


    @commands.command()
    async def vote(self, ctx, *, message):
        with open("vote.json", "r") as f:
            vote = json.load(f)
        user = await util.checkAlt(str(ctx.author.id))

        message = await util.title(message)
        if (vote["rules"]["adding"] == "False") and (not message in vote["items"]):
            await ctx.send("No adding rule was enabled. Please only vote on items from the list below:")
            await self.results(ctx)
            return
        if user in vote["users"]:
            if int(vote["users"][user]) + 1 > int(vote["rules"]["numVotes"]) and int(vote["rules"]["numVotes"]) != -1:
                await ctx.send("You can only vote {0} number of times because a limit was set.".format(vote["rules"]["numVotes"]))
                return
        else:
            vote["users"][user] = 0
        if not message in vote["items"]:
            vote["items"][message] = []
        elif vote["items"][message].count(user) > 0:
            await ctx.send("You cannot vote for the same item twice")
            return

        vote["items"][message].append(user)
        vote["users"][user] += 1
        await ctx.send("Vote cast from {} for {}".format(await util.getName(user), message))

        with open("vote.json", "w") as f:
            json.dump(vote, f)


    @commands.command()
    async def results(self, ctx, *, message = None):
        with open("vote.json", "r") as f:
            vote = json.load(f)

        itemNames=list(vote["items"])
        if message is None:
            itemNames.sort(key=lambda item: len(vote["items"][item]), reverse=True)
            output = "Here is the current tally:\n" + await util.genList(itemNames, dictLam=lambda item: len(vote["items"][item]), numbered=True)
        else:
            message = await util.title(message)
            if message in itemNames:
                
                usernames = [await util.getName(i) for i in vote["items"][message]]
                output = "Here is who voted for {}:\n{}".format(message, await util.genList(usernames, dashed = False))
            else:
                output = "Couldn't find that voting item."
            
        await ctx.send(output)


    @commands.command()
    async def removeVote(self, ctx, *, message):
        with open("vote.json", "r") as f:
            vote = json.load(f)
        user = str(ctx.author.id)
        message = await util.title(message)
        if message in vote["items"]:
            if user in vote["items"][message]:
                vote["items"][message].remove(user)
                vote["users"][user] -= 1
                await ctx.send("Vote successfully removed")
            else:
                await ctx.send("Couldn't find your vote")
        else:
            await ctx.send("Couldn't find the item")

        with open("vote.json", "w") as f:
            json.dump(vote, f)


    @commands.command()
    async def delVote(self, ctx, *, message):
        with open("vote.json", "r") as f:
            vote = json.load(f)

        user = await util.checkAlt(str(ctx.author.id))
        movies = list(vote["items"])
        movie = await util.title(message)
        if not movie in movies:
            await ctx.send("This movie is not up for deletion. It has not been entered")
            return
        if await util.authorize(user):
            del vote["items"][movie]
            await ctx.send("The movie {} has been deleted!".format(movie))
        elif vote["rules"]["adding"] == True:
            if len(vote["items"][movie]) > 0:
                if vote["items"][movie][0] == user:
                    del vote["items"][movie]
                    await ctx.send("The movie {} has been deleted!".format(movie))
                else:
                    await ctx.send("You didn't create this ballot item, so you can't delete it.")
                    return
        else:
            await ctx.send("Permission not granted")
            return
        with open("vote.json", "w") as f:
            json.dump(vote, f)

    @commands.command()
    async def schedule(self, ctx, *, message):
        if await util.authorize(ctx.author.id):
            ctx.send("check")
        else:   
            await ctx.send("Permission not granted, work in progress") 

        
        
        
        


                        
        

        