from flask import Flask, request, jsonify
import sqlite3
from datetime import date

app = Flask(__name__)


def init_db():
    conn = sqlite3.connect('workout_logs.db')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY,
            exercise TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL NOT NULL,
            date TEXT
        )
    ''')
    # Migrate existing databases that lack the date column
    try:
        conn.execute('ALTER TABLE workout_logs ADD COLUMN date TEXT')
    except sqlite3.OperationalError:
        pass  # Column already exists
    conn.commit()
    conn.close()


init_db()


@app.route('/workouts', methods=['POST'])
def create_workout():
    data = request.json
    workout_date = data.get('date') or date.today().isoformat()
    conn = sqlite3.connect('workout_logs.db')
    row = conn.execute(
        'SELECT COALESCE(MAX(id), 0) + 1 FROM workout_logs').fetchone()
    next_id = row[0]
    conn.execute(
        'INSERT INTO workout_logs (id, exercise, sets, reps, weight, date) VALUES (?, ?, ?, ?, ?, ?)',
        (next_id, data['exercise'], data['sets'],
         data['reps'], data['weight'], workout_date)
    )
    conn.commit()
    conn.close()
    return jsonify({'message': 'Workout added'}), 201


@app.route('/workouts', methods=['GET'])
def get_workouts():
    conn = sqlite3.connect('workout_logs.db')
    rows = conn.execute(
        'SELECT id, exercise, sets, reps, weight, date FROM workout_logs').fetchall()
    conn.close()
    workouts = [
        {'id': r[0], 'exercise': r[1], 'sets': r[2],
            'reps': r[3], 'weight': r[4], 'date': r[5]}
        for r in rows
    ]
    return jsonify(workouts)


@app.route('/workouts/<int:id>', methods=['PUT'])
def update_workout(id):
    data = request.json
    workout_date = data.get('date') or date.today().isoformat()
    conn = sqlite3.connect('workout_logs.db')
    cursor = conn.execute(
        'UPDATE workout_logs SET exercise=?, sets=?, reps=?, weight=?, date=? WHERE id=?',
        (data['exercise'], data['sets'], data['reps'],
         data['weight'], workout_date, id)
    )
    conn.commit()
    conn.close()
    if cursor.rowcount == 0:
        return jsonify({'message': 'Workout not found'}), 404
    return jsonify({'message': 'Workout updated'})


@app.route('/workouts', methods=['DELETE'])
def delete_all_workouts():
    conn = sqlite3.connect('workout_logs.db')
    conn.execute('DELETE FROM workout_logs')
    conn.commit()
    conn.close()
    return jsonify({'message': 'All workouts deleted'})


@app.route('/workouts/<int:id>', methods=['DELETE'])
def delete_workout(id):
    conn = sqlite3.connect('workout_logs.db')
    cursor = conn.execute('DELETE FROM workout_logs WHERE id=?', (id,))
    if cursor.rowcount == 0:
        conn.close()
        return jsonify({'message': 'Workout not found'}), 404
    conn.execute('UPDATE workout_logs SET id = id - 1 WHERE id > ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'message': 'Workout deleted'})


if __name__ == '__main__':
    app.run(debug=True)
