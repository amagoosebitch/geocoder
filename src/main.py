import sys
import argparse
import sqlite3
import os
from pathlib import Path
import requests
from pymongo import MongoClient
import re
from xml_parser import Parser
import enchant
import psutil
from collections import Counter


DICTIONARY = enchant.Dict('ru_RU')


def main():
    address = setup_and_parse(sys.argv[1:]).geocode
    if "mongod.exe" not in (p.name() for p in psutil.process_iter()):
        mongodb_connect()
    city_info = find_city(address)
    city_info, initial_city = city_info
    city, region, south, west, north, east = city_info
    street, building = find_street_building(address, initial_city)
    if city not in MongoClient('localhost', 27017).list_database_names():
        create_city_db(city, east, west, north, south)
    addresses = remove_duplicates(find_address(city, street, building))
    for addr in addresses:
        full_street, housenumber, lat, lon = parse_answer(addr)
        print(f'Адрес: {region}, {city}, {full_street} {housenumber}.')
        print(f'Координаты: ({lat}, {lon}).')


def remove_duplicates(addresses):
    answer = []
    streets = [x['addr:street'] for x in addresses]
    counter = Counter(streets)
    for street in counter:
        all_dicts = [x for x in addresses if x['addr:street'] == street]
        all_nodes = sum([x['nodes'] for x in all_dicts], [])
        answer.append({'addr:street': street, 'addr:housenumber': all_dicts[0]['addr:housenumber'], 'nodes': all_nodes})
    return answer


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


def find_street_building(address, initial_city):
    regex = re.compile(r'(\d+?.*?)(\w{0,1}$)')
    for value in address:
        value = value.lower().title()
        if value == initial_city:
            continue
        match = re.match(regex, value)
        if match:
            building = value
        else:
            street = value
    return street, building


def parse_answer(answer):
    nodes = answer['nodes']
    lat = []
    lon = []
    if len(nodes) == 0:
        return answer['addr:street'], answer['addr:housenumber'], None, None
    for node in nodes:
        lat.append(float(node[0]))
        lon.append(float(node[1]))
    lat = round(sum(lat)/len(lat), 7)
    lon = round(sum(lon) / len(lon), 7)
    return answer['addr:street'], answer['addr:housenumber'], lat, lon


def find_address(city, street, building):
    to_del = ['Улица', 'Проспект', 'Бульвар', 'Аллея', 'Переулок', 'Тракт', 'Набережная']
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


def create_city_db(city, east, west, north, south):
    if not os.path.isfile(os.path.join(Path(__file__).parent.parent, f'xml/{city}.xml')):
        download_city_xml(city, east, west, north, south)
    print('Создаем базу данных города.')
    parser = Parser(city)
    parser.parse()
    print('База данных успешно создана.')


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


def setup_and_parse(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--geocode', nargs=3, type=str, required=False, metavar=('city', 'street', 'building'),
                        help='Показывает координаты здания и полный адрес по указанному адресу')
    result = parser.parse_args(args)
    return result


def find_city(values):
    conn = sqlite3.connect(os.path.join(Path(__file__).parent.parent, r'db\cities.db'))
    cursor = conn.cursor()
    for value in values:
        value = value.lower().title()
        cursor.execute(f'SELECT * FROM cities WHERE city="{value}"')
        found_value = cursor.fetchone()
        if found_value:
            return found_value, value
    print('Такого города нет в базе данных городов России.')
    sys.exit(-1)


if __name__ == '__main__':
    main()
