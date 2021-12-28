import xml.etree.ElementTree as ET


def is_building(elem):
    street_flag = False
    housenumber_flag = False
    for child in elem:
        if child.tag == 'tag' and 'addr:street' in child.attrib['k']:
            street_flag = True
        if child.tag == 'tag' and 'addr:housenumber' in child.attrib['k']:
            housenumber_flag = True
        if street_flag and housenumber_flag:
            return True
    return False


node_tags = set()
way_tags = set()
tree = ET.iterparse('Пермь.xml')
rows_count = 0
for event, elem in tree:
    rows_count += 1
    if elem.tag == 'node':
        for tag in list(elem):
            key = tag.attrib['k'].lower()
            if key not in ['id', 'lat', 'lon']:
                node_tags.add(key)
        elem.clear()
    elif elem.tag == 'way':
        for child in list(elem):
            if child.tag == 'tag':
                key = child.attrib['k'].lower()
                if key not in ['id', 'nodes']:
                    way_tags.add(key)
        elem.clear()
    elif elem.tag == 'relation':
        is_building = is_building(list(elem))
        for child in list(elem):
            if child.tag == 'tag' and is_building:
                key = child.attrib['k'].lower()
                if key not in ['id', 'nodes']:
                    way_tags.add(key)
        elem.clear()
t = 0