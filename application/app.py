import click
from flask import Flask, request, jsonify, g
from flask_api import status, exceptions
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config.from_object('application.default_settings')


def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(app.config['DATABASE'])
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


@app.route('/', methods=['GET'])
def hello():
    return '''<h1>Distant Reading Archive</h1>
<p>A prototype API for distant reading of science fiction novels.</p>'''


@app.route('/api/all', methods=['GET'])
def api_all():
    all_users = query_db('SELECT * FROM user;')
    return jsonify(all_users)


@app.route('/user', methods=['GET', 'POST'])
def user():
    if request.method == 'POST':
        return create_user()


def create_user():
    user_data = request.get_json()
    post_fields = {*user_data.keys()}
    required_fields = {'username', 'email', 'password'}

    if not required_fields <= post_fields:
        err = f'Missing fields: {required_fields - post_fields}'
        raise exceptions.ParseError(err)

    username = user_data['username']
    email = user_data['email']
    password = user_data['password']

    hashed = generate_password_hash(password, method='pbkdf2:sha256')

    insert_query = 'INSERT INTO user (username, email, password) VALUES (?, ?, ?)'
    new_user = (username, email, hashed)
    db = get_db()
    try:
        db.execute(insert_query, new_user)
    except sqlite3.Error as err:
        err_string = str(err)
        if 'UNIQUE' not in err_string:
            return err_string, status.HTTP_500_INTERNAL_SERVER_ERROR
        return err_string, status.HTTP_409_CONFLICT
    db.commit()
    user_data['password'] = hashed
    return user_data, status.HTTP_200_OK


@app.route('/follow', methods=['POST'])
def follow():
    user_ids = get_relation_ids()
    return add_follower(*user_ids)


@app.route('/unfollow', methods=['POST'])
def unfollow():
    user_ids = get_relation_ids()
    return remove_follower(*user_ids)


def get_relation_ids():
    relation_data = request.get_json()
    post_fields = {*relation_data.keys()}
    required_fields = {'username', 'user_followed'}
    if not required_fields <= post_fields:
        err = f'Missing Fields: {required_fields - post_fields}'
        return err, status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE
    if relation_data['username'] == relation_data['user_followed']:
        err = 'ERROR: User cannot follow themself.'
        return err, status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE

    username = relation_data['username']
    user_followed = relation_data['user_followed']

    user_query = 'SELECT id, username FROM user WHERE username in (?, ?)'
    user_data = query_db(user_query, (username, user_followed))
    if len(user_data) < 2:
        for data in user_data:
            if data['username'] == username:
                return f'ERROR: Failed to follow {user_followed}. User does not exist in the database.', status.HTTP_404_NOT_FOUND
            else:
                return f'ERROR: {username} does not exist.', status.HTTP_404_NOT_FOUND
            return f'ERROR: Users do not exist.', status.HTTP_404_NOT_FOUND

    follower_id = 0
    following_id = 0
    first_row = user_data[0]
    second_row = user_data[1]
    if first_row['username'] == username:
        follower_id = first_row['id']
        following_id = second_row['id']
    else:
        follower_id = first_row['id']
        following_id = second_row['id']

    return (follower_id, following_id)


def add_follower(follower_id, following_id):
    insert_query = 'INSERT INTO user_relations (follower_id, following_id) VALUES (?, ?)'
    db = get_db()
    try:
        db.execute(insert_query, (follower_id, following_id))
    except sqlite3.Error as err:
        err_string = str(err)
        if 'UNIQUE' not in err_string:
            return err_string, status.HTTP_500_INTERNAL_SERVER_ERROR
        return err_string, status.HTTP_409_CONFLICT
    db.commit()
    success_string = f'User {follower_id} is now following User {following_id}.'
    return success_string, status.HTTP_200_OK


def remove_follower(follower_id, following_id):
    delete_query = 'DELETE FROM user_relations WHERE follower_id=? AND following_id=?'
    db = get_db()
    cur = db.execute(delete_query, (follower_id, following_id))
    rows_deleted = cur.rowcount
    if rows_deleted < 1:
        return 'ERROR: Follow relation not found.', status.HTTP_404_NOT_FOUND

    assert rows_deleted < 2, "Duplicate follow relations should not exist!"

    db.commit()
    success_string = f'User {follower_id} has unfollowed User {following_id}.'
    return success_string, status.HTTP_200_OK


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == '__main__':
    app.run()
