from flask import Flask, render_template, session, flash, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, current_user, logout_user, login_user
from datetime import timedelta
from werkzeug.security import generate_password_hash
import flask_excel as excel


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('project.config.default')

db = SQLAlchemy(app)
excel.init_excel(app)
    
#LOGGING
from .extensions.logging import create_log_file
# CREATE SYSTEM LOG
log = create_log_file('MOVIE_RECOMMENDATION_LOG')
log.info('Start...')

#LOGINMANAGER
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'To use the site please log in!'
login_manager.refresh_view = 'auth.login'
login_manager.needs_refresh_message = 'Log in again!'

# Connecting to THE MOVIE DB API
log.info('Connecting to THE MOVIE DB API...')
from .extensions.REST_THEMOVIEDB import RESTTheMovieDB
def connect_to_TMDB():
    try:
        the_movie_db_api = RESTTheMovieDB(hostname=app.config['THEMOVIEDB_HOSTNAME'],
                        api_key=app.config['THEMOVIEDB_TOKEN'],
                        logger=log)
        log.info('Connecting to THE MOVIE DB API was OK.')
        return the_movie_db_api
    except Exception as e:
        log.info('Connecting to THE MOVIE DB API failed.: {}'.format(e))
        return False
the_movie_db_api = connect_to_TMDB()

# MODELS
from .models.auth import User, Role, RoleAssignment
from .models.movie_genre import Movie, Genre

# CREATE TABLES
db.create_all()
db.session.commit()

# VIEWS
from .views.auth import auth
from .views.logs import log_files
from .views.movie_recomendation import recommendation
from .views.movies import movies
from .views.my_movies import my_movies
from .views.user import user

# BLUEPRINTS
app.register_blueprint(auth)
app.register_blueprint(log_files)
app.register_blueprint(recommendation)
app.register_blueprint(movies)
app.register_blueprint(my_movies)
app.register_blueprint(user)

# Roles
for role in app.config['DEFAULT_ROLES']:
    if not Role.query.filter_by(name=role).first():
        log.info('Create {0} role.'.format(role))
        Role.create(role)

# ADMIN FELHASZNÁLÓ LÉTREHOZÁSA
admin_user= User.query.filter_by(username=app.config['DEFAULT_ADMIN_USERNAME']).first()
if not admin_user:
    admin_user = User(app.config['DEFAULT_ADMIN_USERNAME'])
    admin_user.set_password(app.config['DEFAULT_ADMIN_PASSWORD'])
    db.session.add(admin_user)
    db.session.commit()
    log.info('Create {0} user.'.format(app.config['DEFAULT_ADMIN_USERNAME']))

if not admin_user.has_role(app.config['DEFAULT_ADMIN_ROLE']):
    RoleAssignment.create(app.config['DEFAULT_ADMIN_ROLE'], admin_user.get_id())

# USER FELHASZNÁLÓ LÉTREHOZÁSA
default_user= User.query.filter_by(username=app.config['DEFAULT_USER_USERNAME']).first()
if not default_user:
    default_user = User(app.config['DEFAULT_USER_USERNAME'])
    default_user.set_password(app.config['DEFAULT_USER_PASSWORD'])
    db.session.add(default_user)
    db.session.commit()
    default_user.set_role(app.config['DEFAULT_USER_ROLE'])
    log.info('Create {0} user.'.format(app.config['DEFAULT_USER_USERNAME']))

# UPLOAD DATABASE (GENRE)
responses = the_movie_db_api.get_genres_for_movie()
for response in responses:
    if 'genres' in response.json():
        for genre_from_api in response.json().get('genres', list()):
            genre_in_db = Genre.query.filter(Genre.api_id == genre_from_api.get('id')).first()
            if not genre_in_db:
                genre = Genre(genre_from_api.get('id'), genre_from_api.get('name'))
                db.session.add(genre)
                db.session.commit()

# UPLOAD DATABASE (MOVIES)
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# LOG OUT AFTER 1 HOUR
@app.before_request
def make_session_permanent():
    session.permanent = True
    app.permanent_session_lifetime = timedelta(hours=1)

# INDEX ROUTE
@app.route('/')
def index():
    if current_user.is_authenticated:
        flash('You are already logged in.', 'info')
        return redirect(url_for('home'))
    return render_template('index.html')

# HOME ROUTE
@app.route('/home')
@login_required
def home():
    return render_template('home.html')

# Error route
@app.route('/error')
def error():
    error = {'code': '000', 'title': 'Unknown error',
             'message': 'Something went wrong...'}
    return render_template('error.html', error=error)

# 404 route
@app.errorhandler(404)
def page_not_found(e):
    error = {'code': 404, 'title': 'Az oldal nem található...',
             'message': 'A keresett oldal nem létezik.'}
    return render_template('error.html', error=error)

# GENERAL ERROR HANDLER
@app.errorhandler(Exception)
def handle_exception(e):
    log.error(e)
    error = {'code': '000', 'title': 'Unknown error',
             'message': 'Something went wrong...'}
    return render_template('error.html', error=error)
                
# @app.context_processor
# def utility_processor():
#     def active_menu(endpoint):
#         if request.endpoint:
#             if request.endpoint.split('.')[0] == endpoint:
#                 return True
#         return False
#     def version():
#         return '{0}'.format(app.config['VERSION'])

#     return dict(active_menu=active_menu, version=version)



