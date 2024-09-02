import sqlite3
conn=sqlite3.connect('employees.db')

cur=conn.cursor()

cur.execute("SELECT * FROM company;")

rows=cur.fetchall()

print(rows)