import RANDOM

def lyriclist(string):
    string.split("\n")
    for x in string:
        if string == "\n" or string == "\r":
            string.replace(x , "")
    for x in string:
        if x == "":
            string.remove(x)
    print(string)
    return string

lyriclist("When your legs don't work like they used to before\r\nAnd I can't sweep you off of your feet\r\nWill your mouth still remember the taste of my love?\r\nWill your eyes still smile from your cheeks?\r\nAnd darling I will be loving you till we're 70\r\nAnd baby my heart could still fall as hard at 23\n\nAnd I'm thinking about how\n\n\n\nPeople fall in love in mysterious ways\n\nMaybe just a touch of a hand\n\nWell me I fall in love with you every single day\n\nAnd I just wanna tell you I am\n\n\n\nSo honey now, take me into your loving arms\n\nKiss me under the light of a thousand stars\n\nPlace your head on my beating heart, I'm thinking out loud\n\nAnd maybe we found love right where we are\n\n\n\nWhen my hair's all but gone and my memory fades\n\nAnd the crowds don't remember my name\n\nWhen my hands don't play the strings the same way\n\nI know you will still love me the same\n\nCause honey your soul could never grow old, it's evergreen\n\nAnd baby your smile's forever in my mind and memory\n\nAnd I'm thinking about how\n\n\n\nPeople fall in love in mysterious ways\n\nAnd maybe it's all part of a plan\n\nI'll just keep on making the same mistakes\n\nHoping that you'll understand\n\n\n\nBut baby now, take me into your loving arms\n\nKiss me under the light of a thousand stars\n\nPlace your head on my beating heart, I'm thinking out loud\n\nAnd maybe we found love right where we are\n\n\n\nSo baby now, take me into your loving arms\n\nKiss me under the light of a thousand stars, oh darling\n\nPlace your head on my beating heart, I'm thinking out loud\n\nThat maybe we found love right where we are\n\nAnd baby we found love right where we are\n\nAnd we found love right where we are"
)

def combinesongs(song1, song2):
    topsong = []

    # takes length of shorter song and makes it the length of the new one
    if len(song1) <= len(song2):
        songlength = len(song1)
    else: songlength = len(song2)

    for songlength > 0:
        x = random(1, 2)
