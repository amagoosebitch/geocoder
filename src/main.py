import sys
import argparse
import sqlite3
import os
import requests
from xml.dom import minidom


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
    building = [x for x in address if x != city.lower().title() and x != street][0]
    street = street.lower().title()

    # url = f"https://overpass-api.de/api/map?bbox=" \
    #       f"{west},{south},{east},{north}"
    # print('Делаем запрос')
    # response = requests.get(url, stream=True)
    # print('Ответ получен. Скачиваем файл')
    # with open(f"{city}.xml", 'wb') as f:
    #     for chunk in response.iter_content(chunk_size=10 * 1024 * 1024):
    #         if chunk:
    #             f.write(chunk)
    # print('Загрузка окончена')


def setup_and_parse(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--geocode', nargs=3, type=str, required=False, metavar=('city', 'street', 'building'),
                        help='Показывает координаты здания и полный адрес по указанному адресу')
    result = parser.parse_args(args)
    return result


def find_city(values):
    conn = sqlite3.connect(os.getcwd()[:-3] + r'db\cities.db')
    cursor = conn.cursor()
    for value in values:
        cursor.execute(f'SELECT * FROM cities WHERE city="{value.lower().title()}"')
        found_value = cursor.fetchone()
        if found_value:
            return found_value


if __name__ == '__main__':
    main()