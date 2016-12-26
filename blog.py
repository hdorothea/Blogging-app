from flask import Flask, render_template, request, g, session, redirect, url_for
from flask.ext.login import LoginManager, login_user, UserMixin, current_user
from flask.ext.bootstrap import Bootstrap
import os
import sqlite3
from werkzeug import check_password_hash, generate_password_hash
from contextlib import closing


login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
app = Flask(__name__)
login_manager.init_app(app)
app.secret_key = 'super secret key'
bootstrap = Bootstrap(app)
DATABASE = os.path.join(app.root_path, 'blog.db')
app.config.from_object(__name__)

class User(UserMixin):
    
    def __init__(self, username):
        # i am trying to implement the same thing as in 'flask web development' but without an orm
        # check if the user who tries to login exists 
        self.username = username
        if not self.get_id():
            raise ValueError('No user with that name exists')


    def get_id(self):
        cursor = get_db().cursor()
        self.id = cursor.execute("SELECT id FROM users WHERE username=?", [self.username]).fetchone()[0]
        return self.id

@login_manager.user_loader
def load_user(user_id):
    cursor = get_db().cursor() 
    return User(cursor.execute("SELECT username FROM users WHERE id=?", [user_id]).fetchone()[0])


def init_db():
    db = connect_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.commit()
        g.db.close()


def get_db():
    if not hasattr(g, 'db'):
        g.db = connect_db()
    return g.db


def get_user_id(username):
    cursor = get_db().cursor() 
    return cursor.execute("SELECT id FROM users WHERE username=?", [username]).fetchone()[0]


def connect_db():
    return sqlite3.connect(app.config['DATABASE'])


def insert_title_entry(user_id, title, entry):
    with closing(get_db().cursor()) as cursor:
        cursor.execute('''INSERT INTO entries (userid, title, entry) VALUES(?, ?, ?)''', 
                       [user_id, title, entry])


def insert_username_passwordhash(user_name, password_hash):
    with closing(get_db().cursor()) as cursor:
        cursor.execute('''INSERT INTO users (username, password_hash) VALUES(?, ?)''', 
                       [user_name, password_hash]) 


def get_titles_entries_ids(user_id):
    cursor = get_db().cursor()
    titles_entries_ids = cursor.execute('''SELECT title, entry, id FROM entries WHERE userid = ?''', [user_id]).fetchall()
    return titles_entries_ids


@app.errorhandler(404)
def page_not_found(e):
    return render_template("error.html"), 404


@app.route("/add_entry", methods=['POST',]) 
def do_add_entry():
    insert_title_entry(session['user_id'], request.form['title'], request.form['entry'])
    return redirect(url_for('serve_home'))


@app.route("/add_entry") 
def serve_add_entry():
    return render_template("add_entry.html")


@app.route("/login", methods=['POST',])
def do_login():
    cursor = get_db().cursor()
    if check_password_hash(cursor.execute('''SELECT password_hash FROM users WHERE username=?''', [request.form['username']]).fetchone()[0], request.form['password']):
        try:
            user = User(request.form['username'])
        except ValueError:
            return 'Wrong username'
        # login_user(user, request.form['remember_me'])
        return redirect(url_for("serve_home"))
    return "Wrong username or password"


@app.route("/home")
def serve_home():
    titles_entries_ids = get_titles_entries_ids(current_user.get_id())  
    return render_template("home.html", titles_entries_ids=titles_entries_ids) 


@app.route("/login")
def serve_login():
    return render_template("login.html")


@app.route("/register", methods=['POST',])
def do_register():
    insert_username_passwordhash(request.form['username'], generate_password_hash(request.form['password']))
    # TODO put the username in the login template
    return redirect(url_for('serve_login'))


@app.route("/home/<_id>")
def serve_entry(_id):
    cursor = get_db().cursor()
    title, entry = cursor.execute('''SELECT title, entry FROM entries WHERE id == ?''', [_id]).fetchone()
    return render_template("entry.html", _title=title, entry=entry)

@app.route("/register")
def serve_register():
    return render_template("register.html")


@app.route("/")
def main():
    return render_template("start.html")


if __name__ == "__main__":
    app.run()
