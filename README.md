# football-results

## Introduction

This is a small project to get the results of fixtures of selected football teams for a specific number of matches. It displays the completed, upcoming and live ongoing results of matches associated with the selected teams.  
  
The [Flask](https://flask.palletsprojects.com/en/1.1.x/) web framework is used here for running the web application which has been coded with Python and designed with HTML, CSS and JavaScript.

## Requirements

MySQL Database - For storing the info of fixtures and teams  
Required python libraries can be installed by running the following command in cmd from the project folder:

```
$ pip install -r requirements.txt
```

## Details

This project uses the API provided by [API-Football](https://www.api-football.com/) to obtain all data related to team and fixture information. The documentation for the latest version of the API can be found [here](https://www.api-football.com/documentation-v3).  
  
The required information is stored in SQL tables as needed in a database named **footballproject**. The **CREATE TABLE** statements for the two tables belonging to the database are given below:

**'fixtures'** table is used for storing info related to each fixture
```
CREATE TABLE `fixtures` (
   `id` int NOT NULL AUTO_INCREMENT,
   `fixtureid` int DEFAULT NULL,
   `matchdate` varchar(45) DEFAULT NULL,
   `timestamp` int DEFAULT NULL,
   `teamid` int NOT NULL,
   `homeid` int DEFAULT NULL,
   `hometeam` varchar(45) DEFAULT NULL,
   `awayid` int DEFAULT NULL,
   `awayteam` varchar(45) DEFAULT NULL,
   `hometeamgoals` int DEFAULT NULL,
   `awayteamgoals` int DEFAULT NULL,
   `status` varchar(10) DEFAULT NULL,
   `result` varchar(10) DEFAULT NULL,
   `minutes` int DEFAULT NULL,
   `pengoalshome` int DEFAULT '0',
   `pengoalsaway` int DEFAULT '0',
   PRIMARY KEY (`id`),
   UNIQUE KEY `id_UNIQUE` (`id`)
 ) ENGINE=InnoDB AUTO_INCREMENT=806 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```

**'teams'** table is used for storing team names and their associated IDs

```
CREATE TABLE `teams` (
   `id` int NOT NULL AUTO_INCREMENT,
   `teamid` int DEFAULT NULL,
   `teamname` varchar(45) DEFAULT NULL,
   `present` int DEFAULT '0',
   PRIMARY KEY (`id`),
   UNIQUE KEY `id_UNIQUE` (`id`),
   UNIQUE KEY `teamid_UNIQUE` (`teamid`)
 ) ENGINE=InnoDB AUTO_INCREMENT=3247 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
```
## Files to run

**fixtures.py** is the main Python file that initializes the web app.
**onetime.py** is the file to be run whenever the user needs to add more leagues/teams from the country to be added to the database. 

**Note:** Keep in mind the daily limit of calls imposed by the API depending on the package chosen. This project was tested with the free version of the API which allowed upto 100 calls per day. 
