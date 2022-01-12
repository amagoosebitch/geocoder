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
    with open(Path(__file__).parent.parent / Path('xml') / f'{city}.xml', 'wb') as f:
        for chunk in response.iter_content(chunk_size=10 * 1024 * 1024):
            if chunk:
                f.write(chunk)
    print('Загрузка окончена')


def create_city_db(city, east, west, north, south):
    if not os.path.isfile(Path(__file__).parent.parent / Path('xml') / f'{city}.xml'):
        download_city_xml(city, east, west, north, south)
    print('Создаем базу данных города.')
    parser = Parser(city)
    parser.parse()
    print('База данных успешно создана.')


def find_address(city, street, street_type, building, second_iteration=False):
    client = MongoClient('localhost', 27017)
    ways = client[city]['ways']
    cursor = ways.find({'addr:housenumber': f'{building}', 'addr:street': re.compile(rf'.*?{street}.*?')})
    addresses = []
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


def mongodb_connect():
    config_path = Path(__file__).parent.parent / Path('config') / 'config.txt'
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


def levenshtein_distance(first, second):
    """работает без учёта регистра"""
    first_string = first.lower()
    second_string = second.lower()
    opt = []
    for i in range(len(first_string) + 1):
        opt.append([0]*(len(second_string) + 1))

    for i in range(len(first_string) + 1):
        opt[i][0] = i

    for i in range(len(second_string) + 1):
        opt[0][i] = i

    for i in range(1, len(first_string)+1):
        for j in range(1, len(second_string) + 1):
            left = opt[i-1][j]
            up = opt[i][j-1]
            diagonal = opt[i-1][j-1]
            if first_string[i-1] == second_string[j-1]:
                opt[i][j] = diagonal
            else:
                opt[i][j] = 1 + min(left+1, up+1, diagonal)

    return opt[-1][-1]

