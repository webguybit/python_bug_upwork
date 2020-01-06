from Data_dumping_into_csv import carnival, get_proxys, validate_proxies
from lxml import etree, html
import sys
import json
import random
import time
import urllib
import requests
import requests.exceptions
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
proxies = get_proxys()
print(proxies)
proxies = validate_proxies(proxies, MAIN_URL + '/')
ss = requests.session()
ss.headers = headers
ss.proxies = random.choice(proxies)
print(ss.proxies)

# ss.timeout = 10

# res_am = json.loads(ss.get(allmov_url, verify = False).content)['responseMovies']
# print(res_am)
res_am = [{'code': 'CC00001401', 'name': 'NOW AND EVER', 'censor': 'PG13', 'language': 'MYANMAAR/BURMESE', 'duration': 150, 'genre': '', 'description': 'Thiha (Zenn Kyi) is married to\xa0Wuthmone (Paing\xa0Phyoe Thu), who because of her traumatic past is suffering from psychosis. As a passionate lover,\xa0Thiha takes care of\xa0Wuthmone with much kindness. But in the later years of their marriage\xa0Wuthmone starts to suspect\xa0Thiha might be cheating on her and witnesses that he actually is. She blames only herself and rumination worsens her condition. But could what she saw have an alternative truth? Or, has\xa0Thiha fallen out of love?', 'openingDate': '2020-01-03T14:54:16', 'imageURL': 'CC00001401.JPG', 'actor': ' ZENN  KYI, PAING  PHYO THU, MIN  NYO, YE NAUNG  CHO', 'director': ' CHRISTINA  KYI', 'YouTubeURL': 'https://www.youtube.com/embed/iqKX1r-ycL4'}, {'code': 'CC00001404', 'name': 'Sab Kushal Mangal', 'censor': 'PG', 'language': 'HINDI', 'duration': 135, 'genre': '', 'description': 'Pappu Mishra, the creator and host of a reality show called Musibat Odh Li Maine irks a political leader named Baba Bhandari who is offended with his report. Since they both come from the same town, Bhandari plans to kidnap Pappu when he comes home for Diwali. Incidentally, Pappu and Bhandari fall in love with Mandhira.', 'openingDate': '2020-01-03T00:00:00', 'imageURL': 'CC00001404.JPG', 'actor': ' Akshay Khanna, Apurva Nemleker, Riva Kishan, Satish Kaushik', 'director': ' Karan Vishwanath Kashyap', 'YouTubeURL': 'https://www.youtube.com/embed/yzbyiA10jlk'}, {'code': 'CC00001402', 'name': 'Good Newwz(NC16)', 'censor': 'NC16', 'language': 'HINDI', 'duration': 135, 'genre': '', 'description': 'An educated, urban, working couple from Mumbai has now met with the realization that they need to have a kid before it’s too late. Little did they know that during this process, they’d run into two people who they would’ve otherwise never associated themselves with- a loud, garish, landowner couple from Panipat, Haryana. Both these couples, who detest each other, in their quest to make a baby realize that they have no option but to remain connected, leading to hilarious, often ridiculous situations. How they overcome their hatred for each other and learn to take this ‘reproductive’ journey together forms the crux of this story about love and acceptance, called Good Newwz.', 'openingDate': '2019-12-27T00:00:00', 'imageURL': 'CC00001402.JPG', 'actor': ' Diljit  Dosanjh, Akshay  Kumar, Katrina  Kaif', 'director': '', 'YouTubeURL': 'https://www.youtube.com/embed/r9VJpqoAr84'}, {'code': 'CC00001403', 'name': 'Driving Licence(NC16)', 'censor': 'NC16', 'language': 'MALAYALAM', 'duration': 135, 'genre': '', 'description': 'Superstar Hareendran is well known for his driving skills and craze for cars. Kuruvila Joseph, a motor vehicle inspector, is a die-hard fan of Hareendran. For his latest film, Hareendran needs to submit his driving license but discovers that it is missing. He approaches Kuruvilla for help, but the fan and the superstar get entangled in a fight of their own.', 'openingDate': '2019-12-24T00:00:00', 'imageURL': 'CC00001403.JPG', 'actor': ' Prithviraj  Sukumaran, Miya  George', 'director': ' Jean Paul  Lal', 'YouTubeURL': 'https://www.youtube.com/embed/8pXjSuTdV7o'}, {'code': 'CC00001398', 'name': 'Thambi(NC16)', 'censor': 'NC16', 'language': 'TAMIL', 'duration': 150, 'genre': '', 'description': 'An orphan who takes on the identity of a missing person, years after he has gone missing realises that there are deep dark secrets that the "ideal" family is hiding.', 'openingDate': '2019-12-20T12:05:10', 'imageURL': 'CC00001398.JPG', 'actor': ' JOTHIKA SURYA, KARTHI ,', 'director': ' Jeethu  Joseph', 'YouTubeURL': 'https://www.youtube.com/embed/y2vwIiLyt1Y'}, {'code': 'CC00001399', 'name': 'Prati Roju Pandaage', 'censor': 'PG13', 'language': 'TELUGU', 'duration': 150, 'genre': '', 'description': 'This family drama is the story of a grandson, Sai Tej, who tries to unite his family to make his grandfather Satyaraj`s last ailing days happy and blissful. The film revolves around the old man`s last wishes and the realisation that life is meant to be celebrated.', 'openingDate': '2019-12-20T00:00:00', 'imageURL': 'CC00001399.JPG', 'actor': ' Raashi  Khanna, Sai Dharam  Tej ', 'director': ' Maruthi  Dasari', 'YouTubeURL': 'https://www.youtube.com/embed/dDNz5naywZQ'}, {'code': 'CC00001397', 'name': 'Hero', 'censor': 'PG13', 'language': 'TAMIL', 'duration': 165, 'genre': '', 'description': '', 'openingDate': '2019-12-20T00:00:00', 'imageURL': 'CC00001397.JPG', 'actor': ' SIVA KARTHIKEYAN, Arjun ., Kalyani  Priyadarshan', 'director': '', 'YouTubeURL': 'https://www.youtube.com/embed/5FZnvzAA2iQ'}]

for film in res_am:
    fname = film['name']
    print('Trying {}'.format(fname))
    try:
        dates = json.loads(ss.get(sdates_url.format(fname), verify=False).content)['responseShowDates']
        print('Dates are {}'.format(dates))
    except Exception as e:
        print(e)
        continue



