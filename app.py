#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask,abort, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from sqlalchemy import exc
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from models import db, Show, Venue, Artist
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models. --> models.py
#----------------------------------------------------------------------------#

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  # return babel.dates.format_datetime(date, format)
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  shows = Show.query.all()
  venue = Venue.query.all()
  
  for show in shows:
        show.artist.past_shows_count = 0
        show.artist.upcoming_shows_count =0
        show.venue.past_shows_count=0
        show.venue.upcoming_shows_count=0

        show.venue.update()
        show.artist.update()

  for show in shows:
        date_time_str = show.start_time
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

        if date_time_obj < datetime.now():
              show.artist.past_shows_count += 1      
              show.venue.past_shows_count +=1    
        else:
              show.venue.upcoming_shows_count += 1
              show.artist.upcoming_shows_count += 1

        show.venue.update()
        show.artist.update()

  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------
def boolean_check(result):
  if result == 'y':
        return True
  else:
        return False
      
@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  venues = Venue.query.all()
  cities = db.session.query(Venue.city, Venue.state).distinct(Venue.city)
  areas = []
  for city in cities:
      venue_list = []
      for venue in venues:
        if venue.city == city.city:
          venue = {
            "id": venue.id,
            "name": venue.name,
            "num_upcoming_shows": venue.upcoming_shows_count
            }
          venue_list.append(venue)
        else:
          pass
      area = {
        "city": city.city,
        "state": city.state,
        "venues": venue_list
      }
      areas.append(area)
                  
                      
  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = request.form.get('search_term', '')
  results = Venue.query.order_by(Venue.id).filter(Venue.name.ilike('%{}%'.format(search_term))).all()            
  response = []
  for result in results:
    data = {
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": result.upcoming_shows_count,
      }
    response.append(data)

  return render_template('pages/search_venues.html', results=response, search_term=search_term, count = len(results))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  venue = Venue.query.filter(Venue.id == venue_id).one_or_none()

  #past_shows, upcoming_shows
  shows = Show.query.filter(Show.venue_id==venue_id).all()
  past_shows =[]
  upcoming_shows=[]

  for show in shows:
        date_time_str = show.start_time
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

        if date_time_obj < datetime.now():
              past_show = {"artist_image_link": show.artist.image_link,
              "artist_id": show.artist.id,
              "artist_name":show.artist.name,
              "start_time": show.start_time}

              past_shows.append(past_show)                
        else:
              upcoming_show = {"artist_image_link": show.artist.image_link,
              "artist_id": show.artist.id,
              "artist_name":show.artist.name,
              "start_time": show.start_time}
              
              upcoming_shows.append(upcoming_show)


  return render_template('pages/show_venue.html', venue=venue,
  upcoming_shows=upcoming_shows, past_shows=past_shows)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm(request.form)

  if form.validate():
    try:
        venue = Venue()

        venue.name = request.form.get('name')
        venue.city = request.form.get('city')
        venue.state = request.form.get('state')
        venue.address = request.form.get('address')
        venue.phone = request.form.get('phone')
        venue.genres = form.genres.data
        venue.image_link = request.form.get('image_link', None)
        venue.facebook_link = request.form.get('facebook_link', None)
        venue.website = request.form.get('website', None)
        venue.seeking_description = request.form.get('seeking_description', None)
        venue.seeking_talent = boolean_check(request.form.get('seeking_talent'))

        venue.insert()

      # on successful db insert, flash success
        flash('Venue ' + request.form['name'] + ' was successfully listed!')

    except:
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.filter(Venue.id==venue_id).one_or_none()

  if venue is None:
        abort(404)
  venue.delete()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists = Artist.query.all()

  return render_template('pages/artists.html', artists=artists)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = request.form.get('search_term', '')
  results = Artist.query.order_by(Artist.id).filter(Artist.name.ilike('%{}%'.format(search_term))).all()            
  response = []
  for result in results:
    data = {
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": result.upcoming_shows_count,
      }
    response.append(data)

  return render_template('pages/search_artists.html', results=response, search_term=search_term, count =len(results))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  artist = Artist.query.filter(Artist.id==artist_id).one_or_none()
  #past_shows, upcoming_shows
  shows = Show.query.filter(Show.artist_id==artist_id).all()
  past_shows =[]
  upcoming_shows=[]

  for show in shows:
        date_time_str = show.start_time
        date_time_obj = datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

        if date_time_obj < datetime.now():
              past_show = {"venue_id": show.venue.id,
              "venue_name": show.venue.name,
              "venue_image_link":show.venue.image_link,
              "start_time": show.start_time}

              past_shows.append(past_show)                
        else:
              upcoming_show = {"venue_id": show.venue.id,
              "venue_name": show.venue.name,
              "venue_image_link":show.venue.image_link,
              "start_time": show.start_time}
              
              upcoming_shows.append(upcoming_show)

  return render_template('pages/show_artist.html', artist=artist, upcoming_shows = upcoming_shows,
  past_shows = past_shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.filter(Artist.id==artist_id).one_or_none()

  form.name.data = artist.name
  form.genres.data = artist.genres
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.website.data = artist.website
  form.facebook_link.data = artist.facebook_link
  form.seeking_venue.data = artist.seeking_venue
  form.seeking_description.data = artist.seeking_description
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  artist = Artist.query.filter(Artist.id == artist_id).one_or_none()

  artist.name = request.form['name']
  artist.city = request.form['city']
  artist.state = request.form['state']
  artist.phone = request.form['phone']
  artist.genres = form.genres.data
  artist.image_link = request.form['image_link']
  artist.website = request.form['website']
  artist.seeking_venue = boolean_check(request.form['seeking_venue'])
  artist.seeking_description = request.form['seeking_description']
  artist.facebook_link = request.form['facebook_link']

  artist.update()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  # TODO: populate form with values from venue with ID <venue_id>
  form = VenueForm()

  venue = Venue.query.filter(Venue.id==venue_id).one_or_none()
  
  form.name.data = venue.name
  form.genres.data = venue.genres
  form.address.data = venue.address
  form.city.data = venue.city
  form.state.data = venue.state
  form.phone.data = venue.phone
  form.website.data = venue.website
  form.facebook_link.data = venue.facebook_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description.data = venue.seeking_description
  form.image_link.data = venue.image_link


  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  
  form = VenueForm(request.form)
  venue = Venue.query.filter(Venue.id == venue_id).one_or_none()

  venue.name = request.form['name']
  venue.city = request.form['city']
  venue.state = request.form['state']
  venue.phone = request.form['phone']
  venue.genres = form.genres.data
  venue.image_link = request.form['image_link']
  venue.website = request.form['website']
  venue.seeking_talent = boolean_check(request.form['seeking_talent'])
  venue.seeking_description = request.form['seeking_description']
  venue.facebook_link = request.form['facebook_link']

  venue.update()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = ArtistForm(request.form)

  try:
    artist = Artist()

    artist.name = request.form.get('name')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.genres = form.genres.data
    artist.image_link = request.form.get('image_link', None)
    artist.facebook_link = request.form.get('facebook_link', None)
    artist.website = request.form.get('website', None)
    artist.seeking_venue = boolean_check(request.form.get('seeking_venue', None))
    artist.seeking_description = request.form.get('seeking_description', False)

    artist.insert()

    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  shows = Show.query.all()
  response = []
  for show in shows:
        data = {
          "venue_id": show.venue_id,
          "venue_name":show.venue.name,
          "artist_id": show.artist_id,
          "artist_name": show.artist.name,
          "artist_image_link": show.artist.image_link,
          "start_time": show.start_time
        }
        response.append(data)
  return render_template('pages/shows.html', shows=response)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  form = ShowForm(request.form)
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # try:
  show = Show()
  show.venue_id = request.form['venue_id']
  show.artist_id = request.form['artist_id']
  show.start_time = request.form['start_time']

  show.insert()
# on successful db insert, flash success
  flash('Show was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  
  # except:
    #flash('An error occurred. Show could not be listed.')
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
