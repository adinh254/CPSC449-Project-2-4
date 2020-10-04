import sqlite3
from flask import Flask

app = Flask(__name__)


@app.cli.command('init')
def init_db():
    with app.app_context():
        db = get_db()
        with app.open_resource('books.sql', mode='r') as f:
            db.cursor().execute


if __name__ == '__main__':
    app.run()
