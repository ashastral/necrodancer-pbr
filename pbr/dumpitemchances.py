import xlsxwriter

from pbr import ItemChances
from necrodancerxml import NecrodancerXml

class DumpItemChances:

    def __init__(self, ndxml):
        self.ndxml = ndxml

    def write(self, filename):
        wb = xlsxwriter.Workbook(filename)

        formats = []
        for i in range(256):
            format = wb.add_format()
            format.set_bg_color('#{0:02x}ff{0:02x}'.format(255 - i))
            formats.append(format)

        for chanceType in ('chestChance', 'lockedChestChance', 'shopChance', 'lockedShopChance'):
            sums = [0, 0, 0, 0, 0]
            maxima = [0, 0, 0, 0, 0]
            for item in self.ndxml.items.filter():
                chances = ItemChances(item.__getattr__(chanceType))
                for level in range(5):
                    chance = int(chances.get_chance(level))
                    sums[level] += chance
                    maxima[level] = max(maxima[level], chance)

            sheet = wb.add_worksheet(chanceType)
            for row, item in enumerate(self.ndxml.items.filter(), start=1):
                sheet.write(row, 0, item.name)
                chances = ItemChances(item.__getattr__(chanceType))
                for level in range(5):
                    chance = int(chances.get_chance(level))
                    format_index = int(255 * chance / maxima[level])
                    sheet.write(row, level + 1, chance, formats[format_index])

        wb.close()

def main():
    ndxml = NecrodancerXml(path='necrodancer_123.xml')
    dumper = DumpItemChances(ndxml)
    dumper.write('chances-123.xlsx')

if __name__ == '__main__':
    main()
