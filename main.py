## ATTENTION: ALL DATA IS FROM 2020! ##
## Newer Anime's will not appear most likely! ##

###################
## CONFIGURATION ##
###################
from configparser import ConfigParser
config_obj = ConfigParser()
config_obj.read('config.ini')

ConfigData = config_obj['AnimeConfiguration']

WATCHED_ANIMES = [ #Insert Watched Animes Here
    "Steins;Gate",
    "Spy x Family",
    "Naruto",
]
WATCHED_ANIMES = config_obj.get("AnimeConfiguration", "watched_animes").strip('][').split(', ')
#May need to change the title to their original japanese name to be able to access the anime data

SORT_BY = "Genre"
SORT_BY = ConfigData['sort_by']
# Sorting Types:
#   - Genre (Genre Relation to Your Watched Animes) DEFAULT***
#   - Popularity (Number of People Watching the Show)
#   - Rating (Rating of the Show)


NUMBER_OF_RECCOMENDATIONS = 10
NUMBER_OF_RECCOMENDATIONS = int(ConfigData['number_of_reccomendations'])
# Can go up to 12289 Animes #

USERNAME = "User"
USERNAME = ConfigData['username']
# Can be anything

latestData = True
latestData = str.lower(ConfigData['latestdata']) == "true"
#Latest Data: True (Anime's from before 2020 will be chosen from the dataset)
#Latest Data: False (Anime's from before 2012 will be chosen from the dataset)

############################

"""
config_obj["AnimeConfiguration"] = {
    "WATCHED_ANIMES" : [
        "Steins;Gate",
        "Spy x Family",
        "Naruto",
    ],
    "SORT_BY" : "Genre",
    "NUMBER_OF_RECCOMENDATIONS" : 10,
    "USERNAME" : "User",
    "latestData" : True,
}

with open('config.ini', 'w') as configfile:
    config_obj.write(configfile)
"""

import pandas as pd
import numpy as np
import re
if latestData == True:
    df = pd.read_csv('data/animeUpdated.csv')
    #print(df)
else:
    df = pd.read_csv('data/anime.csv')

lenAdd = 7 #Constant for reccomendation length

def getAnimesByTitle(title): #Returns dataframe of all animes with the given title
    title = str.lower(title)
    title = str.rstrip(title)
    title = re.sub("[^a-z0-9]", "", title)
    #print("----------------"+title+"------------------")
    if latestData == True:
        return df[df['Name'].str.lower().str.rstrip().str.replace("[^a-z0-9]", "", regex = True).str.contains(title)].to_numpy()
    else:
        return df[df['name'].str.lower().str.rstrip().str.replace("[^a-z0-9]", "", regex = True).str.contains(title)].to_numpy()
    
def checkIfSame(title, anims): #Checks if the anime is already in already watched list
    for i in anims:
        if latestData == True:
            anim = i[4]
            if i[4] == "Unknown":
                anim = i[1]
            if (re.sub("[^a-z0-9]", "", str.rstrip(str.lower(anim))).find(re.sub("[^a-z0-9]", "", str.rstrip(str.lower(title)))) != -1 or re.sub("[^a-z0-9]", "", str.rstrip(str.lower(title))).find(re.sub("[^a-z0-9]", "", str.rstrip(str.lower(anim)))) != -1) and re.sub("[^a-z0-9]", "", str.rstrip(str.lower(title))) != "":
                return True
        else:
            if (re.sub("[^a-z0-9]", "", str.rstrip(str.lower(i[1]))).find(re.sub("[^a-z0-9]", "", str.rstrip(str.lower(title)))) != -1 or re.sub("[^a-z0-9]", "", str.rstrip(str.lower(title))).find(re.sub("[^a-z0-9]", "", str.rstrip(str.lower(i[1])))) != -1):
                return True
    return False

def getAllWatchedAnimes():
    arr = []
    for title in WATCHED_ANIMES:
        for anime in getAnimesByTitle(title):
            if latestData == True:
                anim = anime[4]
                if anime[4] == "Unknown":
                    anim = anime[1]
                if len(re.sub("[^a-z0-9]", "", str.rstrip(anim))) < len(re.sub("[^a-z0-9]", "", str.rstrip(title)))+lenAdd:
                    arr.append(anime)
            else:
                if len(re.sub("[^a-z0-9]", "", str.rstrip(anime[1]))) < len(re.sub("[^a-z0-9]", "", str.rstrip(title)))+lenAdd:
                    arr.append(anime)
    return arr

def getGenresFromStr(s):
    if not isinstance(s, str):
        return ["Unknown"]
    ret = s.split(',')
    i = 0
    while i < len(ret):
        ret[i] = str.lower(ret[i]).strip(" ,")
        i += 1
    return ret

def scoreAnime(anime, profile): #Can go from 0-1
    #Anime Arr Setup (Old Data):
    # - [0] = Anime ID
    # - [1] = Anime Name
    # - [2] = Genre
    # - [3] = Type Old
    # - [4] = Episodes
    # - [5] = Rating
    # - [6] = Members

    #Anime Arr Setup (New Data):
    # MAL_ID,Name,Score,Genres,English name,Japanese name,Type,Episodes,Aired,Premiered,Producers,Licensors,Studios,Source,Duration,Rating,Ranked,Popularity,Members...

    GENRE_SCORE = 0 #0-5 Weighted the MOST
    EPISODE_SCORE = 0 #0-5 (5 == Full Season (24 Episodes or Movie), 0 == No Episodes)
    POPULARITY_SCORE = 0 #0-100 (100 == Most Popular)
    RATING_SCORE = 0 #0-5 (5 == Best)

    TopGenres = profile.getTopGenres(5) #Can score 0-5 on Genres

    if latestData == True:
        AnimeGenres = getGenresFromStr(anime[3])
    else:
        AnimeGenres = getGenresFromStr(anime[2])

    for genre in AnimeGenres:
        if genre in TopGenres:
            GENRE_SCORE += 1

    if latestData == True:
        if anime[6] == "TV":
            if anime[7] == "Unknown":
                EPISODE_SCORE = 0
            elif int(anime[7]) >= 24:
                EPISODE_SCORE = 1
            else:
                EPISODE_SCORE = int(anime[7])/24
        else:
            EPISODE_SCORE = 1
        EPISODE_SCORE *= 5
    else:
        if anime[3] == "TV":
            if anime[4] == "Unknown":
                EPISODE_SCORE = 0
            elif int(anime[4]) >= 24:
                EPISODE_SCORE = 1
            else:
                EPISODE_SCORE = int(anime[4])/24
        else:
            EPISODE_SCORE = 1
        EPISODE_SCORE *= 5

    if latestData == True:
        POPULARITY_SCORE = int(anime[18])/2589552
    else:
        POPULARITY_SCORE = anime[6]/10140

    if latestData == True:
        if anime[2] == "Unknown":
            RATING_SCORE = 3
        else:
            RATING_SCORE = float(anime[2])/2
    else:
        RATING_SCORE = anime[5]/2

    if SORT_BY == "Popularity":
        GENRE_SCORE *= 20 #/100
        EPISODE_SCORE *= 1#/5
        POPULARITY_SCORE *= 0.5#/50
        RATING_SCORE *= 4#/20

        return (GENRE_SCORE + EPISODE_SCORE + POPULARITY_SCORE + RATING_SCORE)/175
    elif SORT_BY == "Rating":
        GENRE_SCORE *= 20 #/100
        EPISODE_SCORE *= 1#/5
        POPULARITY_SCORE *= 0#/0
        RATING_SCORE *= 15#/75

        return (GENRE_SCORE + EPISODE_SCORE + POPULARITY_SCORE + RATING_SCORE)/180
    elif SORT_BY == "Genre" or SORT_BY == None:
        GENRE_SCORE *= 20 #/100
        EPISODE_SCORE *= 1#/5
        POPULARITY_SCORE *= 0.2#/20
        RATING_SCORE *= 0#/0

        return (GENRE_SCORE + EPISODE_SCORE + RATING_SCORE + POPULARITY_SCORE)/125

class Profile:
    def __init__(self, name, watched):
        self.name = name
        self.watched_animes = watched
        self.favGenres = {}
        self.matchingAnimes = [] #Names of Animes

    def updateGenres(self):
        self.favGenres = {}
        for i in self.watched_animes:
            if latestData == True:
                genreList = getGenresFromStr(i[3])
            else:
                genreList = getGenresFromStr(i[2])
            for genre in genreList:
                if self.favGenres.get(genre) == None:
                    self.favGenres[genre] = 1
                else:
                    self.favGenres[genre] += 1
    
    def getGenres(self):
        return self.favGenres

    def getTopGenres(self, num): #SOMETHING IS WRONG WITH THIS??? for new data
        sort = []

        def ins(genreName, Num):
            for i in range(len(sort)):
                if sort[i] != None and sort[i][1] <= Num:
                    sort.insert(i, [genreName, Num])
                    return
            sort.append([genreName, Num])


        for i in self.favGenres:
            ins(i, self.favGenres[i])

        ret = {}
        for i in range(num):
            if len(sort) > i:
                ret[sort[i][0]] = sort[i][1]
        return ret

    def getMatchingAnimes(self):
        def SORT_BY_SCORE(e):
            return e[1]

        self.matchingAnimes = []
        for i in range(len(df)):
            if latestData == True:
                anim = [df.loc[i, "MAL_ID"],df.loc[i, "Name"],df.loc[i, "Score"],df.loc[i, "Genres"],df.loc[i, "English name"],df.loc[i, "Japanese name"],df.loc[i, "Type"],df.loc[i, "Episodes"],df.loc[i, "Aired"],df.loc[i, "Premiered"],df.loc[i, "Producers"],df.loc[i, "Licensors"],df.loc[i, "Studios"],df.loc[i, "Source"],df.loc[i, "Duration"],df.loc[i, "Rating"],df.loc[i, "Ranked"],df.loc[i, "Popularity"],df.loc[i, "Members"]]
                SSSSSS = anim[4]
                if anim[4] == "Unknown":
                    SSSSSS = anim[1]
                if checkIfSame(SSSSSS, self.watched_animes) == True:
                    continue
            else:
                anim = [df.loc[i, "anime_id"],df.loc[i, "name"],df.loc[i, "genre"],df.loc[i, "type"],df.loc[i, "episodes"],df.loc[i, "rating"],df.loc[i, "members"]]
                if checkIfSame(anim[1], self.watched_animes) == True:
                    continue

            score = scoreAnime(anim, self)
            #print(len(self.matchingAnimes))

            if len(self.matchingAnimes) < NUMBER_OF_RECCOMENDATIONS+5:
                self.matchingAnimes.append([anim, score])
                continue
            elif score >= self.matchingAnimes[NUMBER_OF_RECCOMENDATIONS+5-1][1]:
                self.matchingAnimes.append([anim, score])
                self.matchingAnimes.sort(key=SORT_BY_SCORE, reverse=True)
                self.matchingAnimes.pop()
        return self.matchingAnimes

    def displayMatchingAnimes(self):
        print("---------------- "+self.name+"'s Anime Reccomendations ------------------")
        print("Sorted by: "+SORT_BY)
        print("")
        iter = 1
        for i in self.matchingAnimes:
            if iter > NUMBER_OF_RECCOMENDATIONS:
                break
            print("Anime #"+str(iter)+": "+str(i[0][1])+" (Comparison: %"+str(i[1]*100)+")")
            iter+= 1
        print("\nTop Anime Genre: "+str(list(self.getTopGenres(1).keys())[0]))
            

print("Creating Profile...")
me = Profile(USERNAME, getAllWatchedAnimes())
print("Updating Genres...")
me.updateGenres()
print("Getting Reccomendations...")
me.getMatchingAnimes()
me.displayMatchingAnimes()
