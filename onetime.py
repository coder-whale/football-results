from flask import Flask,jsonify,render_template
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import json
import http.client
import os
import datetime

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

apiconn.request("GET","/fixtures?league=39&team=33&last=5",headers=headers)
result1 = apiconn.getresponse()
data1 = result1.read()
apiconn.request("GET","/fixtures?league=39&team=33&next=5",headers=headers)
result2 = apiconn.getresponse()
data2 = result2.read()

matchdata = json.loads(data1.decode("utf-8"))['response'] + json.loads(data2.decode("utf-8"))['response']

sqlinsertdata =[]
for row in matchdata:
    templist=[]
    templist.append(row['fixture']['id'])
    templist.append(row['fixture']['date'][:10])
    templist.append(33)
    templist.append(row['teams']['home']['name'])
    templist.append(row['teams']['away']['name'])
    templist.append(row['fixture']['status']['short'])
    templist.append(row['teams']['home']['winner'])
    temptuple=tuple(templist)
    print(temptuple)
    sqlinsertdata.append(temptuple)

sqlcmd="INSERT INTO fixtures_test VALUES(%s,%s,%s,%s,%s,%s,%s)"
cursor.executemany(sqlcmd,sqlinsertdata)
conn.commit()

if __name__=='__main__':
    app.run()