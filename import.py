import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL")) # database engine object from SQLAlchemy that manages connections to the database
                                                    # DATABASE_URL is an environment variable that indicates where the database lives
db = scoped_session(sessionmaker(bind=engine))    # create a 'scoped session' that ensures different users' interactions with the
                                                    # database are kept separate
""" if engine.dialect.has_table(engine, 'books'):
    db.execute('DROP TABLE books;')

db.execute('CREATE TABLE books ('
            'id SERIAL PRIMARY KEY, '
            'isbn VARCHAR NOT NULL, '
            'title VARCHAR NOT NULL, '
            'author VARCHAR NOT NULL, '
            'year VARCHAR NOT NULL);')
 """
if engine.dialect.has_table(engine, 'users'):
    db.execute('DROP TABLE users;')

db.execute('CREATE TABLE users ('
            'id SERIAL PRIMARY KEY, '
            'name VARCHAR NOT NULL, '
            'password VARCHAR NOT NULL, '
            'salt VARCHAR NOT NULL);')

""" f = open("books.csv")
reader = csv.reader(f)
next(reader)

for isbn, title, author, year in reader:
     db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
        {"isbn": isbn, "title": title, "author": author, "year": int(year)}) # substitute values from CSV line into SQL command, as per this dict
 """
db.commit()