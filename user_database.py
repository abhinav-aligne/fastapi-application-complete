from database_connect import connectivity

mydb, mycursor = connectivity()

def user_database_connect():
    mycursor = mydb.cursor(dictionary=True)
    mycursor.execute("SELECT * FROM users")
    user_db = mycursor.fetchall()
    return user_db