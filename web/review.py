"""
This file has been written by Qihan Zhuang (z5271722)
It contains operations for review and rating
"""

from web.auth import login_required
from web.mysql_util import MysqlUtil
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

bp = Blueprint('review', __name__, url_prefix='/review')

@bp.route('/<name>/add_review', methods=('GET','POST'))
@login_required
def add_review(name):
    """
    All system users can add review to a selected movie

    Parameters:
    name (string): name of selected movie

    Returns:
    movie : movie detail with updated review list

    """
    # query movie with its name
    db = MysqlUtil()
    sql = f"SELECT id, name, poster FROM Movies WHERE name = '{name}'"
    movie_detail = db.fetchoneWithoutClose(sql)
    if request.method == 'POST':
        rating = int(request.form['rate'])
        comment = str(request.form['review']).replace("'", "''")
        # add review
        user_id = g.user['id']
        movie_id = movie_detail['id']
        sql = f"INSERT INTO Reviews (user_id, movie_id, rating, comment) VALUES ({user_id}, {movie_id}, {rating}, '{comment}')"
        db.insertWithoutClose(sql)
        # get the average rating of the movie
        sql = f"SELECT avg(rating) FROM Reviews GROUP BY movie_id HAVING movie_id = {movie_id}"
        avg_rating = db.fetchoneWithoutClose(sql)['avg(rating)']
        # update review rating/counts of the movie
        sql = f"UPDATE Movies SET avg_rating = {avg_rating}, count_reviews = count_reviews + 1 WHERE id = {movie_id}"
        db.update(sql)
        return redirect(url_for('movie.details', name=name))
    db.close_db()
    return render_template("user/review.html", movie=movie_detail)


@bp.route('/<name>/del_review/<int:review_id>', methods=('POST', 'GET'))
@login_required
def del_review(name, review_id):
    """
    All system users can delete their own selected review of selected movie.
    Admin can remove any selected reviews

    Parameters:
    name (string): name of selected movie
    review_id (int): ID of selected review

    Returns:
    movie : movie detail with updated review list

    """
    error = None
    # query movie with its name
    db = MysqlUtil()
    sql = f"SELECT id, name, poster FROM Movies WHERE name = '{name}'"
    movie_detail = db.fetchoneWithoutClose(sql)
    movie_id = movie_detail['id']
    # check current user's authority
    cur_user_role = g.user['role']
    cur_user_id = g.user['id']
    sql = f"SELECT user_id, flagged FROM Reviews WHERE id = {review_id}"
    review = db.fetchoneWithoutClose(sql)
    flagged = int(review['flagged'])
    review_user_id = review['user_id']
    if (int(review_user_id) != cur_user_id) and (cur_user_role != "ADMIN"):
        error = "You have no permission to delete this review"
    if error is not None:
        flash(error)
    else:
        if flagged == 1:
            sql = f"DELETE FROM ReviewFlags WHERE review_id = {review_id}"
            db.deleteWithoutClose(sql)
        # delete the review according to the review id
        sql = f"DELETE FROM Reviews WHERE id = {review_id}"
        db.deleteWithoutClose(sql)
        # check if the review is the last one
        sql = f"SELECT count(*) FROM Reviews WHERE movie_id = {movie_id}"
        counter = db.fetchoneWithoutClose(sql)['count(*)']
        avg_rating = None
        if counter == 0 :
            avg_rating = 0
        else :
            # get the average rating of the movie
            sql = f"SELECT avg(rating) FROM Reviews GROUP BY movie_id HAVING movie_id = {movie_id}"
            avg_rating = db.fetchoneWithoutClose(sql)['avg(rating)']
        # update review rating/counts of the movie
        sql = f"UPDATE Movies SET avg_rating = {avg_rating}, count_reviews = count_reviews - 1 WHERE id = {movie_id}"
        db.updateWithoutClose(sql)
    db.close_db()
    return redirect(url_for('movie.details', name=name))


@bp.route('/<name>/edit_review/<int:review_id>', methods=('GET', 'POST'))
@login_required
def edit_review(name, review_id):
    """
    All system users can edit their own selected review of selected movie and cannot edit other users' reviews

    Parameters:
    name (string): name of selected movie
    review_id (int): ID of selected review

    Returns:
    movie : movie detail with updated review list

    """
    # query movie with its name
    db = MysqlUtil()
    sql = f"SELECT M.id, M.name, M.poster, R.rating, R.comment FROM Movies M JOIN Reviews R on M.id = R.movie_id WHERE M.name = '{name}' and R.id = {review_id}"
    movie_detail = db.fetchoneWithoutClose(sql)
    # print(movie_detail)
    cur_user_id = g.user['id']
    error = None
    # check if it's the right user
    sql = f"SELECT user_id FROM Reviews WHERE id = {review_id}"
    review_user_id = db.fetchoneWithoutClose(sql)['user_id'] 
    if int(review_user_id) != cur_user_id:
        error = "You have no permission to edit this review"
    if error is not None:
        flash(error)
        db.close_db()
        return redirect(url_for('movie.details', name=name))
    if request.method == 'POST':
        rating = int(request.form['rate'])
        comment = str(request.form['review']).replace("'", "''")
        # edit review
        movie_id = movie_detail['id']
        sql = f"UPDATE Reviews SET rating = {rating}, comment = '{comment}' WHERE id = {review_id}"
        db.updateWithoutClose(sql)
        # get the average rating of the movie
        sql = f"SELECT avg(rating) FROM Reviews GROUP BY movie_id HAVING movie_id = {movie_id}"
        avg_rating = db.fetchoneWithoutClose(sql)['avg(rating)']
        # update review rating of the movie
        db = MysqlUtil()
        sql = f"UPDATE Movies SET avg_rating = {avg_rating} WHERE id = {movie_id}"
        db.update(sql)
        return redirect(url_for('movie.details', name=name))
    db.close_db()
    return render_template("user/editReview.html", movie=movie_detail)


@bp.route('/<name>/flag_review/<int:review_id>', methods=('POST', 'GET'))
@login_required
def flag_review(name, review_id):
    """
    Admin/Moderator can flag a selected review of selected movie so that admin can see list of reported reviews later to handle them.

    Parameters:
    name (string): name of selected movie
    review_id (int): ID of selected review

    Returns:
    movie : movie detail with updated review list

    """
    # check user's authority
    cur_user_role = g.user['role']
    error = None
    if cur_user_role == "USER":
        error = "You have no permission to flag reviews"
    if error is not None:
        flash(error)
    else:
        # report review and insert a record to ReviewFlags
        cur_user_id = g.user['id']
        db = MysqlUtil()
        sql = f"INSERT INTO ReviewFlags (moderator_id, review_id) VALUES ({cur_user_id}, {review_id})"
        db.insertWithoutClose(sql)
        sql = f"UPDATE Reviews SET flagged = 1 WHERE id = {review_id}"
        db.update(sql)
    return redirect(url_for('movie.details', name=name))


@bp.route('/<name>/unflag_review/<int:review_id>', methods=('POST', 'GET'))
@login_required
def unflag_review(name, review_id):
    """
    Admin/Moderator can flag a selected review of selected movie

    Parameters:
    name (string): name of selected movie
    review_id (int): ID of selected review

    Returns:
    movie : movie detail with updated review list

    """
    # check user's authority
    cur_user_role = g.user['role']
    error = None
    if cur_user_role == "USER":
        error = "You have no permission to unflag reviews"
    if error is not None:
        flash(error)
    else:
        # unreport review and delete a record to ReviewFlags
        cur_user_id = g.user['id']
        db = MysqlUtil()
        sql = f"DELETE FROM ReviewFlags WHERE moderator_id = {cur_user_id} and review_id = {review_id}"
        db.deleteWithoutClose(sql)
        sql = f"UPDATE Reviews SET flagged = 0 WHERE id = {review_id}"
        db.update(sql)
    return redirect(url_for('movie.details', name=name))