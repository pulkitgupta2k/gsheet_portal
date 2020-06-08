from bs4 import BeautifulSoup
from flask import Flask, flash, redirect, render_template, request, session, abort, send_file
import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import csv
import shutil
from creds import username, password

app = Flask(__name__)

def get_gsheets():
    scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
    ]
    file_name = 'client_key.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    client = gspread.authorize(creds)
    spreadsheets = client.openall()
    for i, spreadsheet in enumerate(spreadsheets):
        spreadsheets[i] = spreadsheet.title
    return spreadsheets

def download_gsheet(sheet):
    scope = [
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/drive.file'
    ]
    file_name = 'client_key.json'
    creds = ServiceAccountCredentials.from_json_keyfile_name(file_name,scope)
    client = gspread.authorize(creds)
    try:
        os.makedirs('downloads/{}'.format(sheet))
    except:
        shutil.rmtree('downloads/{}'.format(sheet))
        os.makedirs('downloads/{}'.format(sheet))
    print(sheet)
    spreadsheet = client.open(sheet)
    for worksheet in spreadsheet.worksheets():
        try:
            export_data = worksheet.get_all_values()
            with open("downloads/{}/{}.csv".format(sheet, worksheet.title), "w", encoding='utf8' , newline="") as f:
                writer = csv.writer(f) 
                writer.writerows(export_data)
        except Exception as e:
            print(e)
            pass
    shutil.make_archive("zips/{}".format(sheet), 'zip', 'downloads/{}'.format(sheet))


@app.route('/',)
def index():
    if not session.get('logged_in'):
        return render_template("login.html")
    else:
        sheets = get_gsheets()
        return render_template("index.html", sheets=sheets)

@app.route('/login', methods=["POST"])
def login():
    if request.form['password'] == password and request.form['username'] == username:
        session['logged_in'] = True
    else:
        flash('Wrong Password!')
    return index()

@app.route('/download', methods=["GET","POST"])
def gsheet():
    if not session.get('logged_in'):
        return render_template("login.html")
    else:
        name = []
        selected_sheets = request.form
        for selected_sheet in selected_sheets.values():
            try:
                download_gsheet(selected_sheet)
                name.append(selected_sheet)
            except Exception as e:
                print(e)
        return render_template("download.html", selected_sheets = name)

@app.route('/return-file/')
def downloadFile():
    if not session.get('logged_in'):
        return render_template("login.html")
    else:
        filename = request.query_string.decode("utf-8")
        path = "zips/{}.zip".format(filename)
        return send_file(path, as_attachment=True)

def driver(host, port):
    app.secret_key = os.urandom(12)
    app.run(debug = 'true', host = host, port = port)