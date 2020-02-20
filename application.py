import os
import hashlib

from flask import Flask, session, render_template, request
from flask_session.__init__ import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    if session.get("user") is None:
        return render_template("index.html")
    else:
        return render_template("search.html", user=session['user'])

@app.route("/login", methods=["POST"])
def login():
    login = request.form.get("login")
    
    try:
        key, salt = db.execute("SELECT password, salt FROM users WHERE name = :name", {"name": login}).fetchone()
    except TypeError:
        return render_template("error.html", error="Login or password are incorrect!")
    
    password = request.form.get("password")
    if hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt), 100000) == bytes.fromhex(key):
        session['user'] = login
        return render_template("search.html", user=session['user'])
    else:
        return render_template("error.html", error="Login or password are incorrect!")

@app.route("/register", methods=["POST"])
def register():
    login = request.form.get("login")
    
    if db.execute("SELECT FROM users WHERE name = :name", {"name": login}).rowcount == 0:
        password = request.form.get("password")
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        db.execute("INSERT INTO users (name, password, salt) VALUES (:name, :password, :salt)",
            {"name": login, "password": key.hex(), "salt": salt.hex()})
        db.commit()
        return render_template("success.html", success="User was successfuly registered!")
    else:
        return render_template("error.html", error="User with such login already exists!")

@app.route("/logout", methods=["POST"])
def logout():
    session.pop('user', None)
    return render_template("index.html")

@app.route("/search", methods=["POST"])
def search():
    pass
