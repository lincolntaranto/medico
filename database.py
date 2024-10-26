import sqlite3
from flask import g

DATABASE = 'medical_records.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

def init_db():
    with sqlite3.connect(DATABASE) as db:
        db.executescript('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER,
            gender TEXT
        );
        CREATE TABLE IF NOT EXISTS exams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER,
            exam_type TEXT NOT NULL,
            date TEXT NOT NULL,
            results TEXT,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        );
        ''')

def close_db(e=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()