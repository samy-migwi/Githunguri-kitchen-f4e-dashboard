from flask import Flask, render_template, request, jsonify, send_file
import sqlite3
import csv
import os
from io import StringIO

app = Flask(__name__)

# Initialize SQLite Database
def init_db():
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS extracted_data (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            data TEXT NOT NULL)''')
        conn.commit()

# Home Route@app.route('/')
def home():
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM extracted_data")
        entries = cursor.fetchall()
    return render_template('index.html', entries=entries)

# Save Extracted Data@app.route('/save', methods=['POST'])
def save():
    data = request.json.get('data')
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO extracted_data (data) VALUES (?)", (data,))
        conn.commit()
    return jsonify({"message": "Data saved successfully!"})

# Export Data as CSV@app.route('/export', methods=['GET'])
def export():
    with sqlite3.connect("data.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM extracted_data")
        entries = cursor.fetchall()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID", "Data"])
    writer.writerows(entries)
    output.seek(0)

    return send_file(output, mimetype='text/csv',
                     as_attachment=True, attachment_filename='extracted_data.csv')

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
