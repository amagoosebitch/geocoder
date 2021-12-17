import requests
from bs4 import BeautifulSoup
import re
import sqlite3
import pandas as pd

cnx = sqlite3.connect('cities.db')

df = pd.read_sql_query("SELECT * FROM cities", cnx)
print(df.iloc[0])


overpass_url = 'http://overpass-api.de/api/interpreter'
regex = re.compile(r'title="(.*?)"')
raw_html = requests.get('https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D0%BE%D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B8').text
soup = BeautifulSoup(raw_html, features='html.parser')
table = soup.find('table').text
table = table[table.find('1'):].split('\n')[:-1]
for row in table[:1]:
    number, city, region = row.split()[:3]
    overpass_query = f'''
    [out:json];
    ( area["ISO3166-1:alpha2"="RU"];) ->.a;
    rel[name="{city}"]["place"~"city|town|village|hamlet|isolated_dwelling"]
    (area.a);
    out bb;
    '''
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()['elements'][0]['bounds']
    print(data)

