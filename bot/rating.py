import discord
from discord.ext import commands

import json
import random

import util


class Rating(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Used to set a default movie for rating
    # COMMAND PARAMETERS: The name of the movie (Doesn't handle None type)
    @commands.command()
    async def setPointer(self, ctx, *, message):
        if await util.authorize(ctx.author.id):
            with open("ratings.json", "r") as f:
                rate = json.load(f)
            message = await util.title(str(message))

            rate["pointer"] = message
            if not message in rate["movies"]:
                rate["movies"][message] = {}
                rate["movies"][message]["users"] = {}
                rate["movies"][message]["avg"] = -1

            await ctx.send("Movie has been chosen: {}".format(message))
            with open("ratings.json", "w") as f:
                json.dump(rate, f)
        else:
            await ctx.send("Permission not granted.")

    # Used to retrieve the current default movie for rating
    @commands.command()
    async def getPointer(self, ctx, *, message=None):
        with open("ratings.json", "r") as f:
            rate = json.load(f)

        await ctx.send("The movie selected is {}!".format(rate["pointer"]))

    # Used to rate movies
    # COMMAND PARAMETERS: The name of the movie (optional, if None then substitute with pointer), the rating out of 10 (error handled if not given, or if not supplied correctly)
    @commands.command()
    async def rate(self, ctx, *, message):
        with open("ratings.json", "r") as f:
            rate = json.load(f)

        message = str(message).split()
        if len(message) > 1:
            try:
                num = round(float(message.pop(-1)), 1)
            except ValueError:
                await ctx.send("Please type in a number")
                await ctx.send("Example of what to type:\n>>> |rate Star Wars 6.9")
                return
            movie = await util.title(message)

            movies = list(rate["movies"])
            if not movie in movies:
                await ctx.send("Please only rate movies in the list. You can use |ls to see all of the movies")
                await ctx.send("Example of what to type:\n>>> |rate Star Wars 6.9")
                return
        else: 
            try:
                num = round(float(message[0]), 1)
                movie = rate["pointer"]
            except ValueError:
                await ctx.send("Please type in a number")
                await ctx.send("Example of what to type:\n>>> |rate 6.9")
                return
            

        if not 0 <= num <= 10:
            await ctx.send("Please enter a number between 0 and 10")
            await ctx.send("Example of what to type:\n |rate Star Wars 6.9")
            return
        author = await util.checkAlt(str(ctx.author.id))
        rate["movies"][movie]["users"][author] = str(num)

        rate["movies"][movie]["avg"] = await util.calcAvg(rate["movies"][movie]["users"])
        await ctx.send("{}'s rating for *{}* has been updated to {}!".format(await util.getName(author), movie, num))

        with open("ratings.json", "w") as f:
            json.dump(rate, f)

    # Used to 
    @commands.command()
    async def look(self, ctx, *, message=None):
        with open("ratings.json", "r") as f:
            rate = json.load(f)
        with open("users.json", "r") as f:
            users = json.load(f)

        startList = 0
        endList = None 
        author = await util.checkAlt(str(ctx.author.id))
        
        if message is not None:
            message = str(message).split()
            author = await util.checkAlt(await util.getUserID(message[0]))
            if len(message) == 2:
                if message[1] == 'all':
                    endList = None
                else:
                    endList = int(message[1])
            elif len(message) == 3:
                startList = int(message[1])
                endList = int(message[2])
            

        if not author:
            await ctx.send("Please enter in a valid name. Ex: \n>>> '|look Levi' or \n'|look @J Dog'")
            return
             
        authorName = users[author]["nameIRL"]
        movies = list(rate["movies"])
        ratedMovies = set()
        for i in movies:
            if author in rate["movies"][i]["users"]:
                ratedMovies.add(i)
        unratedMovies = list(set(movies) - ratedMovies)
        ratedMovies = list(ratedMovies)
        ratedMovies.sort(key = lambda i:float(rate["movies"][i]["users"][author]), reverse=True)
        if (len(ratedMovies) > 0):
            await ctx.send("{} has given a rating for:\n{}".format(authorName, await util.genList(ratedMovies, dictLam=lambda i: rate["movies"][i]["users"][author], startIdx = startList, endIdx = endList))) 
        else:
            await ctx.send("{} has not rated any movies".format(authorName))
        if (len(unratedMovies) > 0):       
            await ctx.send("\n{} has not rated:\n{}".format(authorName, await util.genList(unratedMovies, dashed=False)))
        else:
            await ctx.send("{} is all caught up!".format(authorName))
        
    @commands.command()
    async def addMovie(self, ctx, *, message):
        if await util.authorize(ctx.author.id):
            with open("ratings.json", "r") as f:
                rate = json.load(f)

            movie = await util.title(str(message))
            if movie in list(rate["movies"]):
                await ctx.send("Movie has already been entered.")
                return

            rate["movies"][movie] = {}
            rate["movies"][movie]["users"] = {}
            rate["movies"][movie]["avg"] = -1
            await ctx.send("Movie: {} has been added! Let the voting commence.".format(movie))

            with open("ratings.json", "w") as f:
                json.dump(rate, f)
        else:
            await ctx.send("Permission not granted.")

    @commands.command()
    async def ls(self, ctx, *, message=None):
        with open("ratings.json", "r") as f:
            rate = json.load(f)
        startList = 0
        endList = None
        if message == "all":
             endList = None
        elif not message is None:
            message = str(message).split()
            if len(message) > 1:
                if int(message[0]) < int(message[1]):
                    startList = int(message[0]) - 1
                    endList = int(message[1])
                else:
                    startList = int(message[1]) - 1
                    endList = int(message[0])
            else:
                endList = int(message[0])

        movieNames = list(rate["movies"])
        movieNames.sort(
            key=lambda movie: float(rate["movies"][movie]["avg"]), reverse=True)
        output = "{}\n{}".format(
            "Here are the movie ratings by our server",
            await util.genList(
                keyWords=movieNames,
                dictLam=lambda i: rate["movies"][i]["avg"],
                startIdx=startList,
                endIdx=endList,
                numbered=True))
        await ctx.send(output)

    @commands.command()
    async def lsv(self, ctx, *, message=None):
        with open("users.json", "r") as f:
            users = json.load(f)
        with open("ratings.json", "r") as f:
            rate = json.load(f)

        if message is None:
            await ctx.send("Please enter in a movie. Example: |lsv {}".format(random.choice(list(rate["movies"]))))
            return

        message = await util.title(str(message))
        movies = list(rate["movies"])
        if not message in movies:
            await ctx.send("Please enter in a valid movie, type |ls to see the list of valid movies")
            return

        userNames = list(rate["movies"][message]["users"])
        userNames.sort(
            key=lambda user: float(rate["movies"][message]["users"][user]), reverse=True)
        output = "The rating of {}:  \n{}\n The average score of the movie {} - **{}/10**".format(
            message,
            await util.genList(
                keyWords=userNames,
                dictLam=lambda i: rate["movies"][message]["users"][i],
                suffix="/10",
                keyWordLam=lambda i: users[i]["nameIRL"]),
            message,
            str(rate["movies"][message]["avg"]))
        await ctx.send(output)
