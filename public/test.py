import json
import os

def main():
    print(os.listdir(os.path.curdir))
    with open("public/users.json", "r") as f:
        users = json.load(f)
    with open("public/ratings.json", "r") as f:
        ratings = json.load(f)
    out = {}
    for movie in ratings["movies"]:
        for user in ratings["movies"][movie]["users"]:
            if user not in out:
                out[user] = users[user]

    

    with open("public/newusers.json", "w") as f:
        json.dump(out, f)

main()