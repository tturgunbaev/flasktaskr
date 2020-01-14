import sqlite3
from flask import Flask, flash, render_template, request, redirect, url_for, g, session
from functools import wraps
from forms import AddTaskForm

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
            return render_template('login.html', error=error)
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


@app.route('/tasks/')
@login_required
def tasks():
    g.db = connect_db()
    cursor = g.db.cursor()
    cursor.execute("SELECT name, due_date, priority, task_id FROM tasks WHERE status=1")
    open_tasks = [dict(name=row[0], due_date=row[1], priority=row[2], task_id=row[3]) for row in cursor.fetchall()]
    cursor.execute("SELECT name, due_date, priority, task_id FROM tasks WHERE status=0")
    closed_tasks = [dict(name=row[0], due_date=row[1], priority=row[2], task_id=row[3]) for row in cursor.fetchall()]
    g.db.close()
    return render_template('tasks.html', form=AddTaskForm(request.form),
                           open_tasks=open_tasks, closed_tasks=closed_tasks)\



@app.route('/add/', methods=["POST"])
@login_required
def new_task():
    g.db = connect_db()
    name = request.form['name']
    date = request.form['due_date']
    priority = request.form['priority']
    if not name or not priority:
        flash("All fields are required. Please try again!")
        return redirect(url_for('tasks'))
    else:
        g.db.execute("INSERT INTO tasks (name, due_date, priority, status) VALUES (?,?,?,1)", (name, date, priority))
        g.db.commit()
        g.db.close()
        flash("New entry was successfully posted. Thanks")
        return redirect(url_for('tasks'))


@app.route('/complete/<int:task_id>')
@login_required
def complete(task_id):
    g.db = connect_db()
    g.db.execute(f"UPDATE tasks SET status=0 WHERE task_id={task_id}")
    g.db.commit()
    g.db.close()
    flash(f'The task {task_id} was marked as complete')
    return redirect(url_for('tasks'))


@app.route('/delete/<int:task_id>')
@login_required
def delete_entry(task_id):
    g.db = connect_db()
    g.db.execute(f"DELETE FROM tasks WHERE task_id={task_id}")
    g.db.commit()
    g.db.close()
    flash(f"The task {task_id} was successfully deleted")
    return redirect(url_for('tasks'))
