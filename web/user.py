from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)
from werkzeug.exceptions import abort
import json

from web.mysql_util import MysqlUtil
from web.movie import search_movie
from web.wishlist import get_wishlist, remove_from_wishlist, get_specific_wishlist
from web.banlist import show_banlist, remove_banlist, insert_banlist

bp = Blueprint('user', __name__, url_prefix='/user')

@bp.route('/wishlist', methods=(["GET"]))
def wishlist():
    movies = get_wishlist(g.user['id'])
    return render_template('user/wishlist.html', movie=movies, role=g.user['role'])

@bp.route('/wishlist/<name>', methods=(["POST", "GET"]))
def delete_wishlist(name):
    movies = remove_from_wishlist(g.user['id'], name)
    flash(f'{name} has successfully deleted!')
    return render_template('user/wishlist.html', movie=movies, role=g.user['role'])

@bp.route('/banlist', methods=(['GET', 'POST']))
def banlist():
    if request.method =="POST" :
        redirect(url_for('movie.search_movie'))
    show_ban_list = show_banlist(g.user['id'])
    return render_template("user/banlist.html", banned=show_ban_list, role=g.user['role'])

@bp.route('/banlist/del_<name>', methods=(['GET', 'POST']))
def del_banlist(name):
    show_ban_list = remove_banlist(g.user['id'], name)
    flash(f'{name} has successfully deleted!')
    return render_template("user/banlist.html", banned=show_ban_list, role=g.user['role'])

@bp.route('/<bname>/add_ban', methods=(['POST', 'GET']))
def add_banlist(bname):
    show_ban_list, buid = insert_banlist(g.user['id'], bname)
    if g.user['id'] != buid:
        return render_template("user/banlist.html", banned=show_ban_list, role=g.user['role'])
    else:
        return render_template("user/userProfile.html", user=show_ban_list, role=g.user['role'])


@bp.route('/myprofile', methods=(["GET","POST"]))
def myprofile():
    username = g.user['username']
    db = MysqlUtil()
    sql = f"SELECT * FROM Users WHERE username = '{username}'"
    user = db.fetchoneWithoutClose(sql)
    sql = f"select C.id, C.name as cname, M.name, U.username as user, U2.username as approver, C.approved from Contributions C join Movies M on M.id = C.movie_id join Users U on U.id = C.user_id left join Users U2 on U2.id = C.approved where C.user_id = {user['id']}"
    contributionList = db.fetchall(sql)
    for contribution in contributionList:
        if contribution['approver'] is None:
            if contribution['approved'] == -1:
                contribution['approver'] = 'Not approved yet'
            else: 
                contribution['approver'] = 'This contribution has been denied'
    return render_template("user/myProfile.html", user=user, role=g.user['role'], contributions=contributionList)

@bp.route('/userwishlist/<username>', methods=(["GET"]))
def userwishlist(username):
    movies = get_specific_wishlist(username)
    return render_template('user/wishlist.html', movie=movies, role=g.user['role'])