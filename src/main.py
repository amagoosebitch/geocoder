import argparse
import psutil
from tools import *
from input_parser import InputParser


def main():
    #address = setup_parser(sys.argv[1:]).geocode
    address = ['Первомайская', '04Б', 'Электросталь']
    address_without_commas = [x.replace(',', '') for x in address]
    input_parser = InputParser(address_without_commas, ' '.join(address))
    if "mongod.exe" not in (p.name() for p in psutil.process_iter()):
        mongodb_connect()

    city_info, initial_city = input_parser.find_city(address_without_commas)
    input_parser.set_city(initial_city)

    city, region, south, west, north, east = city_info

    if city not in MongoClient('localhost', 27017).list_database_names():
        create_city_db(city, east, west, north, south)

    building = input_parser.find_building()
    street = input_parser.find_street()
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
    parser.add_argument('-g', '--geocode', nargs='+',type=str, required=False, metavar='input_string',
                        help='Показывает координаты здания и полный адрес по указанному адресу')
    result = parser.parse_args(args)
    print(result)
    return result


if __name__ == '__main__':
    main()
