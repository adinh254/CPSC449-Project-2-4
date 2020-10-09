# Mauricio Macias     (mauricio.macias@csu.fullerton.edu) 890741622
# Ariosto Kuit        (Ariostokuitak@csu.fullerton.edu) 889834065
# Andrew Dinh    (decayingapple@csu.fullerton.edu) 893242255
# CPSC449: PROJECT 2
import os

from flask import Flask, request, jsonify, g
from flask_api import status, exceptions
import click
import sqlite3
from datetime import datetime


# Constants
MAX_COUNT = 25


app = Flask(__name__, instance_relative_config=True)
# app.config.from_object('timeline_api.default_settings')


# Application API
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        temp_path = os.path.join(app.instance_path, 'tmp')
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)
        db = g._database = sqlite3.connect(os.path.join(temp_path, 'CPSC449.db'))
        db.row_factory = make_dicts
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


@app.cli.command('init')
def init_db():
    click.echo('Initializing the Database...')
    with app.app_context():
        db = get_db()
        with app.open_resource('sql/schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
            db.commit()


# Timeline Microservice
@app.route('/user/timeline', methods=['GET'])
def getUserTimeline():
    request_data = request.get_json()

    username = request_data['username']

    #Get User id.
    user_id = get_user_id(username)
    if user_id == -1:
        return 'User not found!', status.HTTP_404_NOT_FOUND

    timeline_query = 'SELECT * FROM timeline WHERE user_id=? LIMIT ?'
    recent_posts = query_db(timeline_query, (user_id, MAX_COUNT))
    return jsonify(recent_posts), status.HTTP_200_OK


@app.route('/public', methods=['GET'])
def getPublicTimeline():
    timeline_query = 'SELECT * FROM timeline LIMIT ?'
    recent_posts = query_db(timeline_query, (MAX_COUNT,))
    return jsonify(recent_posts), status.HTTP_200_OK


@app.route('/home', methods=['GET'])
def getHomeTimeline():
    request_data = request.get_json()

    username = request_data['username']

    user_id = get_user_id(username)
    if user_id == -1:
        return 'User not found!', status.HTTP_404_NOT_FOUND

    following_query = 'SELECT following_id FROM user_relations WHERE follower_id=?'
    follow_relations = query_db(following_query, (user_id,))
    if len(follow_relations) < 1:
        return 'User is not following anyone!', status.HTTP_404_NOT_FOUND

    # Iterate through list of dictionaries and turn it into a tuple.
    followed_user_ids = tuple(relation['following_id'] for relation in follow_relations)
    timeline_query = f'SELECT * FROM timeline WHERE user_id IN ({",".join("?" * len(followed_user_ids))}) LIMIT ?'

    recent_posts = query_db(timeline_query, (*followed_user_ids, MAX_COUNT))
    return jsonify(recent_posts), status.HTTP_200_OK


@app.route('/tweet', methods=['POST'])
def postTweet():
    request_data = request.get_json()

    username = request_data['username']
    text = request_data['desc']
    user_id = get_user_id(username)

    if user_id == -1:
        return 'User not found!', status.HTTP_404_NOT_FOUND

    insert_query = 'INSERT INTO timeline (user_id, description) VALUES(?,?)'
    post_data = (user_id, text)

    db = get_db()
    # Insert post data into the timeline table.
    try:
        db.execute(insert_query, post_data)
    except sqlite3Error as err:
        err_string = str(err)
        return err_string, status.HTTP_500_INTERNAL_SERVER_ERROR

    timestamp = datetime.now()
    db.commit()
    return f'New post on {timestamp}', status.HTTP_200_OK


# Helper Functions
def get_user_id(username):
    user_query = 'SELECT DISTINCT id FROM user WHERE username=?'
    db = get_db()
    user_data = query_db(user_query, (username,))
    if len(user_data) < 1:
        return -1
    return user_data[0]['id']

