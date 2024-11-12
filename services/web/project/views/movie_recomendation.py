from flask import Blueprint, request, render_template
from flask import flash, redirect, url_for, session, jsonify
from flask_login import LoginManager, login_required, current_user
from .. import log, db
from .auth import role_required, roles_required, User
from ..models.movie_genre import Movie, Genre
from datetime import datetime
import flask_excel as excel
import random

recommendation = Blueprint('recommendation', __name__)

@recommendation.route('/recommendation' , methods=['GET', 'POST'])
@roles_required(['admin', 'user'])
def index():
    genres = Genre.query.all()
    return render_template('movie_recommendation/index.html', genres=genres)


@recommendation.route('/recommendationresult', methods=['GET', 'POST'])
@roles_required(['admin', 'user'])
def recommendationresult():
    genre_select = request.form.get('genre_select')
    genre_search =(str(genre_select))
    log.info("[{0}] has sent a movie recommendation for {1} genre".format(current_user.username, genre_search))
    movies_from_db = Movie.query.all()
    movies = []
    for movie in movies_from_db:
        if current_user not in movie.users:
            for genre in movie.genres:
                if genre.name==genre_search:
                    movies.append(movie)
    movie = random.choice(movies)
    if not movie:
        pass
    return render_template('movie_recommendation/movieresult.html', movie=movie)
     
