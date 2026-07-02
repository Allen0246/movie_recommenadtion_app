from .. import db

movie_genre = db.Table('movie_genre',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'))
    )

user_movie = db.Table('user_movie',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
    db.Column('rating', db.Integer ),
    db.Column('date', db.String(100))
    )

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.Integer)
    title = db.Column(db.String(500))
    popularity = db.Column(db.Float)
    overview = db.Column(db.String(2500))
    release_date = db.Column(db.String(500))

    # MOVIE-GENRE MANY-MANY CONNECTION
    genres = db.relationship('Genre', secondary=movie_genre, backref='movies')

    # USER-MOVIE MANY-MANY CONNECTION
    users = db.relationship('User', secondary=user_movie, backref='movies')

    def __init__(self, api_id, title):
        self.api_id = api_id
        self.title = title
    


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.Integer)
    name = db.Column(db.String(500))

    def __init__(self, api_id, name):
        self.api_id = api_id
        self.name = name
