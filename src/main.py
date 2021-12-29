import sys
import argparse
import sqlite3
import os
import requests
import mongita
import re
from xml_parser import Parser


def main():
    address = setup_and_parse(sys.argv[1:]).geocode
    city_info = find_city(address)
    if not city_info:
        print('Такого города нет в базе данных городов России.')
        sys.exit(-1)
    city, region, south, west, north, east = city_info
    street = [x for x in address
              if x.lower().title() != city
              and not any(char.isdigit() for char in x)][0]
    regex = re.compile(r"(\d+?.*?)(\w{0,1}$)")
    for value in address:
        if value == street:
            continue
        else:
            match = re.match(regex, value)
            if match:
                building = value
            else:
                street = value
    building = [x for x in address if x != city.lower().title() and x != street][0]
    street = street.lower().title()
    if not os.path.isdir(os.path.abspath(__file__)[:-11] + f'db-mongita\\{city}'):
        create_city_db(city, east, west, north, south)


def find_address(city, street, building):
    to_del = ['Улица', 'Проспект', 'Бульвар', 'Аллея', 'Переулок', 'Тракт', 'Набережная']
    if ' ' in street:
        part1, part2 = street.split()
        if part1 in to_del:
            street = part2
        else:
            street = part1
    path = os.path.abspath(__file__)[:-11] + f'db-mongita\\{city}'
    client = mongita.MongitaClientDisk(host=path)
    ways = client.db.ways
    cursor = ways.find({'addr:housenumber': f'{building}', 'addr:street': 'Валовая улица'})


def create_city_db(city, east, west, north, south):
    if not os.path.isfile(os.path.abspath(__file__)[:-11] + f'xml\\{city}.xml'):
        download_city_xml(city, east, west, north, south)
    parser = Parser(city)
    parser.parse()


def download_city_xml(city, east, west, north, south):
    url = f"https://overpass-api.de/api/map?bbox=" \
          f"{west},{south},{east},{north}"
    print('Делаем запрос')
    response = requests.get(url, stream=True)
    print('Ответ получен. Скачиваем файл')
    with open(f"{city}.xml", 'wb') as f:
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
    conn = sqlite3.connect(os.path.abspath(__file__)[:-11] + r'db\cities.db')
    cursor = conn.cursor()
    for value in values:
        cursor.execute(f'SELECT * FROM cities WHERE city="{value.lower().title()}"')
        found_value = cursor.fetchone()
        if found_value:
            return found_value


if __name__ == '__main__':
    main()
