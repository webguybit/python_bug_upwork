import time
# import mysql.connector
import requests
from lxml import html
from queue import Queue
import random
import threading
import json
import datetime
import sdnotify
#from proxy import is_bad_proxy, get_proxies, validate_proxies
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME

def is_bad_proxy(pip, url):
    """ Check a proxy for it's validity """
    try:
        res = requests.get(
            url,
            proxies={'http':pip},
            headers={'User-agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'},
            timeout=10
        )
    except Exception as e:
        return 1
    if res.status_code == 200:
        return 0

    print(res.status_code)
    return 1

def get_proxies():
    """ Return the valid proxies """
    url = 'https://hidemy.name/ru/loginx'
    url1 = 'https://hidemy.name/api/proxylist.txt?out=plain&lang=ru'
    data = {'c':'169496407732367'}
    s = requests.session()
    s.get(url1)
    s.post(url, data=data)
    res = s.get(url1)
    result = res.text.split('\r\n')
    return result

def validate_proxies(proxies, url):
    """ Validate the incoming proxies against the websites """
    proxies_working = []
    random.shuffle(proxies)
    for proxy in proxies:
        bad_proxy = is_bad_proxy(proxy, url)
        if not bad_proxy:
            print(proxy, "APPROVED!")
            proxies_working.append({'http':proxy})
            if len(proxies_working) == 5:
                break
        elif str(bad_proxy)[0] == '5' and not proxies:
            print('This service is now unavailable (site from scraping is unavailable)')
    if not proxies_working:
        return 0
    return proxies_working

class Scraper(threading.Thread):
    """
    A threading example
    """

    def __init__(self,queue,proxies):

        threading.Thread.__init__(self)
        self.queue = queue
        self.proxies = proxies

    def run(self):

        while True:
            try:
                row = self.queue.get()
            except:
                break
            self.check_seats(row)
            self.queue.task_done()

    def check_seats(self,row):

        n = sdnotify.SystemdNotifier()
        n.notify("WATCHDOG=1")
        name = ""
        name = row['Movie_Url'].split('/')[-1]
        #date = row[0]['start_at']
        #print '{:%Y-%m-%d}T00:00:00'.format(date)#date,'-'.join([str(date.year),date.month,date.day])+'T00:00:00'
        #try:
        try:
            date = '{:%Y-%m-%dT%H:%M}:00'.format(1)
        except:
            date = datetime.datetime.today()
        print(row)

        ss = requests.Session()
        resp = ss.get(row['Movie_Url'])
        #except:
        #date = '{:%Y-%m-%d}T00:00:00'.format(date)
        #rdata = row['start_at']
        #date = '-'.join([rdata.year,rdata.month,rdata.day])+'T00:00:00'
        headers = {
            'Accept':'application/json, text/plain, */*',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'en-GB,en;q=0.5',
            'Host':'service.carnivalcinemas.sg',
            'Origin':'https://carnivalcinemas.sg',
            'Referer':'https://carnivalcinemas.sg/',
            'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux) Gecko/20100101 Firefox/60.0',
            'Token':'aHJWREJmK3g1MktjUzF1cEZuUHJvUXlsZFlpL0NMS0NWcnR5SDhzSEhjYz18aHR0cHM6Ly9jYXJuaXZhbGNpbmVtYXMuc2cvIy9LYWxhdmFuaSUyMDIvS2FsYXZhbmklMjAyfDYzNjk4NzA0OTE0NjkzMDAwMHxyejhMdU90RkJYcGhqOVdRZnZGaA=='
        }
        res_sessids = None
        seat_url = 'https://service.carnivalcinemas.sg/api/SeatLayout/GetSeatLayout?cinemaCode={0}&lngSessionId=%20{1}&noOfSeat=1'
        sessid_url = 'https://service.carnivalcinemas.sg/api/QuickSearch/GetCinemaAndShowTimeByMovie?location=Mumbai&movieCode=%s&date=%s'
        for x in range(5):
            try:
                res_sessids = json.loads(ss.get(sessid_url%(name,date),headers=headers,proxies = random.choice(self.proxies),timeout=20).content)['responseCinemaWithShowTime']
                break
            except Exception as e:
                time.sleep(5)
                print(e)
        try:
            total_seats = row['Total_Seats']
        except TypeError:
            return 0,0
        if res_sessids is None:
            return 0,0
        for rsid in res_sessids:
            newsid = None
            if rsid['showTime'].count(','):
                stimes = [x.strip()[:-1] for x in rsid['showTime'].split(',')]
                #print stimes,'{:%I:%M %p}'.format(row[0]['start_at'])
                if '{:%I:%M %p}'.format(row['start_at']) in stimes:
                    newsid =  rsid['longSessionID'].split(',')[stimes.index('{:%I:%M %p}'.format(row['start_at']))].strip()
                    #print sid
            #else:
            sid = rsid['longSessionID']
            if newsid is not None:
                sid =  newsid #,'<-----------'
            code =  rsid['hoCode'][:4]
            #sid = rsid['longSessionID']
            res_seats = None
            for _ in range(5):
                try:
                    res_seats = json.loads(ss.get(seat_url.format(code,sid.strip()),headers=headers,proxies = random.choice(self.proxies),timeout=20).content)['responseSeatLayout']
                    break
                except Exception as e:
                    time.sleep(5)
                    print(e)
            if res_seats is None:
                continue
            #total = len(res_seats)-1
            total_str = ''
            available = len([seat for seat in res_seats[1:] if seat['strSeatStatus'] == '0'])
            total = available + len([seat for seat in res_seats[1:] if seat['strSeatStatus'] == '1'])
            print(total, available)
            if not total_seats:
                total_str = "Total_Seats=%s, " % total
            for i in range(5):
                try:
                    #print row[0]
                    db = mysql.connector.connect(
                        host=DB_HOST,
                        user=DB_USER,
                        passwd=DB_PASSWORD,
                        db=DB_NAME,
                        connect_timeout=20
                    )
                    cursor = db.cursor()
                    print(total_str, available, row['id'])
                    cursor.execute("UPDATE showtime set %s Available_Seats=%s, Avlb_Seat_Update_datetime=CURRENT_TIMESTAMP() WHERE id=%s"%(total_str, available, row['id']))
                    db.commit()
                    db.close()
                    break
                except Exception as e:
                    print(e)

def main():
    stime = datetime.datetime.now()
    n = sdnotify.SystemdNotifier()
    n.notify("WATCHDOG=1")
    db = mysql.connector.connect(
                    host=DB_HOST,
                    user=DB_USER,
                    passwd=DB_PASSWORD,
                    db=DB_NAME,
                    connect_timeout=20
                )
    queue = Queue()
    proxies = validate_proxies(get_proxies(),'https://carnivalcinemas.sg')
    # proxies = [{'http': '192.119.203.170:48678'}, {'http': '51.158.78.179:8811'}, {'http': '41.210.161.114:80'}, {'http': '86.110.240.166:32246'}, {'http': '202.79.43.139:8080'}]

    for i in range(1):
        print('Thread %s started'%str(i))
        t = Scraper(queue,proxies)
        t.setDaemon(True)
        t.start()
    cursor = db.cursor()
    cursor.execute("SELECT id, Total_Seats, Movie_Url, start_at FROM showtime  WHERE Movie_Url LIKE '%carnivalcinemas.sg%' and start_at >= CURRENT_TIMESTAMP() ORDER BY start_at DESC")

    rows = cursor.fetchall()
    numrows = len(rows)
    print(numrows, rows)
    for row in rows:
        row = {
            'id': row[0],
            'Total_Seats': row[1],
            'Movie_Url': row[2],
            'start_at': row[3]
        }
        queue.put(row)
    queue.join()
    db.close()
    etime = datetime.datetime.now()
    print('Checking time - ',etime-stime)
    print(datetime.datetime.now())

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(e)
