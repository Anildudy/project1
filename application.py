import os
import sys

from flask import Flask, render_template, request
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup")
def reg():
    return render_template("signup.html")

@app.route("/signup/success", methods=["POST"])
def succ():
    username = request.form.get('username')
    if db.execute("SELECT * FROM credentials where username=:username",{"username":username}).rowcount!=0:
        return "Already exist username"
    password = request.form.get('password')
    db.execute("INSERT INTO credentials (username,password) VALUES (:username,:password)",
                {"username":username,"password": password})
    db.commit()
    return render_template("success.html")

@app.route("/homepage", methods=["POST"])
def home():
    username = request.form.get('username')
    password = request.form.get('password')
    if db.execute("SELECT * FROM credentials WHERE username=:username", {"username": username}).rowcount==0:
        return "Invalid username"
    items = db.execute("SELECT * FROM credentials WHERE username = :username",{"username": username}).fetchall()
    for item in items:
        if item.password != password:
            return "Invalid password"
    return render_template("homepage.html")

@app.route("/search", methods=["POST"])
def search():
    q = request.form.get('search')
    q = q + "%q"
    result = db.execute("SELECT * FROM books WHERE id LIKE :q OR isbn LIKE :q OR title LIKE :q OR author LIKE :q OR year LIKE :q",
                {"q": q}).fetchall()
    result_list = []
    for row in result:
        rowList = []
        for i in range(5):
            rowList.append(row[i])
        result_list.append(rowList)

    return render_template("search.html",result=result_list)
