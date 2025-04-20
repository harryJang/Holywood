"""
This file has been written by Yunseok Jang z5286005.
"""

from web.mysql_util import MysqlUtil

def get_movie_sorted_by_selection(key_selected:str, db):
    """
    Map query and value of given the key_selected

    Parameters
    key_selected(str): key (could be "most recent", "highest rating", "most review" etc)
    db: database connector instance
    
    Returns
    list of top 20 movies of the given key
    """
    if key_selected == "most recent":
            sql = "select poster, name, release_date as value from Movies order by release_date DESC;"
            value = "Release Date"
    elif key_selected == "least recent":
            sql = "select poster, name, release_date as value from Movies order by release_date;"
            value = "Release Date"
    elif key_selected == "highest rating":
            sql = "select poster, name, avg_rating as value from Movies order by avg_rating DESC;"
            value = "Average Rating"
    elif key_selected == "lowest rating":
            sql = "select poster, name, avg_rating as value from Movies order by avg_rating;"
            value = "Average Rating"
    elif key_selected == "most review":
            sql = "select poster, name, count_reviews as value from Movies order by count_reviews DESC;"
            value = "Number of Reviews"
    elif key_selected == "least review":
            sql = "select poster, name, count_reviews as value from Movies order by count_reviews;"
            value = "Number of Reviews"
    return db.fetchmany(sql,20), value


def get_default_leaderboard(db):
    """
    Get default leaderboard which is ordered by release date

    Parameters
    db: database connector instance
    
    Returns
    list of movies(poster and name), value(used to order) and key(criteria to order)
    """
    sql = "select poster, name, release_date as value from Movies order by release_date DESC;"
    movies = db.fetchmany(sql, 20)
    value = "Release Date"
    key = "Most Recent"
    return movies, value, key