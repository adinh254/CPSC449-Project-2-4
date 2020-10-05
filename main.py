import click
from flask import Flask, request, jsonify, g
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
        with app.open_resource('sql/user.sql', mode='r') as f:
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

# @app.cli.command('create')
# @click.argument('username')
# @click.argument('email')
# @click.argument('password')
# def create_user(username, email, password):
#     hpassword = generate_password_hash(password)
#     insert_query = 'INSERT INTO user (username, email, password) VALUES (?, ?, ?)'
#     new_user = (username, email, hpassword)
#     db = get_db()
#     db.execute(insert_query, new_user)
#     db.commit()
#     return jsonify(new_user)

@app.route('/authenticateUser/', methods=['GET'])
def auth(): 
    query_parameters = request.args

    username = query_parameters.get('username')
    password = query_parameters.get('password')
    # hash password here
    # hpassword = generate_password_hash(password, method="pbkdf2:sha256")
    print(password)
    # print(hpassword)
    # uhpass = check_password_hash(hpassword,password)
    # print(uhpass)

    query = "SELECT * FROM user WHERE"
    to_filter = []

    if username: 
        query += ' username=? AND'
        to_filter.append(username)
    if password:
        query += ' password=? AND'
        to_filter.append(password)
    if not (username or password):
        return page_not_found(404)
    
    query = query[:-4] + ';'
    result = query_db(query, to_filter)
    # a = result
    a = " ".join([str(elem) for elem in result])


    if not result:
        a = "False"

    return a


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404


if __name__ == '__main__':
    app.run()
