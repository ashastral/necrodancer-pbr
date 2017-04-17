from argparse import ArgumentParser
import sys

from pbr.pbr import PBR

def main():
    argparser = ArgumentParser(description='command-line interface to the NecroDancer PBR generator')
    argparser.add_argument('seed', type=int, help='the seed to use for random number generation')
    argparser.add_argument('mods_directory', help='where to put the mod folder (typically Crypt of the NecroDancer\'s "mods" directory)')
    argparser.add_argument('-c', '--character', type=int, default=0, help='which character ID to assign the build to')
    args = argparser.parse_args()

    pbr = PBR(args.seed, args.character)
    pbr.process()
    pbr.save(args.mods_directory)

if __name__ == '__main__':
    main()
