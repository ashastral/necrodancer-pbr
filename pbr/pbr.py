import os
from random import Random
import shutil

from pbr.necrodancerxml import NecrodancerXml

class PBR(object):

    resources_dir = os.path.join(os.path.dirname(__file__), 'resources')

    def __init__(self, seed, character_id=0):
        self.ndxml = NecrodancerXml(filename=os.path.join(PBR.resources_dir, 'necrodancer.xml'))
        self.seed = seed
        self.character_id = character_id

    def process(self):
        BuildRandomizer(self.ndxml).process(self.seed, self.character_id)
        ItemRebalancer(self.ndxml).process()

    def save(self, mods_directory):
        output_directory = os.path.join(mods_directory, 'pbr_{}'.format(self.seed))
        shutil.copytree(os.path.join(PBR.resources_dir, 'mod_base'), output_directory)
        self.ndxml.save(os.path.join(output_directory, 'necrodancer.xml'))


class BuildRandomizer(object):

    def __init__(self, ndxml):
        self.ndxml = ndxml

    def process(self, seed, character_id):
        self.rng = Random(seed)
        self.build = []
        self.set_shovel()
        self.set_headgear()
        self.set_armor()
        self.set_footwear()
        self.set_torch()
        self.set_ring()
        self.set_spells()
        self.set_hud()
        self.set_misc()
        self.set_weapon()
        self.ndxml.characters.set_initial_equipment(character_id, self.build)

    def pick_slot(self, slot, excluded_names=()):
        choices = []
        for item in self.ndxml.items.filter(slot=slot):
            if item.name not in excluded_names:
                choices.append(item)
        return self.rng.choice(choices)

    def set_slot(self, slot, excluded_names=()):
        self.build.append(self.pick_slot(slot, excluded_names))

    def set_shovel(self):
        self.set_slot('shovel', ('shovel_shard', 'shovel_basic'))

    def set_headgear(self):
        self.set_slot('head', ('head_glass_jaw', 'head_ninja_mask', 'head_crown_of_greed', 'head_sonar'))

    def set_armor(self):
        self.set_slot('body', ('armor_platemail_dorian', 'armor_gi'))

    def set_footwear(self):
        self.set_slot('feet', ('feet_boots_speed'))

    def set_torch(self):
        self.set_slot('torch')

    def set_ring(self):
        self.set_slot('ring', ('ring_shadows', 'ring_phasing', 'ring_becoming', 'ring_wonder'))

    def set_spells(self):
        excluded_spells = ('spell_transmute', 'spell_pulse', 'spell_charm', 'spell_transform')
        spell = self.pick_slot('spell', excluded_spells)
        self.build.append(spell)
        if self.rng.randrange(4) == 0:
            self.set_slot('spell', excluded_spells + (spell.name,))

    def set_hud(self):
        if self.rng.randrange(2) == 0:
            self.build += self.ndxml.items.filter(name='hud_backpack')
        else:
            self.build += self.ndxml.items.filter(name='holster')

    def set_misc(self):
        roll_1d10 = (lambda: self.rng.randrange(10) == 0)
        for item in self.ndxml.items.filter(slot='misc'):
            if item.name not in (   'misc_golden_key', 'misc_golden_key2', 'misc_golden_key3',
                                    'misc_glass_key', 'misc_key', 'misc_magnet', 'misc_potion',
                                    'charm_bomb', 'charm_grenade', 'charm_luck'):
                if roll_1d10():
                    self.build.append(item)

    def set_weapon(self):
        weapons = []
        for weapon in self.ndxml.items.filter(slot='weapon'):
            # Skip character-specific weapons
            if weapon.name in ('weapon_eli', 'weapon_fangs', 'weapon_flower', 'weapon_golden_lute'):
                continue
            # Skip non-special daggers
            if weapon.isDagger and weapon.name not in ( 'weapon_dagger_electric', 'weapon_dagger_jeweled',
                                                        'weapon_dagger_frost', 'weapon_dagger_phasing'):
                continue
            # Skip whips because fuck whips
            if weapon.isWhip:
                continue
            # Skip blood, gold, and glass weapon types
            if weapon.isBlood or weapon.isGold or weapon.isGlass:
                continue
            # Skip base weapon types
            if not (weapon.isDagger or weapon.isBlood or weapon.isGold or weapon.isTitanium
                    or weapon.isObsidian or weapon.isGlass or weapon.isRifle or weapon.isBlunderbuss):
                continue
            weapons.append(weapon)
        self.build.append(self.rng.choice(weapons))


class ItemRebalancer(object):

    def __init__(self, ndxml):
        self.ndxml = ndxml

    def process(self):
        all_items = self.ndxml.items.filter()
        for item in all_items:

            ### General removals

            # Remove spells & rings altogether
            if item.slot in ('spell', 'ring'):
                self.remove_item_chances(item)
            # Remove transmute scroll & tome
            if item.slot == 'action' and item.spell == 'spell_transmute':
                self.remove_item_chances(item)
            # Remove other items that are too powerful
            if item.name in (   'feet_boots_leaping', 'feet_boots_lunging', 'feet_boots_pain',
                                'food_magic_3', 'food_magic_4', 'food_magic_cookies',
                                'head_miners_cap', 'head_monocle', 'head_glass_jaw',
                                'bag_holding', 'misc_map', 'misc_compass', 'charm_strength',
                                'scroll_enchant_weapon', 'scroll_need',
                                'shovel_courage', 'torch_walls'):
                self.remove_item_chances(item)

            # Remove move-attack weapons, special daggers, and guns
            if item.isAxe or item.isCat or item.isRapier:
                self.remove_item_chances(item)
            elif item.name in ( 'weapon_dagger_electric', 'weapon_dagger_jeweled',
                                'weapon_dagger_frost', 'weapon_dagger_phasing'):
                self.remove_item_chances(item)
            elif item.isRifle or item.isBlunderbuss:
                self.remove_item_chances(item)
            # Restrict all other weapons besides blood and gold to locked shops
            elif item.isWeapon and not (item.isBlood or item.isGold):
                self.restrict_to_locked_shops(item)

            # Remove headgear, armor, and footwear from chests and crates
            if item.slot in ('head', 'body', 'feet'):
                item.chestChance = None
                item.lockedChestChance = None

            # Restrict damage-up equipment to locked shops
            if item.name in (   'feet_boots_strength', 'head_sunglasses', 'head_spiked_ears',
                                'shovel_strength', 'torch_strength'):
                self.restrict_to_locked_shops(item, locked_shop_chance='100')

            # Restrict charms and other 'misc' items to locked shops
            if item.slot == 'misc':
                self.restrict_to_locked_shops(item)

            # Remove EVERYTHING from the boss chests
            self.remove_from_boss_chests(item)
            # Restrict armor to the boss chests (black)
            if item.slot == 'body' and item.name not in ('armor_leather', 'armor_platemail_dorian', 'armor_gi'):
                self.restrict_to_boss_chests(item)
            # Restrict bomb-related items to the boss chests (red)
            if item.name in ('head_blast_helm', 'charm_grenade', 'bomb_3'):
                self.restrict_to_boss_chests(item)
            # Add back scrolls and tomes to the boss chests (purple)
            if item.isScroll and item.name not in ( 'scroll_fear', 'scroll_gigantism', 'scroll_riches',
                                                    'scroll_enchant_weapon', 'scroll_need', 'scroll_pulse',
                                                    'scroll_transmute', 'tome_pulse', 'tome_transmute'):
                self.add_to_boss_chests(item)

    def remove_item_chances(self, item):
        item.chestChance = None
        item.shopChance = None
        item.lockedChestChance = None
        item.lockedShopChance = None
        item.urnChance = None

    def restrict_to_locked_shops(self, item, locked_shop_chance=None):
        if locked_shop_chance is None:
            locked_shop_chance = item.lockedShopChance
        self.remove_item_chances(item)
        item.lockedShopChance = locked_shop_chance

    def add_to_boss_chests(self, item):
        chances = ItemChances(item.chestChance)
        chances.set_chance(4, '1')
        item.chestChance = str(chances)

    def remove_from_boss_chests(self, item):
        if item.chestChance:
            chances = ItemChances(item.chestChance)
            chances.remove_chances_past(4)
            item.chestChance = str(chances)

    def restrict_to_boss_chests(self, item):
        self.remove_item_chances(item)
        self.add_to_boss_chests(item)

    def print_item_chances(self, item):
        print('{}: chestChance={}, shopChance={}, lockedChestChance={}, lockedShopChance={}, urnChance={}'
            .format(item.name, item.chestChance, item.shopChance, item.lockedChestChance, item.lockedShopChance, item.urnChance))


class ItemChances(object):
    def __init__(self, string):
        if string:
            self.chances = string.split('|')
        else:
            self.chances = ['0']

    def get_chance(self, floor):
        if floor >= len(self.chances):
            floor = len(self.chances) - 1
        return self.chances[floor]

    def set_chance(self, floor, chance):
        chance = str(chance)
        if floor >= len(self.chances):
            for _ in range(len(self.chances), floor):
                self.chances.append(self.chances[-1])
            self.chances.append(chance)
        else:
            self.chances[floor] = chance
        self.cleanup()

    def remove_chances_past(self, floor):
        if floor >= len(self.chances):
            self.set_chance(floor, '0')
        else:
            self.chances = self.chances[:floor]
            self.chances.append('0')
        self.cleanup()

    def cleanup(self):
        while len(self.chances) > 1 and self.chances[-1] == self.chances[-2]:
            self.chances.pop()

    def __str__(self):
        return '|'.join(self.chances)

    def __repr__(self):
        return str(self)
