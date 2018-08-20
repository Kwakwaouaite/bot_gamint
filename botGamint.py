import json
import time

from discord.ext.commands import Bot


BOT_PREFIX = ("?", "!")

with open('data.json') as json_data:
    d = json.load(json_data)
    TOKEN = d["token"]

SERVERNAME = "BotTest"
MASTERROLE = "Boss"

client = Bot(command_prefix=BOT_PREFIX)


class Game:

    def __init__(self, name, main_nick_name=None):
        self.name = name
        self.nicknames = []  # The 1st one il the "main nickname" which will serve to createsub channel
        print(main_nick_name)
        if not main_nick_name:
            main_nick_name = name
        self.nicknames.append(main_nick_name)

    def add_nickname(self, nick):
        self.nicknames.append(str(nick))

    def get_nicknames(self):
        return self.nicknames

    def get_tuple_for_help(self):
        return self.name, self.nicknames[0]

    def is_the_one(self, name_searched):
        return self.name == name_searched or name_searched in self.nicknames

    def get_chan_root(self):
        return str(self.name).replace(" ", "-")


class GameList:
    gameList = []

    def __init__(self):
        # TODO: récup les données
        pass

    def add(self, name, nickname=None):
        """
        :param name: nom du jeu
        :param nickname: list des surnoms du jeu
        :return:
        """

        if not (self.find_game(name) or self.find_game(nickname)):
            self.gameList.append(Game(name, nickname))
            return True
        else:
            print("Name or Nickname already exist")
            return False
        # TODO: créer les chan

    def get_list(self):
        for e in self.gameList:
            yield e.get_tuple_for_help()

    def find_game(self, search):
        for e in self.gameList:
            if e.is_the_one(search):
                print(e.name + " found!")
                return e
        return None


class Permission_manager():
    master_role = None

    def updt_role(self, name, server):
        for e in server.roles:
            if e.name == name:
                self.master_role = e
                return
        print("Master role not found")

    def get_role(self, name, server):
        for e in server.roles:
            print(e)
            if e.name == name:
                return e
        return None

    def check_permission(self, author):
        print("master =", self.master_role)
        print(author.roles)
        if self.master_role in author.roles:
            return True
        else:
            return False

gameList = GameList()
permManag = Permission_manager()

gameList.add("League of Legends", "lol")
gameList.add("Counter Strike Global Offensive", "csgo")
# {"League of Legends": "LoL", "Dota 2": "Dota"}


def get_server(name):
    for e in client.servers:
        if e.name == name:
            print("Server '{0}' found".format(name))
            return e
    print("Server '{0}' not found".format(name))
    return None

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    server = get_server(SERVERNAME)
    permManag.updt_role(MASTERROLE, server)
    


@client.command(name="jeux",
                description="Liste de tout jeux qui ont leurs propres channels.",
                brief="Jeux disponnible.",
                aliases=["games, roles"],
                pass_context=True)
# Retourne la liste de tout les jeux disponibles sur le serveur
async def get_game_list(ctx):
    string = "Les jeux diponnibles sont:\n"
    print(ctx.message.author.roles)
    for e in gameList.get_list():
        string += "- " + e[0] + " (" + e[1] + ")\n"
    # str ="\n- ".join(list(gameList.keys()) + " (" + gameList.values() + ")")
    # str = "Les jeux diponnibles sont:\n- " + str
    await client.say(string)


# TODO: Ajouter la vérifications des permissions
@client.command(name="nouveau_jeu",
                description="Ajoute un jeu à la liste, et créer leschans correspondants",
                brief="Réservé aux admin",
                aliases=["nJeu"],
                pass_context=True)
async def add_game_to_list(ctx, game, nickname=None):
    if not permManag.check_permission(ctx.message.author):
        await client.say("Sorry you're not allowed to use that :/")
        return

    if gameList.add(game, nickname):
        await client.say(game + " successfuly added !")
    else:
        await client.say(game + " already exist.")


@client.command(name="isPresent",
                description="Dit si le jeu est présent ou non",
                brief="Dit si le jeu est présent ou non",
                aliases=["isP"],
                pass_context=False)
async def search_game(search):
    result = gameList.find_game(search)
    if result:
        await client.say(result.name + " found !")
        return
    await client.say("Sorry, maybe tou should search somewhere else :/")

client.run(TOKEN)
