

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

    def remove(self, name_or_nick):

        game = self.find_game(name_or_nick)

        if not game:
            return None

    def get_list(self):
        for e in self.gameList:
            yield e.get_tuple_for_help()

    def find_game(self, search):
        for e in self.gameList:
            if e.is_the_one(search):
                print(e.name + " found!")
                return e
        return None
