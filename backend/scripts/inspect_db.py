import os
import sqlite3

p = r'D:\hackthon\karanataka police\Criminal Justice\backend\synthetic_demo.db'
print('exists', os.path.exists(p))
conn = sqlite3.connect(p)
cur = conn.cursor()
cur.execute('SELECT name FROM sqlite_master WHERE type="table" AND name="employees"')
print('employees table', cur.fetchone())
cur.execute('SELECT COUNT(*) FROM employees')
print('employee count', cur.fetchone()[0])
cur.execute('SELECT username FROM employees LIMIT 10')
print('usernames', cur.fetchall())
conn.close()
