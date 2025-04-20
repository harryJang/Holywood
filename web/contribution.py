"""
This file has been written by Qihan Zhuang (z5271722)
It contains operations of contribution part
"""
from web.auth import login_required
from web.mysql_util import MysqlUtil
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

bp = Blueprint('contribution', __name__, url_prefix='/contribution')


@bp.route('/details/<int:contribution_id>', methods=('GET',))
@login_required
def details(contribution_id):
    """
    Admin/Moderator can check detail of a selected contribution 

    Parameters:
    contribution_id (int): ID of selected contribution

    Returns:
    movie : The contribution detail (Movie name, Movie poster, Movie director, Movie casts, Movie Realease Date, Movie Description)

    """
    # get the record
    db = MysqlUtil()
    sql = f"SELECT * FROM Contributions WHERE id = '{contribution_id}'"
    contribution_detail = db.fetchoneWithoutClose(sql)
    # query genres of the movie
    sql = f"SELECT G.name from Genres G JOIN Genres_of_Movies GoM on G.id = GoM.genre_id JOIN Movies M on M.id = GoM.movie_id where M.id = {contribution_detail['movie_id']}"
    genres = db.fetchall(sql)
    # process genres to list of strings(genre name)
    genre_list = [genre['name'] for genre in genres]
    # perform data masking
    desired_keys = ["name", "poster", "director", "casts", "release_date", "description"]
    movies = {key : value for key, value in contribution_detail.items() if key in desired_keys}
    # turn genre and casts to list of string
    movies['genres'] = genre_list
    movies['casts'] = movies['casts'].strip("[]").replace('"', '').split(",")
    movies['contribution_id'] = contribution_id
    return render_template("/admin/viewDetail.html", movie=movies)


@bp.route('/validate/<int:contribution_id>', methods=('GET', 'POST'))
@login_required
def validate_contribution(contribution_id):
    """
    Admin/Moderator can validate a selected contribution to update corresponding movie 

    Parameters:
    contribution_id (int): ID of selected contribution

    Returns:
    contribution : updated list of contribution detail

    """
    # query the contribution with its id
    db = MysqlUtil()
    sql = f"SELECT * FROM Contributions WHERE id = {contribution_id}"
    contribution_detail = db.fetchoneWithoutClose(sql)
    curr_user_role = g.user['role']
    curr_user_id = g.user['id']
    contributionList = None
    if curr_user_role == 'USER':
        error = "You have no permission to validate this contribution"
        flash(error)
    else:
        # set the contribution to be approved by the current moderator/admin
        sql = f"UPDATE Contributions SET approved = {curr_user_id} WHERE id = {contribution_id}"
        db.updateWithoutClose(sql)
        # update the movie after approval
        name = str(contribution_detail['name']).replace("'", "''")
        poster = str(contribution_detail['poster'])
        director = str(contribution_detail['director'])
        casts = str(contribution_detail['casts'])
        description = str(contribution_detail['description']).replace("'", "''")
        date = contribution_detail['release_date']
        sql = f"UPDATE Movies SET name = '{name}', poster = '{poster}', director = '{director}', casts = '{casts}', description =' {description}', release_date='{date}' where id = {contribution_detail['movie_id']}"
        db.updateWithoutClose(sql)
        # display the updated contribution list
        sql = f"select C.id, C.name as cname, M.name, U.username as user, U2.username as approver from Contributions C join Movies M on M.id = C.movie_id join Users U on U.id = C.user_id left join Users U2 on U2.id = C.approved where C.approved != -2"
        contributionList = db.fetchall(sql)
        for contribution in contributionList:
            if contribution['approver'] is None:
                contribution['approver'] = 'Not approved yet'
        return redirect(url_for('admin.get_contributions'))
    db.close_db()
    return render_template("admin/reviewContribution.html", contribution=contributionList)


@bp.route('/unvalidate/<int:contribution_id>', methods=('GET', 'POST'))
@login_required
def unvalidate_contribution(contribution_id):
    """
    Admin/Moderator can unvalidate a selected contribution to not review the contribution in the list

    Parameters:
    contribution_id (int): ID of selected contribution

    Returns:
    contribution : updated list of contribution detail

    """
    curr_user_role = g.user['role']
    contributionList = None
    if curr_user_role == 'USER':
        error = "You have no permission to validate this contribution"
        flash(error)
    else:
        # set the contribution to not approved by the current moderator/admin
        db = MysqlUtil()
        sql = f"UPDATE Contributions SET approved = -2 WHERE id = {contribution_id}"
        db.updateWithoutClose(sql)
        # display the updated contribution list
        sql = f"select C.id, C.name as cname, M.name, U.username as user, U2.username as approver from Contributions C join Movies M on M.id = C.movie_id join Users U on U.id = C.user_id left join Users U2 on U2.id = C.approved where C.approved != -2"
        contributionList = db.fetchall(sql)
        for contribution in contributionList:
            if contribution['approver'] is None:
                contribution['approver'] = 'Not approved yet'
        return redirect(url_for('admin.get_contributions'))
    return render_template("admin/reviewContribution.html", contribution=contributionList)


@bp.route('/update/<name>', methods=('GET', 'POST'))
@login_required
def update_movie(name):
    """
    Contributer can update movie by create a contribution
    If the contributer's role is user then the contribution will be displayed in contribution list that admin/moderator can review from.
    If the contributer's role is not user (admin/moderator) then the contribution will update movie immediately with authorization of the contributer.

    Parameters:
    contribution_id (int): ID of selected contribution

    Returns:
    contribution : updated list of contribution detail

    """
    # query one movie with its name
    db = MysqlUtil()
    sql = f"SELECT * FROM Movies WHERE name = '{name}'"
    movie_detail = db.fetchoneWithoutClose(sql)
    cur_user_id = g.user['id']
    cur_user_role = g.user['role']
    if request.method == 'POST':
        # get all the updated attributes from frontend
        updatedName = str(request.form['moviename']).replace("'", "''")
        poster = str(request.form['poster'])
        director = str(request.form['director'])
        casts = str(request.form['casts'])
        release_date = request.form['releaseDate']
        description = str(request.form['description']).replace("'", "''")
        # insert a contribution record
        sql = f"INSERT INTO Contributions (user_id, movie_id, name, poster, director, casts, description, release_date) VALUES ({cur_user_id}, {movie_detail['id']}, '{updatedName}', '{poster}', '{director}', '{casts}', '{description}', '{release_date}')"
        db.insertWithoutClose(sql)
        if cur_user_role != "USER":
            # if the current user are admin/moderators, then the contribution can be approved by themselves
            sql = f"SELECT * FROM Contributions WHERE name = '{updatedName}'"
            contribution_detail = db.fetchoneWithoutClose(sql)
            sql = f"UPDATE Contributions SET approved = {cur_user_id} WHERE id = {contribution_detail['id']}"
            db.updateWithoutClose(sql)
            # update the movie after approval
            sql = f"UPDATE Movies SET name = '{updatedName}', poster = '{poster}', director = '{director}', casts = '{casts}', description = '{description}', release_date='{release_date}' where name = '{name}'"
            db.update(sql)
            return redirect(url_for('admin.get_contributions'))
        db.close_db()
        return redirect(url_for('user.myprofile'))
    db.close_db()
    return render_template("user/userContribute.html", movie=movie_detail)

