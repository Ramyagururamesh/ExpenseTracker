from flask import Flask, render_template, request, redirect, send_file
import sqlite3
from datetime import date
import pandas as pd

app = Flask(__name__)

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('expenses.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create table if not exists
def create_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date TEXT NOT NULL,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

create_table()

@app.route('/')
def index():
    conn = get_db_connection()
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    today = date.today().isoformat()
    total_today = conn.execute('SELECT SUM(amount) FROM expenses WHERE date = ?', (today,)).fetchone()[0] or 0
    total_all = conn.execute('SELECT SUM(amount) FROM expenses').fetchone()[0] or 0
    conn.close()
    return render_template('index.html',
                           expenses=expenses,
                           total_today=total_today,
                           total_all=total_all,
                           today=today)

@app.route('/add', methods=['POST'])
def add_expense():
    amount = request.form['amount']
    category = request.form['category']
    date_val = request.form['date']
    note = request.form['note']
    conn = get_db_connection()
    conn.execute('INSERT INTO expenses (amount, category, date, note) VALUES (?, ?, ?, ?)',
                 (amount, category, date_val, note))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/delete/<int:expense_id>', methods=['POST'])
def delete_expense(expense_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM expenses WHERE id = ?', (expense_id,))
    conn.commit()
    conn.close()
    return redirect('/')

@app.route('/total_by_date', methods=['POST'])
def total_by_date():
    query_date = request.form['query_date']
    conn = get_db_connection()
    total_on_date = conn.execute('SELECT SUM(amount) FROM expenses WHERE date = ?', (query_date,)).fetchone()[0] or 0
    expenses = conn.execute('SELECT * FROM expenses ORDER BY date DESC').fetchall()
    today = date.today().isoformat()
    total_today = conn.execute('SELECT SUM(amount) FROM expenses WHERE date = ?', (today,)).fetchone()[0] or 0
    total_all = conn.execute('SELECT SUM(amount) FROM expenses').fetchone()[0] or 0
    conn.close()
    return render_template('index.html',
                           expenses=expenses,
                           total_today=total_today,
                           total_all=total_all,
                           today=today,
                           total_on_date=total_on_date,
                           query_date=query_date)

# ✅ Moved this above the app.run line
@app.route('/export_excel')
def export_excel():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM expenses ORDER BY id ASC", conn)

    
    conn.close()
    file_path = "expenses_export.xlsx"
    df.to_excel(file_path, index=False)
    return send_file(file_path, as_attachment=True)

# ✅ This should be at the end
if __name__ == '__main__':
    app.run(debug=True)
