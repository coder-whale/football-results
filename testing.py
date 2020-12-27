from flask import Flask,jsonify,render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import json

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'footballproject'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor=conn.cursor()

cursor.execute('SELECT * FROM TEST;')
l=list(cursor)
print(l)

@app.route('/')
def hello_world():
    return 'Hello'

@app.route('/completed')
def completed_page():
    return render_template('test.html',result = l)

@app.route('/ongoing')
def ongoing_page():
    return 'Hello world'

@app.route('/upcoming')
def upcoming_page():
    return 'Upcoming matches'

if __name__=='__main__':
    app.run()