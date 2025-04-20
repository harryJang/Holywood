from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
import json
import string

from web.auth import login_required
from web.mysql_util import MysqlUtil
from web.search import search
from web.wishlist import insert_wishlist
from web.sorting import get_movie_sorted_by_selection, get_default_leaderboard
from web.movie_recommendation import recommendation_for_home_page, recommendation_for_detail_page
from web.theater import search_theater

bp = Blueprint('movie', __name__, url_prefix='/movie')

@bp.route('/search', methods=(['POST',])) # POST, GET, DELETE, PUT
@login_required
def search_movie():
    """
    Search movie in the database

    Returns:
    render the search page with the results after the search function is executed
    """
    key_selected = request.form["key"]
    value = request.form["value"]
    results = search(json.dumps({key_selected: value}))
    if results is None:
        flash('There is no movie matching with the '+str(key_selected))
    return render_template('movie/search.html', movies=results, role=g.user['role'])

@bp.route('/', methods=(('GET',)))
@login_required
def index():
    """
    The default page after login

    Returns
    Render the home page
    """
    # query 20 movies
    db = MysqlUtil()
    sql = "select * from Movies order by release_date DESC;"
    movies_detail = db.fetchmanyWithoutClose(sql,20)
    # perform data masking
    desired_keys = ["name", "poster", "release_date"]
    movies = [{key : value for key, value in movie.items() if key in desired_keys} for movie in movies_detail]

    recommendation = recommendation_for_home_page(db, g.user['id'])
    return render_template("movie/home.html", movies=movies, role=g.user['role'], recommendation=recommendation)


@bp.route('/details/<name>', methods=('GET', 'POST'))
@login_required
def details(name):
    """
    To shows all the element of the movie from our database

    Params:
    name - name of the movie

    Returns:
    render the detail page
    """
    uid = g.user['id']
    # query one movie with its name
    db = MysqlUtil()
    sql = f"SELECT * FROM Movies WHERE name = '{name}'"
    movie_detail = db.fetchoneWithoutClose(sql)
    # get movie id to process reviews and genres
    movie_id = movie_detail['id']
    # query reviews of the movie
    sql = f"SELECT R.id, username, rating, comment, flagged FROM Reviews R JOIN Movies M on M.id = R.movie_id JOIN Users U on U.id = R.user_id where M.id = {movie_id} and R.user_id not in (select b.banned_user_id from BannedLists b where b.banning_user_id = {uid})"
    reviews = db.fetchallWithoutClose(sql)
    # query genres of the movie
    sql = f"SELECT G.name, G.id from Genres G JOIN Genres_of_Movies GoM on G.id = GoM.genre_id JOIN Movies M on M.id = GoM.movie_id where M.id = {movie_id}"
    genres = db.fetchallWithoutClose(sql)
    # process genres to list of strings(genre name)
    genre_list = [genre['name'] for genre in genres]
    # perform data masking
    desired_keys = ["name", "poster", "director", "casts", "release_date", "description", "avg_rating", "count_reviews"]
    movies = {key : value for key, value in movie_detail.items() if key in desired_keys}
    # turn genre and casts to list of string
    movies['genres'] = genre_list
    movies['casts'] = movies['casts'].strip("[]").replace('"', '').split(",")
    movies['reviews'] = reviews

    recommendation = recommendation_for_detail_page(db, genres, movie_detail)
    
    if request.method == "POST":
        value = request.form["value"]
    else:
        value = "Sydney, Australia"
        
    showtimes= search_theater(name,value)
    return render_template("movie/detail.html", movie=movies, recommendation=recommendation, showtimes=showtimes)

@bp.route('/details/<name>/add_wishlist', methods=(['POST', 'GET']))
def add_wishlist(name):
    '''
    Add the current movie to the wishlish

    Params:
    name- name of the movie

    Returns:
    Direct to the wishlist page
    '''
    insert_wishlist(g.user['id'], name)
    return redirect(url_for('user.wishlist', name=name, role=g.user['role']))

@bp.route('/sorting', methods=('POST','GET'))
def sorting():
    '''
    User can choose the sorting element and return results accordingly
    Default sort by Most Recent

    Returns:
    The top 20 sorted results.
    '''
    db = MysqlUtil()
    if request.method == "POST":
        key_selected = request.form["sort-select"] # either most recent, highest rating and most review
        movies, value = get_movie_sorted_by_selection(key_selected, db)
        key=string.capwords(key_selected)
        return render_template("movie/sorting.html", movies=movies, value=value, key=key, role=g.user['role'])
    
    movies, value, key = get_default_leaderboard(db)
    return render_template("movie/sorting.html", movies=movies, value=value, key=key,  role=g.user['role'])

@bp.route('/user/<username>', methods=('GET',))
def user(username):
    '''
    If the other user was selected, will be direct to the user's profile

    Params:
    username - the selected username

    Returns:
    the user's profile
    '''
    db = MysqlUtil()
    sql = f"SELECT * FROM Users WHERE username = '{username}'"
    user = db.fetchoneWithoutClose(sql)
    if username == g.user['username']:
        return render_template("user/myProfile.html", user=user, role=g.user['role'])

    sql = f"select m.name, m.poster, m.release_date \
            from Movies m join WishLists wl on m.id = wl.movie_id\
            join Users u on wl.user_id = u.id \
            where u.id = {user['id']};"
    movies_all = db.fetchall(sql)
    desired_keys = ["name", "poster", "release_date"]
    movies = [{key : value for key, value in movie.items() if key in desired_keys} for movie in movies_all]
    return render_template("user/userProfile.html", user=user, movies=movies, role=g.user['role'])

@bp.route('/search/<key>/<value>', methods=('GET', "POST"))
def tag_search(key,value):
    '''
    If the tag was selected it will return a search result of the
    selected tag

    Params:
    key - the type of search for example genre or keywords
    value - the value to be searched

    Returns:
    the search results
    '''
    value = str(value).strip()
    results = search(json.dumps({key: value}))
    if results is None:
        flash('There is no movie matching with the '+str(key))
    return render_template('movie/search.html', movies=results, role=g.user['role'])

@bp.route('/movieAll', methods=(['GET', 'POST']))
@login_required
def getAllMovies():
    '''
    return every movie to the movielist
    '''
    db = MysqlUtil()
    sql = "select * from Movies;"
    movies = db.fetchall(sql)
    return render_template("admin/movieList.html", movies=movies, role=g.user['role'])