import bcrypt
import pymysql

# Database connection
connection = pymysql.connect(
    host='localhost',        # Your MySQL host (default is localhost)
    user='root',             # Your MySQL username
    password='root', # Your MySQL password
    database='quiz_db'       # Your database name
)

cursor = connection.cursor()

# Admin users with plaintext passwords (you can replace these with your own values)
admins = [
    {"username": "admin1", "password": "admin123"},
    {"username": "admin2", "password": "admin456"}
]

for admin in admins:
    # Hash the password
    hashed_password = bcrypt.hashpw(admin['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    # Update the password in the database
    cursor.execute("UPDATE admins SET password = %s WHERE username = %s", (hashed_password, admin['username']))

connection.commit()
cursor.close()
connection.close()

print("Admin passwords updated successfully!")
