import sqlite3
conn=sqlite3.connect('tests_data/employees.db')

cur=conn.cursor()

cur.execute("SELECT * FROM company;")

rows=cur.fetchall()

print(rows)