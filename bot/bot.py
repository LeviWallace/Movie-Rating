import discord
from discord.ext import commands

import os
import json

import vote
import rating
import util
import cah
import michelle
import lobby

os.chdir(r"C:\Users\Ethan\OneDrive\Desktop\Coding\Python\Project Discord")

TOKEN = "NjYwNjEzNjY0MzgxOTkyOTcx.XgfawQ.iCq8eJt1peyITPJ8J9JEiVtkOh8"

client = commands.Bot(command_prefix="|", help_command=None)
client.add_cog(vote.Vote(client))
client.add_cog(rating.Rating(client))
client.add_cog(cah.CAH(client))
client.add_cog(michelle.Michelle(client))
client.add_cog(lobby.Lobby(client))

@client.command()
async def help(ctx):
    await ctx.send("Usage: |<command> <option>")
    await ctx.send(
        "**__GENERAL:__** \n\
        >>> ***help***\n\
            Shows this list\n\
            |help \n\
***ping*** \n\
            Prints out 'Pong!' \n\
            |ping \n\
***echo <message>***\n\
            Repeats the message entered \n\
            |echo Hello World")
    await ctx.send(
        "\n**__VOTING:__** \n\
        >>> ***vote <item>*** \n\
            Registers your vote for that item \n\
            |vote Star Wars \n\
***results <optional item>***\n\
            Shows current tally of votes. If name is given, shows who voted for that item \n\
            |results Star Wars\n\
***removeVote <item>***\n\
            Removes your vote from the item\n\
            |removeVote Star Wars\n\
***delVote <item>***\n\
            Deletes item from ballot. Can  be done if the first person to vote for it and not leave \n\
            |delVote Star Wars\n")
    await ctx.send(
        "\n**__RATING:__** \n\
        >>> ***rate <optional movie> <rating>*** \n\
            Registers your rating of the movie from 0 to 10\n\
            |rate Star Wars 6.9 \n\
***ls <optional end/start list> <optional end list>***\n\
            Shows average ratings of movies. Can be given numbers to limit view \n\
            |ls 1 3\n\
***lsv <movie>***\n\
            Shows ratings for specified movie\n\
            |lsv Star Wars\n\
***look <optional user>***\n\
            Shows ratings from user. Defaults to message author if no name is given\n\
            |look Ethan")


    
#RATING
#> **Rate** <Movie name> <Rating>
#>     Used to give a  rating for a movie on a scale of 0 to 10
#>     |rate Rounders 7.8

@client.event
async def on_ready():
    print("Bot is ready")


@client.command()
async def ping(ctx):
    await ctx.send("Pong!")

@client.command()
async def echo(ctx, *, message):
    await ctx.send(message)


@client.command()
async def isThisMichelleObama():
    pass

# TEMP:
@client.command()
async def createUsers(ctx):
    if await util.authorize(ctx.author.id):
        with open("users.json", "r") as f:
            users = json.load(f)
        for member in ctx.guild.members:
            userID = str(member.id)
            if not userID in users:
                users[userID] = {}
                users[userID]["name"] = member.name
                users[userID]["nameIRL"] = member.name
                users[userID]["customDesc"] = ""
                users[userID]["isAltFor"] = None
            users[userID]["nickname"] = member.nick if not member.nick is None else member.name
            
        with open("users.json", "w") as f:
            json.dump(users, f)
    else:
        await ctx.send("Permission not granted.")


@client.command()
async def mention(ctx, *, message=None):
    if str(ctx.author.id) in ["130199913148579840", "184023919919890433", "269961227923357696"]:
        #member = discord.utils.find(lambda m: m.name == message, ctx.guild.members)
        for i in range(50):
            await ctx.send(ctx.author.mention)



client.run(TOKEN)
