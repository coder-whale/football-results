from flask import Flask
from flask import jsonify
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'root'
app.config['MYSQL_DATABASE_DB'] = 'footballproject'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

conn = mysql.connect()
cursor=conn.cursor()

cursor.execute('SELECT * FROM TEST;')
data = cursor.fetchall()

@app.route('/')
def hello_world():
    return jsonify(data)

@app.route('/completed')
def completed_page():
    return 'Completed matches'

@app.route('/ongoing')
def ongoing_page():
    return 'Hello world'

@app.route('/upcoming')
def upcoming_page():
    return 'Upcoming matches'

if __name__=='__main__':
    app.run()