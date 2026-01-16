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

import topsonggenerator as tsgPy

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
    chart_num TEXT NOT NULL,
    lyrics TEXT NOT NULL
);""")

# try opening APIs (try/except) to insert data into APIs
try:
    with urllib.request.urlopen("https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/date/2015-11-07.json") as response:
        a = json.loads(response.read())
        for song in a['data']:
            command = "INSERT OR IGNORE INTO song_data(song_name, artist, chart_num, lyrics) VALUES(?, ?, ?, ?)"
            categories = (song['song'], song['artist'], song['last_week'], '')
            #print(categories)
            c.execute(command, categories)
except Exception as e:
    print(f"*********Error with Billboard API: {e}*********")

db.commit()

# get lyrics for songs
c.execute("SELECT song_name, artist FROM song_data")
song_list = c.fetchall()
#print("\n",song_list)

for song in song_list[:30]:
    # (name, artist)
    song_name = urllib.parse.quote(song[0])
    artist = urllib.parse.quote(song[1])
    try:
        url = f"https://api.lyrics.ovh/v1/{artist}/{song_name}"
        #print(url)
        with urllib.request.urlopen(url) as response:
            a = json.loads(response.read())
            lyrics = a.get('lyrics')

            if lyrics:
                c.execute("UPDATE song_data SET lyrics = ? WHERE song_name = ? AND artist = ?", (lyrics, song_name, artist))
                #print(lyrics)
            else:
                c.execute("DELETE FROM song_data WHERE song_name = ? AND artist = ?",
                          (song_name, artist))
        db.commit()
    except Exception as e:
        print(f"*Error with Lyrics API for {song}: {e}*")

print("\n*********FINISH LYRICS*********")

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
    return render_template('profile.html', bio=bio[0])

@app.route("/edit_profile", methods=['GET', 'POST'])
def edit_profile():
    if not loggedin():
        return redirect(url_for('login'))

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()
        current_bio = c.execute("SELECT bio FROM user_data WHERE username=?", (session['username'],)).fetchone()
        print(current_bio)
        if request.method == 'POST':
            newbio = request.form.get('newbio').strip()
            c.execute("UPDATE user_data SET bio=? WHERE username=?", (newbio, session['username'],))
            db.commit()
            return redirect(url_for('profile'))

    return render_template('edit_profile.html', current_bio=current_bio[0])

@app.route("/tsg/<link>", methods=['GET', 'POST'])
def tsg(link):
    if not loggedin():
        return redirect(url_for('login'))

    session['selected_list'] = "[Adventure of a Lifetime, Coldplay], [Blank Space, Taylor Swift]"
    session['selected_list'] = stringToList(session['selected_list'])

    if 'selected_list' not in session or 'selected_list' is None or len(session['selected_list']) < 2:
        return redirect(url_for('speech-text'))

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()

        firstSong = c.execute("SELECT lyrics FROM song_data where song_name = ? AND artist = ?",
                              (session['selected_list'][0][0], session['selected_list'][0][1])).fetchone()
        secondSong = c.execute("SELECT lyrics FROM song_data where song_name = ? AND artist = ?",
                              (session['selected_list'][1][0], session['selected_list'][1][1])).fetchone()

        if firstSong:
            firstSong = firstSong[0] #tuple to string
        else:
            firstSong = ""

        if secondSong:
            secondSong = secondSong[0]
        else:
            secondSong = ""

        print(f"\n\n{firstSong}\n\n")
        print(f"\n\n{secondSong}\n\n")

    newSongLyrics = tsgPy.combinesongs(firstSong, secondSong)
    newSongTitle = ''

    if request.method == 'POST':
        newSongTitle = link

        if not newSongTitle:
            return redirect(url_for('speech-text'))

        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            result = c.execute("SELECT saved_songs, total_songs FROM user_data WHERE username = ?", (session['username'],))
            old_songs_result = result.fetchone()

            if result:
                old_songs, old_num = old_songs_result
            else:
                old_songs, old_num = ("", 0)

            old_songs += newSongTitle + "~"
            old_num += 1

            c.execute("UPDATE user_data SET saved_songs = ?, total_songs = ? WHERE username=?",
                      (old_songs, old_num, session['username']))

            db.commit()

    return tsgpage(newSongLyrics=newSongLyrics, newSongTitle=newSongTitle,
                   user=session['username'])

@app.route("/speech-text", methods=['GET', 'POST'])
def speechText():
    if not loggedin():
        return redirect(url_for('login'))

    if request.method == "POST":
        givenTitle = request.form.get("title", "").strip()

        if givenTitle == "":
            return speechTextPage(allSongList = session.get('mySongs', []),
                          user=session['username'])

        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            sixSongs = c.execute("SELECT * FROM song_data ORDER BY RANDOM() LIMIT 6")
            session["mySongs"] = sixSongs.fetchall()
            # [{"song_name": "Golden", "artist": "HUNTRIX", "image": "https://developers.elementor.com/docs/hooks/placeholder-image/"},
            # {"song_name": "IDK", "artist": "some person", "image": "https://developers.elementor.com/docs/hooks/placeholder-image/"}]

            return redirect(url_for('tsg', link=urllib.parse.quote(givenTitle)))

        db.commit()

    print(session.get('mySongs', []))
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

def tsgpage(newSongLyrics, newSongTitle, user=''):
    return render_template('tsg.html', newSongLyrics=newSongLyrics,
                           newSongTitle=newSongTitle, user=user)

def speechTextPage(allSongList, user=''):
    return render_template('speech-text.html', allSongList=allSongList, user=user)

def leaderboardpage(user=''):
    return render_template("leaderboard.html", user=user, top_players=top_players)

def stringToList(string):
    final = []

    songs = string.split("],")
    for song in songs:
        song = song.replace("[", "").replace("]","") # songs and artists split
        song = song.strip()

        split_song = song.split(",")
        final.append(split_song)
    return final


#====================================================================================#
if __name__ == "__main__":  # false if this file imported as module
    #app.debug = True  # enable PSOD, auto-server-restart on code chg
    app.run(port=5000)
