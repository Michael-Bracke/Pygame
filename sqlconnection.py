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
