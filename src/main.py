import sys
import argparse
import sqlite3
import os
import requests
from mongita import MongitaClientDisk
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
        if value == city:
            continue
        else:
            match = re.match(regex, value)
            if match:
                building = value
            else:
                street = value
    building = building.lower().title()
    street = street.lower().title()
    path = os.path.abspath(__file__)[:-11] + f'db-mongita\\{city}'
    if not os.path.exists(path) or len(os.listdir(path)) == 0:
        create_city_db(city, east, west, north, south)
    address = find_address(city, street, building)
    if not address:
        print('Адрес не найден.')
        sys.exit(-2)
    if len(address) > 1:
        print('TODO: найдено несколько адресов.')
        sys.exit(-3)
    full_street, housenumber, lat, lon = parse_answer(address[0])
    print(f'Адрес: {region}, {city}, {full_street} {housenumber}.')
    print(f'Координаты: ({lat}, {lon}).')


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
    answer = []
    to_del = ['улица', 'проспект', 'бульвар', 'аллея', 'переулок', 'тракт', 'набережная']
    if ' ' in street:
        part1, part2 = street.split()
        if part1 in to_del:
            street = part2
        else:
            street = part1
    client = MongitaClientDisk(os.path.abspath(__file__)[:-11] + f'db-mongita\\{city}')
    ways = client.db.ways
    for extra in to_del:
        current_street1 = street + ' ' + extra
        current_street2 = extra + ' ' + street
        cursor = ways.find({'addr:housenumber': building, 'addr:street': current_street1})
        for c in cursor:
            answer.append(c)
        if len(answer) == 0:
            cursor = ways.find({'addr:housenumber': building, 'addr:street': current_street2})
            for c in cursor:
                answer.append(c)
            if len(answer) == 0:
                continue
            else:
                return answer
        else:
            return answer
    return None


def create_city_db(city, east, west, north, south):
    if not os.path.isfile(os.path.abspath(__file__)[:-11] + f'xml\\{city}.xml'):
        download_city_xml(city, east, west, north, south)
    print('Создаем базу данных города.')
    parser = Parser(city)
    parser.parse()
    print('База данных успешно создана.')


def download_city_xml(city, east, west, north, south):
    url = f"https://overpass-api.de/api/map?bbox=" \
          f"{west},{south},{east},{north}"
    print('Делаем запрос')
    response = requests.get(url, stream=True)
    print('Ответ получен. Скачиваем xml файл')
    with open(os.path.abspath(__file__)[:-11] + f'xml\\{city}.xml', 'wb') as f:
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
