from flask import Blueprint, request, render_template
from flask import flash, redirect, url_for, session, jsonify
from flask_login import LoginManager, login_required, current_user
from .. import log, db, the_movie_db_api
from .auth import role_required, roles_required, User
from ..models.movie_genre import Genre,Movie, user_movie
from datetime import datetime
import flask_excel as excel
from ..forms.ratings import DateForm

movies = Blueprint('movies', __name__)

@movies.route('/movies')
@roles_required(['admin', 'user'])
def index():
    movies = Movie.query.all()
    return render_template('movies/index.html', movies=movies)

@movies.route('/movies/saw/<id>', methods=['GET', 'POST'])
@roles_required(['admin', 'user'])
def saw(id):    
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
        if existing_entry:
            flash('You have already watched this movie.', 'info')
            return redirect(url_for('movies.index'))
        else:
            user_movie_entry = user_movie.insert().values(user_id=user.id, movie_id=movie.id, rating=rating, date=date)
            db.session.execute(user_movie_entry)
            db.session.commit()
            log.info("[{0}] has rate the movie: {1} and watched in this time: {2}. ".format(current_user.username, rating, date ))
            flash('The rating and date set on the watched movie!', 'success')
            return redirect(url_for('movies.index'))
    elif request.method == 'POST':
        flash('The date can not be in the future!', 'danger')
    return render_template('movies/ratings.html', form=form)

@movies.route('/movies/rewatch/<id>',  methods=['GET', 'POST'])
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
            flash('You have not seen this movie.', 'error')
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
        return redirect(url_for('movies.index'))
    elif request.method == 'POST':
        flash('The date can not be in the future!', 'danger')
    return render_template('movies/ratings.html', form=form)

@movies.route('/movies/not_seen/<id>')
@roles_required(['admin', 'user'])
def not_seen(id):
    movie = Movie.query.filter(Movie.id == id).first()
    if not movie:
        flash('The Movie does not exist or cannot be edited.', 'info')
        return redirect(url_for('movies.index'))

    user = User.query.filter(User.id == current_user.id).first()
    if not user:
        flash('The User does not exist or cannot be edited.', 'info')
        return redirect(url_for('movies.index'))
    
    if user not in movie.users:
        flash("The User haven't seen the film yet!", 'info')
        return redirect(url_for('movies.index'))

    movie.users.remove(user)
    db.session.commit()
    log.info("[{0}] has not seen this movie: {1}".format(current_user.username, movie.title))
    return redirect(url_for('movies.index')) 

@movies.route('/movies/export', methods=['GET'])
@roles_required(['admin','user'])
def export():
    movies = Movie.query.all()
    return excel.make_response_from_query_sets(
      movies,   # query sets
      ['title', 'overview', 'release_date', 'popularity'],  # column names
      'xlsx',              # file extension,
      sheet_name='movies',
      file_name='movies_{0}'.format(datetime.now().strftime('%Y%m%d%H%M%S')))

@movies.route('/movies/update', methods=['GET'])
@roles_required(['admin','user'])
def update():
    responses = the_movie_db_api.get_movies()
    for response in responses:
        if 'results' in response.json():
            for movie_from_api in response.json().get('results', list()):
                movie_in_db = Movie.query.filter(Movie.api_id == movie_from_api.get('id')).first()
                if not movie_in_db:
                    movie = Movie(movie_from_api.get('id'), movie_from_api.get('title'))
                    movie.overview = movie_from_api.get('overview')
                    movie.popularity = movie_from_api.get('popularity')
                    movie.release_date = movie_from_api.get('release_date')
                    # MOVIE_GENRE CONNECTION
                    for genre in movie_from_api.get('genre_ids', list()):
                        genre_in_db =  Genre.query.filter(Genre.api_id == genre).first()
                        if genre_in_db:
                            movie.genres.append(genre_in_db)
                    db.session.add(movie)
                    db.session.commit()
    log.info("[{0}] updated the database.".format(current_user.username))
    return redirect(url_for('movies.index'))

