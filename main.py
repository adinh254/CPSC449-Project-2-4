from flask import Flask, request, jsonify, g
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import click
import json


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

@app.route('/authenticateUser', methods=['GET','POST'])
def auth(): 
    # get data from user
    data = request.json
    username = data["username"]
    password = data["password"]

    #get the hash password from user
    query = "SELECT password FROM user WHERE"
    to_filter = []

    if username:
        query += ' username=? AND'
        to_filter.append(username)
    if not username:
        return page_not_found(404)
    
    query = query[:-4] + ';'
    result = query_db(query, to_filter)[0]
    hpassword = result['password']
    
    print(hpassword)
    answer = False
    
    #checks if user input password is correct or not.
    if check_password_hash(hpassword,password):
        answer = True
    print(str(answer))

    return answer


@app.route('/getTime/', methods=['GET'])
def userTime(): 
    query_parameters = request.args

    author = query_parameters.get('author')

    query = "SELECT * FROM timeline WHERE"
    to_filter = []

    if author: 
        query += ' author=? AND'
        to_filter.append(author)
    if not (author):
        return page_not_found(404)

    query = query[:-4] + ';'
    result = query_db(query, to_filter)
    a = "True"

    if not result:
        a = "False"
    return a


@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.route('/postTweet', methods=['GET','POST'])
def postTweet():
    # get data from user
    data = request.json
    username = data["username"]
    tweet = data["tweet"]

    #get user id from user
    user_query = 'SELECT id FROM user WHERE username= ?;'
    user_id = query_db(user_query, username)

    # insert tweet to timeline
    insert_query = 'INSERT INTO timeline (user_id, tweet) VALUES (?, ?)'
    get_db().execute(insert_query,(user_id, tweet))
    
    
@app.route('/getHomeTimeline', methods=['GET','POST'])
def postTweet():
    # get username
    data = request.json
    username = data["username"]
    friends = [] # list of friends
    
    #Query to get list of follows
    friendQuery = 'SELECT following FROM user_relations WHERE follower= ?'
    friendResult = query_db(friendQuery,username)

    #get list this user follows
    for friend in friendResult:
        friends.append(friend)


if __name__ == '__main__':
    app.run()
