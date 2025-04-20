"""
This file has been written by Qihan Zhuang (z5271722)
It contains basic operations of admin/moderators
"""
from web.auth import login_required
from web.mysql_util import MysqlUtil
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

bp = Blueprint('admin', __name__, url_prefix='/admin')


@bp.route('/flagged_reviews', methods=('GET',))
@login_required
def get_flagged_reviews():
    """
    Admin can get list of reported reviews and 
    see each review in detail (Movie name, Reported review owner, Reported review rating, Reported review comment) so that he/she can properly handle reported reviews

    Parameters:
    No Arguments

    Returns:
    reviews : list of reported review detail

    """
    # check current user's role 
    cur_user_role = g.user['role']
    flaggedReviewList = None
    error = None
    if cur_user_role != "ADMIN":
        error = "You have no permission to view the flagged review list"
    if error is not None:
        flash(error)
    else:
        db = MysqlUtil()
        sql = f"SELECT M.name, U.username, R.rating, R.comment, R.id FROM ReviewFlags RF JOIN Reviews R on R.id = RF.review_id JOIN Movies M on M.id = R.movie_id JOIN Users U on U.id = R.user_id"
        flaggedReviewList = db.fetchall(sql)
    return render_template("admin/adminFlag.html", reviews=flaggedReviewList)


@bp.route('/contributions', methods=('GET',))
@login_required
def get_contributions():
    """
    Admin/Moderators can get list of contributions and 
    see each contribution in detail (Contribution name, Movie name, Contributer Name, Approver Name).
    If a contribution has been denied by admin/moderators, then admin/moderators will not see the contribution in the list anymore

    Parameters:
    No Arguments

    Returns:
    contribution : list of contribution detail

    """
    # check current user's role 
    cur_user_role = g.user['role']
    contributionList = None
    error = None
    if cur_user_role == "USER":
        error = "You have no permission to view the flagged review list"
    if error is not None:
        flash(error)
    else:
        db = MysqlUtil()
        sql = f"select C.id, C.name as cname, M.name, U.username as user, U2.username as approver from Contributions C join Movies M on M.id = C.movie_id join Users U on U.id = C.user_id left join Users U2 on U2.id = C.approved where C.approved != -2"
        contributionList = db.fetchall(sql)
        for contribution in contributionList:
            if contribution['approver'] is None:
                contribution['approver'] = 'Not approved yet'
    return render_template("admin/reviewContribution.html", contribution=contributionList)



@bp.route('/users', methods=('GET',))
@login_required
def get_users():
    """
    Admin can grant/remove moderator role of the user and 
    see role changes in a list of user info (User ID, User name, User role)

    Parameters:
    No Arguments

    Returns:
    users : The user info list

    """
    cur_user_role = g.user['role']
    users = None
    error = None
    if cur_user_role != "ADMIN":
        error = "You have no permission to view this user list"
    if error is not None:
        flash(error)
    else:
        db = MysqlUtil()
        sql = f"SELECT * FROM Users"
        users = db.fetchall(sql)
    return render_template("admin/selectModerator.html", users=users)


@bp.route('/grant/<int:granted_user_id>', methods=('GET', 'POST'))
@login_required
def grant_moderator(granted_user_id):
    """
    Admin can grant/remove moderator role of the user and 
    see role changes in a list of user info

    Parameters:
    granted_user_id (int): The user whose role will be changed by admin

    Returns:
    users : The updated user info list

    """
    # check current user's role 
    cur_user_role = g.user['role']
    error = None
    if cur_user_role != "ADMIN":
        error = "You have no permission to grant access to other users"
    elif cur_user_role == "ADMIN" and granted_user_id == g.user['id']:
        error = "You (admin) can't grant yourself to other roles"
    # get granted user info
    db = MysqlUtil()
    sql = f"Select * from Users where id = {granted_user_id}"
    user = db.fetchoneWithoutClose(sql) 
    if error is not None:
        flash(error)
    elif user["role"] == "MODERATOR":
        # grant user role to moderator users
        sql = f"UPDATE Users SET role = 'USER' where id = {granted_user_id}"
        db.update(sql)
    else:
        # grant moderator role to normal users
        sql = f"UPDATE Users SET role = 'MODERATOR' where id = {granted_user_id}"
        db.update(sql)
    return redirect(url_for('admin.get_users'))
