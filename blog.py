from flask import Flask, render_template, request, g
from flask.ext.bootstrap import Bootstrap
import os
import sqlite3
from werkzeug import check_password_hash, generate_password_hash



app = Flask(__name__)
bootstrap = Bootstrap(app)
DATABASE = os.path.join(app.root_path, 'blog.db')
app.config.from_object(__name__)

def init_db():
    db = connect_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'db'):
        g.db.close()


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db



def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404


@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        get_db()
        cursor = g.db.cursor()
        cursor.execute('''INSERT INTO users (username, password_hash) VALUES(?, ?)''', [request.form['username'], generate_password_hash(request.form['password'])])
        g.db.commit()
        return '{}, {}'.format(request.form['username'], generate_password_hash(request.form['password']))
    return render_template("reg.html")


@app.route("/")
def main():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
