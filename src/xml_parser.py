import os
from pathlib import Path
from xml.etree import ElementTree
from pymongo import MongoClient
from src.prefixes_class import Prefixes

NODES_COUNT = 200000
WAYS_COUNT = 100000
RELATIONS_COUNT = 100000


class Parser:
    def __init__(self, city):
        client = MongoClient('localhost', 27017)
        db = client[city]
        self.ways = db['ways']
        self.nodes = db['nodes']
        self.city_file = city + '.xml'
        self.i = 0
        self.nodes_result = []
        self.ways_result = []
        self.nodes_coordinates = {}
        self.ways_coordinates = {}
        self.prefixes = Prefixes()

    def parse(self):
        tree = ElementTree.iterparse(Path(__file__).parent.parent / Path('xml') / f'{self.city_file}')
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
                street_name, street_type = self.normalize_street(tag.attrib['v'])
                result[key] = street_name
                result['addr:street_type'] = street_type
                street = True
            if key == 'addr:housenumber':
                result[key] = self.normalize_building(tag.attrib['v'])
                housenumber = True
        self.nodes_result.append(result)
        if len(self.nodes_result) > NODES_COUNT:
            self.nodes.insert_many(self.nodes_result)
            self.nodes_result = []
        if street and housenumber:
            self.ways.insert_many([result])

    def normalize_street(self, street):
        street_type = None
        street_splited = street.split()
        for part in street.split():
            title_part = part.lower().title()
            if title_part in self.prefixes.street_replacements.keys():
                street_type = title_part
                street_splited.remove(part)
            else:
                for key in self.prefixes.street_replacements.keys():
                    if title_part in self.prefixes.street_replacements[key]:
                        street_type = key
                        street_splited.remove(part)
        street_name = ' '.join([x.lower().title() for x in street_splited])
        return street_name, street_type

    def normalize_building(self, building):
        building = building.replace('.', '')
        result = ''
        for part in building.split():
            for key in self.prefixes.building_replacements.keys():
                if key == part or (len(part) > len(key) and part[:len(key)] == key):
                    part = self.prefixes.building_replacements[key] + ' '
                    break
            result += part + ' '
        result = result.replace('  ', '')
        return result[:-1]

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
                    street_name, street_type = self.normalize_street(child.attrib['v'])
                    result[key] = street_name
                    result['addr:street_type'] = street_type
                    street = True
                if key == 'addr:housenumber':
                    result[key] = self.normalize_building(child.attrib['v'])
                    housenumber = True
        if street and housenumber:
            result['nodes'] = tuple(nodes)
            self.ways_result.append(result)
            self.ways_coordinates[attributes['id']] = tuple(nodes)
            if len(self.ways_result) > WAYS_COUNT:
                self.ways.insert_many(self.ways_result)
                self.ways_result = []


if __name__ == '__main__':
    Parser('Челябинск').parse()
