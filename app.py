from flask import Flask, g, render_template, jsonify, request
import sqlite3
import os

DATABASE = "./restaurant.db"

# Create app
app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'super-secret'

# check if the database exist, if not create the table and insert a few lines of data
if not os.path.exists(DATABASE):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute("""CREATE TABLE `menu` (
        `menu_ID` text(5) PRIMARY KEY,
        `menu_Name` text(50) NOT NULL,
        `menu_Type` number(2) NOT NULL,
        `menu_price` number(4)
        );
    """)
    # conn.commit()
    cur.execute(
        "INSERT INTO menu VALUES('m0001', 'ข้าวผัดอเมริกัน', '1', '70');")
    cur.execute("INSERT INTO menu VALUES('m0002', 'ไอศกรีม', '2' , '50');")
    cur.execute("INSERT INTO menu VALUES('m0003', 'ข้าวผัดปู', '1', '80');")
    cur.execute(
        "INSERT INTO menu VALUES('m0004', 'ผัดมักกะโรนีกุ้ง', '1', '100');")
    cur.execute("INSERT INTO menu VALUES('m0005', 'ปอเปี๊ยะสด', '3', '60');")
    cur.execute("INSERT INTO menu VALUES('m0006', 'ปอเปี๊ยะทอด', '3', '60');")
    cur.execute("INSERT INTO menu VALUES('m0007', 'ขนมกล้วย', '2', '30');")
    conn.commit()
    conn.close()


# helper method to get the database since calls are per thread,
# and everything function is a new thread when called
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert_db(query, args=()):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    conn.close()
    return True


def update_db(query, args=()):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute(query, args)
    conn.commit()
    conn.close()
    return True


# helper to close
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# api


def get_by_id(menu_id):
    res = query_db("select * from menu where menu_ID =?",
                   [menu_id], one=True)
    return res


# view
@app.route("/")
def index():
    cur = get_db().cursor()
    res = cur.execute("select * from menu")
    return render_template("index.html", menu=res, pagename="หน้าหลักโปรแกรม")


@app.route("/adds", methods=['GET', 'POST'])
def add():
    res = []
    if request.method == 'GET':

        return render_template("add.html", menu=res, pagename="เพิ่มรายการอาหาร")
    elif request.method == 'POST':
        r = request.json
        res = get_by_id(r['menu_ID'])
        if res is not None:
            return jsonify({'error': 'รหัสเมนู ถูกใช้ไปแล้ว'})
        insert_db("INSERT INTO menu VALUES(?,?,?,?);", [
            r['menu_ID'], r['menu_Name'], r['menu_Type'], r['menu_price']])
        return jsonify({'status': 'ok'})


@app.route("/search", methods=['GET', 'POST'])
def search():
    res = []
    if request.method == 'GET':
        cur = get_db().cursor()
        res = cur.execute("select * from menu")
        return render_template("search.html", menu=res, pagename="ค้นหาข้อมูล")
    elif request.method == 'POST':
        r = request.json
        if r.get('menu_ID'):
            print('ID')
            res = query_db(
                "select * from menu where menu_ID =?", [r['menu_ID']])
        elif r.get('menu_Name'):
            print('NAME')
            res = query_db(
                "select * from menu where menu_Name LIKE ?", ["%" + r['menu_Name'] + "%"])
        else:
            res = query_db("select * from menu")
        return jsonify({'status': 'ok', 'menu': res})


@app.route("/edit", methods=['GET', 'POST'])
def edit():
    res = []
    if request.method == 'GET':
        cur = get_db().cursor()
        res = cur.execute("select * from menu")
        return render_template("edit.html", menu=res, pagename="แก้ไขข้อมูล")
    elif request.method == 'POST':
        r = request.json
        if r.get('action') == 'query':
            print(r['menu_query_ID'])
            res = get_by_id(r['menu_query_ID'])
            if res is not None:
                return jsonify({'status': 'ok', 'menu': res})
            else:
                return jsonify({'error': 'ไม่พบข้อมูล'})
        elif r.get('action') == 'edit':
            update_db('UPDATE menu SET menu_Name= ?, menu_Type= ?, menu_price= ? WHERE menu_ID = ?', [
                      r['menu_Name'], r['menu_Type'], r['menu_price'], r['menu_ID']])
            return jsonify({'status': 'ok'})


@app.route("/delete", methods=['GET', 'POST'])
def delete():
    res = []
    if request.method == 'GET':
        cur = get_db().cursor()
        res = cur.execute("select * from menu")
        return render_template("delete.html", menu=res, pagename="ลบข้อมูล")
    elif request.method == 'POST':
        r = request.json
        if r.get('action') == 'delete':
            update_db('DELETE from menu WHERE menu_ID = ?', [r['menu_ID']])
            return jsonify({'status': 'ok'})


if __name__ == "__main__":
    app.run()
