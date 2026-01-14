# TARGET SHIP DATE: 2026-01-16
# Ethan Cheung (PM), Amy Shrestha, Jason Chan, Matthew Ciu
# JAMEs
# SoftDev
# P02
# 2025-01-09
# time spent: 0.0

from flask import Flask
from flask import render_template  # facilitate jinja templating
from flask import request, redirect, url_for  # facilitate form submission
from flask import session
import sqlite3   #enable control of an sqlite database
import urllib.request
import json

#FLASK Declaration
#====================================================================================#
app = Flask(__name__)  # create Flask object
app.secret_key = b'weRtheJAMEs'


#SQLITE3 Databases
#====================================================================================#
DB_FILE="songs.db"

db = sqlite3.connect(DB_FILE, check_same_thread=False) #open if file exists, otherwise create
c = db.cursor()

# create db tables
c.execute("""
CREATE TABLE IF NOT EXISTS user_data(
    user_id INTEGER PRIMARY KEY NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    saved_songs TEXT,
    total_songs INT
);""")

c.execute("""
CREATE TABLE IF NOT EXISTS chord_data(
    chord_name TEXT NOT NULL,
    string_pattern TEXT NOT NULL
);""")

# try opening APIs (try/except) to insert data into APIs




#Helper Functions
#====================================================================================#
usernames = {}
with sqlite3.connect(DB_FILE) as db:
    c = db.cursor()
    c.execute("SELECT username, password FROM user_data")
    rows = c.fetchall()
    for row in rows:
        usernames[row[0]] = row[1]

print(usernames)

def loggedin():
    if 'username' in session:
        return True
    return False

idVals = 0

#Webpage Sites
#====================================================================================#
@app.route("/home", methods=['GET', 'POST'])
def home():
    return homepage()

@app.route("/register", methods=['GET', 'POST'])
def register():
    if loggedin():
        return redirect(url_for('start'))
    else:
        global idVals
        if request.method == 'POST':
            with sqlite3.connect(DB_FILE) as db:
                c = db.cursor()

                rows = c.execute("SELECT username FROM user_data WHERE username = ?", (request.form['username'],))
                result = rows.fetchone()
                if result:
                    return registerpage(False, "Duplicate username")
                session.permanent = True

                # for invalid requests / empty form responses
                t = ""
                if(request.form['username'] == "" or request.form['password'] == ""):
                    t = "Please enter a valid "
                    if(request.form['username'] == ""):
                        t = t + "username "
                    if(request.form['password'] == ""):
                        t = t + "password "
                    return registerpage(False, t)

                c.execute("INSERT INTO user_data VALUES (?, ?, ?, ?, ?);", (idVals, request.form['username'].lower(), request.form['password'], "", 0))
                idVals += 1
                idVals += 1
                db.commit()

                session.clear()
                session.permanent = True
                session['username'] = request.form['username']
                return redirect(url_for('home'))
    return registerpage()

@app.route("/login", methods=['GET', 'POST'])
def login():
    if loggedin():
        return redirect(url_for('home'))

    if request.method == 'POST':
        session.clear()
        session.permanent = True
        with sqlite3.connect(DB_FILE) as db:
                c = db.cursor()
                rows = c.execute("SELECT * FROM user_data WHERE username = ?;", (request.form['username'],))
                result = rows.fetchone()

                if result is None:
                    return loginpage(False, "Username does not exist")
                elif (request.form['password'] != result[1]):
                    return loginpage(False, "Your password was incorrect")

                session['username'] = request.form['username']
                return redirect(url_for('start'))
    else:
        return loginpage(True)

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if not loggedin():
        return redirect(url_for('login'))

    # do stuff
    return profilepage()

@app.route("/activities", methods=['GET', 'POST'])
def activities():
    if not loggedin():
        return redirect(url_for('login'))

    return activitiespage()

@app.route("/tsg", methods=['GET', 'POST'])
def tsg():
    if not loggedin():
        return redirect(url_for('login'))

    return tsgpage()

@app.route("/speech-text", methods=['GET', 'POST'])
def speechText():
    if not loggedin():
        return redirect(url_for('login'))

    return speechTextPage()

@app.route("/leaderboard", methods=['GET', 'POST'])
def leaderboard():
    if not loggedin():
        return redirect(url_for('login'))

    with sqlite3.connect("songs.db") as db:
        c = db.cursor()
        c.execute('SELECT username, total_songs FROM user_data ORDER BY total_songs DESC LIMIT 10')
        top_players = c.fetchall()

    return render_template(
        "leaderboard.html",
        username=session["username"],  # Pass current username to leaderboard.html
        top_players=top_players  # Pass the top 10 players to leaderboard.html
    )

@app.route("/logout")
def logout():
    session.pop('username', None) # remove username from session
    return redirect(url_for('login'))

#HTML Pages
#====================================================================================#
def homepage():
    return render_template('home.html')

def registerpage(valid=True, invalid=''):
    if(valid==True):
        return render_template('register.html',invalid=invalid)
    else:
        return render_template('register.html',invalid=invalid)
    return render_template('register.html')

def loginpage(valid=True, invalid=''):
    if(valid==True):
        return render_template('login.html',invalid=invalid)
    else:
        return render_template('login.html',invalid=invalid)

def profilepage(user=''):
    return render_template('profile.html', user=user)

def activitiespage(user=''):
    return render_template('activities.html', user=user)

def tsgpage(user=''):
    return render_template('tsg.html', user=user)

def speechTextPage(user=''):
    return render_template('speech-text.html', user=user)


#====================================================================================#
if __name__ == "__main__":  # false if this file imported as module
    #app.debug = True  # enable PSOD, auto-server-restart on code chg
    app.run(port=5000)
