from . import database_for_chess


class PlayersTable(database_for_chess.Model):
    """
    This class is used to construct the table in the database referring to a game that is being played. Every entry
    represents a player and the game that he might be in. The player is related to by the user_acronym, the game he is
    entering is referred to through the game code and the color of the pieces he is playing with is the
    user_pieces_color. This class is instantiated when a player either creates a code or introduces an existing one,
    sending the players to the lobby.
    """

    id = database_for_chess.Column("id", database_for_chess.Integer, primary_key=True)
    user_pieces_color = database_for_chess.Column(database_for_chess.String(16))
    game_code = database_for_chess.Column(database_for_chess.String(8))
    user_acronym = database_for_chess.Column(database_for_chess.String(20))

    def __init__(self, user_pieces_color: str, game_code: str, user_acronym: str):
        """
        :param user_pieces_color: name of the color of the pieces ("white"/"black")
        :param game_code: string representing the code of the game a user is about to join
        :param user_acronym: the user acronym of a player (related to the UserAccountsTable.user_acronym)
        """
        self.user_pieces_color = user_pieces_color
        self.game_code = game_code
        self.user_acronym = user_acronym
        self.in_lobby = False


class UserAccountsTable(database_for_chess.Model):
    """
    This class is used to construct the table in the database in charge of keeping track of the users registered in the
    application. It contains their user acronym and the associated password. This table is populated whenever someone
    signs up.
    """
    id = database_for_chess.Column("id", database_for_chess.Integer, primary_key=True)
    user_acronym = database_for_chess.Column(database_for_chess.String(20))
    password = database_for_chess.Column(database_for_chess.String(20))

    def __init__(self, user_acronym: str, password: str):
        """
        :param user_acronym: the acronym of the user selected at sign up
        :param password: the password of the user, selected at sign up
        """
        self.user_acronym = user_acronym
        self.password = password