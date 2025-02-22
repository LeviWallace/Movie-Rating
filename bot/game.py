import discord
from discord.ext import commands

class Game(commands.Cog):
    def __init__(self, users, kickVotes):
        self.users = users
        self.kickVotes = kickVotes
        self.start()

    async def start(self):
        pass

    async def removeUser(self, userID):
        self.users.remove(userID)

    async def addUsers(self, newUsers):
        self.users = list(set(self.users)|set(newUsers)|)


    async def kick(self, kicker, kickee):
        