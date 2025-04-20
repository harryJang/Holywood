import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from web.mysql_util import MysqlUtil


bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/')
def loginView():
    """
    Defult login page 

    Parameters:
    None

    Returns:
    Login page

    """
    return render_template('auth/signin.html')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    """
    Register page 

    Parameters:
    None

    Returns:
    Back to login page

    """
    error = None
    if request.method == 'POST':
        # receive username and password by request
        username = request.form['username']
        password = request.form['password']
        confirmpassword = request.form['confirmpassword']
        email = request.form['email']
        # determine whether the user input information meets the standards
        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif len(password) < 6:
            error = 'Password cannot be less than 6 character!'
        elif not email:
            error = 'Email is required'
        # add password double check function
        elif password != confirmpassword:
            error = 'Two entered passwords do not match'
        db = MysqlUtil()
        # add duplicate name check function
        sql = f'select * from Users where username=%s'
        cur = db.cursor
        cur.execute(sql, (username, ))
        result = cur.fetchone()
        if result != None:
            error = 'Username already exists, please use another name.'
        # if no error, insert user info into database
        if error is None:
            sql_sum = f'select count(*) from Users'
            cur.execute(sql_sum, )
            user_capacity = int(cur.fetchone()[0])
            if user_capacity == 0:
                sql = f"INSERT INTO Users (username, password, email, role) VALUES ('{username}', '{generate_password_hash(password)}', '{email}','ADMIN')"
            else:
                sql = f"INSERT INTO Users (username, password, email, role) VALUES ('{username}', '{generate_password_hash(password)}', '{email}','USER')"
            db.insert(sql)

            return redirect(url_for("auth.login"))

    return render_template('auth/signup.html', error=error)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = MysqlUtil()
        sql = f"SELECT * FROM Users WHERE username = '{username}'"
        user = db.fetchone(sql)

    return render_template('auth/signin.html', error=error)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        db = MysqlUtil()
        sql = f"SELECT * FROM Users WHERE id = {user_id}"
        g.user = db.fetchone(sql)


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view