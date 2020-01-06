import sys
import json
import random
import time
import urllib
import os
from datetime import datetime, timedelta
from io import StringIO
import re
# import brotlii
import cfscrape
import requests
import requests.exceptions
from bs4 import BeautifulSoup
from lxml import etree, html

import requests

def is_bad_proxy(pip, url, headers=None):
    
    timeout = 10

    try:
        if 'shaw' in url:
            res = requests.get(url, proxies={'https': pip}, headers={
                'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'}, timeout=timeout)
        else:
            res = requests.get(url, proxies={'http': pip}, headers=headers, timeout=timeout)
    except Exception as detail:
        # print("ERROR: %s" % detail)
        return 1
    if res.status_code == 200 and 'bad' not in res.text.lower() and 'request' not in res.text.lower():
        return 0
    else:
        #print(res.status_code)
        return 1


def get_proxys():
    url = 'https://hidemy.name/ru/loginx'
    url1 = 'https://hidemy.name/api/proxylist.txt?out=plain&lang=ru'
    data = {'c': '169496407732367'}
    s = requests.session()
    s.get(url1)
    s.post(url, data=data)
    res = s.get(url1)
    result = res.text.split('\r\n')
    return result


def validate_proxies(proxies, url, headers=None):
    proxys = []
    random.shuffle(proxies)
    stime = datetime.now() + timedelta(minutes=30)
    for proxy in proxies:
        if stime < datetime.now():
            break
        bad_proxy = is_bad_proxy(proxy, url, headers)
        if not bad_proxy:
            print(proxy, "APPROVED!")
            if 'shaw' not in url:
                proxys.append({'http': proxy})
            else:
                proxys.append({'https': proxy})
            if os.path.isdir('/home/sriabt/databaseUpload/') and 'cathay' not in url:
                if len(proxys) == 5:
                    break
            else:
                if len(proxys) == 1:
                    break
        elif str(bad_proxy)[0] == '5' and len(proxys) == 0:
            print('This service is now unavailable (site from scraping is unavailable)')
    if len(proxys) == 0:
        return 0
    return proxys


def choice_proxy(proxies):
    return proxies[random.randint(0, len(proxies) - 1)]


def paged(string):
    htmlparser = etree.HTMLParser()
    return etree.parse(StringIO(string), htmlparser)


def scrape(next_page_url, lxml_grab=None, proxies=None):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36'};
    if proxies != 0 and len(proxies) > 0:
        plist = proxies[:]
        status_code = 0
        while len(plist) > 0 and status_code != 200:
            choiced = choice_proxy(plist)
            try:
                response = requests.get(next_page_url, headers=headers, timeout=10, proxies=choiced)
                status_code = response.status_code
                if status_code == 200:
                    break
            except:
                pass
            plist.remove(choiced)
    else:
        response = requests.get(next_page_url, headers=headers, timeout=10)
        if response.status_code != 200:
            return 0
    if lxml_grab is None:
        # soup = BeautifulSoup(response.text, "html5lib")
        soup = BeautifulSoup(response.text, "html.parser")
    else:
        soup = paged(response.text)
    return soup


def request(date, viewstate, eventValidation, proxies=None):
    url = "http://tickets.fgcineplex.com.sg/visInternetTicketing/visShowtimes.aspx"
    payload = "__EVENTTARGET=ddlFilterDate&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=" + urllib.quote_plus(
        viewstate) + "&__EVENTVALIDATION=" + urllib.quote_plus(
        eventValidation) + "&ddlFilterDate=" + date + "&radListBy=radListByCinema"
    headers = {
        'cookie': "AspxAutoDetectCookieSupport=1; ASP.NET_SessionId=pax3ay5515svju45dd2hgm2x; __utma=200437049.338039226.1512312200.1512312200.1512312200.1; __utmc=200437049; __utmz=200437049.1512312200.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); visSessionID=5236dbce0391413eaf105078af107962",
        'origin': "http://tickets.fgcineplex.com.sg",
        'accept-encoding': "gzip, deflate",
        'accept-language': "en-US,en;q=0.8",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'cache-control': "no-cache",
        'referer': "http://tickets.fgcineplex.com.sg/visInternetTicketing/visShowtimes.aspx",
        'connection': "keep-alive",
        'postman-token': "57b3b197-a7e9-799c-403d-6133223c739d"
    }
    proxys = proxies[:]
    status_code = 0
    while len(proxys) > 0 and status_code != 200:
        print(proxys)
        choiced = choice_proxy(proxys)
        proxys.remove(choiced)
        try:
            response = requests.request("POST", url, data=payload, headers=headers, proxies=choiced)
            status_code = response.status_code
        except:
            print('Cant load with proxy')
            pass

    if status_code != 200:
        try:
            print('Cant connect via proxy, trying connect directly')
            response = requests.request("POST", url, data=payload, headers=headers)
        except:
            return 0
    return response


def scrapeurl(date, viewstate, eventValidation, proxies=None):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = request(date, viewstate, eventValidation, proxies)
    if response != 0:
        # soup = BeautifulSoup(response.text, "html5lib")
        soup = BeautifulSoup(response.text, "html.parser")
    else:
        return 0
    return soup


def requestShaw(viewstate, date, proxies=None):
    url = "http://www.shaw.sg/sw_buytickets.aspx"
    payload = "__EVENTTARGET=ctl00%24Content%24ddlShowDate&__EVENTARGUMENT=&__LASTFOCUS=&__VIEWSTATE=" + urllib.quote_plus(
        viewstate) + "&__VIEWSTATEGENERATOR=0500EEBB&__VIEWSTATEENCRYPTED=&CplexCode=&FilmCode=&ctl00%24Content%24ddlShowDate=" + urllib.quote_plus(
        date) + "&ctl00%24Content%24rblSelectSeating=M&ctl00%24Content%24txtAvail=&ctl00%24Content%24txtSellFast=&ctl00%24Content%24txtSoldOut="
    headers = {
        'cookie': "ASP.NET_SessionId=sdi1lk553tmoz545mpazuxzw; cookieCheck=12/3/2017 8:51:13 PM; __utmt=1; __utma=196025459.800268039.1512305405.1512311797.1512321588.4; __utmb=196025459.9.10.1512321588; __utmc=196025459; __utmz=196025459.1512321588.4.4.utmcsr=google|utmccn=(organic)|utmcmd=organic|utmctr=(not%20provided); __atuvc=18%7C49; __atuvs=5a243232620ce92b008",
        'origin': "http://www.shaw.sg",
        'accept-encoding': "gzip, deflate",
        'accept-language': "en-US,en;q=0.8",
        'upgrade-insecure-requests': "1",
        'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'cache-control': "no-cache",
        'referer': "http://www.shaw.sg/sw_buytickets.aspx",
        'connection': "keep-alive",
        'postman-token': "6eb3446a-f9f2-1f8a-6743-a4e5f3b8dcd5"
    }
    if proxies != 0:
        response = requests.request("POST", url, data=payload, headers=headers, proxies=choice_proxy(proxies))
    else:
        print("Can't get response from unavailable %s (Error code 5XX)" % url)
        return 0
    return response


def scrapeUrlshaw(viewstate, date, proxies=None):
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requestShaw(viewstate, date, proxies)
    if response != 0:
        soup = BeautifulSoup(response.text, "html.parser")
    else:
        return 0
    return soup


def getCinemas(proxies=None):
    print('<<<<< gv cinema process started >>>>>')
    url = "https://www.gv.com.sg/.gv-api/cinemas"
    headers = {
        'origin': "https://www.gv.com.sg",
        'accept-encoding': "gzip, deflate, br",
        'x_developer': "ENOVAX",
        'accept-language': "en-US,en;q=0.8",
        'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
        'content-type': "application/json; charset=UTF-8",
        'accept': "application/json, text/plain, */*",
        'referer': "https://www.gv.com.sg/GVBuyTickets",
        'authority': "www.gv.com.sg",
        # 'cookie': "__cfduid=d848fb1f803ddc4406880fd4dfceb7eca1511894040; __atuvc=1%7C49; JSESSIONID=0GRgIfUqqxpuAKKEsKrO95dt.undefined; _ga=GA1.3.640411893.1511894050; _gid=GA1.3.1043315194.151230618$
        'cookie': "__cfduid=db4aa507ed20675598e5500ff69d2dc841525162952; _ga=GA1.3.1520606575.1525163281; _gid=GA1.3.638964924.1525163281; _gat=1; publica_session_id=ef4d7367-4966-3ac1-c21b-b2ca57c6ec72; JSESSIONID=20AA6103A27DE2F707B4D624064B18EE",
        'cache-control': "no-cache",
        'path': '/.gv-api/v2buytickets?t=387_1525167473252'
        # 'postman-token': "872dd435-61f6-8021-6e2f-cc9fba3a40cf"
    }
    headers = {
        'origin': 'https://www.gv.com.sg',
        'content-type': 'application/json; charset=UTF-8',
        'referer': 'https://www.gv.com.sg/GVBuyTickets',
        'x_developer': 'ENOVAX',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
    }
    proxies = validate_proxies(proxies, url)
    if proxies != 0:
        response = requests.request("POST", url, headers=headers, proxies=choice_proxy(proxies))  # , proxies=proxyDict)
    else:
        response = requests.request("POST", url, headers=headers)
    try:
        data_return = (brotli.decompress(response.content))
    except:
        data_return = response.content
    # print data_return.decode('utf-8')
    # print(response.text)
    data = json.loads(data_return.decode())
    cinemas = {}
    for i in data['data']:
        cinemas[i['id']] = i['name']
    return cinemas
    print('<<<<< gv cinema process ended >>>>>')


def timeConvert(timeStr):
    time = timeStr.split(':')
    type = ''
    if (int(time[0]) > 11):
        if (int(time[0]) == 12):
            time = time[0] + ":" + time[1]
        else:
            time = str(int(time[0]) - 12) + ':' + time[1]
        type = ' PM'
    else:
        time = time[0] + ':' + time[1]
        type = ' AM'
    return time + type


def month_string_to_number(string):
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr': 4,
        'may': 5,
        'jun': 6,
        'jul': 7,
        'aug': 8,
        'sep': 9,
        'oct': 10,
        'nov': 11,
        'dec': 12
    }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')


def dateConvert(dateStr):
    date = dateStr.split(' ')
    month = str(month_string_to_number(date[2]))
    year = str(datetime.now().year)
    return date[1] + '/' + month + '/' + year


def fileWrite(string):
    print(string)
    data.append(string)


def carnival(proxies=None):
    print("<<<<< carnival cinema process started >>>>>")
    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'en-GB,en;q=0.5',
        'Host': 'service.carnivalcinemas.sg',
        'Origin': 'https://carnivalcinemas.sg',
        'Referer': 'https://carnivalcinemas.sg/',
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux) Gecko/20100101 Firefox/60.0',
        'Token': 'bXpFNVc2bHR1d3IvK3lSb3F3UHVFVDJqNE8rN2VWN3ZiNEJ0Mnd3TXorbz18aHR0cHM6Ly9jYXJuaXZhbGNpbmVtYXMuc2cvIy9ib29rU2VhdHw2MzY2NjEzNDAwNzA2MzAwMDB8cno4THVPdEZCWHBoajlXUWZ2Rmg='
    }
    MAIN_URL = 'https://carnivalcinemas.sg/#'
    allmov_url = 'https://service.carnivalcinemas.sg/api/QuickSearch/GetAllMovieDetail?locationName=Mumbai'
    sdates_url = 'https://service.carnivalcinemas.sg/api/QuickSearch/GetShowDatesByMovies?location=Mumbai&movieCode={0}'
    times_url = 'https://service.carnivalcinemas.sg/api/QuickSearch/GetCinemaAndShowTimeByMovie?location=Mumbai&movieCode={0}&date={1}'
    link = 'https://carnivalcinemas.sg/#/{0}/{1}'
    if len(proxies) > 0:
        proxies = validate_proxies(proxies, MAIN_URL + '/')
        ss = requests.session()
        ss.headers = headers
        ss.proxies = random.choice(proxies)
        ss.timeout = 10
    else:
        ss = requests.session()
        ss.headers = headers

    try:
        res_am = json.loads(ss.get(allmov_url, verify = False).content)['responseMovies']
    except Exception as e:
        print(e)
        raise Exception
    for film in res_am:
        fname = film['name']
        try:
            dates = json.loads(ss.get(sdates_url.format(fname)).content)['responseShowDates']
        except Exception as e:
            print(e)
            continue
        for date in dates:
            qdate = date['showDateValue']
            try:
                times = json.loads(ss.get(times_url.format(fname, qdate)).content)['responseCinemaWithShowTime']
            except Exception as e:
                print(e)
                continue
            for t in times:
                cinemaname = ' '.join(t['cinemaName'].split()[2:])
                if cinemaname.count('Shaw Tower'):
                    cinemaname = 'Beach Road'
                dd = qdate.split('T')[0].split('-')
                dd.reverse()
                if t['showTime'].count(','):
                    ts = [x.strip()[:-1] for x in t['showTime'].split(',')]
                    for ti in ts:
                        ti.strip()
                        if ti.count('T'):
                            ti = ti[:-1]
                        data = '/'.join(dd)
                        time = ti.strip()
                        if 'AM' in time:
                            cp_time = ''.join([time.split('AM')[0].strip(), ':00'])
                            time = ' '.join([cp_time, 'AM'])
                        elif 'PM' in time:
                            cp_time = ''.join([time.split('PM')[0].strip(), ':00'])
                            time = ' '.join([cp_time, 'PM'])
                        link = f'https://carnivalcinemas.sg/#/{fname}/{fname}'
                        link = link.format(fname, fname).replace(' ', '%20')
                        line = f'"{fname.strip()}","{cinemaname}","Carnival","{data}","{time}","{link}"'
                        fileWrite(line)
                else:
                    data = '/'.join(dd)
                    time = t['showTime'].strip()[:-1]
                    if 'AM' in time:
                        cp_time = ''.join([time.split('AM')[0].strip(), ':00'])
                        time = ' '.join([cp_time, 'AM'])
                    elif 'PM' in time:
                        cp_time = ''.join([time.split('PM')[0].strip(), ':00'])
                        time = ' '.join([cp_time, 'PM'])
                    link = f'https://carnivalcinemas.sg/#/{fname}/{fname}'
                    link = link.format(fname, fname).replace(' ', '%20')
                    line = f'"{fname.strip()}","{cinemaname}","Carnival","{data}","{time}","{link}"'
                    fileWrite(line)
    print("<<<<< carnival cinema process ended >>>>>")


def cathay(proxies=None):
    print("<<<<< cathay cinema process started >>>>>")
    url = "http://www.cathaycineplexes.com.sg/showtimes.aspx"
    sess = requests.session()
    proxies = validate_proxies(proxies, "http://www.cathaycineplexes.com.sg")
    # proxies = [{'http': x} for x in proxies]
    plist = proxies[:]
    status = 0
    while len(plist) > 0 and status != 200:
        choiced = choice_proxy(plist)
        sess.proxies = choiced
        sess.headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
        try:
            response = sess.get(url)
            status = response.status_code
            soup = paged(response.text)
        except Exception as e:
            print(e)
            status = 0
        plist.remove(choiced)
    if status != 200:
        sess = requests.session()
       # scraper = cfscrape.create_scraper(sess, delay=40)
        response = sess.get(url)
        try:
            soup = paged(response.text)
        except Exception as e:
            print(e)
            return 0
    divArray = ['ContentPlaceHolder1_wucST_tabs', 'ContentPlaceHolder1_wucST1_tabs',
                'ContentPlaceHolder1_wucST2_tabs', 'ContentPlaceHolder1_wucST3_tabs', 'ContentPlaceHolder1_wucST4_tabs',
                'ContentPlaceHolder1_wucST5_tabs', 'ContentPlaceHolder1_wucST6_tabs',
                'ContentPlaceHolder1_wucSTPMS_tabs']
    titles = ['AMK HUB', 'CAUSEWAY POINT', 'CINELEISURE ORCHARD', 'DOWNTOWN EAST', 'JEM', 'PARKWAY PARADE',
              'THE CATHAY', 'WEST MALL', 'Platinum Movie Suite']
    for i in range(0, len(divArray)):
        div = divArray[i]
        title = titles[i]
        try:
            tabs = soup.xpath('//div[@id="%s"]' % div)[0]
            dates = tabs.xpath('ul/li/a/span[@class="smalldate"]/text()')
            containers = tabs.xpath('div[@class="tabbers"]')
            for i in range(0, len(containers)):
                movie_containers = containers[i].xpath('div')
                date = dates[i]
                timediv = date.split(' ')
                date = str(timediv[0]) + '/' + str(month_string_to_number(timediv[1])) + '/' + str(datetime.now().year)
                for j in range(0, len(movie_containers)):
                    hall = ''
                    hall_div = movie_containers[j].xpath('div[@class="movie-desc"]/strong')
                    if (len(hall_div) > 1):
                        hall = hall_div[0].text
                    film = ''
                    film_div = movie_containers[j].xpath('div[@class="movie-desc"]/span[@class="mobileLink"]/strong/a')
                    if (len(film_div) > 0):
                        film = film_div[0].text
                    if (film == ''):
                        continue
                    if (hall == ''):
                        hall = title
                    times = movie_containers[j].xpath(
                        'div[@class="movie-timings"]/div[@class="showtimeitem_time_pms"]/a')
                    for k in times:
                        if k.get('data-href') is None:
                            continue
                        time = timeConvert(k.text.strip())
                        if 'AM' in time:
                            cp_time = ''.join([time.split('AM')[0].strip(), ':00'])
                            time = ' '.join([cp_time, 'AM'])
                        elif 'PM' in time:
                            cp_time = ''.join([time.split('PM')[0].strip(), ':00'])
                            time = ' '.join([cp_time, 'PM'])
                        link = k.get('data-href')
                        line = f'"{film.strip()}","{title}","{hall}","{date}","{time}","{link}"'
                        fileWrite(str(line.encode('ascii', 'ignore').decode('ascii')))
        except Exception as e:
            warnings.append(f'(Cathay) Error extraction {title}: {e}')
            raise ParserError
    print("<<<<< cathay cinema process ended >>>>>")


def fg(proxies=None):
    print("<<<<< fg cinema process started >>>>>")
    url = "https://fgcineplex.com.sg/"
    proxies = validate_proxies(proxies, url)
    soup = scrape(url, proxies=proxies)
    if soup == 0:
        return 0
    imgs = soup.select(".tour-img > a img")
    links = [i.a['href'] for i in soup.select(".show-read-more")]
    for link in links:
        soup = scrape(link, proxies=proxies)
        film = soup.select('.movie-list-indvisuals > h2 > b')[0].text
        for section in soup.select('.movie-cinema-box'):
            # nome do cinema:
            # caixa.find('div', class_='cinema-title').text.split('-')[1].strip()
            hall = section.find('div', class_='cinema-title').text.split('-')[1].strip()
            for div in section.select('#content > ul > li'):
                date = div.select('.date')[0].text
                cod = div.select('a')[0]['href']
                div2 = section.select('#content')[0]
                tabPane = div2.select(u'#{} > div > ul > li'.format(cod[1:]))
                for tm in tabPane:
                    time = tm.a.text.strip()
                    if 'am' in time:
                        cp_time = ''.join([time.split('am')[0].strip(), ':00'])
                        time = ' '.join([cp_time, 'AM'])
                    elif 'pm' in time:
                        cp_time = ''.join([time.split('pm')[0].strip(), ':00'])
                        time = ' '.join([cp_time, 'PM'])
                    link = tm.a['href']
                    year = str(datetime.now().year)
                    line = u'"{}","{}","{}","{}","{}","{}"'.format(
                        film, hall, hall, ''.join([date, '/', year]), time, link
                    )
                    fileWrite(line)
    print("<<<<< fg cinema process ended >>>>>")


def gv(proxies=None):
    proxies = validate_proxies(get_proxys(), "https://www.gv.com.sg")
    dateArray = []
    dateArray.append(int(time.mktime(datetime.now().date().timetuple()) * 1000))
    for i in range(1, 7):
        newDate = (datetime.now() + timedelta(days=i)).date()
        unixtime = time.mktime(newDate.timetuple())
        dateArray.append(int(unixtime * 1000))
    for j in dateArray:
        sess = requests.session()
        if proxies != 0:
            sess.proxies = {'http': choice_proxy(proxies)}
            sess.headers = {
                'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}
        scraper = cfscrape.create_scraper(sess, delay=15)
        url = "https://www.gv.com.sg/.gv-api/v2buytickets"
        print(str(j))
        payload = '{"cinemaId":"","filmCode":"","date":' + str(j) + ',"advanceSales":false}'
        headers = {
            'origin': "https://www.gv.com.sg",
            'accept-encoding': "gzip, deflate, br",
            'x_developer': "ENOVAX",
            'accept-language': "en-US,en;q=0.8",
            'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36",
            'content-type': "application/json; charset=UTF-8",
            'accept': "application/json, text/plain, */*",
            'referer': "https://www.gv.com.sg/GVBuyTickets",
            'authority': "www.gv.com.sg",
            # 'cookie': "__cfduid=d848fb1f803ddc4406880fd4dfceb7eca1511894040; __atuvc=1%7C49; JSESSIONID=0GRgIfUqqxpuAKKEsKrO95dt.undefined; _ga=GA1.3.640411893.1511894050; _gid=GA1.3.1043315194.1512306186; _gat=1",
            'cookie': "__cfduid=db4aa507ed20675598e5500ff69d2dc841525162952; _ga=GA1.3.1520606575.1525163281; _gid=GA1.3.638964924.1525163281; _gat=1; publica_session_id=ef4d7367-4966-3ac1-c21b-b2ca57c6ec72; JSESSIONID=20AA6103A27DE2F707B4D624064B18EE",
            'cache-control': "no-cache",
            'path': '/.gv-api/v2buytickets?t=387_1525167473252'
            # 'postman-token': "872dd435-61f6-8021-6e2f-cc9fba3a40cf"
        }
        headers = {
            'origin': 'https://www.gv.com.sg',
            'content-type': 'application/json; charset=UTF-8',
            'referer': 'https://www.gv.com.sg/GVBuyTickets',
            'x_developer': 'ENOVAX',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'
        }
        try:
            response = sess.post(url, data=payload, headers=headers)
        except Exception as e:
            print(e)
            warnings.append('(Gv) Error extraction %s ' % (str(j)))
        try:
            data_return = ((response.content))
        except:
            continue
        data = json.loads(data_return.decode())
        halls = (data['data']['cinemas'])
        cinemas = getCinemas(proxies=proxies)
        for j in halls:
            hall = cinemas[j['id']]
            for k in j['movies']:
                film = k['filmTitle']
                for n in k['times']:
                    timeNow = n['time12'][:-2] + ' ' + n['time12'][-2:]
                    date = n['showDate'].replace('-', '/')
                    link = "https://www.gv.com.sg/GVSeatSelection#/cinemaId/" + j['id'] + "/filmCode/" + k[
                        'filmCd'] + "/showDate/" + n['showDate'] + "/showTime/" + n['time24'] + "/hallNumber/" + n[
                               'hall']
                    timer = ''
                    if 'AM' in timeNow:
                        cp_time = ''.join([timeNow.split('AM')[0].strip(), ':00'])
                        timer = ' '.join([cp_time, 'AM'])
                    elif 'PM' in timeNow:
                        cp_time = ''.join([timeNow.split('PM')[0].strip(), ':00'])
                        timer = ' '.join([cp_time, 'PM'])
                    line = f'"{film.strip()}","{hall}","{hall}","{date}","{timer}","{link}"'
                    # line = '"' + film.strip() + '","' + hall + '","' + hall + '","' + date + '","' + timeNow.strip() + '","' + link + '"'
                    fileWrite(str(line.encode('ascii', 'ignore').decode('ascii')))


def shaw(proxies=None):
    print("<<<<< shaw cinema process started >>>>>")
    cookies = {
        '_ga': 'GA1.2.2058276489.1555937404',
        '_gid': 'GA1.2.1392350065.1555937404',
        'joe-chnlcustid': '1426492936',
        '_fbp': 'fb.1.1555937404307.1562389095',
        'pnctest': '1',
        'spd-custhash': 'c2f674ee2bb5a92c1567ead4df14ee906a058ecc',
        'ASP.NET_SessionId': 'oxcouayivcafpjfjnqvvnrv3',
        '_gat': '1',
        '_gat_gtag_UA_2073474_116': '1',
    }

    headers = {
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,vi;q=0.6',
        'Referer': 'https://www.google.com.pk/'

    }
    url = "https://www.shaw.sg/"
    proxies = validate_proxies(proxies, url, headers)
    soup = scrape(url, proxies=proxies)
    # response = scraper.post(url,headers=headers,cookies=cookies)
    # response = get(url,headers=headers,cookies=cookies)
    # response = request("POST", url, data=payload, headers=headers,proxies=choice_proxy(proxies))
    # soup = bs(response.text, 'html.parser')
    if soup == 0:
        return 0
    datas = [x['value'] for x in soup.select('.date-top-selector > option')]
    for dt in datas:
        cookies = {
            '_ga': 'GA1.2.1626712709.1554123147',
            '_gid': 'GA1.2.505595873.1554123147',
            'joe-chnlcustid': '1179089963',
            '_fbp': 'fb.1.1554123147788.60010941',
            'spd-custhash': '44cdff717f1a4ee634a3248bd96619be47d7963a',
            'pnctest': '1',
            '_gat_EcommerceTracker': '1',
            '_gat_gtag_UA_2073474_116': '1',
        }

        headers = {
            'Origin': 'https://www.shaw.sg',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,vi;q=0.6',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
            'Content-Type': 'application/json;',
            'Accept': '*/*',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
        }

        dados1 = "{'strAction':'LIST_SHOWTIMES'"
        dados2 = f"'vStrSelectPerformanceDate': '{dt}'"
        dados3 = "'vStrSelectEventMasterCode':'All'"
        dados4 = "'vStrSelectLocationCode':'All'}"
        data = "%s,%s,%s,%s" % (dados1, dados2, dados3, dados4)
        url = 'https://www.shaw.sg/DataForHandleBars'
        # proxies = 0#validate_proxies(proxies,url)
        # soup = scrape(url,proxies=proxies)
        if proxies != 0:
            response = requests.request("POST", url, headers=headers, proxies=choice_proxy(proxies), data=data)
        else:
            response = requests.request("POST", url, headers=headers, data=data)
        for text in response.json()[:-1]:
            try:
                performance_code = text['performance_code']
                film = text['movie_title_primary']
                hall = text['location_name']
                date = text['performance_display_date']
                date = date.split('-')
                '''
                    se array do date na posição 2 de segundo elemento for 0
                    pegar do array da segunda posição o segundo elemento
                    caso contrário pega o array da segunda posição completo
                '''
                day = date[2][1] if date[2][0] == '0' else date[2]
                month = date[1][1] if date[1][0] == '0' else date[1]
                date = day + '/' + month + '/' + date[0]
                time = text['performance_display_time']
                if 'AM' in time:
                    cp_time = ''.join([time.split('AM')[0].strip(), ':00'])
                    time = ' '.join([cp_time, 'AM'])
                elif 'PM' in time:
                    cp_time = ''.join([time.split('PM')[0].strip(), ':00'])
                    time = ' '.join([cp_time, 'PM'])
                link = f'https://www.shaw.sg/seat-selection/{performance_code}'
                line = f'"{film}","{hall}","{hall}","{date}","{time}","{link}"'
                fileWrite(line)
            except Exception as error:
                print(f'Error.: {error}')
                continue

    print("<<<<< shaw cinema process ended >>>>>")


def we(proxies=None):
    print("<<<<< we cinema process started >>>>>")
    url = "https://www.wecinemas.com.sg/buy-ticket.aspx"
    proxies = 0  # validate_proxies(proxies,url)
    soup = scrape(url, proxies=proxies, lxml_grab=True)
    if soup == 0:
        return 0
    days = soup.xpath(
        '/html/body/form/div[6]/table/tr/td/div/div/div[7]/div/table/tr[2]/td/table/tr/td[1]/table/tr[1]/td/table/tr/td/table/tr[6]/td/table/tr/td/table/tr[5]/td/table/tr/td/table/tr/td/table')
    for day in range(len(days)):
        date = days[day].xpath('tr[1]/td/div[@class="showtime-date-con"]/div[@class="showtime-date"]/text()')[0].split(
            ' ')
        date = '/'.join([str(date[0]), str(month_string_to_number(date[1])), str(date[2].split(',')[0])])
        dm = soup.xpath(
            '/html/body/form/div[6]/table/tr/td/div/div/div[7]/div/table/tr[2]/td/table/tr/td[1]/table/tr[1]/td/table/tr/td/table/tr[6]/td/table/tr/td/table/tr[5]/td/table/tr/td/table/tr[%s]/td/table/tr[3]/td' % str(
                day + 1 + 2 * day))
        for x in range(len(dm[0].xpath('table/tr'))):
            fname = dm[0].xpath('table/tr[%s]/td/h3/a/text()' % str(2 + 7 * x))
            if len(fname) > 0:
                times = dm[0].xpath('table/tr[%s]/td/table/tr[2]/td/div[@class="showtimes-but"]/a' % str(5 + 7 * x))
                for t in times:
                    if fname[0].count('First Class'):
                        hall = '321 Clementi (First Class)'
                    else:
                        hall = '321 Clementi'
                    time = ' '.join([re.findall('\d+:\d+', t.text)[0], t.text[-2:]])
                    if 'AM' in time:
                        cp_time = ''.join([time.split('AM')[0].strip(), ':00'])
                        time = ' '.join([cp_time, 'AM'])
                    elif 'PM' in time:
                        cp_time = ''.join([time.split('PM')[0].strip(), ':00'])
                        time = ' '.join([cp_time, 'PM'])
                    line = '"' + fname[0] + '","' + hall + '","' + 'WE-Clementi' + '","' + date + '","' + time + '","' + \
                           t.xpath('@href')[0] + '"'
                    fileWrite(str(line.encode('ascii', 'ignore').decode('ascii')))
    print("<<<<< we cinema process ended >>>>>")


def eaglewings(proxies=None):
    print("<<<<< eaglewings cinema process started >>>>>")
    url = "https://www.eaglewingscinematics.com.sg/browsing/Movies/NowShowing"
    proxies = validate_proxies(proxies, url)
    soup = scrape(url, proxies=proxies)
    if soup == 0:
        return 0
    links = [l for l in soup.select('.list-item.main-action > a')]
    for lnk in soup.select('.list-item .main-action > a'):
        link = lnk['href']
        url = f'https:{link}'
        soup = scrape(url, proxies=proxies)
        film = soup.select('.boxout-title')[0].text
        for hr in soup.findAll('a', class_='session-time'):
            date = hr.find('time')['datetime'].split('T')[0]
            date = invertDate(date)
            time = hr.find('time')['datetime'].split('T')[1].split(':')
            time = ':'.join((time[0], time[1]))
            time = timeConvert(time)
            if 'AM' in time:
                cp_time = ''.join([time.split('AM')[0].strip(), ':00'])
                time = ' '.join([cp_time, 'AM'])
            elif 'PM' in time:
                cp_time = ''.join([time.split('PM')[0].strip(), ':00'])
                time = ' '.join([cp_time, 'PM'])
            link = u'http:{}'.format(hr['href'])
            hall = hr.find('img')['alt']
            line = f'"{film}","{hall}","{hall}","{date}","{time}","{link}'
            fileWrite(line)
    print("<<<<< eaglewings cinema process ended >>>>>")


def invertDate(date):
    year = date.split('-')[0]
    month = date.split('-')[1]
    day = date.split('-')[2]
    if date.split('-')[1][0] == '0':
        month = date.split('-')[1][1]
    if date.split('-')[2][0] == '0':
        day = date.split('-')[2][1]
    return u'{}/{}/{}'.format(day, month, year)


def debug():
    from pdb import set_trace
    set_trace()


# TRYING_QUOTA = 5
# data = []
# # proxies = get_proxys()
# warnings = []
# shaw_status = 0
# carnival_status = 0
# cathay_status = 0
# fg_status = 0
# we_status = 0
# gv_status = 0
# eaglewings_status = 0

# start_time = datetime.now()
# #####  CARNIVAL ################## DONE
# carnival_counter=0
# while carnival_status == 0 and TRYING_QUOTA > carnival_counter:
#     try:
#         carnival(proxies=proxies)
#         carnival_status = 1
#     except Exception as e:
#         warnings.append(f"Carnival error scraping: {e}")
#     carnival_counter += 1

# #### WE ############################ DONE
# we_counter = 0
# while we_status == 0 and TRYING_QUOTA > we_counter:
#     try:
#         we(proxies=proxies)
#         we_status = 1
#     except Exception as e:
#         warnings.append(f"We error scraping: {e}")
#     we_counter += 1

# #######  CATHAY  ################### DONE
# cathay_counter = 0
# while cathay_status == 0 and TRYING_QUOTA > cathay_counter:
#     try:
#         cathay(proxies=proxies)
#         cathay_status = 1
#     except Exception as e:
#         warnings.append(f"Cathay error scraping: {e}")
#         # from pdb import post_mortem
#         # post_mortem()
#     cathay_counter += 1

# ######  FG  ########################## DONE
# fg_counter = 0
# while fg_status == 0 and TRYING_QUOTA > fg_counter:
#     try:
#         fg(proxies=proxies)
#         fg_status = 1
#     except Exception as e:
#         warnings.append(f"FG error scraping: {e}")
#     fg_counter += 1

# #######  GV  ######################### DONE
# gv_counter = 0
# while gv_status == 0 and TRYING_QUOTA > gv_counter:
#     try:
#         gv(proxies=proxies)
#         gv_status = 1
#     except Exception as e:
#         warnings.append("Gv error scraping: %s" % e)
#         # from pdb import post_mortem
#         # post_mortem()
#     gv_counter += 1

# ######  EAGLEWINGS  ######################### DONE
# eaglewings_counter = 0
# while eaglewings_status == 0 and TRYING_QUOTA > eaglewings_counter:
#     try:
#         eaglewings(proxies=proxies)
#         eaglewings_status = 1
#     except Exception as e:
#         warnings.append(f"Eaglewings error scraping: {e}")
#     eaglewings_counter += 1

# ########  SHAW  #################### DONE
# shaw_counter = 0
# while shaw_status == 0 and TRYING_QUOTA > shaw_counter:
#     try:
#         shaw(proxies=proxies)
#         shaw_status = 1
#     except Exception as e:
#         warnings.append(f"Shaw error scraping: {e}")
#     shaw_counter +=1

# #######################################
# end_time = datetime.now()

# for war in warnings:
#     print(war)

# data = list(set(data))
# if os.path.isdir('/home/sriabt/databaseUpload/'):
#     with open('/home/sriabt/databaseUpload/movie_data.csv','w') as f:
#         for i in data:
#             f.write(i + '\n')
# else:
#     with open('movie_data.csv', 'w') as f:
#         for i in data:
#             f.write(i + '\n')

# print('Working time - ', end_time - start_time)
# print(end_time)
# print("##########################################")
# print("Script ends")
# print("##########################################")
