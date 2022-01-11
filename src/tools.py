import sqlite3
import os
from pathlib import Path
import sys
import requests
from xml_parser import Parser
from pymongo import MongoClient
import re
from collections import Counter
from prefixes_class import Prefixes


def download_city_xml(city, east, west, north, south):
    url = f"https://overpass-api.de/api/map?bbox=" \
          f"{west},{south},{east},{north}"
    print('Делаем запрос.')
    response = requests.get(url, stream=True)
    print('Ответ получен. Скачиваем xml файл.')
    with open(os.path.join(Path(__file__).parent.parent, f'xml/{city}.xml'), 'wb') as f:
        for chunk in response.iter_content(chunk_size=10 * 1024 * 1024):
            if chunk:
                f.write(chunk)
    print('Загрузка окончена')


def create_city_db(city, east, west, north, south):
    if not os.path.isfile(os.path.join(Path(__file__).parent.parent, f'xml/{city}.xml')):
        download_city_xml(city, east, west, north, south)
    print('Создаем базу данных города.')
    parser = Parser(city)
    parser.parse()
    print('База данных успешно создана.')


def find_address(city, street, building):
    print(city, street, building)
    prefixes_class = Prefixes()
    to_del = prefixes_class.street_prefixes[:8]
    if ' ' in street:
        part1, part2 = street.split()
        if part1 in to_del:
            street = part2
        else:
            street = part1
    client = MongoClient('localhost', 27017)
    ways = client[city]['ways']
    cursor = ways.find({'addr:housenumber': f'{building}', 'addr:street': re.compile(rf'.*?{street}.*?')})
    addresses = []
    for c in cursor:
        addresses.append(c)
    if len(addresses) == 0:
        print('Адрес не найден.')
        sys.exit(-2)
    return addresses


def mongodb_connect():
    config_path = os.path.join(Path(__file__).parent.parent, 'config/config.txt')
    if not os.path.isfile(config_path):
        print('Файл config.txt отсутствует. Создайте файл в папке config и впишите туда путь до mongod.exe.')
        sys.exit(-4)
    with open(config_path, 'r') as file:
        mongodb_path = file.readline()
    try:
        os.startfile(mongodb_path)
    except:  # windows error?
        print('Не удалось запустить MongoDB. Убедитесь в том, что правильно указали путь до bin папки вашего MongoDB.')
        sys.exit(-5)


def remove_duplicates(addresses):
    answer = []
    streets = [x['addr:street'] for x in addresses]
    counter = Counter(streets)
    for street in counter:
        all_dicts = [x for x in addresses if x['addr:street'] == street]
        all_nodes = sum([x['nodes'] for x in all_dicts], [])
        answer.append({'addr:street': street, 'addr:housenumber': all_dicts[0]['addr:housenumber'], 'nodes': all_nodes})
    return answer
