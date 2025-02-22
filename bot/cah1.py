import game
import json

class CAH(game):
    async def start():
        with open("cah.json", "r") as f:
            cah = json.load(f)
        self.userHands = {x:{"Hand":[],"Won":[]} for x in self.users}
        self.whiteCardPile = list(range(len(cah["whiteCards"])))
        self.blackCardPile = list(range(len(cah["blackCards"])))


    async def gameLoop(self):
        while True:
            if phase == "draw":

            return

    async def draw():
        

    @staticmethod    
    async def getCardName(id, isWhite):
        with open("cah.json", "r") as f:
            cah = json.load(f)
        if isWhite:
            return "*" + cah["whiteCards"][id] + "*"
        return "**" + cah["blackCards"][id]["text"] + "**"

