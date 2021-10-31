import pyodbc 

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=localhost\\SQLEXPRESS;'
                      'Database=pygame;'
                      'Trusted_Connection=yes;')

cursor = conn.cursor()

def printScoreboard():
    cursor.execute('SELECT * FROM Scoreboard')
    for i in cursor:
      print(i)

def CreateUser(name):
    sql_string = f"INSERT INTO Users (name) OUTPUT Inserted.Id VALUES('{name}');"
    print(sql_string)
    cursor.execute(sql_string)
    conn.commit() 
    return cursor

