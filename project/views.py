import sqlite3
from flask import Flask, flash, render_template, request, redirect, url_for, g, session
from functools import wraps

app = Flask(__name__)
app.config.from_object('_config')


def connect_db():
    return sqlite3.connect(app.config['DATABASE_PATH'])


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if "logged_in" in session:
            return func(*args, **kwargs)
        else:
            flash("Authentication is required, please login")
            return redirect(url_for('login'))
    return wrapper


@app.route('/', methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form['username'] != app.config['USERNAME'] or request.form['password'] != app.config['PASSWORD']:
            error = "Invalid user credentials, please try again"
            return render_template('logint.html', error=error)
        else:
            session['logged_in'] = True
            flash('Welcome!!!')
            return redirect(url_for('tasks'))
    return render_template('login.html')


@app.route('/logout/')
def logout():
    session.pop('logged_in', None)
    flash('Goodbye!!!')
    return redirect(url_for('login'))