import sqlite3
p=r'D:/hackthon/karanataka police/Criminal Justice/backend/synthetic_demo.db'
conn=sqlite3.connect(p)
c=conn.cursor()
try:
    c.execute('SELECT id, username, role FROM employees')
    rows=c.fetchall()
    print('employees count', len(rows))
    for r in rows[:50]:
        print(r)
except Exception as e:
    print('ERROR', e)
finally:
    conn.close()
