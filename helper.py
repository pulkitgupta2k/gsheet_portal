from bs4 import BeautifulSoup
from flask import Flask, flash, redirect, render_template, request, session, abort
import os

app = Flask(__name__)

@app.route('/')
def index():
    if not session.get('logged_in'):
        return render_template("login.html")
    else:
        return render_template("index.html", **locals())

@app.route('/login', methods=["POST"])
def login():
    print(request.form)
    if request.form['password'] == 'pass' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('Wrong Password!')
    return index()

def driver(host, port):
    app.secret_key = os.urandom(12)
    app.run(debug = 'true', host = host, port = port)