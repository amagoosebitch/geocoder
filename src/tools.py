import sqlite3
import os
from pathlib import Path
import sys
import requests
from src.xml_parser import Parser
from pymongo import MongoClient
import re
from collections import Counter
from fuzzywuzzy import process


def download_city_xml(city, east, west, north, south):
    url = f"https://overpass-api.de/api/map?bbox=" \
          f"{west},{south},{east},{north}"
    print('Делаем запрос.')
    response = requests.get(url, stream=True)
    print('Ответ получен. Скачиваем xml файл.')
    with open(Path(__file__).parent.parent / Path('xml') / f'{city.replace(" ", "_")}.xml', 'wb') as f:
        for chunk in response.iter_content(chunk_size=10 * 1024 * 1024):
            if chunk:
                f.write(chunk)
    print('Загрузка окончена')


def create_city_db(city, east, west, north, south):
    if not os.path.isfile(Path(__file__).parent.parent / Path('xml') / f'{city.replace(" ", "_")}.xml'):
        download_city_xml(city, east, west, north, south)
    print('Создаем базу данных города.')
    parser = Parser(city)
    parser.parse()
    print('База данных успешно создана.')


def find_address(city, street, street_type, building, second_iteration=False):
    client = MongoClient('localhost', 27017)
    ways = client[city]['ways']
    street_keys = ['addr:street', 'addr:street2']
    addresses = []
    for street_key in street_keys:
        cursor = ways.find({'addr:housenumber': f'{building}', street_key: re.compile(rf'.*?{street}.*?')})
        for c in cursor:
            addresses.append(c)
    if len(addresses) == 0 and not second_iteration:
        possible_street = handle_mistake_in_street(ways, street)
        if not possible_street:
            print('Адрес не найден.')
            sys.exit(-2)
        else:
            return find_address(city, possible_street, street_type, building, True)
    elif len(addresses) == 0 and second_iteration:
        print('Адрес не найден.')
        sys.exit(-2)
    else:
        return addresses


def handle_mistake_in_street(ways, street):
    possible_street = None
    streets = ways.distinct('addr:street')
    possible_street, coef = process.extractOne(street, streets)
    return possible_street


def remove_duplicates(addresses):
    answer = []
    streets = [x['addr:street'] for x in addresses]
    counter = Counter(streets)
    for street in counter:
        all_dicts = [x for x in addresses if x['addr:street'] == street]
        all_nodes = []
        for dict in all_dicts:
            if 'nodes' in dict.keys():
                all_nodes += dict['nodes']
            elif 'lat' in dict.keys() and 'lon' in dict.keys():
                all_nodes.append([dict['lat'], dict['lon']])
        answer.append({'addr:street': street, 'addr:housenumber': all_dicts[0]['addr:housenumber'], 'nodes': all_nodes})
    return answer

