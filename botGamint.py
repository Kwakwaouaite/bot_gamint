import json

from discord.ext.commands import Bot

BOT_PREFIX = ("?", "!")

with open('data.json') as json_data:
    d = json.load(json_data)
    TOKEN = d["token"]


client = Bot(command_prefix=BOT_PREFIX)

class Game:


    def __init__(self, name, mainNickName = None):
        self.name = name
        self.nicknames = []  # The 1st one il the "main nickname" which will serve to createsub channel
        print(mainNickName)
        if not mainNickName:
            mainNickName = name
        self.nicknames.append(mainNickName)

    def addNickname(self, nick):
        self.nicknames.append(str(nick))

    def getNicknames(self):
        return self.nicknames

    def getTupleForHelp(self):
        return (self.name, self.nicknames[0])

    def isTheOne(self, nameSearched):
        #print(self.name, nameSearched, self.nicknames)
        return self.name == nameSearched or nameSearched in self.nicknames

    def getChanRoot(self):
        return str(self.name).replace(" ", "-")

class GameList:
    gameList = []

    def __init__(self):
        # TODO: récup les données
        pass

    def add(self, name, nickname=None):
        '''
        :param name: nom du jeu
        :param nickname: list des surnoms du jeu
        :return:
        '''
        if not (self.findGame(name) or self.findGame(nickname)):
            self.gameList.append(Game(name, nickname))
            return True
        else:
            print("Name or Nickname already exist")
            return False
        #TODO: créer les chan

    def getList(self):
        for e in self.gameList:
            yield e.getTupleForHelp()

    def findGame(self,search):
        for e in self.gameList:
            if e.isTheOne(search):
                print(e.name + " found!")
                return e
        return None


gameList = GameList()
gameList.add("League of Legends", "lol")
gameList.add("Counter Strike Global Offensive", "csgo")
    #{"League of Legends": "LoL", "Dota 2": "Dota"}



@client.command(name="jeux",
                description="Liste de tout jeux qui ont leurs propres channels.",
                brief="Jeux disponnible.",
                aliases=["games, roles"],
                pass_context=False)
# Retourne la liste de tout les jeux disponibles sur le serveur
async def getGameList():
    str = "Les jeux diponnibles sont:\n"
    for e in gameList.getList():
        str += "- " + e[0] + " (" + e[1] + ")\n"
    # str ="\n- ".join(list(gameList.keys()) + " (" + gameList.values() + ")")
    # str = "Les jeux diponnibles sont:\n- " + str
    await client.say(str)

#TODO: Ajouter la vérifications des permissions
@client.command(name="nouveau_jeu",
                description="Ajoute un jeu à la liste, et créer leschans correspondants",
                brief="Réservé aux admin",
                aliases=["nJeu"],
                pass_context=False)
async def addGameToList(game, nickname=None):
    gameList.add(game, nickname)
    await client.say(game + " successfuly added !")

@client.command(name="isPresent",
                description="Dit si le jeu est présent ou non",
                brief="Dit si le jeu est présent ou non",
                aliases=["isP"],
                pass_context=False)
async def searchGame(search):
    result = gameList.findGame(search)
    if result:
        await client.say(result.name + " found !")
        return
    await client.say("Sorry, maybe tou should search somewhere else :/")

client.run(TOKEN)
