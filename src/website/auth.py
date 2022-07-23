from flask import Blueprint, render_template, request, redirect, flash, url_for, session
from . import database_for_chess
from models import PlayersTable, UserAccountsTable
from . import database_for_chess

auth = Blueprint('auth', __name__)

@auth.route("/log_in", methods=['POST', 'GET'])
def login_page():
    """
    This function defines the functionality of the login page.

    :return: template for the login page
    """

    # whenever this page is visited, any user is logged out
    session["logged_in"] = False
    #del session["user_acronym"]

    # the text in the user acronym and password fields in the form are being saved and checked against existing accounts
    if request.method == "POST":
        user_acronym = request.form["username"]
        user_password = request.form["password"]

        username_in_db = UserAccountsTable.query.filter_by(user_acronym=user_acronym).first()

        # if no user in the database has the current acronym, a flag message is issued
        if not username_in_db:
            flash(f"The username or password do not match an existing account. Please try again.")
            return redirect(url_for("auth.login_page"))

        # otherwise, if the user acronym matches but the password doesn't, the same message as above is flagged
        # if the password and acronym match, the user is saved in the session and it is redirected to the main page
        else:
            if username_in_db.password == user_password:
                session["user_acronym"] = user_acronym
                session["logged_in"] = True

                flash(f"You have been logged in as {user_acronym}.")
                return redirect(url_for("views.main_page"))

            else:
                flash(f"The username or password do not match an existing account. Please try again.")
                return redirect(url_for("auth.login_page"))

    return render_template("log_in.html")


@auth.route("/sign_in", methods=['POST', 'GET'])
def sign_in_page():
    """
    This function defines the functionality of the login page.

    :return: template for the login page
    """

    # whenever this page is visited, any user is logged out
    session["logged_in"] = False
    # del session["user_acronym"]

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
            return redirect(url_for("views.main_page"))

        else:
            flash("The username seems to already exist. Please try another one.")
            return redirect(url_for("auth.sign_in_page"))

    return render_template("sign_in.html")



