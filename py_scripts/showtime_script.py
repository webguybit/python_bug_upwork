import pymysql
import csv
from datetime import datetime
import os

def formatDate(date):
    tempDate = date.split('/')
    return tempDate[2]+'-'+tempDate[1]+'-'+tempDate[0]


def formatTime(time):
    tempTime = time.split(' ')
    if(len(tempTime)>1):
        type = tempTime[1]
        hours = tempTime[0].split(':')[0]
        minutes = tempTime[0].split(':')[1]
        if(type == 'AM'):
            return hours+':'+minutes+':00'
        elif(type == 'PM'):
            if(hours == '12'):
                return hours+':'+minutes+':00'
            else:
                hours = str(int(hours)+12)
                return hours+':'+minutes+':00'
    return time


def idTheatre(name):
    sql = 'SELECT * FROM `theatre` WHERE `Movie_Company_Location` LIKE %s'
    cur.execute(sql, (f"%{name}%"))
    return cur.fetchall()


def getConnection(sql, fields):
    if (os.name != 'posix'):
        connection = pymysql.connect(
            host="localhost",  # your host
            user="root",  # username
            passwd="iu00q71o",  # password
            db="2sw53e15l",  # name of the database
            connect_timeout=20,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )
    else:
        connection = pymysql.connect(
            host="db-2sw53e15l.aliwebs.com",
            user="2sw53e15l",
            passwd="Cine_7534",
            db="2sw53e15l",
            connect_timeout=20,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor
        )

    if 'INSERT' in sql or 'UPDATE' in sql or 'DELETE' in sql:
        id = 0
        try:
            with connection.cursor() as cursor:
                print(sql,fields)
                cursor.execute(sql, fields)
                id = cursor.lastrowid
            connection.commit()
            return id
        except Exception as err:
            print(f"Error.: {err}")
        finally:
            connection.close()
    else:
        try:
            with connection.cursor() as cursor:
                # print(sql,fields)
                cursor.execute(sql, fields)
                return cursor.fetchall()
        finally:
            connection.close()

if (os.name != 'posix'):
    db = pymysql.connect(host="localhost",  # your host
                         user="root",  # username
                         passwd="iu00q71o",  # password
                         db="2sw53e15l")  # name of the database
else:
    db = pymysql.connect(host="db-2sw53e15l.aliwebs.com",  # your host
                         user="2sw53e15l",  # username
                         passwd="Cine_7534",  # password
                         db="2sw53e15l")  # name of the database

cur = db.cursor()
cur.execute("TRUNCATE TABLE missing_data_showtime")

with open('movie_data.csv') as csvfile:
    readCSV = csv.reader(csvfile, delimiter=',')
    for row in readCSV:
        movieName = u'{}'.format(row[0])
        theatreName = '{}'.format(row[1])
        date = row[3]
        time = row[4]
        datahour = u'{} {}'.format(formatDate(date),formatTime(time))
        link = '{}'.format(row[5])
        sql = 'SELECT * FROM bridging_moviename WHERE `Theatre_Movie_Name` = %s'
        # sql = 'SELECT * FROM `movies` WHERE Movie_name=%s'
        cur.execute(sql, (movieName))
        fetch = cur.fetchall()
        # if len(fetch)>0 and fetch[0][2] != None:
        if len(fetch)>0 and fetch[0][0] != None:
            movieId = str(fetch[0][2])
        else:
            sqlmissing = 'INSERT INTO `missing_data_showtime` \
                (`movie_name`, `theatre_name`, `cine_type`, `start_at`, `movie_Url`, `language` )' \
                 ' VALUES (%s,%s,"Dolby",%s,%s,"");'
            cur.execute(sqlmissing, (movieName,theatreName,datahour,link))
            # Save in table movie
            # sqlmovie = 'INSERT INTO `movies`(`Movie_name`) VALUES (%s)'
            # fields = []
            # fields.append(row[0])
            # movieId = getConnection(sqlmovie, fields)
        # theatreId = '66'
        # theatreId = idTheatre(theatreName)
        print(movieName)
        print(theatreName)
        #print time,formatTime(time)
        # exit(0)
        print(f'SELECT * FROM theatre WHERE Theatre_name={theatreName}')
        # cur.execute('SELECT * FROM theatre WHERE Movie_Company_Location="' + theatreName + '"')
        sql = 'SELECT * FROM theatre WHERE Movie_Company_Location=%s'
        cur.execute(sql, (theatreName))
        fetch = cur.fetchall()
        if (len(fetch) > 0):
            theatreId = str(fetch[0][0])
        else:
            # print 'Unknown theatreName - %s'%theatreName
            # cur.execute('INSERT INTO missing_data_showtime(`movie_name`,`theatre_name`,`cine_type`,`start_at`,`movie_Url`,`language`) VALUES ("' + movieName + '","' + theatreName + '","Dolby","' + formatDate(date) + ' ' + formatTime(time) + '","' + link + '","");')
            sqlmissing = 'INSERT INTO `missing_data_showtime` ( \
                `movie_name`, `theatre_name`, `cine_type`, \
                `start_at`, `movie_Url`, `language` \
                ) VALUES (%s,%s,"Dolby",%s,%s,"");'
            cur.execute(sqlmissing, (movieName,theatreName,datahour,link))
            # print('INSERT INTO missing_data_showtime ('
            #       '`movie_name`,`theatre_name`,`cine_type`, `start_at`,'
            #       '`movie_Url`,`language`) '
            #       'VALUES ('
            #       '"' + movieName + '",'
            #       '"' + theatreName + '",'
            #       '"Dolby",'
            #       '"' + formatDate(date) + ''
            #       '' + formatTime(time) + '","' + link + '","");')
            # continue
        # print("INSERT INTO showtime "
        #       "(`movie_id`,`theatre_id`,`cine_type`, `start_at`,`Movie_Url`,"
        #       "`language`, `subtitle_language`,`Total_Seats`,`Available_Seats`) "
        #       "VALUES (" + movieId + "," + theatreId + ","
        #       "'Dolby', '" + formatDate(date) + " " + formatTime(time) + "','" + link + "','','',0,0);")
        if link.count('carnival'):
            # print theatreId, movieId
            sql = 'SELECT * FROM showtime WHERE \
                start_at=%s AND Movie_Url=%s AND theatre_id=%s'
            cur.execute(sql, (datahour,link,theatreId))
        else:
            # cur.execute('SELECT * FROM showtime WHERE Movie_Url="' + link + '"')
            sql = 'SELECT * FROM showtime WHERE Movie_Url=%s'
            cur.execute(sql,(link))
        fetch = cur.fetchall()
        if(len(fetch)>0):
            print('this is already yet')
        else:
            # sqlExists ='SELECT s.movie_id, s.theatre_id, s.start_at, s.Movie_Url FROM showtime AS s ' \
            #            'WHERE EXISTS ' \
            #            '(SELECT d.movie_id, d.theatre_id, d.start_at, d.Movie_Url FROM showtime AS d ' \
            #            'WHERE d.Movie_Url = %s ' \
            #            'AND d.theatre_id = %s ' \
            #            'AND  d.start_at = %s)LIMIT 1'
            # resul = cur.execute(sqlExists, (link, theatreId, datahour))
            sqlExists ='SELECT s.movie_id, s.theatre_id, s.start_at, s.Movie_Url FROM showtime AS s ' \
                       'WHERE EXISTS ' \
                       '(SELECT d.movie_id, d.theatre_id, d.start_at, d.Movie_Url FROM showtime AS d ' \
                       'WHERE d.Movie_Url = %s ' \
                       'AND d.theatre_id = %s ' \
                       'AND  d.start_at = %s)LIMIT 1'
            resul = cur.execute(sqlExists, (link, theatreId, datahour))            
            print(f"Movie exists? {resul}")
            if resul == 0:
                sqlmovie = "INSERT INTO `showtime` \
                    (`movie_id`,`theatre_id`,`start_at`,`Movie_Url`) " \
                      "VALUES ( %s,%s,%s,%s)"
                fields = [movieId, theatreId, datahour, link]
                salveId = getConnection(sqlmovie, fields)
    db.commit()

print("##########################################")
print("Script ends")
print("##########################################")
