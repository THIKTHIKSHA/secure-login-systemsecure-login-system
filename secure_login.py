from flask import Flask, render_template_string, request, redirect, session
from flask_bcrypt import Bcrypt
import sqlite3

# -----------------------------------------
# FLASK APP SETUP
# -----------------------------------------

app = Flask(__name__)
app.secret_key = "supersecretkey"

bcrypt = Bcrypt(app)

# -----------------------------------------
# DATABASE SETUP
# -----------------------------------------

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

conn.commit()
conn.close()

# -----------------------------------------
# HTML TEMPLATE
# -----------------------------------------

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Secure Login System</title>

    <style>

        body{
            font-family: Arial;
            background: #f4f4f4;
            text-align: center;
            padding-top: 50px;
        }

        .box{
            width: 350px;
            background: white;
            margin: auto;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0px 0px 10px gray;
        }

        input{
            width: 90%;
            padding: 10px;
            margin: 10px;
        }

        button{
            padding: 10px 20px;
            background: #007bff;
            color: white;
            border: none;
            cursor: pointer;
        }

        a{
            text-decoration: none;
        }

    </style>

</head>

<body>

<div class="box">

<h2>{{ title }}</h2>

<form method="POST">

<input type="text"
       name="username"
       placeholder="Username"
       required>

<input type="password"
       name="password"
       placeholder="Password"
       required>

<button type="submit">
{{ button }}
</button>

</form>

<p style="color:red;">
{{ message }}
</p>

{% if page == "register" %}
<a href="/login">Already have an account? Login</a>
{% endif %}

{% if page == "login" %}
<a href="/register">Create Account</a>
{% endif %}

</div>

</body>
</html>
"""

# -----------------------------------------
# HOME PAGE
# -----------------------------------------

@app.route("/")
def home():
    return redirect("/login")

# -----------------------------------------
# REGISTER PAGE
# -----------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():

    message = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        # Input Validation
        if len(password) < 6:

            message = "Password must be at least 6 characters"

            return render_template_string(
                HTML,
                title="Register",
                button="Register",
                message=message,
                page="register"
            )

        # Hash Password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")

        try:

            conn = sqlite3.connect("users.db")
            cursor = conn.cursor()

            # SQL Injection Protected Query
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (username, hashed_password)
            )

            conn.commit()
            conn.close()

            return redirect("/login")

        except:

            message = "Username already exists"

    return render_template_string(
        HTML,
        title="Register",
        button="Register",
        message=message,
        page="register"
    )

# -----------------------------------------
# LOGIN PAGE
# -----------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():

    message = ""

    if request.method == "POST":

        username = request.form["username"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        )

        user = cursor.fetchone()

        conn.close()

        # Check Password Hash
        if user and bcrypt.check_password_hash(user[2], password):

            session["user"] = username

            return redirect("/dashboard")

        else:

            message = "Invalid Username or Password"

    return render_template_string(
        HTML,
        title="Login",
        button="Login",
        message=message,
        page="login"
    )

# -----------------------------------------
# DASHBOARD
# -----------------------------------------

@app.route("/dashboard")
def dashboard():

    if "user" in session:

        return f'''

        <h1>
        Welcome, {session["user"]}
        </h1>

        <br>

        <a href="/logout">
        Logout
        </a>

        '''

    return redirect("/login")

# -----------------------------------------
# LOGOUT
# -----------------------------------------

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect("/login")

# -----------------------------------------
# RUN APP
# -----------------------------------------

if __name__ == "__main__":

    app.run(debug=True)