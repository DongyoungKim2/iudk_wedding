from flask import Flask, render_template, Response, request, redirect, url_for, jsonify

import sqlite3
import datetime
import random
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    if random.randrange(0,2) == 0:
        return render_template('iu.html')
    else:
        return render_template('dk.html')

@app.route('/dk')
def dk():
    return render_template('dk.html')

@app.route('/iu')
def iu():
    return render_template('iu.html')

# get client's ip test
@app.route('/ip', methods=['GET','POST'])
def client_ip():
    cip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    print(cip)
    return cip

# attend db
@app.route('/db_attend', methods=['GET','POST'])
def add_attend():
    # create db connection
    conn = sqlite3.connect("attend.db")
    cur = conn.cursor()

    # get values
    attlsit = cur.execute("SELECT acc_no FROM attend").fetchall()
    current_no = max(attlsit)[0]
    next_no = current_no+1
    next_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    next_date = str(datetime.datetime.today())

    #set to db
    cur.executemany( 'INSERT INTO attend VALUES (?,?,?)', [
        (next_ip, next_date, next_no)
    ] )
    conn.commit()
    conn.close()
    return 'Done'

@app.route('/dbview_book', methods=['GET','POST'])
def dbview_book():
    dbname = "book.db"
    conn = sqlite3.connect(dbname)
    df = pd.read_sql_query("SELECT * FROM attend", conn)
    return df.to_html()

@app.route('/dbview_attend', methods=['GET','POST'])
def dbview_attend():
    dbname = "attend.db"
    conn = sqlite3.connect(dbname)
    df = pd.read_sql_query("SELECT * FROM attend", conn)
    return df.to_html()

# geuestbook db
@app.route('/db_book', methods=['GET','POST'])
def add_book():
    # get data
    data = request.get_json()
    # print(data)
    the_name = data["name"]
    the_phone = data["phone"]
    the_message = data["message"]

    # create db connection
    conn = sqlite3.connect("book.db")
    cur = conn.cursor()

    # get values
    attlsit = cur.execute("SELECT no FROM attend").fetchall()
    current_no = len(attlsit)
    next_no = current_no+1
    next_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
    next_date = str(datetime.datetime.today())
    # set to db
    cur.executemany( 'INSERT INTO attend VALUES (?,?,?,?,?,?)', [
        (next_no, next_ip, next_date, the_name, the_phone, the_message)
    ] )
    conn.commit()
    conn.close()

    # print db
    # print_db("book.db")
    dbdata = get_db("book.db")
    formedata = {}
    for i in range(5):
        try:
            formedata["name%d"%(i+1)] = dbdata[i][3]
            formedata["text%d"%(i+1)] = dbdata[i][5]
        except:
            formedata["name%d"%(i+1)] = ""
            formedata["text%d"%(i+1)] = ""

    return jsonify(result = "success", data = formedata)

def print_db(dbname):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute("SELECT * FROM attend")
    rows = cur.fetchall()
    for row in rows: 
        print(row)

def get_db(dbname, thelist=5):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute("SELECT * FROM attend")
    rows = cur.fetchall()
    if len(rows) < thelist:
        return rows[::-1]
    else:
        return rows[len(rows)-thelist:][::-1]

# geuestbook db
@app.route('/load_book', methods=['GET','POST'])
def load_book():
    # print_db("book.db")
    dbdata = get_db("book.db")
    formedata = {}
    for i in range(5):
        try:
            formedata["name%d"%(i+1)] = dbdata[i][3]
            formedata["text%d"%(i+1)] = dbdata[i][5]
        except:
            formedata["name%d"%(i+1)] = ""
            formedata["text%d"%(i+1)] = ""

    return jsonify(result = "success", data = formedata)
    
def get_db(dbname, thelist=5):
    conn = sqlite3.connect(dbname)
    cur = conn.cursor()
    cur.execute("SELECT * FROM attend")
    rows = cur.fetchall()
    if len(rows) < thelist:
        return rows[::-1]
    else:
        return rows[len(rows)-thelist:][::-1]

if __name__ == '__main__':
    # create db
    conn = sqlite3.connect("attend.db")
    cur = conn.cursor()
    conn.execute('CREATE TABLE IF NOT EXISTS attend(ip TEXT, date TEXT, acc_no INTEGER)')

    conn = sqlite3.connect("book.db")
    cur = conn.cursor()
    conn.execute('CREATE TABLE IF NOT EXISTS attend(no INTEGER, ip TEXT, date TEXT, name TEXT, phone TEXT, comment TEXT)')

    # start application
    app.run(host = '0.0.0.0', port = 80, debug = False)