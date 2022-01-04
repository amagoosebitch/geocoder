import argparse
import enchant
import psutil
from tools import *


DICTIONARY = enchant.Dict('ru_RU')


def main():
    address = setup_parser(sys.argv[1:]).geocode
    if "mongod.exe" not in (p.name() for p in psutil.process_iter()):
        mongodb_connect()
    city_info, initial_city = find_city(address)
    city, region, south, west, north, east = city_info
    street, building = find_street_building(address, initial_city)
    if city not in MongoClient('localhost', 27017).list_database_names():
        create_city_db(city, east, west, north, south)
    addresses = remove_duplicates(find_address(city, street, building))
    for addr in addresses:
        full_street, housenumber, lat, lon = parse_answer(addr)
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


def setup_parser(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-g', '--geocode', nargs=3, type=str, required=False, metavar=('city', 'street', 'building'),
                        help='Показывает координаты здания и полный адрес по указанному адресу')
    result = parser.parse_args(args)
    print(result)
    return result


if __name__ == '__main__':
    main()
