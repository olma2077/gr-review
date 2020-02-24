import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# database engine object from SQLAlchemy manages connections to the database
# DATABASE_URL is an environment variable with path where the database lives
engine = create_engine(os.getenv("DATABASE_URL"))

# create a 'scoped session' that ensures different users' interactions with
# the database are kept separate
db = scoped_session(sessionmaker(bind=engine))

if engine.dialect.has_table(engine, 'books'):
    db.execute('DROP TABLE books;')
db.execute('CREATE TABLE books ('
           'id SERIAL PRIMARY KEY, '
           'isbn VARCHAR NOT NULL, '
           'title VARCHAR NOT NULL, '
           'author VARCHAR NOT NULL, '
           'year VARCHAR NOT NULL);')

if engine.dialect.has_table(engine, 'users'):
    db.execute('DROP TABLE users;')
db.execute('CREATE TABLE users ('
           'id SERIAL PRIMARY KEY, '
           'name VARCHAR NOT NULL, '
           'password VARCHAR NOT NULL, '
           'salt VARCHAR NOT NULL);')

if engine.dialect.has_table(engine, 'reviews'):
    db.execute('DROP TABLE reviews;')
db.execute('CREATE TABLE reviews ('
           'id SERIAL PRIMARY KEY, '
           'user_id INT REFERENCES users(id), '
           'book_id INT REFERENCES books(id), '
           'rating SMALLINT NOT NULL, '
           'review VARCHAR NOT NULL);')

f = open("books.csv")
reader = csv.reader(f)
next(reader)
for isbn, title, author, year in reader:
    db.execute("INSERT INTO books (isbn, title, author, year)"
               "VALUES (:isbn, :title, :author, :year)",
               {"isbn": isbn, "title": title,
                "author": author, "year": int(year)})

db.commit()
