from flask import Flask,jsonify,render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import json
import http.client
import os

app = Flask(__name__)
mysql = MySQL(cursorclass=DictCursor)

#Can type the values here or obtain them by setting them as environment variables. The latter is done for security purposes
#app.config['MYSQL_DATABASE_USER'] = 'username'
#app.config['MYSQL_DATABASE_PASSWORD'] = 'password'

app.config['MYSQL_DATABASE_USER'] = os.environ['MYSQL_USERNAME']
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ['MYSQL_PASSWORD']
app.config['MYSQL_DATABASE_DB'] = 'footballproject'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)

#Obtaining key to access api from a text file stored in the project root. Can also directly input it as text in the headers of the api connection request
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT_DIR, 'api_key.txt')) as f:
    API_KEY = f.read().strip()
conn = mysql.connect()
cursor=conn.cursor()
apiconn=http.client.HTTPSConnection("v3.football.api-sports.io")
headers={'x-rapidapi-host':"v3.football.api-sports.io",'x-rapidapi-key':API_KEY}

apiconn.request("GET","/fixtures?league=39&team=33&last=10",headers=headers)
cursor.execute('SELECT * FROM TEST;')
l=list(cursor)
print(l)
res = apiconn.getresponse()
data = res.read()

print(data.decode("utf-8"))

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