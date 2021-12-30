import os
from xml.etree import ElementTree
from mongita import MongitaClientDisk
#from pymongo import MongoClient

NODES_COUNT = 200000
WAYS_COUNT = 100000
RELATIONS_COUNT = 100000


class Parser:
    def __init__(self, city):
        path = os.path.abspath(__file__)[:-17] + f'db-mongita\\{city}'
        if not os.path.exists(path):
            os.makedirs(path)
        client = MongitaClientDisk(path)
        db = client['db']
        self.ways = db['ways']
        self.nodes = db['nodes']
        self.city_file = city + '.xml'
        self.i = 0
        self.nodes_result = []
        self.ways_result = []
        self.nodes_coordinates = {}
        self.ways_coordinates = {}

    def parse(self):
        tree = ElementTree.iterparse(os.path.abspath(__file__)[:-17] + f'xml\\{self.city_file}')
        for _, element in tree:
            if element.tag == 'node':
                self.parse_node(element)
                element.clear()
            elif element.tag == 'way':
                if len(self.nodes_result) > 0:
                    self.nodes.insert_many(self.nodes_result)
                    self.nodes_result = []
                self.parse_way(element)
                element.clear()
        if len(self.ways_result) > 0:
            self.ways.insert_many(self.ways_result)
            self.ways_result = []
        del tree

    def parse_node(self, elem):
        tags = list(elem)
        attr = elem.attrib
        result = {'id': attr['id'], 'lat': attr['lat'], 'lon': attr['lon']}
        self.nodes_coordinates[attr['id']] = (attr['lat'], attr['lon'])
        street = False
        housenumber = False
        for tag in tags:
            key = tag.attrib['k'].lower()
            if key == 'addr:street':
                result[key] = tag.attrib['v']
                street = True
            if key == 'addr:housenumber':
                result[key] = tag.attrib['v']
                housenumber = True
        self.nodes_result.append(result)
        if len(self.nodes_result) > NODES_COUNT:
            self.nodes.insert_many(self.nodes_result)
            self.nodes_result = []
        if street and housenumber:
            self.ways.insert_many([result])

    def parse_way(self, way):
        subelements = list(way)
        attributes = way.attrib
        result = {'id': attributes['id']}
        nodes = []
        street = False
        housenumber = False
        for child in subelements:
            if child.tag == 'nd':
                ref = child.attrib['ref']
                nodes.append(self.nodes_coordinates[ref])
            elif child.tag == 'tag':
                key = child.attrib['k'].lower()
                if key == 'addr:street':
                    street = True
                    result[key] = child.attrib['v']
                if key == 'addr:housenumber':
                    housenumber = True
                    result[key] = child.attrib['v']
        if street and housenumber:
            result['nodes'] = tuple(nodes)
            self.ways_result.append(result)
            self.ways_coordinates[attributes['id']] = tuple(nodes)
            if len(self.ways_result) > WAYS_COUNT:
                self.ways.insert_many(self.ways_result)
                self.ways_result = []


if __name__ == '__main__':
    Parser('Челябинск').parse()
