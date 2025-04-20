import os, sys

from flask import Flask, redirect, url_for
from web.wishlist_email import wishlist_notification
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

def close_running_threads(scheduler):
    scheduler.shutdown()

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    app.secret_key = 'fdnjkfegthkgnrfejfgh'

    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    from . import auth
    app.register_blueprint(auth.bp)

    from . import movie
    app.register_blueprint(movie.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    from . import user
    app.register_blueprint(user.bp)

    from . import contribution
    app.register_blueprint(contribution.bp)

    from . import review
    app.register_blueprint(review.bp)


    # set schedule for sending wishlist notification every 24 hours.
    scheduler = BackgroundScheduler()
    scheduler.add_job(wishlist_notification, 'interval', hours=24)
    scheduler.start()

    atexit.register(close_running_threads, scheduler)

    return app