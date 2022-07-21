from flask import Flask, redirect, request, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import pyperclip
import random
import string
import time

# instantiated a flask application
app = Flask(__name__)


# instantiated the SQLAlchemy database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "mysecret"

database_for_chess = SQLAlchemy(app)


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


@app.route("/", methods=['POST', 'GET'])
def main_page():
    """
    This function defines the functionality of the main page of the application. If a user accesses this page and there
    is no account logged in, it redirects to the login page.

    :return: template for the main page or login page, if nobody is logged in
    """
    try:
        if not session["logged_in"]:
            return redirect(url_for("login_page"))

    except KeyError:
        return redirect(url_for("login_page"))
    return render_template("index.html")


@app.route("/play_friend", methods=['POST', 'GET'])
def play_friends_page():
    """
    This function defines the functionality of the page where a user can enter and the game code is automatically
    created for him to later share it with another user. From this page, he can enter the lobby page, where the user
    will wait for the other opponent to play.

    :return: template for the page where the game code is created or login page, if nobody is logged in
    """

    # if there is no user logged in, the page sends the user to the login page
    try:
        user_acronym = session["user_acronym"]
    except KeyError:
        return redirect(url_for("login_page"))

    # the code is randomly generated and the function to copy it is put into a dictionary to be used in frontend
    current_code = generate_random_code()
    func_dict = {
        'copy_func': copy_text_to_clipboard
    }

    # a game instance is created, with the current user having the white pieces by default and the game code that was
    # generated above, and the database is then populated
    player_obj_1 = PlayersTable(user_pieces_color="white", game_code=current_code, user_acronym=user_acronym)
    database_for_chess.session.add(player_obj_1)
    database_for_chess.session.commit()

    # the game code is added to the session
    session["game_code"] = current_code
    return render_template("play_friend_main.html", current_code=current_code, func_dict=func_dict)


@app.route("/lobby", methods=['POST', 'GET'])
def lobby():
    """
    This function defines the functionality of the lobby page. A user can enter a page like this if he created a game
    code or has one from another user. When 2 players have the same game code, they can start the game from this page.
    Further logic implementations need to be implemented for when the game can start and how the players choose their
    piece colors.

    :return: template for the page where the lobby is created or login page, if nobody is logged in
    """
    # if there is no user logged in, the page sends the user to the login page
    try:
        user_acronym = session["user_acronym"]
    except KeyError:
        return redirect(url_for("login_page"))

    current_code = session["game_code"]

    # get the list of objects from the db table containing game instances that have the same game code as the one in
    # the current session
    list_of_players_on_current_game = PlayersTable.query.filter_by(game_code=current_code).all()

    # if a player wants to start the game, the application checks if the number of players who have the same game code
    # is equal to 2 and if that is the case, redirect to the game board page. Otherwise flag a message
    if request.method == "POST":
        if len(list_of_players_on_current_game) == 2:
            # THIS NEEDS REVISION (DOESN'T WORK)
            # for player in list_of_players_on_current_game:
            #     if not player.in_lobby:
            #         flash(f"Player {player.user_acronym} not in lobby.")
            #         return redirect(url_for("lobby"))

            player_1 = list_of_players_on_current_game[0].user_acronym
            player_2 = list_of_players_on_current_game[1].user_acronym

            return redirect(url_for("game_table_page", player_1=player_1, player_2=player_2))

        else:
            flash(f"The number of players for this game is not 2.")
            return redirect(url_for("lobby"))

    return render_template("lobby.html", current_code=current_code,
                           list_of_players=list_of_players_on_current_game)


@app.route("/create_put_code", methods=['POST', 'GET'])
def create_or_put_code():
    """
    This function defines the functionality of the page where a user can select if he wants to create a game code or
    he wants to insert an existing one.

    :return: template for the create/put game code page or login page, if nobody is logged in
    """
    # if there is no user logged in, the page sends the user to the login page
    try:
        user_acronym = session["user_acronym"]
    except KeyError:
        return redirect(url_for("login_page"))

    return render_template("create_or_put_code.html")


@app.route("/log_in", methods=['POST', 'GET'])
def login_page():
    """
    This function defines the functionality of the login page.

    :return: template for the login page
    """

    # whenever this page is visited, any user is logged out
    session["logged_in"] = False
    del session["user_acronym"]

    # the text in the user acronym and password fields in the form are being saved and checked against existing accounts
    if request.method == "POST":
        user_acronym = request.form["username"]
        user_password = request.form["password"]

        username_in_db = UserAccountsTable.query.filter_by(user_acronym=user_acronym).first()

        # if no user in the database has the current acronym, a flag message is issued
        if not username_in_db:
            flash(f"The username or password do not match an existing account. Please try again.")
            return redirect(url_for("login_page"))

        # otherwise, if the user acronym matches but the password doesn't, the same message as above is flagged
        # if the password and acronym match, the user is saved in the session and it is redirected to the main page
        else:
            if username_in_db.password == user_password:
                session["user_acronym"] = user_acronym
                session["logged_in"] = True

                flash(f"You have been logged in as {user_acronym}.")
                return redirect(url_for("main_page"))

            else:
                flash(f"The username or password do not match an existing account. Please try again.")
                return redirect(url_for("login_page"))

    return render_template("log_in.html")


@app.route("/sign_in", methods=['POST', 'GET'])
def sign_in_page():
    """
    This function defines the functionality of the login page.

    :return: template for the login page
    """

    # whenever this page is visited, any user is logged out
    session["logged_in"] = False
    del session["user_acronym"]

    # if the user acronym does not match an existing account, the new user acronym and password are saved and logged in
    # otherwise, a flagging message is displayed
    if request.method == "POST":
        user_acronym = request.form["username"]
        user_password = request.form["password"]

        username_in_db = UserAccountsTable.query.filter_by(user_acronym=user_acronym).first()
        if not username_in_db:
            session["user_acronym"] = user_acronym
            session["logged_in"] = True

            new_user = UserAccountsTable(user_acronym, user_password)
            database_for_chess.session.add(new_user)
            database_for_chess.session.commit()

            flash(f"You have been signed up as {user_acronym}.")
            return redirect(url_for("main_page"))

        else:
            flash("The username seems to already exist. Please try another one.")
            return redirect(url_for("sign_in_page"))

    return render_template("sign_in.html")


@app.route("/join_w_code", methods=['POST', 'GET'])
def join_with_code():
    """
    This function presents the functionality of the 'join_with_code' page. A user can access this page and introduce a
    game code which links to a game. If the number of players is already 2 or the game code does not exist, a flag
    message is displayed. Otherwise, if there is room for 1 more player or the user has already been in the game, the
    user is redirected to the lobby page.

    :return: the template of the 'join_w_code' page
    """
    if request.method == "POST":
        try:
            user_acronym = session["user_acronym"]
        except KeyError:
            flash("There is no user logged in. To play, please log in.")
            return redirect(url_for("log_in"))
        game_code = request.form["game_code"]

        all_game_codes = PlayersTable.query.filter_by(game_code=game_code).all()

        # if there are no games with the current game code, flag a message
        if not all_game_codes:
            flash(f"The game code {game_code} is not available. Try another one.")
            return redirect(url_for("join_with_code"))

        # if the game already has 2 players, but the user is one of them, redirect to the lobby. If the user is not one
        # of the players, flag a message
        elif len(all_game_codes) == 2:
            for game_object in all_game_codes:
                if game_object.user_acronym == user_acronym:
                    flash(f"You have entered this game lobby as {user_acronym}.")
                    return redirect(url_for("lobby"))

            flash(f"The game with code {game_code} has the full amount of players. Try another game code.")
            return redirect(url_for("join_with_code"))

        # if there is room for one more player, include the user as the other player (playing with black pieces)
        elif len(all_game_codes) == 1:
            if all_game_codes[0].user_acronym == user_acronym:
                flash(f"You have entered this game lobby as {user_acronym}.")
                return redirect(url_for("lobby"))
            else:
                player_2 = PlayersTable(user_pieces_color="black", game_code=game_code, user_acronym=user_acronym)
                database_for_chess.session.add(player_2)
                database_for_chess.session.commit()

                flash(f"You have entered this game lobby as {user_acronym}.")
                return redirect(url_for("lobby"))

    return render_template("join_w_code.html")


def copy_text_to_clipboard(text_to_copy: str):
    """
    Function to copy text to clipboard, used in the page where the game code is generated.

    :param text_to_copy: the text to be copied in the clipboard
    :return: Nothing
    """
    pyperclip.copy(text_to_copy)


def generate_random_code(length=8):
    """
    This function is used to generate a random code of a given length, which is used as game code.

    :param length: integer determining the length of the code to be randomly generated (default: 8)
    :return: generated random code
    """
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return result_str


@app.route("/game_table/<player_1>/<player_2>", methods=['POST', 'GET'])
def game_table_page(player_1, player_2):

    return render_template("game_table.html",
                           player_1=player_1,
                           player_2=player_2)


# database_for_chess.drop_all()
database_for_chess.create_all()
if __name__ == "__main__":
    app.run(debug=True)