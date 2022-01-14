import argparse
from src.tools import *
from src.input_parser import InputParser


def main():
    splitted_address = setup_parser(sys.argv[1:]).geocode
    # splitted_address = ['Екатеринбург, Малышева 25']
    print("до убирания кавычек")
    print(splitted_address)
    # splitted_address = ['Санкт-Петербург,', 'Сапёрный', 'переулок,', '13', 'лит', 'Г']
    # splitted_address = ['Санкт-Петербург', 'малый', 'проспект,', '64/39']
    temp = []
    for i in range(len(splitted_address)):
        temp += splitted_address[i].replace("'", '').replace('"', '').split()
    splitted_address = temp

    print("после")
    print(splitted_address)

    #
    # # splitted_address = ["Екатеринбург", "Баумана", "2"]
    input_parser = InputParser(splitted_address, ' '.join(splitted_address).replace('\'', '').replace('"',''))
    city_info, initial_city, street, street_type, building = input_parser.parse()
    print(initial_city, street, building)
    city, region, south, west, north, east = city_info

    database_names = MongoClient('localhost', 27017).list_database_names()
    if city.replace(' ', "_") not in database_names:
        create_city_db(city, east, west, north, south)

    addresses = remove_duplicates(find_address(city.replace(' ', '_'), street, street_type, building))

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
    parser.add_argument('-g', '--geocode', nargs='+', type=str, required=False, metavar='input_string',
                        help='Показывает координаты здания и полный адрес по указанному адресу')
    result = parser.parse_args(args)
    return result


if __name__ == '__main__':
    main()
