"""
This file has been written by Yunseok Jang z5286005.
"""

from web.mysql_util import MysqlUtil

def insert_wishlist(uid:int, mname:str):
    """
    Add movie to the wishlist

    Parameters
    uid(int): user id
    mname(str): movie name
    
    Returns
    None
    """
    db = MysqlUtil()
    sql = f"select m.id from Movies m where m.name = '{mname}';"
    mid = db.fetchoneWithoutClose(sql)
    sql = f"insert into WishLists (user_id, movie_id) values ({uid}, {mid['id']});"
    db.insert(sql)

def get_wishlist(uid:int):
    """
    Fetch wishlist of the user

    Parameters
    uid(int): user id
    
    Returns
    list of Name, Poster and release_date of all the movies in the user's wishlist
    """
    db = MysqlUtil()
    sql = f"select m.name, m.poster, m.release_date \
            from Movies m join WishLists wl on m.id = wl.movie_id\
            join users u on wl.user_id = u.id \
            where u.id = {uid};"
    movies_all = db.fetchall(sql)
    desired_keys = ["name", "poster", "release_date"]
    return [{key : value for key, value in movie.items() if key in desired_keys} for movie in movies_all]

def remove_from_wishlist(uid:int, mname:str):
    """
    Remove the movie from wishlist

    Parameters
    uid(int): user id
    mname(str): movie name
    
    Returns
    list of Name, Poster and release_date of all the movies in the user's wishlist after removing given movie
    """
    db = MysqlUtil()
    sql = f"delete wl\
            from Movies m join WishLists wl on m.id = wl.movie_id\
            join users u on wl.user_id = u.id \
            where u.id = {uid} and m.name='{mname}';"
    db.deleteWithoutClose(sql)
    sql = f"select m.name, m.poster \
            from Movies m join WishLists wl on m.id = wl.movie_id\
            join users u on wl.user_id = u.id \
            where u.id = {uid};"
    movies_all = db.fetchall(sql)
    desired_keys = ["name", "poster"]
    return [{key : value for key, value in movie.items() if key in desired_keys} for movie in movies_all]

def get_specific_wishlist(uname:str):
    """
    Fetch wishlist of the user with name

    Parameters
    uname(str): user name
    
    Returns
    list of Name, Poster and release_date of all the movies in the user's wishlist
    """
    db = MysqlUtil()
    sql = f"SELECT * FROM Users WHERE username = '{uname}'"
    user = db.fetchoneWithoutClose(sql)
    return get_wishlist(user['id'])
