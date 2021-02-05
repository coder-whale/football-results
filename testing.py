from flask import Flask,jsonify,render_template,redirect,url_for,request,make_response
from flaskext.mysql import MySQL
from pymysql.cursors import DictCursor
import json
import http.client
import os
import datetime
import time

def update_fixtures(teamid):
    apiconn.request("GET","/fixtures?team="+str(teamid)+"&last=6",headers=headers)
    result1 = apiconn.getresponse()
    data1 = result1.read()
    apiconn.request("GET","/fixtures?team="+str(teamid)+"&next=5",headers=headers)
    result2 = apiconn.getresponse()
    data2 = result2.read()
    matchdata = json.loads(data1.decode("utf-8"))['response'] + json.loads(data2.decode("utf-8"))['response']
    sqlinsertdata =[]
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
        templist.append(row['score']['penalty']['home'])
        templist.append(row['score']['penalty']['away'])
        temptuple=tuple(templist)
        sqlinsertdata.append(temptuple)
    
    sqlcmd="INSERT INTO fixtures(fixtureid,matchdate,timestamp,teamid,homeid,hometeam,awayid,awayteam,hometeamgoals,awayteamgoals,status,result,pengoalshome,pengoalsaway) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.executemany(sqlcmd,sqlinsertdata)
    conn.commit()

curctime=time.ctime()
def update_time():
    global curctime
    curctime=time.time()

def get_fixtures(idparam):
    update_time()
    global finishedmatches,upcomingmatches
    cursor.execute('SELECT * FROM fixtures WHERE timestamp<%s AND teamid=%s AND status IN (\'FT\',\'AET\',\'PEN\') ORDER BY timestamp DESC limit 5;',(curctime,idparam))
    finishedmatches=list(cursor)
    cursor.execute('SELECT * FROM fixtures WHERE timestamp>%s AND teamid=%s ORDER BY timestamp;',(curctime,idparam))
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
    live_fixtures()
    
def live_fixtures():
    update_time()
    global ongoingmatches
    cursor.execute('SELECT fixtureid FROM fixtures WHERE %s-timestamp<10800 AND %s-timestamp>0 AND status NOT IN (\'FT\',\'AET\',\'PEN\') ;',(curctime,curctime))
    ongoingids=list(cursor)
    ongoingset=set([d['fixtureid'] for d in ongoingids])
    if(len(ongoingset)>0):
        apiconn.request("GET","/fixtures?live=all",headers=headers)
        result3 = apiconn.getresponse()
        data3 = result3.read()
        matchdata3 = json.loads(data3.decode("utf-8"))['response']
        for row in matchdata3:
            if(row['fixture']['id'] in ongoingset):
                goalshome=row['goals']['home']
                goalsaway=row['goals']['away']
                minutes=row['fixture']['status']['elapsed']
                status=row['fixture']['status']['short']
                penhome=row['score']['penalty']['home']
                penaway=row['score']['penalty']['away']
                cursor.execute("UPDATE fixtures SET hometeamgoals=%s,awayteamgoals=%s,minutes=%s,status=%s,pengoalshome=%s,pengoalsaway=%s where fixtureid=%s;",(goalshome,goalsaway,minutes,status,penhome,penaway,row['fixture']['id']))
                conn.commit()
                ongoingset.remove(row['fixture']['id'])
        for s in ongoingset:
            apiconn.request("GET","/fixtures?id="+str(s),headers=headers)
            resultfin = apiconn.getresponse()
            datafin = resultfin.read()
            matchdatafin = json.loads(datafin.decode("utf-8"))['response']
            for row in matchdatafin:
                goalshome=row['goals']['home']
                goalsaway=row['goals']['away']
                status=row['fixture']['status']['short']
                penhome=row['score']['penalty']['home']
                penaway=row['score']['penalty']['away']
                cursor.execute("UPDATE fixtures SET hometeamgoals=%s,awayteamgoals=%s,status=%s where fixtureid=%s;",(goalshome,goalsaway,status,penhome,penaway,row['fixture']['id']))
                conn.commit()
    cursor.execute('SELECT * FROM fixtures WHERE %s-timestamp<10800 AND %s-timestamp>0 AND status NOT IN (\'FT\',\'AET\',\'PEN\') ;',(curctime,curctime))
    ongoingmatches=list(cursor)       
    
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
teamids=[]
currentteam=-1
with open(os.path.join(ROOT_DIR,'fixtures_data.json'),'r+') as f:
    data=json.load(f)
    teamlist=data['teams']
    teamids=data['ids']
    if data['lastUpdated']!=str(date):
        cursor.execute('DELETE FROM fixtures')
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
    live_fixtures()
    return render_template('ongoing.html',fixtures = ongoingmatches,teams=teamlist)

@app.route('/upcoming')
def upcoming_page():
    global currentteam
    tempid=request.args.get('teamid')
    if tempid is not None and tempid != currentteam:
        if str(tempid) in teamids:
            get_fixtures(tempid)
            currentteam=tempid
        else:
            currentteam=teamlist[0]['id']
            get_fixtures(currentteam)
    if tempid is None:
        if str(currentteam) not in teamids:
            currentteam=teamlist[0]['id']
            get_fixtures(currentteam)
    return render_template('test.html',fixtures = upcomingmatches,teams=teamlist)
    
@app.route('/edit_teams')
def edit_teams_page():
    return render_template('edit_teams.html',allteams=json.dumps(allteams),teams=json.dumps(teamlist))
    
@app.route('/edit_teams/make_changes', methods=['POST'])
def make_changes():
    global teamlist,teamids
    req = request.get_json()
    res = make_response(jsonify({"message": "OK"}), 200)
    for tempteam in teamlist:
        if tempteam not in req:
            cursor.execute("DELETE FROM fixtures WHERE teamid=%s;",(tempteam['id']))
            conn.commit()
    teamlist=req
    with open(os.path.join(ROOT_DIR,'fixtures_data.json'),'r+') as f:
        data=json.load(f)
        data['teams']=req
        teamids=data['ids']
        data['ids']=[]
        for team in teamlist:
            data['ids'].append(team['id'])
            if str(team['id']) not in teamids:
                update_fixtures(team['id'])
        f.seek(0)
        teamids=data['ids']
        json.dump(data,f)
        f.truncate()
    return res

@app.errorhandler(404)
def not_found(e):
    return render_template('pagenotfound.html')
    
if __name__=='__main__':
    app.debug=True
    app.run()