# TARGET SHIP DATE: 2026-01-16
# Ethan Cheung (PM), Amy Shrestha, Jason Chan, Matthew Ciu
# JAMEs
# SoftDev
# P02
# 2025-01-09
# time spent: 28.0

from flask import Flask
from flask import render_template  # facilitate jinja templating
from flask import request, redirect, url_for  # facilitate form submission
from flask import session
import sqlite3  # enable control of an sqlite database
import urllib.request
import json
import random

import topsonggenerator as tsgPy

# FLASK Declaration
# ====================================================================================#
app = Flask(__name__)  # create Flask object
app.secret_key = b"weRtheJAMEs"


def getRealArtist(string):
    lst = [" Featuring ", " + ", " & "]
    for i in lst:
        if i in string:
            string = string.split(i)[0]
            break

    return string


# SQLITE3 Databases
# ====================================================================================#
DB_FILE = "songs.db"

db = sqlite3.connect(
    DB_FILE, check_same_thread=False
)  # open if file exists, otherwise create
c = db.cursor()

# create db tables
c.execute(
    """
CREATE TABLE IF NOT EXISTS user_data(
    user_id INTEGER PRIMARY KEY NOT NULL,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    saved_songs TEXT,
    total_songs INTEGER,
    bio TEXT
);"""
)

c.execute(
    """
CREATE TABLE IF NOT EXISTS song_data(
    song_name TEXT NOT NULL,
    artist TEXT NOT NULL,
    chart_num TEXT NOT NULL,
    lyrics TEXT NOT NULL,
    cover TEXT,
    UNIQUE(song_name, artist)
);"""
)

# try opening APIs (try/except) to insert data into APIs
try:
    with urllib.request.urlopen(
        "https://raw.githubusercontent.com/mhollingshead/billboard-hot-100/main/date/2015-11-07.json"
    ) as response:
        a = json.loads(response.read())
        for song in a["data"]:
            command = "INSERT OR IGNORE INTO song_data(song_name, artist, chart_num, lyrics, cover) VALUES(?, ?, ?, ?, ?)"
            categories = (song["song"], song["artist"], song["last_week"], "", "")
            # print(categories)
            c.execute(command, categories)
except Exception as e:
    print(f"*********Error with Billboard API: {e}*********")

db.commit()

# get lyrics for songs
c.execute("SELECT song_name, artist FROM song_data")
song_list = c.fetchall()
# print("\n",song_list)

for song in song_list:
    # (name, artist)
    song_name = song[0]
    artist = song[1]
    realArtist = getRealArtist(song[1])

    song_name_url = urllib.parse.quote(song_name)
    artist_url = urllib.parse.quote(realArtist)
    try:
        url = f"https://api.lyrics.ovh/v1/{artist_url}/{song_name_url}"
        # print(url)
        with urllib.request.urlopen(url) as response:
            a = json.loads(response.read())
            lyrics = a.get("lyrics")

            if lyrics:
                c.execute(
                    "UPDATE song_data SET lyrics = ? WHERE song_name = ? AND artist = ?",
                    (lyrics, song_name, artist),
                )
                # print(lyrics)
        db.commit()
    except Exception as e:
        print(f"*Error with Lyrics API for {song}: {e}*")


print("\n*********FINISH LYRICS*********")
db.commit()


c.execute("SELECT DISTINCT artist FROM song_data")
song_list2 = c.fetchall()

with open("app/keys/key_albumcover.txt", "r") as a:
    key = a.read().strip()

for song in song_list2:
    try:
        artist = urllib.parse.quote(getRealArtist(song[0]))
        oldArtist = song[0]
        with urllib.request.urlopen(
            f"http://ws.audioscrobbler.com/2.0/?method=artist.gettopalbums&artist={artist}&api_key={key}&format=json"
        ) as response:
            a = json.loads(response.read())
            albums = a["topalbums"].get("album")

            randCovers = random.choice(albums).get("image")
            randCover = ""
            for i in randCovers:
                if i.get("#text") and i.get("size") == "large":
                    randCover = i["#text"]
                    break

            if randCover:
                c.execute(
                    "UPDATE song_data SET cover = ? WHERE artist = ?",
                    (randCover, oldArtist),
                )
    except Exception as e:
        print(f"*********Error with Album Cover API: {e}*********")

db.commit()


# Helper Functions
# ====================================================================================#
usernames = {}
with sqlite3.connect(DB_FILE) as db:
    c = db.cursor()
    c.execute("SELECT username, password FROM user_data")
    rows = c.fetchall()
    for row in rows:
        usernames[row[0]] = row[1]

print(usernames)


def loggedin():
    if "username" in session:
        return True
    return False


def stringToList(string):
    final = []

    songs = string.split("],")
    for song in songs:
        song = song.replace("[", "").replace("]", "")  # songs and artists split
        song = song.strip()

        split_song = song.split(",")
        final.append(split_song)
    return final


# Webpage Sites
# ====================================================================================#
@app.route("/home", methods=["GET", "POST"])
def home():
    return homepage()


@app.route("/register", methods=["GET", "POST"])
def register():
    idVals = 0
    if loggedin():
        return redirect(url_for("home"))
    else:
        if request.method == "POST":
            with sqlite3.connect(DB_FILE) as db:
                c = db.cursor()

                rows = c.execute(
                    "SELECT username FROM user_data WHERE username = ?",
                    (request.form["username"],),
                )
                result = rows.fetchone()
                if result:
                    return registerpage(False, "Duplicate username")
                session.permanent = True

                # for invalid requests / empty form responses
                t = ""
                if request.form["username"] == "" or request.form["password"] == "":
                    t = "Please enter a valid "
                    if request.form["username"] == "":
                        t = t + "username "
                    if request.form["password"] == "":
                        t = t + "password "
                    return registerpage(False, t)

                c.execute(
                    "INSERT INTO user_data VALUES (?, ?, ?, ?, ?, ?);",
                    (
                        None,
                        request.form["username"],
                        request.form["password"],
                        "",
                        0,
                        "No bio",
                    ),
                )
                db.commit()

                session.clear()
                session.permanent = True
                session["username"] = request.form["username"]
                return redirect(url_for("home"))
    return registerpage()


@app.route("/login", methods=["GET", "POST"])
def login():
    if loggedin():
        return redirect(url_for("home"))

    if request.method == "POST":
        session.clear()
        session.permanent = True
        with sqlite3.connect(DB_FILE) as db:
            c = db.cursor()
            rows = c.execute(
                "SELECT * FROM user_data WHERE username = ?;",
                (request.form["username"],),
            )
            result = rows.fetchone()

            if result is None:
                return loginpage(False, "Username does not exist")
            elif request.form["password"] != result[2]:
                return loginpage(False, "Your password was incorrect")

            session["username"] = request.form["username"]
            return redirect(url_for("home"))
    else:
        return loginpage(True)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if not loggedin():
        return redirect(url_for("login"))

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()
        r = c.execute(
            "SELECT bio, saved_songs, total_songs FROM user_data WHERE username=?",
            (session["username"],),
        ).fetchone()

    if r:
        bio, saved_songs_string, total_songs = r
        saved_songs = []
        if saved_songs_string:
            for item in saved_songs_string.strip("~").split("~"):
                if "|" in item:
                    name, artist = item.split("|")
                    d = {"name": name, "artist": artist}
                    saved_songs.append(d)
    else:
        bio, saved_songs_string, total_songs = "No bio", [], 0
    # do stuff
    return render_template(
        "profile.html",
        bio=bio,
        total_songs=total_songs,
        saved_songs=saved_songs,
        name=session["username"],
    )


@app.route("/edit_profile", methods=["GET", "POST"])
def edit_profile():
    if not loggedin():
        return redirect(url_for("login"))

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()
        current_bio = c.execute(
            "SELECT bio FROM user_data WHERE username=?", (session["username"],)
        ).fetchone()
        print(current_bio)
        if request.method == "POST":
            newbio = request.form.get("newbio").strip()
            c.execute(
                "UPDATE user_data SET bio=? WHERE username=?",
                (
                    newbio,
                    session["username"],
                ),
            )
            db.commit()
            return redirect(url_for("profile"))

    return render_template(
        "edit_profile.html", current_bio=current_bio[0], name=session["username"]
    )


@app.route("/tsg/<link>", methods=["GET", "POST"])
def tsg(link):
    if not loggedin():
        return redirect(url_for("login"))

    # session['selected_list'] = "[Adventure of a Lifetime, Coldplay], [Cheerleader, OMI]"
    # session['selected_list'] = stringToList(session['selected_list'])

    if (
        "selected_list" not in session
        or "selected_list" is None
        or len(session["selected_list"]) < 2
    ):
        return redirect(url_for("speech-text"))

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()

        firstSong = c.execute(
            "SELECT lyrics FROM song_data where song_name = ? AND artist = ?",
            (
                session["selected_list"][0][0],
                getRealArtist(session["selected_list"][0][1]),
            ),
        ).fetchone()
        secondSong = c.execute(
            "SELECT lyrics FROM song_data where song_name = ? AND artist = ?",
            (
                session["selected_list"][1][0],
                getRealArtist(session["selected_list"][1][1]),
            ),
        ).fetchone()
        print("DB artist:", session["selected_list"][0][1])
        print("Querying with:", getRealArtist(session["selected_list"][0][1]))

        if firstSong:
            firstSong = firstSong[0]  # tuple to string
        else:
            firstSong = ""

        if secondSong:
            secondSong = secondSong[0]
        else:
            secondSong = ""

        # print(f"\n\n{firstSong}\n\n")
        # print(f"\n\n{secondSong}\n\n")

    newSongLyrics = ""

    if firstSong and secondSong:
        firstSongList = tsgPy.lyriclist(firstSong)
        secondSongList = tsgPy.lyriclist(secondSong)
        newSongLyrics = tsgPy.combinesongs(firstSongList, secondSongList)

    print(f"\n\n{newSongLyrics}\n\n")
    newSongTitle = urllib.parse.unquote(link)

    firstSongD = {
        "name": session["selected_list"][0][0],
        "artist": getRealArtist(session["selected_list"][0][1]),
    }
    secondSongD = {
        "name": session["selected_list"][1][0],
        "artist": getRealArtist(session["selected_list"][1][1]),
    }

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()
        result = c.execute(
            "SELECT saved_songs, total_songs FROM user_data WHERE username = ?",
            (session["username"],),
        )
        old_songs_result = result.fetchone()

        if result:
            old_songs, old_num = old_songs_result
        else:
            old_songs, old_num = ("", 0)

        for song in [firstSongD, secondSongD]:
            old_songs += f"{song['name']}|{song['artist']}~"
            old_num += 1

        c.execute(
            "UPDATE user_data SET saved_songs = ?, total_songs = ? WHERE username=?",
            (old_songs, old_num, session["username"]),
        )

        db.commit()

    session.pop("selected_list", None)
    session.pop("mySongs", None)

    return tsgpage(
        newSongLyrics=newSongLyrics,
        newSongTitle=newSongTitle,
        a=[firstSongD, secondSongD],
        user=session["username"],
    )


@app.route("/speech-text", methods=["GET", "POST"])
def speechText():
    if not loggedin():
        return redirect(url_for("login"))
    givenTitle = ""

    with sqlite3.connect(DB_FILE) as db:
        c = db.cursor()
        sixSongs = c.execute(
            "SELECT song_name, artist, cover FROM song_data WHERE lyrics IS NOT NULL AND lyrics != '' ORDER BY RANDOM() LIMIT 6"
        )
        sixSongs = sixSongs.fetchall()
        # [{"song_name": "Golden", "artist": "HUNTRIX", "image": "https://developers.elementor.com/docs/hooks/placeholder-image/"},
        # {"song_name": "IDK", "artist": "some person", "image": "https://developers.elementor.com/docs/hooks/placeholder-image/"}]
    db.commit()

    if "selected_list" not in session or session["selected_list"] is None:
        session["selected_list"] = []
    if "mySongs" not in session:
        session["mySongs"] = sixSongs

    if request.method == "POST":
        chooseSong = request.form.get("select")
        if chooseSong:
            song_name, artist = chooseSong.split("|")
            session["selected_list"].append([song_name.strip(), artist.strip()])
        if "create_song" in request.form:
            givenTitle = request.form.get("title")

        if givenTitle:
            return redirect(url_for("tsg", link=urllib.parse.quote(givenTitle)))
        else:
            return speechTextPage(
                allSongList=session["mySongs"],
                song_list=session["selected_list"],
                user=session["username"],
            )
    # print(session.get('mySongs', []))
    return speechTextPage(
        allSongList=session["mySongs"],
        song_list=session["selected_list"],
        user=session["username"],
    )


@app.route("/leaderboard", methods=["GET", "POST"])
def leaderboard():
    if not loggedin():
        return redirect(url_for("login"))

    with sqlite3.connect("songs.db") as db:
        c = db.cursor()
        c.execute(
            "SELECT username, total_songs FROM user_data ORDER BY total_songs DESC LIMIT 10"
        )
        top_players = c.fetchall()

    return render_template(
        "leaderboard.html",
        username=session["username"],  # Pass current username to leaderboard.html
        top_players=top_players,  # Pass the top 10 players to leaderboard.html
    )


@app.route("/logout")
def logout():
    session.pop("username", None)  # remove username from session
    return redirect(url_for("login"))


# HTML Pages
# ====================================================================================#
def homepage():
    return render_template("home.html")


def registerpage(valid=True, invalid=""):
    if valid == True:
        return render_template("register.html", invalid=invalid)
    else:
        return render_template("register.html", invalid=invalid)
    return render_template("register.html")


def loginpage(valid=True, invalid=""):
    if valid == True:
        return render_template("login.html", invalid=invalid)
    else:
        return render_template("login.html", invalid=invalid)


def tsgpage(newSongLyrics, newSongTitle, a, user=""):
    return render_template(
        "tsg.html",
        newSongLyrics=newSongLyrics,
        newSongTitle=newSongTitle,
        a=a,
        user=user,
    )


def speechTextPage(allSongList, song_list, user=""):
    return render_template(
        "speech-text.html", allSongList=allSongList, song_list=song_list, user=user
    )


def leaderboardpage(user=""):
    return render_template("leaderboard.html", user=user, top_players=top_players)


# ====================================================================================#
if __name__ == "__main__":  # false if this file imported as module
    app.debug = True  # enable PSOD, auto-server-restart on code chg
    app.run(port=5000)
