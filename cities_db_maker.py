import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import json
import time


WIKIPEDIA = 'https://ru.wikipedia.org/wiki/%D0%A1%D0%BF%D0%B8%D1%81%D0%BE%D0%BA_' \
            '%D0%B3%D0%BE%D1%80%D0%BE%D0%B4%D0%BE%D0%B2_%D0%A0%D0%BE%D1%81%D1%81%D0%B8%D0%B8'


def overpass_request(city):
    answer = []
    overpass_url = 'http://overpass-api.de/api/interpreter'
    overpass_query = f'''
        [out:json];
        (area["ISO3166-1:alpha2"="RU"];) ->.a;
        rel[name="{city}"][place~"city|town"]
        (area.a);
        out bb;
        '''
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()['elements']
    if len(data) == 0:
        return [(None, None)]
    for i in range(len(data)):
        bb = data[i]['bounds']
        if 'add:region' in data[i]['tags'].keys():
            answer.append((data[i]['tags']['addr:region'], bb))
        elif 'wikipedia' in data[i]['tags']:
            answer.append(('Крым', bb))
        else:
            answer.append((None, bb))
    return answer


def create_database():
    conn = sqlite3.connect('cities.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE cities
                      (city text, region text, south real, west real, north real, east real)
                   ''')
    return conn, cursor


def update_database(conn, cursor, *args):
    city, region, south, west, north, east = args
    cursor.execute(f"""INSERT INTO cities
                      VALUES ('{city}', '{region}', '{south}', '{west}', '{north}', '{east}')""")
    conn.commit()


def get_wikipedia_cities_table():
    raw_html = requests.get(WIKIPEDIA).text
    soup = BeautifulSoup(raw_html, features='html.parser')
    table = soup.find('table').text
    return table[table.find('1'):].split('\n')[:-1]


def fill_database(table):
    conn, cursor = create_database()
    for row in table:
        city, wiki_region = row.split('  ')[1:3]
        try:
            answer = overpass_request(city)
        except (json.decoder.JSONDecodeError, requests.exceptions.ConnectionError):
            time.sleep(60)
            answer = overpass_request(city)
        for region, bb in answer:
            if not bb:
                continue
            if not region:
                region = wiki_region
            update_database(conn, cursor, city, region, bb['minlat'], bb['minlon'], bb['maxlat'], bb['maxlon'])


def make_cities_db():
    fill_database(get_wikipedia_cities_table())


if __name__ == '__main__':
    conn = sqlite3.connect('cities.db')
    df = pd.read_sql_query("SELECT * FROM cities", conn)
    print(df)
