import json

async def title(text):
    if type(text) is str:
        text = text.split()
    output = ""
    for i in range(len(text)):
        output += text[i].capitalize()
        if i == len(text)-1:
            break
        output += " "
    return output


async def calcAvg(users):
    usernames = list(users)
    avg = 0
    for i in usernames:
        avg += float(users[i])
    avg /= len(users)

    return round(avg, 1)


async def authorize(authorID):
    return str(authorID) in ["130199913148579840", "184023919919890433", "269961227923357696"]


async def genList(keyWords,  dictLam=lambda i: " ", startIdx=0, endIdx=None, numbered=False, suffix="", keyWordLam=lambda key: key, dashed = True):
    if len(keyWords) == 0:
        output = ">>> There is nothing in this list"
        return output
    if endIdx is None:
        endIdx = len(keyWords)
    output = "Showing {} through {}:\n>>> ".format(
        startIdx + 1, min(endIdx, len(keyWords)))
    for i in range(startIdx, min(endIdx, len(keyWords))):
        if numbered:
            output += str(i + 1) + ") "
        output += "{0} {1} **{2}{3}**\n".format(keyWordLam(keyWords[i]), "-" if dashed else "", dictLam(keyWords[i]), suffix)
    return output

async def getUserID(message):
    with open("users.json", "r") as f:
        users = json.load(f)

    output = False
    message = await title(message)
    userIDs = list(users)
    if message[0:3] == "<@!":
        message = message[3:-1]
        if message in userIDs:
            output = message
    else:
        for user in userIDs:
            if message == users[user]["nameIRL"] or message == users[user]["name"] or message == users[user]["nickname"]:
                output = user
                break

    return output          

async def checkAlt(id):
    with open("users.json", "r") as f:
        users = json.load(f)
    if not users[id]["isAltFor"] is None:
        return users[id]["isAltFor"]
    return id

async def getName(id):
    with open("users.json", "r") as f:
        users = json.load(f)
    return users[id]["nameIRL"]