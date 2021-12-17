import sys
import argparse


def main():
    args = setup_and_parse(sys.argv[1:])


def setup_and_parse(args):
    parser = argparse.ArgumentParser()
    #parser.add_mutually_exclusive_group()
    parser.add_argument('-g', '--geocoder', nargs=3, type=str, required=False, metavar='address',
                        help='Показывает координаты здания по указанному адресу')
    result = parser.parse_args(args)
    check_args(result)
    return result


def check_args(args):
    return


if __name__ == '__main__':
    main()


