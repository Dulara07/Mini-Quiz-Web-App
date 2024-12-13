from flask import Flask
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'  
app.config['MYSQL_DB'] = 'quiz_db'

mysql = MySQL(app)

with app.app_context():
    # Dummy user data
    users = [
        ('user1', 'password1'),
        ('user2', 'password2'),
        ('user3', 'password3'),
    ]

    cur = mysql.connection.cursor()
    for username, password in users:
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
    
    mysql.connection.commit()  # Save changes
    cur.close()

print("Dummy data inserted successfully.")