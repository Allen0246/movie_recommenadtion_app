from flask import Blueprint, request, render_template
from flask import flash, redirect, url_for, session, jsonify
from flask_login import LoginManager, login_required, current_user
from .. import log, db
from .auth import role_required, roles_required, User
from ..models.movie_genre import Movie, user_movie
from datetime import datetime
import flask_excel as excel
import random
from ..forms.ratings import DateForm

my_movies = Blueprint('my_movies', __name__)

@my_movies.route('/my_movies')
@roles_required(['admin', 'user'])  
def index():
    movies_from_db = Movie.query.join(user_movie).filter(user_movie.c.user_id == current_user.id).all()
    movies = []
    for movie in movies_from_db:
        if current_user in movie.users:
            genres = [genre.name for genre in movie.genres]
            user_movie_entry = db.session.query(user_movie).filter_by(user_id=current_user.id, movie_id=movie.id).first()
            rating = user_movie_entry.rating if user_movie_entry else None
            date = user_movie_entry.date if user_movie_entry else None
            movies.append({
                'id': movie.id,
                'title': movie.title,
                'release_date': movie.release_date,
                'genres': genres,
                'rating': rating,  
                'date': date  
            })
    return render_template('my_movies/index.html', movies=movies)

@my_movies.route('/my_movies/rewatch/<id>',  methods=['GET', 'POST'])
@roles_required(['admin', 'user'])
def rewatch(id):
    form = DateForm()
    if form.validate_on_submit():
        rating = request.form.get('rating')
        date = request.form['date']
        movie = Movie.query.filter(Movie.id == id).first()
        if not movie:
            flash('The Movie does not exist or cannot be edited.', 'info')
            return redirect(url_for('movies.index'))
        user = User.query.filter(User.id == current_user.id).first()
        if not user:
            flash('The User does not exist or cannot be edited.', 'info')
            return redirect(url_for('movies.index'))
        user_movie_entry = user_movie.select().where(user_movie.c.user_id == user.id, user_movie.c.movie_id == movie.id)
        existing_entry = db.session.execute(user_movie_entry).fetchone()
        if not existing_entry:
            flash('You have not seen this movie.', 'danger')
            return redirect(url_for('movies.index'))
        user_movie_query = user_movie.update().where(
        db.and_(user_movie.c.movie_id == id, user_movie.c.user_id == current_user.id)
        ).values(
            rating=rating,
            date=date
        )
        db.session.execute(user_movie_query)
        db.session.commit()
        log.info("[{0}] has re rate the movie: {1} and re watched in this time: {2}. ".format(current_user.username, rating, date ))
        flash('The rating and date reset on the watched movie!', 'success')
        return redirect(url_for('my_movies.index'))
    elif request.method == 'POST':
        flash('The date can not be in the future!', 'error')
    return render_template('movies/ratings.html', form=form)

@my_movies.route('/my_movies/not_seen/<id>')
@roles_required(['admin', 'user'])
def not_seen(id):
    movie = Movie.query.filter(Movie.id == id).first()
    if not movie:
        flash('The Movie does not exist or cannot be edited.', 'info')
        return redirect(url_for('my_movies.index'))

    user = User.query.filter(User.id == current_user.id).first()
    if not user:
        flash('The User does not exist or cannot be edited.', 'info')
        return redirect(url_for('my_movies.index'))
    
    if user not in movie.users:
        flash("The User haven't seen the film yet!", 'info')
        return redirect(url_for('my_movies.index'))

    movie.users.remove(user)
    db.session.commit()
    log.info("[{0}] has not seen this movie: {1}".format(current_user.username, movie.title))
    return redirect(url_for('my_movies.index'))

@my_movies.route('/my_movies/export', methods=['GET'])
@roles_required(['admin','user'])
def export():
    movies_from_db = Movie.query.all()
    movies = []
    for movie in movies_from_db:
        if current_user in movie.users:
            movies.append(movie)

    if not movies:  # Check if movies list is empty
        flash('No movies available.', 'error')
        return redirect(url_for('my_movies.index'))
    
    return excel.make_response_from_query_sets(
      movies,   
      ['title', 'overview', 'release_date', 'popularity'],  # column names
      'xlsx',              # file extension,
      sheet_name='movies',
      file_name='movies_{0}'.format(datetime.now().strftime('%Y%m%d%H%M%S')))
