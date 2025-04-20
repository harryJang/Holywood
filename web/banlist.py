"""
This file has been written by WenQi Zhao (z5315820)
It contains operations for balist
"""

from web.mysql_util import MysqlUtil
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, jsonify
)


def show_banlist(uid: int):
    """
    Show the banlist 

    Parameters:
    uid (int): ID of user who own this banlist

    Returns:
    List of users who are banned

    """
    # find user's banlist by uid
    db = MysqlUtil()
    sql = f"select banu.username, banu.email \
            from Users banu join BannedLists bl on banu.id = bl.Banned_user_id\
            join Users u on bl.banning_user_id = u.id \
            where u.id = {uid}"
    ban_user = db.fetchall(sql)
    # show banned users' username and email
    desired_keys = ["username", "email"]
    return [{key : value for key, value in ban_name.items() if key in desired_keys} for ban_name in ban_user]

def remove_banlist(uid: int, name: str):
    """
    Remove an user from banlist 

    Parameters:
    uid (int): ID of user who own this ban list
    name (str): be banned user name

    Returns:
    List of users who are banned

    """
    db = MysqlUtil()
    sql = f"select u.id from Users u where u.username = '{name}'"
    user_detail = db.fetchone(sql)
    buid = user_detail['id']
    # remove banned user from banlist by banned user id buid
    db = MysqlUtil()
    sql = f"delete from BannedLists where banning_user_id = {uid} and banned_user_id = {buid}"
    db.delete(sql)
    # after delete, return banlist
    db = MysqlUtil()
    sql = f"select banu.username, banu.email \
            from Users banu join BannedLists bl on banu.id = bl.Banned_user_id\
            join Users u on bl.banning_user_id = u.id \
            where u.id = {uid}"
    ban_user = db.fetchall(sql)
    desired_keys = ["username", "email"]
    return [{key : value for key, value in ban_name.items() if key in desired_keys} for ban_name in ban_user]

def insert_banlist(uid: int, bname: str):
    """
    Insert an user from banlist 

    Parameters:
    uid (int): ID of user who own this ban list
    bname (str): be banned user name

    Returns:
    List of users who are banned

    """
    # find user id who wanna ban by bname
    db = MysqlUtil()
    sql = f"select u.id from Users u where u.username = '{bname}'"
    user_detail = db.fetchone(sql)
    buid = user_detail['id']
    # user cannot ban themselves, so only if uid != buid, insert fucntion will be sucessful
    if uid != buid:
        # add banlist
        db = MysqlUtil()
        sql = f"insert into BannedLists (banning_user_id, banned_user_id) values ({uid}, {buid})"
        db.insert(sql)
        db = MysqlUtil()
        sql = f"select banu.username, banu.email \
                from Users banu join BannedLists bl on banu.id = bl.Banned_user_id\
                join Users u on bl.banning_user_id = u.id \
                where u.id = {uid}"
        ban_user = db.fetchall(sql)
        desired_keys = ["username", "email"]
        return [{key : value for key, value in ban_name.items() if key in desired_keys} for ban_name in ban_user], buid
    # if user wanna ban themselves, they will fail
    else:
        db = MysqlUtil()
        sql = f"SELECT * FROM Users WHERE username = '{bname}'"
        return db.fetchone(sql), buid