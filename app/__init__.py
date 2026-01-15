# TARGET SHIP DATE: 2026-01-16
# Ethan Cheung (PM), Amy Shrestha, Jason Chan, Matthew Ciu
# JAMEs
# SoftDev
# P02
# 2025-01-09
# time spent: 20.0

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
    total_songs INTEGER,
    bio TEXT
);""")

c.execute("""
CREATE TABLE IF NOT EXISTS song_data(
    song_name TEXT NOT NULL,
    artist TEXT NOT NULL,
    chart_rank INTEGER NOT NULL,
    lyrics TEXT NOT NULL
);""")


# try opening APIs (try/except) to insert data into APIs
try:
    with urllib.request.urlopen("https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/recent.json") as response:
        a = json.loads(response.read())
        for song in a['data']:
            command = "INSERT OR IGNORE INTO song_data(song_name, artist, chart_rank, lyrics) VALUES(?, ?, ?, ?)"
            categories = (song['song'], song['artist'], song['this_week'], '')
            c.execute(command, categories)
        db.commit()
except:
    print("*********Error with Billboard API*********")


# get lyrics for songs
c.execute("SELECT song_name, artist FROM song_data")
song_list = c.fetchall()
#print(song_list)

'''
for song in song_list:
    # (name, artist)
    song_name = urllib.parse.quote(song[0])
    artist = urllib.parse.quote(song[1])
    try:
        url = f"https://api.lyrics.ovh/v1/{artist}/{song_name}"
        with urllib.request.urlopen(url) as response:
            a = json.loads(response.read())
            lyrics = a.get('lyrics')
            c.execute("UPDATE song_data SET lyrics = ? WHERE song_name = ? AND artist = ?", (lyrics, song_name, artist))
    except:
        print("*********Error with Lyrics API*********")

db.commit()
'''

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

#Webpage Sites
#====================================================================================#
@app.route("/home", methods=['GET', 'POST'])
def home():
    return homepage()

@app.route("/register", methods=['GET', 'POST'])
def register():
    idVals = 0
    if loggedin():
        return redirect(url_for('home'))
    else:
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

                c.execute("INSERT INTO user_data VALUES (?, ?, ?, ?, ?, ?);", (None, request.form['username'], request.form['password'], "", 0, "No bio"))
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
                elif (request.form['password'] != result[2]):
                    return loginpage(False, "Your password was incorrect")

                session['username'] = request.form['username']
                return redirect(url_for('home'))
    else:
        return loginpage(True)

@app.route("/profile", methods=['GET', 'POST'])
def profile():
    if not loggedin():
        return redirect(url_for('login'))

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()
        bio = c.execute("SELECT bio FROM user_data WHERE username=?", (session['username'],)).fetchone()

    # do stuff
    return render_template('profile.html', bio=bio)

@app.route("/edit_profile", methods=['GET', 'POST'])
def edit_profile():
    if not loggedin():
        return redirect(url_for('login'))

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()
        current_bio = c.execute("SELECT bio FROM user_data WHERE username=?", (session['username'],)).fetchone()
        if request.method == 'POST':
            newbio = request.form.get('newbio').strip()
            c.execute("UPDATE user_data SET bio=? WHERE username=?", (newbio, session['username'],))
            #db.commit()
            return redirect(url_for('profile'))

    return render_template('edit_profile.html', current_bio=current_bio)

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

    if request.method == "POST":
        db = sqlite3.connect(DB_FILE)
        c = db.cursor()
        #sixSongs = c.execute("SELECT * FROM song_data ORDER BY RANDOM() LIMIT 6")
        session["mySongs"] = [{"song_name": "Golden", "artist": "HUNTRIX", "image": "https://developers.elementor.com/docs/hooks/placeholder-image/"},
                              {"song_name": "IDK", "artist": "some person", "image": "https://developers.elementor.com/docs/hooks/placeholder-image/"}]
                              #sixSongs.fetchall()

        db.commit()
        db.close()

    return speechTextPage(allSongList = session.get('mySongs', []),
                          user=session['username'])

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

def speechTextPage(allSongList, user=''):
    return render_template('speech-text.html', allSongList=allSongList, user=user)


def leaderboardpage(user=''):
    return render_template("leaderboard.html", user=user, top_players=top_players)

#====================================================================================#
if __name__ == "__main__":  # false if this file imported as module
    #app.debug = True  # enable PSOD, auto-server-restart on code chg
    app.run(port=5000)
