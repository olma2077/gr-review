import os
import hashlib
import goodreads

from flask import Flask, session, render_template, request, jsonify
from flask_session.__init__ import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
if not os.getenv("GR_KEY"):
    raise RuntimeError("GR_KEY is not set")

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
        return render_template("search.html",
                               user=session['user'])


@app.route("/login", methods=["POST"])
def login():
    login = request.form.get("login")

    try:
        key, salt = db.execute("SELECT password, salt"
                               "FROM users"
                               "WHERE name = :name",
                               {"name": login}).fetchone()
    except TypeError:
        return render_template("error.html",
                               error="Login or password are incorrect!")

    password = request.form.get("password")
    if hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                           bytes.fromhex(salt), 100000) == bytes.fromhex(key):
        session['user'] = login
        session['user_id'] = db.execute("SELECT id"
                                        "FROM users"
                                        "WHERE name = :name",
                                        {"name": login}).fetchone().id
        return render_template("search.html",
                               user=session['user'])
    else:
        return render_template("error.html",
                               error="Login or password are incorrect!")


@app.route("/register", methods=["POST"])
def register():
    login = request.form.get("login")

    if db.execute("SELECT FROM users"
                  "WHERE name = :name",
                  {"name": login}).rowcount == 0:
        password = request.form.get("password")
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'),
                                  salt, 100000)
        db.execute("INSERT INTO users (name, password, salt)"
                   "VALUES (:name, :password, :salt)",
                   {"name": login, "password": key.hex(), "salt": salt.hex()})
        db.commit()
        return render_template("success.html",
                               success="User was successfuly registered!")
    else:
        return render_template("error.html",
                               error="User with such login already exists!")


@app.route("/logout", methods=["POST"])
def logout():
    session.pop('user', None)
    session.pop('user_id', None)
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    isbn = request.form.get("isbn")
    title = request.form.get("title")
    author = request.form.get("author")
    books = db.execute("SELECT * FROM books"
                       "WHERE isbn like :isbn and"
                       "author like :author and"
                       "title like :title",
                       {"isbn": '%'+isbn+'%',
                        "author": '%'+author+'%',
                        "title": '%'+title+'%'}).fetchall()
    return render_template("search.html",
                           user=session['user'], books=books)


@app.route("/book/<book_isbn>")
def book(book_isbn):
    book = db.execute("SELECT * FROM books"
                      "WHERE isbn = :isbn",
                      {"isbn": book_isbn}).fetchone()
    reviews = db.execute("SELECT *"
                         "FROM reviews JOIN users"
                         "on reviews.user_id = users.id"
                         "WHERE reviews.book_id = :id",
                         {"id": book.id}).fetchall()
    gr = goodreads.fetch_review_counts(os.getenv("GR_KEY"), book_isbn)
    return render_template("book.html",
                           user=session['user'], book=book,
                           goodreads=gr, reviews=reviews)


@app.route("/book/<book_id>/review", methods=["POST"])
def review(book_id):
    if db.execute("SELECT * FROM reviews"
                  "WHERE book_id = :book and user_id = :user",
                  {"book": book_id, "user": session['user_id']}).rowcount == 0:
        rating = request.form.get("rating")
        review = request.form.get("review")
        db.execute("INSERT INTO reviews (book_id, user_id, rating, review)"
                   "VALUES (:book_id, :user_id, :rating, :review)",
                   {"book_id": book_id, "user_id": session['user_id'],
                    "rating": rating, "review": review})
        db.commit()
        return render_template("success.html",
                               success="Your review was submitted!")
    else:
        return render_template("error.html",
                               error="You've already reviewed this book!")


@app.route("/api/<isbn>")
def get_book(isbn):
    """ Return details about a book by ISBN """

    book = book = db.execute("SELECT * FROM books"
                             "WHERE isbn = :isbn",
                             {"isbn": isbn}).fetchone()

    if book is None:
        return jsonify({"error": "Book is not found"}), 404

    gr = goodreads.fetch_review_counts(os.getenv("GR_KEY"), isbn)
    return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": isbn,
            "review_count": gr.reviews_count,
            "average_score": gr.average_rating
        })
