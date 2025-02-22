import discord
from discord.ext import commands

import json
import random

import lobby
import util

# if you manage to type something in incorrectly you will penelized.
# Displays a picture
# Enter in yes if you think this is michelle obama, otherwise type no
# yes, no, y, n,
# if incorrect input, then it takes off a point
#
# (keep track of points)
# (keep track of wins)
# given 10 rounds
# if you get more than 5 you win


# 12 pictures of michelle obama
# 15 pictures of not michelle obama
# 3 jokes

class Michelle(commands.Cog, name="michelle"):
    def __init__(self, bot):
        self.bot = bot
        self.channel = None
        self.playerID = None

    @commands.command()
    async def michelle(self, ctx, *, message=None):
        self.gameChannel = ctx.guild.get_channel(704835784703737957)
        self.playerID = ctx.author.id
        await self.gameLoop(ctx)

    async def gameLoop(self, ctx):
        with open("michelle.json", "r") as f:
            michelle = json.load(f)
            f.close()
        random.shuffle(michelle["pictures"])  # mutates michelle
        score = 0
        for elem in michelle["pictures"]:
            print(elem)
            await ctx.send(elem["name"])  # sends lable: debugging
            # send the picture through discord
            await ctx.send(file=discord.File('pictures/test.png'))
            answer = await self.getInput(ctx)  # boolean answer
            await ctx.send(answer)  # debugging
            if answer == await Michelle.isMichelle(elem):
                score += 1
        await ctx.send("Your score was: {}".format(score))

        if score > len(michelle["pictures"])/2:
            if score == len(michelle["pictures"]) - 1:
                await ctx.send("Wow, that went well, congraduations you aced it!")
            else:
                await ctx.send("You won! You obtained a score of {} and above!".format(len(michelle["picture"])/2))
            if self.playerID not in michelle["wins"]:
                michelle["wins"][self.playerID] = 1
            else:
                michelle["wins"][self.playerID] += 1
        else:
            await ctx.send("Your score did not reach the requirement of a win, pulled a Justin. :( unlucky - Tyler")

    @staticmethod
    async def isMichelle(elem) -> bool:
        return elem['name'] == "Michelle Obama"

    async def getInput(self, ctx) -> bool:
        await ctx.send("Type 'yes' if you believe this is Michelle Obama. Type 'no' if you do not")
        await ctx.send("*PS. if it is neither, it will be read as 'no'")
        msg = await self.bot.wait_for('message', check=lambda msg: msg.author == ctx.author)
        msg.content.lower()
        return msg.content == 'yes' or msg.content == 'y'
