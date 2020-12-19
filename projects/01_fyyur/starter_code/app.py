#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# shows_table = db.Table('Shows',
#                        db.Column('artist_id', db.Integer, db.ForeignKey(
#                            'Artist.id'), primary_key=True),
#                        db.Column('venue_id', db.Integer, db.ForeignKey(
#                            'Venue.id'), primary_key=True),
#                        db.Column('start_time', db.DateTime, nullable=False)
#                        )


class Show(db.Model):
    __tablename__ = 'Show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'Artist.id', ondelete='CASCADE'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'Venue.id', ondelete='CASCADE'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    artist = db.relationship("Artist", back_populates="venues")
    venue = db.relationship("Venue", back_populates="artists")


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500))

    artists = db.relationship("Show", back_populates="venue")


class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500))

    venues = db.relationship("Show", back_populates="artist")


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format)


app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#


@ app.route('/')
def index():
    return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

#  Create Venue
#  ----------------------------------------------------------------


@ app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@ app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    error = False
    try:
        venue = Venue()
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.facebook_link = request.form['facebook_link']
        venue.image_link = request.form['image_link']

        venue.website = request.form['website']
        venue.seeking_talent = True if (
            'seeking_talent' in request.form.keys() and
            request.form['seeking_talent'] == 'y') else False
        venue.seeking_description = request.form['seeking_description']
        db.session.add(venue)
        db.session.commit()
    except Exception as exp:
        error = True
        db.session.rollback()
        print(str(exp))
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be listed.', 'error')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')


#  Read Venue
#  ----------------------------------------------------------------

@ app.route('/venues')
def venues():
    venues = Venue.query.order_by(Venue.city, Venue.state).all()
    cities_dict = {}
    for venue in venues:
        if not venue.city in cities_dict.keys():
            cities_dict[venue.city] = {}
        if not venue.state in cities_dict[venue.city].keys():
            cities_dict[venue.city][venue.state] = {}
            cities_dict[venue.city][venue.state]["venues"] = []
        cities_dict[venue.city][venue.state]["venues"].append(
            {
                "id": venue.id,
                "name": venue.name,
                "num_upcoming_shows": len(Show.query.filter(Show.venue_id == venue.id).filter(Show.start_time > datetime.today()).all())
            }
        )

    data = []
    for city in cities_dict:
        for state in cities_dict[city]:

            data.append({
                "city": city,
                "state": state,
                "venues": cities_dict[city][state]["venues"]
            })
    return render_template('pages/venues.html', areas=data)


@ app.route('/venues/search', methods=['POST'])
def search_venues():
    st = request.form['search_term']
    venues = Venue.query.filter(Venue.name.ilike(f'%{st}%')).all()
    print(request.form['search_term'])
    data = []
    for v in venues:
        shows = Show.query.filter(Show.venue_id == v.id).filter(
            Show.start_time > datetime.today()).all()
        data.append({
            "id": v.id,
            "name": v.name,
            "num_upcoming_shows": len(shows)
        })
    response = {
        "count": len(venues),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    venue = Venue.query.get(venue_id)
    if venue is None:
        return not_found_error('')
    venue.past_shows = []
    venue.upcoming_shows = []
    shows = Show.query.filter(
        Show.venue_id == venue_id
    ).all()
    for s in shows:
        print(s)
        row = {
            "artist_id": s.artist.id,
            "artist_name": s.artist.name,
            "artist_image_link": s.artist.image_link,
            "start_time": str(s.start_time)
        }
        if s.start_time > datetime.today():
            venue.upcoming_shows.append(row)
        else:
            venue.past_shows.append(row)
    venue.past_shows_count = len(venue.past_shows)
    venue.upcoming_shows_count = len(venue.upcoming_shows)

    return render_template('pages/show_venue.html', venue=venue)

#  UPDATE Venue
#  ----------------------------------------------------------------


@ app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    form = VenueForm()
    venue = Venue()
    error = False
    try:
        venue = Venue.query.get(venue_id)
        if venue is None:
            return not_found_error('')
        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.address.data = venue.address
        form.phone.data = venue.phone
        form.genres.data = venue.genres
        form.facebook_link.data = venue.facebook_link
        form.image_link.data = venue.image_link
        form.website.data = venue.website
        form.seeking_talent.data = venue.seeking_talent
        form.seeking_description.data = venue.seeking_description
    except Exception as exp:
        error = True
        print(str(exp))
    finally:
        db.session.close()
    if error:
        flash('An error occurred', 'error')

    return render_template('forms/edit_venue.html', form=form, venue=venue)


@ app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    error = False
    try:
        venue = Venue.query.get(venue_id)
        if venue is None:
            return not_found_error('')
        venue.name = request.form['name']
        venue.city = request.form['city']
        venue.state = request.form['state']
        venue.address = request.form['address']
        venue.phone = request.form['phone']
        venue.genres = request.form.getlist('genres')
        venue.facebook_link = request.form['facebook_link']
        venue.image_link = request.form['image_link']

        venue.website = request.form['website']
        venue.seeking_talent = True if (
            'seeking_talent' in request.form.keys() and
            request.form['seeking_talent'] == 'y') else False
        venue.seeking_description = request.form['seeking_description']
        db.session.commit()
    except Exception as exp:
        error = True
        db.session.rollback()
        print(str(exp))
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Venue ' +
              request.form['name'] + ' could not be edited.', 'error')
    else:
        flash('Venue ' + request.form['name'] + ' was successfully edited!')

    return redirect(url_for('show_venue', venue_id=venue_id))


#  Delete Venue
#  ----------------------------------------------------------------
@ app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    error = False
    try:
        Venue.query.filter_by(id=venue_id).delete()
        db.session.commit()
    except Exception as exp:
        error = True
        db.session.rollback()
        print(str(exp))
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Venue could not be deleted.', 'error')
    else:
        flash('Venue was successfully deleted!')
    return redirect(url_for('index'), 200)


#  Artists
#  ----------------------------------------------------------------

#  Create Artist
#  ----------------------------------------------------------------

@ app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@ app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    error = False
    try:
        artist = Artist()
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        artist.website = request.form['website']
        artist.seeking_venue = True if (
            'seeking_venue' in request.form.keys() and
            request.form['seeking_venue'] == 'y') else False
        artist.seeking_description = request.form['seeking_description']
        db.session.add(artist)
        db.session.commit()
    except Exception as exp:
        error = True
        db.session.rollback()
        print(str(exp))
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be listed.', 'error')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')

#  Read Artist
#  ----------------------------------------------------------------


@ app.route('/artists')
def artists():
    artists = Artist.query.all()
    return render_template('pages/artists.html', artists=artists)


@ app.route('/artists/search', methods=['POST'])
def search_artists():
    st = request.form['search_term']
    artists = Artist.query.filter(Artist.name.ilike(f'%{st}%')).all()
    print(request.form['search_term'])
    data = []
    for a in artists:
        shows = Show.query.filter(Show.artist_id == a.id).filter(
            Show.start_time > datetime.today()).all()
        data.append({
            "id": a.id,
            "name": a.name,
            "num_upcoming_shows": len(shows)
        })
    response = {
        "count": len(artists),
        "data": data
    }
    return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))


@ app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    artist = Artist.query.get(artist_id)
    if artist is None:
        return not_found_error('')
    artist.past_shows = []
    artist.upcoming_shows = []
    shows = Show.query.filter(
        Show.artist_id == artist_id
    ).all()
    for s in shows:
        print(s)
        row = {
            "venue_id": s.venue.id,
            "venue_name": s.venue.name,
            "venue_image_link": s.venue.image_link,
            "start_time": str(s.start_time)
        }
        if s.start_time > datetime.today():
            artist.upcoming_shows.append(row)
        else:
            artist.past_shows.append(row)
    artist.past_shows_count = len(artist.past_shows)
    artist.upcoming_shows_count = len(artist.upcoming_shows)
    return render_template('pages/show_artist.html', artist=artist)


#  Update Artist
#  ----------------------------------------------------------------


@ app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    form = ArtistForm()
    artist = Artist()
    error = False
    try:
        artist = Artist.query.get(artist_id)
        if artist is None:
            return not_found_error('')
        form.name.data = artist.name
        form.city.data = artist.city
        form.state.data = artist.state
        form.phone.data = artist.phone
        form.genres.data = artist.genres
        form.facebook_link.data = artist.facebook_link
        form.image_link.data = artist.image_link
        form.website.data = artist.website
        form.seeking_venue.data = artist.seeking_venue
        form.seeking_description.data = artist.seeking_description
    except Exception as exp:
        error = True
        print(str(exp))
    finally:
        db.session.close()
    if error:
        flash('An error occurred', 'error')
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@ app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    error = False
    try:
        artist = Artist.query.get(artist_id)
        if artist is None:
            return not_found_error('')
        artist.name = request.form['name']
        artist.city = request.form['city']
        artist.state = request.form['state']
        artist.phone = request.form['phone']
        artist.genres = request.form.getlist('genres')
        artist.facebook_link = request.form['facebook_link']
        artist.image_link = request.form['image_link']
        artist.website = request.form['website']
        artist.seeking_venue = True if (
            'seeking_venue' in request.form.keys() and
            request.form['seeking_venue'] == 'y') else False
        artist.seeking_description = request.form['seeking_description']
        db.session.commit()
    except Exception as exp:
        error = True
        db.session.rollback()
        print(str(exp))
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Artist ' +
              request.form['name'] + ' could not be edited.', 'error')
    else:
        flash('Artist ' + request.form['name'] + ' was successfully edited!')

    return redirect(url_for('show_artist', artist_id=artist_id))

#  Delete Artist
#  ----------------------------------------------------------------


@ app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    error = False
    try:
        Artist.query.filter_by(id=artist_id).delete()
        db.session.commit()
    except Exception as exp:
        error = True
        db.session.rollback()
        print(str(exp))
    finally:
        db.session.close()
    if error:
        flash('An error occurred. Artist could not be deleted.', 'error')
    else:
        flash('Artist was successfully deleted!')
    return redirect(url_for('index'), 200)


#  Shows
#  ----------------------------------------------------------------

#  Create Show
#  ----------------------------------------------------------------
@ app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@ app.route('/shows/create', methods=['POST'])
def create_show_submission():
    error = False
    try:
        show = Show()
        show.artist_id = request.form['artist_id']
        show.venue_id = request.form['venue_id']
        show.start_time = request.form['start_time']
        db.session.add(show)
        db.session.commit()
    except Exception as exp:
        error = True
        db.session.rollback()
        print(str(exp))
    finally:
        db.session.close()

    if error:
        flash('An error occurred. Show could not be listed.', 'error')
    else:
        flash('Show was successfully listed!')
    return render_template('pages/home.html')

#  Read Show
#  ----------------------------------------------------------------


@ app.route('/shows')
def shows():
    all_shows = Show.query.all()
    data = []
    for s in all_shows:
        data.append({
            "venue_id": s.venue.id,
            "venue_name": s.venue.name,
            "artist_id": s.artist.id,
            "artist_name": s.artist.name,
            "artist_image_link": s.artist.image_link,
            "start_time": str(s.start_time)
        })
    return render_template('pages/shows.html', shows=data)


@ app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@ app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
