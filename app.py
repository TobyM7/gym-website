from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'supersecretkey'

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS workouts
                 (id INTEGER PRIMARY KEY, exercise TEXT, sets INTEGER, reps INTEGER, weights TEXT, date TEXT)''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    if 'loggedin' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        password = request.form['password']
        if password == 'yourpassword':  # Replace with a more secure method
            session['loggedin'] = True
            return redirect(url_for('home'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'loggedin' in session:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM workouts')
        workouts = c.fetchall()
        conn.close()

        return render_template('dashboard.html', workouts=workouts)
    return redirect(url_for('login'))

@app.route('/add_workout', methods=['POST'])
def add_workout():
    if 'loggedin' in session:
        exercise = request.form['exercise']
        sets = int(request.form['sets'])
        reps = request.form['reps']
        weights = ','.join(request.form.getlist('weights'))
        date = datetime.now().strftime('%Y-%m-%d')

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO workouts (exercise, sets, reps, weights, date) VALUES (?, ?, ?, ?, ?)",
                  (exercise, sets, reps, weights, date))
        conn.commit()
        conn.close()

        return redirect(url_for('home'))
    return redirect(url_for('login'))

@app.route('/history')
def history():
    if 'loggedin' in session:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM workouts')
        workouts = c.fetchall()
        conn.close()

        return render_template('history.html', workouts=workouts)
    return redirect(url_for('login'))

@app.route('/delete_workout/<int:workout_id>', methods=['POST'])
def delete_workout(workout_id):
    if 'loggedin' in session:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('DELETE FROM workouts WHERE id = ?', (workout_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('history'))
    return redirect(url_for('login'))
if __name__ == '__main__':
    init_db()
    app.run(debug=True)
