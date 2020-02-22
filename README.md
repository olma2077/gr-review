CS50W first project using Pyton, Flask, PostgreSQL@Heroku and integration with GoodReads API to fetch review counts. No ORM used for this project as prescribed by task.

Trivial review site with books' sample DB.

User is able to:
* Register.
* Log in/log out.
* Search boks by (partial) ISBN, author or title.
* View book page with basic information including review counts and average review from GoodReads.
* Check rating and reviews, posted by __local__ users.
* Post own rating and review (one per book).

Public API at /api/<isbn> is also available to fetch some book data.

Hosted on https://gr-review.herokuapp.com/