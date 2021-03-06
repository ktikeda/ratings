"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                   session)

from flask_sqlalchemy import SQLAlchemy

from model import User, Rating, Movie, connect_to_db, db

from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db

from datetime import datetime


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

    #redirect to user profile if logged in


@app.route('/users')
def user_list():
    """List of users with email addresses and ids."""

    users = User.query.all()

    return render_template('user_list.html', users=users)


@app.route('/users/<user_id>')
def user_profile(user_id):
    """Individual user profile including movies rated and scores."""

    # user = User.query.get(user_id)
    # movie_ratings = db.session.query(Movie.title, Rating.score).join(Rating).filter(Rating.user_id==user_id).order_by(Movie.title).all()

    # movies = sorted([rating.movie.title for rating in user.ratings])

    user = User.query.options(db.joinedload('ratings').joinedload('movie')).get(user_id)

    # movies = sorted([rating.movie.title, for rating in user.ratings])

    return render_template('user_profile.html', user=user)


@app.route('/movies')
def movie_list():
    """List of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template('movie_list.html', movies=movies)


@app.route('/movies/<movie_id>')
def movie_ratings(movie_id):
    """Info about movie including past ratings plus ratings form."""
    movie = Movie.query.get(movie_id)
    release_date = datetime.strftime(movie.released_at, '%B %-d, %Y')

    all_ratings = ', '.join([str(rating.score) for rating in movie.ratings])

    return render_template('movie_profile.html', movie=movie, released_at=release_date, all_ratings=all_ratings)


@app.route('/movies/<movie_id>', methods=["POST"])
def add_rating(movie_id):
    """Adds new rating to db or updates existing rating for user."""

    new_score = request.form.get("score")

    try:
        new_score = int(new_score)
    except ValueError:
        flash('This is not a valid rating.') 

    if new_score < 1 or new_score > 5:
        flash('This is not a valid rating.')

    else:
        user = session['user_id']
        rating = Rating.query.filter(Rating.movie_id == movie_id, Rating.user_id == user).first()
        # print q
        if rating: #if list is not empty
            rating.score = new_score
            db.session.commit()
            flash("Your rating has been updated")

        else:
            new_movie_rating = Rating(score=new_score, movie_id=movie_id, user_id=user)
            db.session.add(new_movie_rating)
            db.session.commit()
            flash("Your rating has been added")
            
    return redirect('/movies/' + str(movie_id))


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

    if q: #if list is not empty
        flash("The user already exists")
        return render_template('register.html')
    else: #if empty list
        new_user = User(email=user_email, password=password)
        print new_user
        db.session.add(new_user)
        db.session.commit()
        flash("Your account has been created")
        return redirect('/login')

    
@app.route('/login')
def login_form():
    """Show login form"""
    # redirect user to homepage if logged in
    if 'user_id' in session:
        return redirect('/users/')
    else:
        return render_template('login.html')


@app.route('/login', methods=["POST"])
def login_user():
    """Logs in a user if they are in the database"""

    user_email = request.form.get('email')
    password = request.form.get('pw')

    user_q = User.query.filter(User.email == user_email).all()
    print user_q

    if user_q:
        user = user_q[0]
        if user.password == password:
            flash('Logged in')
            session['user_id'] = user.user_id
            return redirect('/users/' + str(session['user_id']))
        else:
            flash('Wrong password -- try again')
            return render_template('login.html')
    else:
        flash('This user/password combination does not exist. Try again.')
        return render_template('login.html')


@app.route('/logout')
def logout_user():
    """Logs out user"""
    # session['user_id'] = None
    session.clear()
    return redirect('/')


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
