"""
This file has been written by Yunseok Jang z5286005 since 29 / 3 / 2023.
"""

from web.mysql_util import MysqlUtil, get_pw

import numpy as np
from surprise import Reader, Dataset, SVD

import mysql.connector as connection
import pandas as pd

from scipy import sparse

from sklearn.metrics.pairwise import cosine_similarity 

import xgboost as xgb

import warnings

from datetime import date

warnings.filterwarnings('ignore')

def recommendation_for_home_page(db, uid:int):
    """
    Get recommendation for home page

    Parameters
    db: database connector instance
    uid(int): user id
    
    Returns
    list of recommended movies
    """
    how_many_recommendation = 5
    recommended_movies = get_recommendation_by_user(uid)[:how_many_recommendation]
    recommendation = []
    for mid in recommended_movies:
        sql = f"select * from Movies where id = {mid};"
        movie = db.fetchoneWithoutClose(sql)
        recommendation.append(movie)
    db.close_db()
    return recommendation

def recommendation_for_detail_page(db, genres, movie_detail):
    """
    Get recommendation for detail page

    Parameters
    db: database connector instance
    genres: list of genres of the movie
    movie_detail: details of the movie
    
    Returns
    list of recommended movies
    """
    how_many_recommendation = 3
    recommended_movies = []
    for genre in genres:
        recommended_movies += get_recommendation_by_genre(genre['id'])[:how_many_recommendation]
    recommended_movies = list(set(recommended_movies))
    if movie_detail['id'] in recommended_movies:
        recommended_movies.remove(movie_detail['id'])

    recommendation = []
    for mid in recommended_movies:
        sql = f"select * from Movies where id = {mid};"
        movie = db.fetchoneWithoutClose(sql)
        recommendation.append(movie)
    db.close_db()
    return recommendation


"""
RECOMMENDATION FUNCTIONS
1. Recommend by user reivews
2. Recommend by movie search
3. Recemmend by movie genre
"""

def get_recommendation_by_user(user_id:int):
    """
    Determine whether user is new or not.
    Use appropriate method to get recommendation depending on user's status.

    Parameters
    user_id(int): user id
    
    Returns
    list of recommended movies for the user based on user's reviews
    """
    if new_user(user_id):
        return cold_start()
    recommendation = collaborative_filter(user_id)
    return fill_recommendation(recommendation)

def get_recommendation_by_movie(user_id:int, movie_id:int):
    """
    Similar movie recommendation

    Parameters
    user_id(int): user id
    movie_id(int): movie id
    
    Returns
    list of recommended movies which is similar to the searched movie
    """
    train_data, _, _, _ = matrix_factorization(user_id)
    train_sparse_matrix = sparse.csr_matrix((train_data.rating.values, (train_data.user_id.values, train_data.movie_id.values)))
    movie_sim = cosine_similarity(train_sparse_matrix[:,movie_id].T, train_sparse_matrix.T).ravel()
    top_sim_movies = list(movie_sim.argsort()[::-1][1:])
    top_sim_movies.remove(0)
    return fill_recommendation(top_sim_movies)

def get_recommendation_by_genre(genre:int):
    """
    Similar movie recommendation by genre

    Parameters
    genre(int): genre id
    
    Returns
    list of recommended movies which has genre of selected genre
    """
    db = MysqlUtil()
    sql = f"select movie_id from Genres_of_Movies where genre_id = {genre}"
    m_ids = [m['movie_id'] for m in db.fetchall(sql)]
    avg_rating_factor = 3
    popularity_factor = 1
    wishlist_count_factor = 3
    release_date_factor = 100

    movie_with_score = []
    for id in m_ids:
        db = MysqlUtil()
        sql = f"select avg_rating, count_reviews, release_date from Movies where id = {id}"
        res1 = db.fetchone(sql)
        db = MysqlUtil()
        sql = f"select count(*) as wishlist_count from WishLists where movie_id = {id}"
        res2 = db.fetchone(sql)

        score = res1['avg_rating']*avg_rating_factor + res1['count_reviews']*popularity_factor + res2['wishlist_count']*wishlist_count_factor
        if (date.today()-res1['release_date']).days < 365:
            score += release_date_factor
        movie_with_score.append({"id": id, "score": score})

    rank = sorted(movie_with_score, key=lambda d: d['score'], reverse=True)
    rank_in_id = [movie['id'] for movie in rank]
    return rank_in_id

"""
HELPER FUNCTIONS
"""

def collaborative_filter(user_id:int):
    """
    Apply collaborative filtering to predict recommended movies

    Parameters
    user_id(int): user id
    
    Returns
    list of movies selected by applying collaborative filterting
    """
    train_data, user_data, train_pred_mf, user_pred_mf = matrix_factorization(user_id)
    if user_data.empty:
            return cold_start()
    final_train_data, final_user_data = hand_craft(train_data, train_pred_mf, user_data, user_pred_mf)
    final_model = create_model(final_train_data)
    prediction = predict(final_model, final_user_data)
    return predicted_movie_ratings_to_ids(prediction, final_user_data)

def matrix_factorization(user_id):
    """
    By matrix factorization, prepare train data and user data

    Parameters
    user_id(int): user id
    
    Returns
    train data, user data and prediction for each
    """
    train_data = data_as_dataframe()
    user_data = user_prediction_dataframe(user_id)

    # create the train data from the data frame
    train_data_mf = Dataset.load_from_df(train_data[['user_id', 'movie_id', 'rating']], Reader(rating_scale=(1,5)))
    user_data_mf = Dataset.load_from_df(user_data[['user_id', 'movie_id', 'rating']], Reader(rating_scale=(1,5)))

    # build the train set from traindata. 
    # it is of dataset format from surprise library
    trainset = train_data_mf.build_full_trainset()
    userset = user_data_mf.build_full_trainset()

    svd = SVD(n_factors=100, biased=True, random_state=15, verbose=False)
    svd.fit(trainset)

    # getting predictions of train set
    train_preds = svd.test(trainset.build_testset())
    train_pred_mf = np.array([pred.est for pred in train_preds])

    svd.fit(userset)
    user_preds = svd.test(userset.build_testset())
    user_pred_mf = np.array([pred.est for pred in user_preds])

    return train_data, user_data, train_pred_mf, user_pred_mf

def hand_craft(train_data, train_mf_svd, user_data, user_mf_svd):
    """
    Calculate some information using the data that will be used as an input to create a model

    Parameters
    train_data, train_mf_svd, user_data, user_mf_svd
    
    Returns
    train result and user result
    """
    # Creating a sparse matrix
    train_sparse_matrix = sparse.csr_matrix((train_data.rating.values, (train_data.user_id.values, train_data.movie_id.values)))
    train_averages = get_train_averages(train_sparse_matrix)

    train_result_data = []

    for index, row in train_data.iterrows():
        user = row['user_id']
        movie = row['movie_id']
        rating = row['rating']
        top_sim_users_ratings = top_sim_users(train_sparse_matrix, train_averages, user, movie, 5)
        top_sim_movies_ratings = top_sim_movies(train_sparse_matrix, train_averages, user, movie, 5)

        train_result_data.append([user, movie, train_averages['global']]+top_sim_users_ratings+top_sim_movies_ratings+[train_averages['user'][user], train_averages['movie'][movie], rating, train_mf_svd[index]])
    train_result_data = pd.DataFrame(train_result_data, columns=['user', 'movie', 'GAvg', 'sur1', 'sur2', 'sur3', 'sur4', 'sur5', 'smr1', 'smr2', 'smr3', 'smr4', 'smr5', 'UAvg', 'MAvg', 'rating', 'mf_svd'])

    user_result_data = []

    for index, row in user_data.iterrows():
        user = row['user_id']
        movie = row['movie_id']
        rating = row['rating']
        top_sim_users_ratings = top_sim_users(train_sparse_matrix, train_averages, user, movie, 5)
        top_sim_movies_ratings = top_sim_movies(train_sparse_matrix, train_averages, user, movie, 5)

        user_result_data.append([user, movie, train_averages['global']]+top_sim_users_ratings+top_sim_movies_ratings+[train_averages['user'][user], train_averages['movie'][movie], rating, user_mf_svd[index]])
    user_result_data = pd.DataFrame(user_result_data, columns=['user', 'movie', 'GAvg', 'sur1', 'sur2', 'sur3', 'sur4', 'sur5', 'smr1', 'smr2', 'smr3', 'smr4', 'smr5', 'UAvg', 'MAvg', 'rating', 'mf_svd'])

    return train_result_data, user_result_data

def get_train_averages(train_sparse_matrix):
    """
    Calculates
    1. average of rates of all movies
    2. average of rates of all the movie that user have rated
    3. average of rates of the movie

    Parameters
    train_sparse_matrix
    
    Returns
    average calculated values
    """
    train_averages = dict()
    train_global_average = train_sparse_matrix.sum()/train_sparse_matrix.count_nonzero()
    train_averages['global'] = train_global_average
    train_averages['user'] = get_average_ratings(train_sparse_matrix, of_users=True)
    train_averages['movie'] = get_average_ratings(train_sparse_matrix, of_users=False)
    return train_averages

def get_average_ratings(sparse_matrix, of_users):
    """
    Calculate the average rating in dictionary (key: user_id/movie_id, value: avg rating)

    Parameters
    sparse_matrix, of_users
    
    Returns
    average ratings
    """
    ax = 1 if of_users else 0 # 1 - User axes,0 - Movie axes
    sum_of_ratings = sparse_matrix.sum(axis=ax).A1
    is_rated = sparse_matrix!=0
    no_of_ratings = is_rated.sum(axis=ax).A1
    u,m = sparse_matrix.shape
    average_ratings = {i : sum_of_ratings[i]/no_of_ratings[i] for i in range(u if of_users else m) if no_of_ratings[i] !=0}
    return average_ratings

def top_sim_users(train_sparse_matrix, train_averages, user, movie, length):
    """
    Find similar users to length many using cosine similarity in the sparse matrix

    Parameters
    train_sparse_matrix, train_averages, user, movie, length
    
    Returns
    list of five top similar user ratings
    """
    # compute the similar Users of the "user"
    user_sim = cosine_similarity(train_sparse_matrix[user], train_sparse_matrix).ravel()
    top_sim_users = user_sim.argsort()[::-1][1:] # we are ignoring 'The User' from its similar users.
    # get the ratings of most similar users for this movie
    top_ratings = train_sparse_matrix[top_sim_users, movie].toarray().ravel()
    # we will make it's length "5" by adding movie averages to
    top_sim_users_ratings = list(top_ratings[top_ratings != 0][:length])
    top_sim_users_ratings.extend([train_averages['movie'][movie]]*(length -len(top_sim_users_ratings)))
    return top_sim_users_ratings

def top_sim_movies(train_sparse_matrix, train_averages, user, movie, length):
    """
    Find similar movies to length many using cosine similarity in the sparse matrix

    Parameters
    train_sparse_matrix, train_averages, user, movie, length
    
    Returns
    list of five top similar movie ratings
    """
    # compute the similar movies of the "movie"
    movie_sim = cosine_similarity(train_sparse_matrix[:,movie].T, train_sparse_matrix.T).ravel()
    top_sim_movies = movie_sim.argsort()[::-1][1:]
    # we are ignoring 'The User' from its similar users.
    # get the ratings of most similar movie rated by this user
    top_ratings = train_sparse_matrix[user, top_sim_movies].toarray().ravel()
    # we will make it's length "5" by adding user averages to
    top_sim_movies_ratings = list(top_ratings[top_ratings != 0][:length])
    top_sim_movies_ratings.extend([train_averages['user'][user]]*(length-len(top_sim_movies_ratings)))
    return top_sim_movies_ratings

def create_model(final_data):
    """
    Using the train data, create a regression model

    Parameters
    final_data
    
    Returns
    prediction model
    """
    # prepare train data
    x_train = final_data.drop(['user', 'movie', 'rating'], axis=1)
    y_train = final_data['rating']
    # initialize XGBoost model
    xgb_model = xgb.XGBRegressor(verbosity=0, n_jobs=13, random_state=15, n_estimators=100)
    # fit the model
    xgb_model.fit(x_train, y_train, eval_metric = 'rmse')

    return xgb_model

def predict(model, user_data):
    """
    Using the model and user data,
    it predicts the possible rating of the movie that user haven't watched yet by the user.

    Parameters
    model, user_data
    
    Returns
    prediction
    """
    input = user_data.drop(['user', 'movie', 'rating'], axis=1)
    prediction = model.predict(input)
    return prediction

def predicted_movie_ratings_to_ids(predicted_ratings, final_user_data):
    """
    Returns list of movie ids in the order of predicted rating of the user

    Parameters
    predicted_ratings, final_user_data
    
    Returns
    id of movies to be recommended
    """
    movie_dict = []
    for index, row in final_user_data.iterrows():
        id = int(row['movie'])
        movie_dict.append({"id": id, "rating": predicted_ratings[index]})

    movie_dict = sorted(movie_dict, key=lambda d: d['rating'], reverse=True)

    movie_ids = []
    for movie in movie_dict:
        movie_ids.append(movie["id"])

    return movie_ids

def fill_recommendation(collab_result):
    """
    When the result of collaborative filtering is small(less than 50), append movies of high ratings to fill up the recommendation part.

    Parameters
    collab_result
    
    Returns
    recommendation filled up to 50 movies
    """
    if len(collab_result) > 50:
        return collab_result

    high_rate_movies = list(set(cold_start()) - set(collab_result))

    for i in range(min(50-len(collab_result), len(high_rate_movies))):
        collab_result.append(high_rate_movies[i])

    return collab_result

def cold_start():
    """
    Recommendation for new users

    Parameters
    None
    
    Returns
    list of movies for the cold start(highest rating)
    """
    sql = "select id from Movies order by avg_rating DESC;"
    db = MysqlUtil()
    result = db.fetchall(sql)
    movie_ids = [movie["id"] for movie in result]
    return movie_ids

def new_user(user_id:int):
    """
    Check if user is a cold start(no reviews)

    Parameters
    user_id(int): user id
    
    Returns
    Boolean
    """
    sql = f"select count(id) as review_count from Reviews where user_id = {user_id}"
    db = MysqlUtil()
    result = db.fetchone(sql)
    review_count = result["review_count"]
    if review_count:
        return False
    return True

def data_as_dataframe():
    """
    Get training data(ratings of movies from users) in the form of data frame

    Parameters
    None
    
    Returns
    train data
    """
    try:
        mydb = connection.connect(host="localhost",\
                                  database = 'holywood',\
                                  user="root", \
                                  passwd=get_pw(),\
                                  use_pure=True)
        query = "select user_id, movie_id, rating from Reviews;"
        train_data = pd.read_sql(query, mydb)
        mydb.close() #close the connection
    except Exception as e:
        mydb.close()
        print(str(e))
    return train_data

def user_prediction_dataframe(user_id:int):
    """
    Get a data frame of movie ids such that the user haven't watched(not reviewed) and the movie has been rated at least once.

    Parameters
    user_id(int): user id
    
    Returns
    user data
    """
    try:
        mydb = connection.connect(host="localhost",\
                                  database = 'holywood',\
                                  user="root", \
                                  passwd=get_pw(),\
                                  use_pure=True)
        query = f"select m.id as movie_id from Movies m left join Reviews r on m.id = r.movie_id and r.user_id = {user_id} where r.rating is null and m.avg_rating > 0;"
        user_data = pd.read_sql(query, mydb)
        mydb.close() #close the connection
    except Exception as e:
        mydb.close()
        print(str(e))
    user_data['user_id'] = [user_id]*len(user_data)
    user_data['rating'] = [0]*len(user_data)
    return user_data