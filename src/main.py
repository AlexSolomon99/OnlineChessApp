from flask import Flask, redirect, request, render_template, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import pyperclip
import random
import string
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

database_for_chess = SQLAlchemy(app)


class PlayersTable(database_for_chess.Model):
    id = database_for_chess.Column("id", database_for_chess.Integer, primary_key=True)
    user_pieces_color = database_for_chess.Column(database_for_chess.String(16))
    game_code = database_for_chess.Column(database_for_chess.String(8))
    user_acronym = database_for_chess.Column(database_for_chess.String(20))

    def __init__(self, user_pieces_color, game_code, user_acronym):
        self.user_pieces_color = user_pieces_color
        self.game_code = game_code
        self.user_acronym = user_acronym
        self.in_lobby = False


class UserAccountsTable(database_for_chess.Model):
    id = database_for_chess.Column("id", database_for_chess.Integer, primary_key=True)
    user_acronym = database_for_chess.Column(database_for_chess.String(20))
    password = database_for_chess.Column(database_for_chess.String(20))

    def __init__(self, user_acronym, password):
        self.user_acronym = user_acronym
        self.password = password


app.secret_key = "mysecret"
parola_juriu = "ZWAKc9gyM8"
admin_pass = "alex.balex25"


@app.route("/", methods=['POST', 'GET'])
def main_page():
    try:
        if not session["logged_in"]:
            return redirect(url_for("login_page"))

    except KeyError:
        return redirect(url_for("login_page"))
    return render_template("index.html")


@app.route("/play_friend", methods=['POST', 'GET'])
def play_friends_page():
    current_code = generate_random_code()
    func_dict = {
        'copy_func': copy_text_to_clipboard
    }
    try:
        user_acronym = session["user_acronym"]
    except KeyError:
        return redirect(url_for("login_page"))

    player_obj_1 = PlayersTable(user_pieces_color="white", game_code=current_code, user_acronym=user_acronym)
    database_for_chess.session.add(player_obj_1)
    database_for_chess.session.commit()

    session["user_id"] = player_obj_1.id
    session["game_code"] = current_code
    return render_template("play_friend_main.html", current_code=current_code, func_dict=func_dict)


@app.route("/lobby", methods=['POST', 'GET'])
def lobby():
    current_code = session["game_code"]

    list_of_players_on_current_game = PlayersTable.query.filter_by(game_code=current_code).all()

    if request.method == "POST":
        if len(list_of_players_on_current_game) == 2:
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
    return render_template("create_or_put_code.html")


@app.route("/log_in", methods=['POST', 'GET'])
def login_page():
    session["logged_in"] = False
    if request.method == "POST":
        user_acronym = request.form["username"]
        user_password = request.form["password"]

        username_in_db = UserAccountsTable.query.filter_by(user_acronym=user_acronym).first()
        if not username_in_db:
            flash(f"The username or password do not match an existing account. Please try again.")
            return redirect(url_for("login_page"))

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
    session["logged_in"] = False
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
    if request.method == "POST":
        try:
            user_acronym = session["user_acronym"]
        except KeyError:
            flash("There is no user logged in. To play, please log in.")
            return redirect(url_for("log_in"))
        game_code = request.form["game_code"]

        all_game_codes = PlayersTable.query.filter_by(game_code=game_code).all()
        if not all_game_codes:
            flash(f"The game code {game_code} is not available. Try another one.")
            return redirect(url_for("join_with_code"))

        elif len(all_game_codes) == 2:
            for game_object in all_game_codes:
                if game_object.user_acronym == user_acronym:
                    flash(f"You have entered this game lobby as {user_acronym}.")
                    return redirect(url_for("lobby"))

            flash(f"The game with code {game_code} has the full amount of players. Try another game code.")
            return redirect(url_for("join_with_code"))

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
    pyperclip.copy(text_to_copy)


def generate_random_code(length=8):
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return result_str


@app.route("/game_table/<player_1>/<player_2>", methods=['POST', 'GET'])
def game_table_page(player_1, player_2):

    # print(player_1.user_acronym)
    return render_template("game_table.html",
                           player_1=player_1,
                           player_2=player_2)


# database_for_chess.drop_all()
database_for_chess.create_all()
if __name__ == "__main__":
    app.run(debug=True)