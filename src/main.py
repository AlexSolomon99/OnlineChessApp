from flask import Flask, redirect, request, render_template, url_for, session
from flask_sqlalchemy import SQLAlchemy
import time

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

app.secret_key = "mysecret"
parola_juriu = "ZWAKc9gyM8"
admin_pass = "alex.balex25"


@app.route("/", methods=['POST', 'GET'])
def judge_public():
    return render_template("index.html")


@app.route("/play_friend", methods=['POST', 'GET'])
def play_friends_page():
    return render_template("play_friend_main.html")


if __name__ == "__main__":
    app.run(debug=True)