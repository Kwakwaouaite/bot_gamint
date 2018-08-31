import json
from game import GameList
from permissionManager import PermissionManager
from discord import utils

from discord.ext.commands import Bot

gameList = GameList()
permManag = PermissionManager()

with open('config.json') as json_data:
    d = json.load(json_data)
    TOKEN = d["token"]
    SERVERNAME = d["server"]
    MASTERROLE = d["master_role"]
    UPPERBOUND = d["upper_bound"]

    for e in d["games"]:
        gameList.add(e["name"], e["nickname"])

BOT_PREFIX = ("?", "!")

client = Bot(command_prefix=BOT_PREFIX)


def get_server(name):
    for el in client.servers:
        if el.name == name:
            print("Server '{0}' found".format(name))
            return el
    raise NameError("Server '{0}' not found".format(name))


def get_role_from_name_or_nickname(server, role_name):
    game = gameList.find_game(role_name)
    is_in_list = True
    if not game:
        name = role_name
        is_in_list = False
    else:
        name = game.name
    role = utils.get(server.roles, name=name)
    return role


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
    for el in gameList.get_list():
        string += "- " + el[0] + " (" + el[1] + ")\n"
    await client.say(string)


@client.command(name="estPresent",
                description="Dit si le jeu est présent ou non",
                brief="Dit si le jeu est présent ou non",
                aliases=["eP", "isPresent", "iP"],
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

    role = get_role_from_name_or_nickname(user.server, role_name)

    if not role:
        await client.say("Role inconnu.")
        return

    if not permManag.check_join_permission(role):
        await client.say("Impossible d'avoir ce rôle via cette commande")
        return
    if role in ctx.message.author.roles:
        await client.say("Tu as déjà ce rôle.")
        return
    await client.add_roles(user, role)
    await client.say("Tu as bien été ajouté !")


@client.command(name="quitter",
                description="Quitte un role",
                brief="Quitte un role",
                aliases=["q", "quit", "leave", "l"],
                pass_context=True)
async def quit_role(ctx, role_name):
    user = ctx.message.author

    role = get_role_from_name_or_nickname(user.server, role_name)

    if not permManag.check_join_permission(role):
        await client.say("Impossible de quitter ce rôle via cette commande")
        return
    await client.remove_roles(user, role)
    await client.say("Au revoir _{0}_ :wave:".format(role.name))


@client.command(name="nouveau_jeu",
                description="Ajoute un jeu à la liste, et créer leschans correspondants",
                brief="Réservé aux admin",
                hidden=True,
                aliases=["nJeu", "nj", "newGame", "ng"],
                pass_context=True)
async def add_game_to_list(ctx, game, nickname=None):
    if not permManag.check_master_permission(ctx.message.author):
        await client.say("Sorry you're not allowed to use that :/")
        return

    if gameList.add(game, nickname):
        await client.say(game + " successfuly added !")
    else:
        await client.say(game + " already exist.")


@client.command(name="supprimer_jeu",
                description="Enleve un jeu à la liste",
                brief="Réservé aux admin",
                hidden=True,
                aliases=["sJeu", "delGame", "dg"],
                pass_context=True)
async def remove_game(ctx, game):
    if not permManag.check_master_permission(ctx.message.author):
        return

    if gameList.add(game):
        await client.say(game + " successfuly added !")
    else:
        await client.say(game + " already exist.")

client.run(TOKEN)
