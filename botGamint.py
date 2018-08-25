import json


from discord.ext.commands import Bot
from discord import utils

BOT_PREFIX = ("?", "!")

with open('data.json') as json_data:
    d = json.load(json_data)
    TOKEN = d["token"]
    SERVERNAME = d["server"]
    MASTERROLE = d["master_role"]
    UPPERBOUND = d["upper_bound"]

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


class PermissionManager:
    master_roles = []
    upper_bound_role = None

    # Met à jour le role "Master"
    def add_master_role(self, role):
        self.master_roles.append(role)

    def remove_master_role(self, role):
        self.master_roles.remove(role)

    def check_master_permission(self, author):
        print("master =", self.master_roles)
        print(author.roles)
        if self.master_roles in author.roles:
            return True
        else:
            return False

    def updt_upper_bound_role(self, role):
        self.upper_bound_role = role

    # Check if the role is one we can freely join
    def check_join_permission(self, role):
        if not self.upper_bound_role:
            return True
        else:
            return self.upper_bound_role > role


# Permet de trouver un role en fonction du serveur
def get_role(name, server):
    for e in server.roles:
        if e.name == name:
            return e
    return None

gameList = GameList()
permManag = PermissionManager()

gameList.add("League of Legends", "lol")
gameList.add("Counter Strike Global Offensive", "csgo")
# {"League of Legends": "LoL", "Dota 2": "Dota"}



def get_server(name):
    for e in client.servers:
        if e.name == name:
            print("Server '{0}' found".format(name))
            return e
    raise NameError("Server '{0}' not found".format(name))
    #return None

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')
    server = get_server(SERVERNAME)
    role = utils.get(server.roles, name=MASTERROLE)
    if role:
        permManag.add_master_role(role)
    else:
        print("Master role '{0}' not found".format(MASTERROLE))
    role = utils.get(server.roles, name=UPPERBOUND)
    if role:
        permManag.updt_upper_bound_role(role)
    else:
        print("Master role '{0}' not found".format(UPPERBOUND))

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


@client.command(name="rejoindre",
                description="Rejoins un role",
                brief="Rejoins un role",
                aliases=["r", "join", "j"],
                pass_context=True)
async def join_role(ctx, role_name):
    user = ctx.message.author
    name = gameList.find_game(role_name).name
    game = True
    if not name:
        name = role_name
        game = False
    role = utils.get(user.server.roles, name=name)
    if not role:
        if game:
            # Si il fait partie de la liste de jeu mais n'a pas de role
            print("Oh no, '{0}' was not created".format(name))
            # TODO: pm master ?
            await client.say("Role inconnu, un modo devrait le créer bientôt.")
        else:
            await client.say("Role inconnu.")
        return
    if not permManag.check_join_permission(role):
        await client.say("Impossible d'avoir ce rôle via cette commande")
        return
    if role in ctx.message.author.roles:
        await client.say("Tu as déjà ce rôle.")
        return
    await client.add_roles(user, role)
    await client.say("Tu as bien était ajouté !")


@client.command(name="quitter",
                description="Quitte un role",
                brief="Quitte un role",
                aliases=["q", "quit", "leave", "l"],
                pass_context=True)
async def quit_role(ctx, role_name):
    user = ctx.message.author
    name = gameList.find_game(role_name).name
    game = True
    if not name:
        name = role_name
        game = False
    role = utils.get(user.server.roles, name=name)
    if not role:
        if game:
            # Si il fait partie de la liste de jeu mais n'a pas de role
            print("Oh no, '{0}' was not created".format(name))
            # TODO: pm master ?
            await client.say("Role inconnu, un modo devrait le créer bientôt.")
        else:
            await client.say("Role inconnu.")
    if not permManag.check_join_permission(role):
        await client.say("Impossible de quitter ce rôle via cette commande")
        return
    await client.remove_roles(user, role)
    await client.say("Au revoir _{0}_ :wave:".format(role.name))


# TODO: Ajouter la vérifications des permissions
@client.command(name="nouveau_jeu",
                description="Ajoute un jeu à la liste, et créer leschans correspondants",
                brief="Réservé aux admin",
                hidden=True,
                aliases=["nJeu, nj, newGame, ng"],
                pass_context=True)
async def add_game_to_list(ctx, game, nickname=None):
    if not permManag.check_master_permission(ctx.message.author):
        await client.say("Sorry you're not allowed to use that :/")
        return

    if gameList.add(game, nickname):
        await client.say(game + " successfuly added !")
    else:
        await client.say(game + " already exist.")


# TODO: Ajouter la vérifications des permissions
@client.command(name="supprimer_jeu",
                description="Enleve un jeu à la liste",
                brief="Réservé aux admin",
                hidden=True,
                aliases=["sJeu, delGame, dg"],
                pass_context=True)
async def add_game_to_list(ctx, game, nickname=None):
    if not permManag.check_master_permission(ctx.message.author):
        await client.say("Sorry you're not allowed to use that :/")
        return

    if gameList.add(game, nickname):
        await client.say(game + " successfuly added !")
    else:
        await client.say(game + " already exist.")

client.run(TOKEN)
