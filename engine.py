import lenskit.datasets as ds
import pandas as pd
import csv
import wikidataManager as wm
from json import loads, dumps

  
def joinRatingWithGenreAndTitle(ratings,data):
    joined_data = ratings.join(data.movies['genres'], on='item')
    joined_data = joined_data.join(data.movies['title'], on='item')

    return joined_data

#1.1
data = ds.MovieLens('./datasets/')

print("Successfully installed dataset.")

#1.2
rows_to_show = 10   # <-- Try changing this number to see more rows of data
data.ratings.head(rows_to_show)  # <-- Try changing "ratings" to "movies", "tags", or "links" to see the kinds of data that's stored in the other MovieLens files
#print(data.ratings.head(rows_to_show))

#1.3
joined_data = joinRatingWithGenreAndTitle(data.ratings,data)
joined_data.head(rows_to_show)

#print(joined_data.head(rows_to_show))
#print(getUserRatings(joined_data,5))

#2.1.1
average_ratings = (data.ratings).groupby(['item']).mean()
sorted_avg_ratings = average_ratings.sort_values(by="rating", ascending=False)
joined_data = joinRatingWithGenreAndTitle(sorted_avg_ratings,data)
joined_data = joined_data[joined_data.columns[1:]]

print("RECOMMENDED FOR ANYBODY:")

#2.1.2
average_ratings = (data.ratings).groupby('item') \
       .agg(count=('user', 'size'), rating=('rating', 'mean')) \
       .reset_index()

sorted_avg_ratings = average_ratings.sort_values(by="rating", ascending=False)
joined_data = joinRatingWithGenreAndTitle(sorted_avg_ratings,data)
joined_data = joined_data[joined_data.columns[1:]]


print("RECOMMENDED FOR ANYBODY:")

#2.2
minimum_to_include = 20 #<-- You can try changing this minimum to include movies rated by fewer or more people

average_ratings = (data.ratings).groupby(['item']).mean()
rating_counts = (data.ratings).groupby(['item']).count()
average_ratings = average_ratings.loc[rating_counts['rating'] > minimum_to_include]
sorted_avg_ratings = average_ratings.sort_values(by="rating", ascending=False)
joined_data = joinRatingWithGenreAndTitle(sorted_avg_ratings,data)
joined_data = joined_data[joined_data.columns[3:]]

print("RECOMMENDED FOR ANYBODY:")


#2.3
def recommendedMoviesBasedOnGenre(genre,minimum_to_include):
    average_ratings = (data.ratings).groupby(['item']).mean()
    rating_counts = (data.ratings).groupby(['item']).count()
    average_ratings = average_ratings.loc[rating_counts['rating'] > minimum_to_include]
    average_ratings = average_ratings.join(data.movies['genres'], on='item')
    average_ratings = average_ratings.loc[average_ratings['genres'].str.contains(genre)]

    sorted_avg_ratings = average_ratings.sort_values(by="rating", ascending=False)
    joined_data = sorted_avg_ratings.join(data.movies['title'], on='item')
    joined_data = joined_data[joined_data.columns[3:]]
    print("RECOMMENDED FOR {} MOVIES FANS:".format(genre))
    
#recommendedMoviesBasedOnGenre('Action',minimum_to_include)
#recommendedMoviesBasedOnGenre('Romance',minimum_to_include)

"""import csv

jabril_rating_dict = {}
jgb_rating_dict = {}

with open("../datasets/jabril-movie-ratings.csv", newline='') as csvfile:
  ratings_reader = csv.DictReader(csvfile)
  for row in ratings_reader:
    if ((row['ratings'] != "") and (float(row['ratings']) > 0) and (float(row['ratings']) < 6)):
      jabril_rating_dict.update({int(row['item']): float(row['ratings'])})
      
with open("../datasets/jgb-movie-ratings.csv", newline='') as csvfile:
  ratings_reader = csv.DictReader(csvfile)
  for row in ratings_reader:
    if ((row['ratings'] != "") and (float(row['ratings']) > 0) and (float(row['ratings']) < 6)):
      jgb_rating_dict.update({int(row['item']): float(row['ratings'])})
     
print("Rating dictionaries assembled!")
print("Sanity check:")
print("\tJabril's rating for 1197 (The Princess Bride) is " + str(jabril_rating_dict[1197]))
print("\tJohn-Green-Bot's rating for 1197 (The Princess Bride) is " + str(jgb_rating_dict[1197]))
"""

def updateDict(record,dict):
    if ((record['rating'] != "") and (float(record['rating']) > 0) and (float(record['rating']) < 6)):
        dict.update({int(record['movieId']): float(record['rating'])})
  
def getUsersDics(userId1,userId2):
    user1RatingDict = {}
    user2RatingDict = {}
    with open("datasets/ratings.csv", newline='') as csvfile:
        ratings_reader = csv.DictReader(csvfile)
        for row in ratings_reader:
            if(row['userId'] == userId1):
                updateDict(row,user1RatingDict)
            elif(row['userId'] == userId2):
                updateDict(row,user2RatingDict)
            else:
                continue
    return user1RatingDict, user2RatingDict
  
from lenskit.algorithms import Recommender
from lenskit.algorithms.user_knn import UserUser

numberOfRecommendations = 10  #<---- This is the number of recommendations to generate. You can change this if you want to see more recommendations

userUser = UserUser(15, min_nbrs=3) #These two numbers set the minimum (3) and maximum (15) number of neighbors to consider. These are considered "reasonable defaults," but you can experiment with others too
algo = Recommender.adapt(userUser)
algo.fit(data.ratings)

print("Set up a User-User algorithm!")

def getDictRecommendations(userDict):
    userRecommendations = algo.recommend(-1, numberOfRecommendations, ratings=pd.Series(userDict))  #Here, -1 tells it that it's not an existing user in the set, that we're giving new ratings, while 10 is how many recommendations it should generate

    joinedData = joinRatingWithGenreAndTitle(userRecommendations,data)
    joinedData = joinedData[joinedData.columns[2:]]
    return joinedData
  
def getCombinedDict(dict1,dict2):
    combinedDict = {}
    for k in dict1:
      if k in dict2:
        combinedDict.update({k: float((dict1[k]+dict2[k])/2)})
      else:
        combinedDict.update({k:dict1[k]})
    for k in dict2:
      if k not in combinedDict:
          combinedDict.update({k:dict2[k]})
    return combinedDict
  

def geLensKitRecommendations(user1,user2,type):
    if(user2 == '""'):
        user1Dict, user2Dict = getUsersDics(user1,user1)
        return getDictRecommendations(user1Dict)
    else:
        user1Dict, user2Dict = getUsersDics(user1,user2)

        if (type == True):
            combinedDict = getCombinedDict(user1Dict,user2Dict)
            return getDictRecommendations(combinedDict)
        else:
            user1Recommendations = getDictRecommendations(user1Dict)
            user2Recommendations = getDictRecommendations(user2Dict)

            recommendations = pd.concat([user1Recommendations,user2Recommendations],axis=0)
            return recommendations.drop_duplicates(subset="title")
def getUserRatings(data,userId):
    id = 0
    if(len(userId)!= 0):
        id = int(userId)
    filtered_data = data.ratings[data.ratings['user'] == id]
    return filtered_data

def joinImdbId(ratings,numberOfRecordes):
    joinedRatines = ratings.join(data.links['imdbId'], on='item')
    joinedRatines = joinedRatines.sort_values(by="rating", ascending=False)
    joinedRatines = joinedRatines.head(numberOfRecordes)
    joinedRatines = joinedRatines[joinedRatines.columns[4:]]
    JoinedRatingsJsonString = joinedRatines.to_json(orient="records")
    joinedRatingsJson=loads(JoinedRatingsJsonString)
    return joinedRatingsJson

def getWikidataRecommendations(userId1,userId2):
    numberOfRecordes = 10
    user1ratings = getUserRatings(data,userId1)
    user1ratingsJson = joinImdbId(user1ratings,numberOfRecordes)
    ratings = user1ratingsJson
    print(ratings)

    if(len(userId2) >0):
        user2ratings = getUserRatings(data,userId2)
        user2ratingsJson = joinImdbId(user2ratings,numberOfRecordes)
        ratings+=user2ratingsJson
    imdbIds = []
    for rating in ratings:
        imdbIds.append("tt"+ str(rating["imdbId"]))
    movies = wm.getRecommendation(imdbIds)
    return removeDoublicats(movies)
def removeDoublicats(list):
    uniqueVeluesList = []
    newList = []
    for movie in list:
       if(movie["title"] not in uniqueVeluesList):
           uniqueVeluesList.append(movie["title"])
           newList.append(movie)
    return newList
#getUsersRecommendations("2","3",True)
#print(joined_data.head(rows_to_show))
#datad = joinRatingWithGenreAndTitle(user1Dict,data)
user1Dict = getUserRatings(data,"2")

datad = user1Dict.join(data.links['imdbId'], on='item')
datad = datad.sort_values(by="rating", ascending=False)
datad = datad.head(5)
recommendations = datad.to_json(orient="records")
l=loads(recommendations)
g=getWikidataRecommendations("2","3")
f=removeDoublicats(g)
print(f)
