import xml.etree.ElementTree as ET

class NecrodancerXml(object):

    def __init__(self, *, filename=None, fileobj=None, data=None):
        args_provided = sum(1 for arg in (filename, fileobj, data) if arg is not None)
        if args_provided != 1:
            raise ValueError('must provide exactly one of `filename`, `fileobj`, `data`')

        if filename:
            self.xml = ET.parse(filename)
        elif fileobj:
            self.xml = ET.parse(fileobj)
        elif data:
            self.xml = ET.fromstring(data)

        root = self.xml.getroot()

        self.items = NecrodancerItems(root.find('items'))
        self.characters = NecrodancerCharacters(root.find('characters'))

    def save(self, filename):
        self.xml.write(filename)


class NecrodancerItems(object):

    def __init__(self, items):
        self.items = items

    def filter(self, **kwargs):
        result = []
        for item in self.items:
            item_matches = True
            for attr, value in kwargs.items():
                if attr == 'name' and item.tag != value:
                    item_matches = False
                    break
                elif item.get(attr) != value:
                    item_matches = False
                    break
            if item_matches:
                result.append(NecrodancerItem(item))
        return result


class NecrodancerItem(object):

    def __init__(self, item):
        object.__setattr__(self, 'item', item)

    def __getattr__(self, name):
        if name == 'name':
            return self.__dict__['item'].tag
        else:
            return self.__dict__['item'].get(name)

    def __setattr__(self, name, value):
        if name == 'name':
            raise AttributeError('cannot modify item name')
        if value is None:
            self.item.attrib.pop(name, None)
        else:
            self.item.set(name, value)

class NecrodancerCharacters(object):

    def __init__(self, characters):
        self.characters = characters

    def set_initial_equipment(self, character_id, build):
        for character in self.characters:
            if character.get('id') == str(character_id):
                initial_equipment = character.find('initial_equipment')
                for item in initial_equipment.findall('item'):
                    initial_equipment.remove(item)
                for nd_item in build:
                    new_item = ET.SubElement(initial_equipment, 'item')
                    new_item.set('type', nd_item.name)
