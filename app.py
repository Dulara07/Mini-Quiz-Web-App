from flask import Flask, render_template, request, redirect, session, flash
from flask_mysqldb import MySQL
import bcrypt

app = Flask(__name__)


app.secret_key = 'rachitha'


app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'rachitha'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'quiz_db'

mysql = MySQL(app)

# First Page: Login Choice
@app.route('/')
def login_choice():
    return render_template('login_choice.html')

# Admin Login Route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  

        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM admins WHERE username = %s", (username,))
        admin = cur.fetchone()
        cur.close()

        if admin:  
            stored_hash = admin[0]
            try:
                # Compare input password with stored hash
                if bcrypt.checkpw(password, stored_hash.encode('utf-8')):
                    session['admin_username'] = username
                    flash("Admin logged in successfully!")
                    return redirect('/admin_dashboard')
            except Exception as e:
                print("Error during password validation:", e)  
                flash("Password validation failed. Please contact support.")
                return redirect('/admin_login')

        flash("Invalid admin credentials. Please try again.")
        return redirect('/admin_login')

    return render_template('admin_login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  
        
        # Query the database for the Student
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()
        cur.close()

        # If the student exists and the password matches
        if user and bcrypt.checkpw(password, user[0].encode('utf-8')):
            session['username'] = username  
            flash("Logged in successfully!")
            return redirect('/quiz')  
        
        flash("Invalid credentials. Please try again.")
        return redirect('/login')  

    return render_template('login.html')  

# Admin Dashboard Route
@app.route('/admin_dashboard')
def admin_dashboard():
    if 'admin_username' not in session:
        return redirect('/admin_login')
    
    
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT users.username, COUNT(*) as score 
        FROM results 
        INNER JOIN users ON results.user_id = users.id 
        WHERE results.is_correct = 1 
        GROUP BY users.id
    """)
    results = cur.fetchall()
    cur.close()

    return render_template('admin_dashboard.html', results=results)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password'].encode('utf-8')  
        
        # Hash the password
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt()).decode('utf-8') 
        
        
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
        mysql.connection.commit()
        cur.close()
        
        flash("Registration successful! Please log in.")
        return redirect('/login')
    
    return render_template('register.html')

@app.route('/result', methods=['POST'])
def result():
    if 'username' not in session:
        return redirect('/login')
    
    score = 0
    answers = request.form
    cur = mysql.connection.cursor()
    
    # Get the user ID and username
    cur.execute("SELECT id, username FROM users WHERE username = %s", (session['username'],))
    user = cur.fetchone()
    user_id = user[0]
    username = user[1]
    
    for question_id, user_answer in answers.items():
        cur.execute("SELECT answer FROM quizzes WHERE id = %s", (question_id,))
        correct_answer = cur.fetchone()
        
        if correct_answer and user_answer == correct_answer[0]:
            score += 1

    # Save the final score for the user
    cur.execute("INSERT INTO results (user_id, username, score) VALUES (%s, %s, %s)",
                (user_id, username, score))
    
    cur.close()
    mysql.connection.commit()
    return render_template('result.html', score=score)

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if 'admin_username' not in session:
        flash("Please log in as admin.")
        return redirect('/admin_login')  
    
    if request.method == 'POST':
        # Handle form submission
        question = request.form['question']
        option_a = request.form['option_a']
        option_b = request.form['option_b']
        option_c = request.form['option_c']
        option_d = request.form['option_d']
        answer = request.form['answer']
        
        # Insert new question into the database
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO quizzes (question, option_a, option_b, option_c, option_d, answer) VALUES (%s, %s, %s, %s, %s, %s)",
                    (question, option_a, option_b, option_c, option_d, answer))
        mysql.connection.commit()
        cur.close()
        
        flash("Question added successfully!")
        return redirect('/admin_dashboard')  # Redirect back to the dashboard
    
    return render_template('add_question.html')

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    if 'username' not in session:
        return redirect('/login') 

  
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM quizzes")  
    questions = cur.fetchall()
    cur.close()

    if request.method == 'POST':
        answers = request.form
        print(answers) 
        
        return redirect('/result')  

    return render_template('quiz.html', questions=questions)

@app.route('/view_results')
def view_results():
    if 'admin_username' not in session:
        return redirect('/admin_login')

    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT users.username, results.score
        FROM results
        INNER JOIN users ON results.user_id = users.id
    """)
    results = cur.fetchall()  # Fetch all results
    cur.close()

    return render_template('view_results.html', results=results)


if __name__ == '__main__':
    app.run(debug=True)
