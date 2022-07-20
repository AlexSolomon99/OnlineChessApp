from flask import Flask, redirect, request, render_template, url_for, session
from flask_sqlalchemy import SQLAlchemy
import pyperclip
import random
import string
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
    current_code = generate_random_code()
    func_dict = {
        'copy_func': copy_text_to_clipboard
    }
    return render_template("play_friend_main.html", current_code=current_code, func_dict=func_dict)


@app.route("/create_put_code", methods=['POST', 'GET'])
def create_or_put_code():
    return render_template("create_or_put_code.html")


def copy_text_to_clipboard(text_to_copy: str):
    pyperclip.copy(text_to_copy)


def generate_random_code(length=8):
    # With combination of lower and upper case
    result_str = ''.join(random.choice(string.ascii_letters) for i in range(length))
    return result_str


if __name__ == "__main__":
    app.run(debug=True)