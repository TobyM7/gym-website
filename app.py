from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import sqlite3
from datetime import datetime
from fuzzywuzzy import process
import utils

app = Flask(__name__)
app.secret_key = 'supersecretkey'

exercises_list = utils.load_exercises('exercises.txt')

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS workouts
                 (id INTEGER PRIMARY KEY, exercise TEXT, sets INTEGER, reps INTEGER, weights TEXT, date TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS workout_templates
                 (id INTEGER PRIMARY KEY, name TEXT, exercises TEXT)''')
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

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if query:
        results = process.extract(query, exercises_list, limit=10)
        results = [result[0] for result in results]  # Extract the matched exercise names
    else:
        results = []
    return jsonify(results)

#Workouts from below here


@app.route('/workout_templates', methods=['GET', 'POST'])
def workout_templates():
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            exercises = []
            i = 1
            while f'exercise_name_{i}' in request.form:
                exercise_name = request.form[f'exercise_name_{i}']
                sets = request.form[f'sets_{i}']
                reps = request.form[f'reps_{i}']
                exercises.append({'name': exercise_name, 'sets': int(sets), 'reps': int(reps)})
                i += 1

            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO workout_templates (name, exercises) VALUES (?, ?)", (name, str(exercises)))
            conn.commit()
            conn.close()

            return redirect(url_for('workout_templates'))

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM workout_templates')
        templates = c.fetchall()
        conn.close()

        return render_template('workout_templates.html', templates=templates)
    return redirect(url_for('login'))

@app.route('/existing_templates',  methods=['GET', 'POST'])
def existing_templates():
    if 'loggedin' in session:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM workout_templates')
        templates = c.fetchall()
        conn.close()

        return render_template('existing_templates.html', templates=templates)
    return redirect(url_for('login'))

@app.route('/create_template', methods=['POST'])
def create_template():
    if 'loggedin' in session:
        name = request.form['name']
        exercises = ','.join(request.form.getlist('exercises'))

        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO workout_templates (name, exercises) VALUES (?, ?)", (name, exercises))
        conn.commit()
        conn.close()

        return redirect(url_for('workout_templates'))
    return redirect(url_for('login'))

@app.route('/delete_template/<int:template_id>', methods=['POST'])
def delete_template(template_id):
    if 'loggedin' in session:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('DELETE FROM workout_templates WHERE id = ?', (template_id,))
        conn.commit()
        conn.close()
        return redirect(url_for('workout_templates'))
    return redirect(url_for('login'))

@app.route('/edit_template/<int:template_id>', methods=['GET', 'POST'])
def edit_template(template_id):
    if 'loggedin' in session:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        if request.method == 'POST':
            name = request.form['name']
            exercises = []
            i = 1
            while f'exercise_name_{i}' in request.form:
                exercise_name = request.form[f'exercise_name_{i}']
                sets = request.form[f'sets_{i}']
                reps = request.form[f'reps_{i}']
                exercises.append({'name': exercise_name, 'sets': int(sets), 'reps': int(reps)})
                i += 1

            c.execute("UPDATE workout_templates SET name = ?, exercises = ? WHERE id = ?", (name, str(exercises), template_id))
            conn.commit()
            conn.close()
            return redirect(url_for('workout_templates'))
        
        c.execute('SELECT * FROM workout_templates WHERE id = ?', (template_id,))
        template = c.fetchone()
        conn.close()

        exercises = eval(template[2])  # Convert string back to list of dictionaries
        return render_template('edit_template.html', template=template, exercises=exercises)
    return redirect(url_for('login'))

@app.route('/run_workout/<int:template_id>', methods=['GET', 'POST'])
def run_workout(template_id):
    if 'loggedin' in session:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM workout_templates WHERE id = ?', (template_id,))
        template = c.fetchone()
        conn.close()

        if request.method == 'POST':
            for exercise_data in request.form.getlist('exercise_data'):
                exercise_name, sets, reps = exercise_data.split(';')
                weights = []
                for i in range(1, int(sets) + 1):
                    weight = request.form.get(f'weight_{exercise_name}_{i}')
                    if weight:
                        weights.append(weight)
                date = datetime.now().strftime('%Y-%m-%d')
                weights_str = ','.join(weights)

                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute("INSERT INTO workouts (exercise, sets, reps, weights, date) VALUES (?, ?, ?, ?, ?)",
                          (exercise_name, sets, reps, weights_str, date))
                conn.commit()
                conn.close()

            return redirect(url_for('history'))

        exercises = eval(template[2])  # Convert string back to list of dictionaries
        return render_template('run_workout.html', template=template, exercises=exercises)
    return redirect(url_for('login'))

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
