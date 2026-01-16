import random

#takes api call and turns it into a list of lyric strings
def lyriclist(string):
    lyrics = string.splitlines()
    for x in lyrics:
        lyrics[lyrics.index(x)] = x.replace("\n", "")
        lyrics[lyrics.index(x)] = x.replace("\r", "")
    lyrics = list(filter(None, map(str.strip, lyrics))) #got this pretty line of code off "geeks for geeks"
    #print(lyrics)
    return lyrics

#takes the two lists, picks the shorter one, randomly picks the lyrics between the two of them
def combinesongs(song1, song2):
    '''
    song1 = lyriclist(song1)
    song2 = lyriclist(song2)
    '''
    topsong = []
    oneselect = 0
    twoselect = 0
    linenum = 0

    # takes length of shorter song and makes it amount of strings in topsong 
    if len(song1) <= len(song2):
        songlength = len(song1)
    else:
        songlength = len(song2)
    #print(songlength)

    # for the length of lines in the new song, choose between song one and song two and add the correspondign line from either song
    # oneselect and twoselect are just for checking how many line are from each song
    #linenum to retrieve from song1 and song2
    while songlength > 0:
        x = random.randint(1, 2)
        if x == 1: 
            topsong.append(song1[linenum])
            linenum = linenum + 1
            oneselect = oneselect + 1
            songlength = songlength - 1
        else:
            topsong.append(song2[linenum])
            linenum = linenum + 1
            twoselect = twoselect + 1
            songlength = songlength - 1
    
    #print(topsong)
    #print(oneselect)
    #print(twoselect)

    return topsong

# test variables
thinkingoutloud = "When your legs don't work like they used to before\r\nAnd I can't sweep you off of your feet\r\nWill your mouth still remember the taste of my love?\r\nWill your eyes still smile from your cheeks?\r\nAnd darling I will be loving you till we're 70\r\nAnd baby my heart could still fall as hard at 23\n\nAnd I'm thinking about how\n\n\n\nPeople fall in love in mysterious ways\n\nMaybe just a touch of a hand\n\nWell me I fall in love with you every single day\n\nAnd I just wanna tell you I am\n\n\n\nSo honey now, take me into your loving arms\n\nKiss me under the light of a thousand stars\n\nPlace your head on my beating heart, I'm thinking out loud\n\nAnd maybe we found love right where we are\n\n\n\nWhen my hair's all but gone and my memory fades\n\nAnd the crowds don't remember my name\n\nWhen my hands don't play the strings the same way\n\nI know you will still love me the same\n\nCause honey your soul could never grow old, it's evergreen\n\nAnd baby your smile's forever in my mind and memory\n\nAnd I'm thinking about how\n\n\n\nPeople fall in love in mysterious ways\n\nAnd maybe it's all part of a plan\n\nI'll just keep on making the same mistakes\n\nHoping that you'll understand\n\n\n\nBut baby now, take me into your loving arms\n\nKiss me under the light of a thousand stars\n\nPlace your head on my beating heart, I'm thinking out loud\n\nAnd maybe we found love right where we are\n\n\n\nSo baby now, take me into your loving arms\n\nKiss me under the light of a thousand stars, oh darling\n\nPlace your head on my beating heart, I'm thinking out loud\n\nThat maybe we found love right where we are\n\nAnd baby we found love right where we are\n\nAnd we found love right where we are"
adventureofalifetime = "Turn your magic on, Umi she'd say\r\nEverything you want's a dream away\r\nWe are legends, every day\r\nThat's what she told me\r\nTurn your magic on, to me she'd say\n\nEverything you want's a dream away\n\nUnder this pressure, under this weight\n\nWe are diamonds \n\n\n\nI feel my heart beating\n\nI feel my heart underneath my skin\n\nI feel my heart beating\n\nOh, you make me feel\n\nLike I'm alive again\n\n\n\nAlive again!\n\n\n\nOh, you make me feel\n\nLike I'm alive again\n\n\n\nSaid I can't go on, not in this way\n\nI'm a dream that died by light of day\n\nGonna hold up half the sky and say\n\nOnly I own me\n\n\n\nI feel my heart beating\n\nI feel my heart underneath my skin\n\nOh, I can feel my heart beating\n\n'Cause you make me feel\n\nLike I'm alive again\n\n\n\nAlive again!\n\n\n\nOh, you make me feel\n\nLike I'm alive again\n\n\n\nTurn your magic on, Umi she'd say\n\nEverything you want's a dream away\n\nUnder this pressure, under this weight\n\nWe are diamonds taking shape\n\nWe are diamonds taking shape\n\n\n\n(Woo, woo)\n\n\n\nIf we've only got this life\n\nThis adventure, oh then I\n\nAnd if we've only got this life\n\nYou'll get me through alive\n\nAnd if we've only got this life\n\nIn this adventure, oh then I\n\nWanna share it with you\n\nWith you, with you\n\nI said, oh, say oh\n\n\n\n(Woo hoo, woo hoo...)"
a = "1a\r\n2a\r\n3a\n\n4a\r\n"
b = "1b\r\n2b\r\n3b\n\n4b\r\n"

# test cases
#print(len(lyriclist(thinkingoutloud)))
#print(len(lyriclist(adventureofalifetime)))
#combinesongs(thinkingoutloud, adventureofalifetime)
#combinesongs(a, b)
