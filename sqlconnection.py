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
    for value in cursor:
        retrieved_user_id = value
    conn.commit()    
    return retrieved_user_id[0]

def UpdateScoreboard(user_id, score, time):
    sql_string_insert = f"INSERT INTO Scoreboard VALUES({user_id}, {score},  CONVERT(TIME, DATEADD(MILLISECOND, {time}, 0), 114))"
    sql_string_update = f"UPDATE Scoreboard SET Score = {score}, TimeToComplete = CONVERT(TIME, DATEADD(MILLISECOND, {time}, 0), 114) WHERE UserId = {user_id} AND Score < {score}"
    sql = f"IF (NOT EXISTS(SELECT * FROM Scoreboard WHERE UserId = {user_id})) BEGIN {sql_string_insert} END ELSE BEGIN {sql_string_update} END"
    print(sql)
    cursor.execute(sql)
    conn.commit() 

def GetLeaderboard():
    sql_string = f"Select * FROM Scoreboard"
