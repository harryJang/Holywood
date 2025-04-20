"""
This file contains functions to connect to SMTP server and send emails
Created by Yunseok Jang z5286005
"""

import smtplib, ssl
from web.mysql_util import MysqlUtil
from datetime import date

def send_release_email(movie_name:str, receiver_email:str, user_name:str):
    """
    sends email to the user

    Parameters
    movie_name(str): movie name
    receiver_email(str): user email
    user_name(str): user name
    
    Returns
    None
    """
    port = 465  # For SSL
    context = ssl.create_default_context() # Create a secure SSL context
    sender_email = "cp3900testing@gmail.com"
    sender_password = "vvcsjnezhhpnzxuh"
    message = f"""\
    Subject: Hi {user_name}

    Your wishlist movie '{movie_name}' has been released!"""
    with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, message)

def wishlist_notification(today=date.today()):
    """
    Send nofitication to users who have the movie released today in their wishlist

    Parameters
    today(date): date (default->date of today)
    
    Returns
    None
    """
    sql = f"select id, name from Movies where DATE(release_date) = '{today}'"
    db = MysqlUtil()
    movies = db.fetchallWithoutClose(sql)

    for movie in movies:
        mid = movie['id']
        mname = movie['name']

        sql = f"select wl.user_id from Wishlists wl where wl.movie_id = {mid}"
        users = db.fetchallWithoutClose(sql)
        
        for user in users:
            uid = user['user_id']
            sql = f"select email, username from Users where id = {uid}"
            user_info = db.fetchoneWithoutClose(sql)
            email = user_info['email']
            uname = user_info['username']
            send_release_email(mname, email, uname)
    db.close_db()