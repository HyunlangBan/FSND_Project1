from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        
    
    def __repr__(self):
        return f'<Venue {self.start_time}>'

    

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    address = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), nullable = False)
    genres = db.Column(db.ARRAY(db.String), nullable = False)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String())
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    upcoming_shows_count = db.Column(db.Integer, default = 0)
    past_shows_count = db.Column(db.Integer, default = 0)
    shows_ven = db.relationship('Show', backref='venue')


    # TODO: implement any missing fields, as a database migration using Flask-Migrate


    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<Venue {self.id} {self.name}>'


class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable = False)
    city = db.Column(db.String(120), nullable = False)
    state = db.Column(db.String(120), nullable = False)
    phone = db.Column(db.String(120), nullable = False)
    genres = db.Column(db.ARRAY(db.String), nullable = False)
    image_link = db.Column(db.String(500))
    website = db.Column(db.String())
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(200))
    upcoming_shows_count = db.Column(db.Integer, default = 0)
    past_shows_count = db.Column(db.Integer, default = 0)
    facebook_link = db.Column(db.String())
    shows_art = db.relationship('Show', backref='artist')


    def insert(self):
        db.session.add(self)
        db.session.commit()
    
    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __repr__(self):
        return f'<Aritst {self.id} {self.name}>'


    # TODO: implement any missing fields, as a database migration using Flask-Migrate
# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.