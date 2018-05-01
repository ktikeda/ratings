"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from flask_sqlalchemy import SQLAlchemy

from model import User, Rating, Movie, connect_to_db, db

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined

# DB_URI = "postgresql:///ratings"

# db = SQLAlchemy()


@app.route('/')
def index():
    """Homepage."""
    return render_template('homepage.html')


@app.route('/users')
def user_list():
    """List of users with email addresses and ids."""

    users = User.query.all()

    return render_template('user_list.html', users=users)


@app.route('/register')
def register_user_form():
    """Shows a registration form."""
    return render_template('register.html')


@app.route('/register', methods=["POST"])
def register_user():
    """Checks if email is in db and adds if not"""

    user_email = request.form.get('email')
    password = request.form.get('pw')

    q = User.query.filter(User.email == user_email).all()

    if q:
        print "The user already exists"
    else:
        new_user = User(email=user_email, password=password)
        print new_user
        db.session.add(new_user)
        db.session.commit()

    return render_template('register.html')


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    # make sure templates, etc. are not cached in debug mode
    app.jinja_env.auto_reload = app.debug

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(port=5000, host='0.0.0.0')
