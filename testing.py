from flask import Flask,jsonify,render_template,redirect,url_for,request,make_response
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import json
import http.client
import os
import datetime
import time

def update_fixtures(teamid):
    apiconn.request("GET","/fixtures?team="+str(teamid)+"&last=5",headers=headers)
    result1 = apiconn.getresponse()
    data1 = result1.read()
    apiconn.request("GET","/fixtures?team="+str(teamid)+"&next=5",headers=headers)
    result2 = apiconn.getresponse()
    data2 = result2.read()
    matchdata = json.loads(data1.decode("utf-8"))['response'] + json.loads(data2.decode("utf-8"))['response']
    sqlinsertdata =[]
    #print(matchdata)
    for row in matchdata:
        templist=[]
        templist.append(row['fixture']['id'])
        templist.append(row['fixture']['date'])
        templist.append(row['fixture']['timestamp'])
        templist.append(teamid)
        templist.append(row['teams']['home']['id'])
        templist.append(row['teams']['home']['name'])
        templist.append(row['teams']['away']['id'])
        templist.append(row['teams']['away']['name'])
        templist.append(row['goals']['home'])
        templist.append(row['goals']['away'])
        templist.append(row['fixture']['status']['short'])
        templist.append(row['teams']['home']['winner'])
        temptuple=tuple(templist)
        sqlinsertdata.append(temptuple)
    
    sqlcmd="INSERT INTO fixtures_test VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.executemany(sqlcmd,sqlinsertdata)
    conn.commit()

def get_fixtures(idparam):
    global finishedmatches,upcomingmatches
    cursor.execute('SELECT * FROM fixtures_test WHERE matchdate<%s AND teamid=%s ORDER BY timestamp DESC;',(date,idparam))
    finishedmatches=list(cursor)
    cursor.execute('SELECT * FROM fixtures_test WHERE matchdate>%s AND teamid=%s ORDER BY timestamp;',(date,idparam))
    upcomingmatches=list(cursor)
    
    for row in finishedmatches:
        temp=row['timestamp']
        tempdate = datetime.datetime.strptime(time.ctime(temp), "%a %b %d %H:%M:%S %Y")
        row['day']=tempdate.strftime('%a %d %b')
        row['time']=tempdate.strftime('%H:%M')
    
    for row in upcomingmatches:
        temp=row['timestamp']
        tempdate = datetime.datetime.strptime(time.ctime(temp), "%a %b %d %H:%M:%S %Y")
        row['day']=tempdate.strftime('%a %d %b')
        row['time']=tempdate.strftime('%H:%M')
    
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

date=datetime.date.today()
teamlist=[]
currentteam=-1
with open(os.path.join(ROOT_DIR,'fixtures_data.json'),'r+') as f:
    data=json.load(f)
    teamlist=data['teams']
    if data['lastUpdated']!=str(date):
        cursor.execute('DELETE FROM fixtures_test')
        conn.commit()
        for team in teamlist:
            teamid=team['id']
            update_fixtures(teamid)
        data['lastUpdated']=str(date)
        f.seek(0)
        json.dump(data,f)
        f.truncate()
currentteam=teamlist[0]['id']
finishedmatches=[]
upcomingmatches=[]
get_fixtures(currentteam)

#Get data of all available teams
cursor.execute('SELECT * FROM teams;')
allteams=list(cursor)

@app.route('/')
def hello_world():
    return redirect(url_for('upcoming_page'))

@app.route('/completed')
def completed_page():
    global currentteam
    tempid=request.args.get('teamid')
    if tempid is not None and tempid != currentteam:
        get_fixtures(tempid)
        currentteam=tempid
    return render_template('test.html',fixtures = finishedmatches,teams=teamlist)

@app.route('/ongoing')
def ongoing_page():
    return 'Hello world'

@app.route('/upcoming')
def upcoming_page():
    global currentteam
    tempid=request.args.get('teamid')
    if tempid is not None and tempid != currentteam:
        get_fixtures(tempid)
        currentteam=tempid
    return render_template('test.html',fixtures = upcomingmatches,teams=teamlist)
    
@app.route('/edit_teams')
def edit_teams_page():
    newteamlist = request.get_json()
    return render_template('edit_teams.html',allteams=json.dumps(allteams),teams=json.dumps(teamlist))
    
@app.route('/edit_teams/make_changes', methods=['POST'])
def make_changes():
    req = request.get_json()
    print(req)
    with open(os.path.join(ROOT_DIR,'fixtures_data.json'),'r+') as f:
        data=json.load(f)
        data['teams']=req
        f.seek(0)
        json.dump(data,f)
        f.truncate()
    res = make_response(jsonify({"message": "OK"}), 200)
    teamlist=req
    redirect(url_for('upcoming_page'))

@app.errorhandler(404)
def not_found(e):
    return render_template('pagenotfound.html')
    
if __name__=='__main__':
    app.debug=True
    app.run()