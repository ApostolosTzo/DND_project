class Weapon:
    def __init__(self, name, damage_dice, damage_type, properties=None, stats_bonus=None):
        self.name = name
        self.damage_dice = damage_dice
        self.damage_type = damage_type
        self.properties = properties or []
        self.stats_bonus = stats_bonus or {}
        self.category = "weapon"

class Armor:
    def __init__(self, name, base_ac, armor_type, dex_limit=None, properties=None, stats_bonus=None):
        self.name = name
        self.base_ac = base_ac
        self.armor_type = armor_type
        self.dex_limit = dex_limit
        self.properties = properties or []
        self.stats_bonus = stats_bonus or {}
        self.category = "armor"

class Item:
    def __init__(self, name, description, effect=None, stats_bonus=None):
        self.name = name
        self.description = description
        self.effect = effect
        self.stats_bonus = stats_bonus or {}
        self.category = "item"

ITEMS = {
    
    # Weapons (melee)
    "Longsword": Weapon("Longsword", "1d8", "slashing", ["versatile"], stats_bonus={"STR": 1}),
    "Greatsword": Weapon("Greatsword", "2d6", "slashing", ["two-handed", "heavy"], stats_bonus={"STR": 2}),
    "Battle Axe": Weapon("Battle Axe", "1d8", "slashing", ["versatile"], stats_bonus={"STR": 1}),
    "War Hammer": Weapon("War Hammer", "1d10", "bludgeoning", ["versatile"], stats_bonus={"STR": 1}),
    "Mace": Weapon("Mace", "1d6", "bludgeoning", ["versatile"], stats_bonus={"STR": 1}),
    "Flail": Weapon("Flail", "1d8", "bludgeoning", ["versatile"], stats_bonus={"STR": 1}),
    "Spear": Weapon("Spear", "1d6", "piercing", ["versatile", "thrown"], stats_bonus={"STR": 1}),
    "Rapier": Weapon("Rapier", "1d8", "piercing", ["finesse"], stats_bonus={"DEX": 1}),
    "Dagger": Weapon("Dagger", "1d4", "piercing", ["finesse", "light", "thrown"], stats_bonus={"DEX": 1}),
    "Quarterstaff": Weapon("Quarterstaff", "1d6", "bludgeoning", ["versatile"], stats_bonus={"STR": 1}),
    
    # Weapons (ranged)
    "Shortbow": Weapon("Shortbow", "1d6", "piercing", ["two-handed", "ranged"], stats_bonus={"DEX": 1}),
    "Longbow": Weapon("Longbow", "1d8", "piercing", ["two-handed", "ranged", "heavy"], stats_bonus={"DEX": 1}),
    "Crossbow": Weapon("Crossbow", "1d10", "piercing", ["two-handed", "ranged", "loading"], stats_bonus={"DEX": 1}),
    "Hand Crossbow": Weapon("Hand Crossbow", "1d6", "piercing", ["ranged", "light"], stats_bonus={"DEX": 1}),
    
    # Weapons (magical)
    "Magic Staff": Weapon("Magic Staff", "1d6", "bludgeoning", ["versatile", "magic"]),
    "Arcane Staff": Weapon("Arcane Staff", "1d8", "force", ["two-handed", "magic"], stats_bonus={"INT": 1}),
    "Wand": Weapon("Wand", "1d4", "force", ["magic", "ranged"]),
    "Lampada": Weapon("Lampada", "1d6", "fire_damage", ["versatile", "magic"]),
    
    # Armors (light)
    "Leather": Armor("Leather", 11, "light"),
    "Studded Leather": Armor("Studded Leather", 12, "light", stats_bonus={"DEX": 1}),
    
    # Armors (medium)
    "Hide": Armor("Hide", 13, "medium", 2),
    "Chainmail": Armor("Chainmail", 14, "medium", 2), 
    "Scale Mail": Armor("Scale Mail", 14, "medium", 2),
    "Breastplate": Armor("Breastplate", 14, "medium", 2),
    "Half Plate": Armor("Half Plate", 15, "medium", 2),
    
    # Armors (heavy)
    "Ring Mail": Armor("Ring Mail", 14, "heavy"),
    "Plate": Armor("Plate", 17, "heavy"),
    "Splint": Armor("Splint", 17, "heavy"),
    "Titanium": Armor("Titanium", 18, "heavy"),
    "Dragon Scale": Armor("Dragon Scale", 19, "heavy", stats_bonus={"CON": 8}),
    
    # Shields
    "Shield": Armor("Shield", 2, "shield"),
    "Iron Shield": Armor("Iron Shield", 3, "shield", stats_bonus={"STR": 1, "DEX": 3}),
    "Tower Shield": Armor("Tower Shield", 4, "shield", stats_bonus={"STR": 2, "DEX": 2}),
    "Magic Shield": Armor("Magic Shield", 5, "shield", stats_bonus={"INT": 2, "WIS": 2}),
    "Dragon Shield": Armor("Dragon Shield", 6, "shield", stats_bonus={"STR": 4, "DEX": 4, "CON": 4}),
    "Aegis Shield": Armor("Aegis Shield", 7, "shield", stats_bonus={"STR": 5, "DEX": 5, "CON": 5}),
    
    # Special armor
    "Wizard Robe": Armor("Wizard Robe", 10, "light", properties=["magic"], stats_bonus={"INT": 9}),
    
    # Items (potions & consumables)
    "Healing Potion": Item("Healing Potion", "Restores 9 HP", "heal"),
    "Greater Healing Potion": Item("Greater Healing Potion", "Restores 20 HP", "heal_strong"),
    #"Mana Potion": Item("Mana Potion", "Restores mana (future use)", "mana"),
    #"Antidote": Item("Antidote", "Cures poison (future use)", "antidote"),
    
    # Items (scrolls - future use)
    "Scroll of Fireball": Item("Scroll of Fireball", "Deals fire damage (future use)", "scroll_fireball"),
    "Scroll of Healing": Item("Scroll of Healing", "Heals ally (future use)", "scroll_heal"),
    
    # Items (misc)
    "Arcane Ring": Item("Arcane Ring", "A ring humming with magic", None, {"INT": 1}),

























    # --- Extra weapons (added: 30) ---
    "Shortsword": Weapon("Shortsword", "1d6", "slashing", ["versatile"], stats_bonus={"STR": 1}),
    "Sabre": Weapon("Sabre", "1d8", "slashing", ["finesse"], stats_bonus={"DEX": 1}),
    "Scimitar": Weapon("Scimitar", "1d8", "slashing", ["finesse", "light"], stats_bonus={"DEX": 1}),
    "Claymore": Weapon("Claymore", "2d6", "slashing", ["two-handed", "heavy"], stats_bonus={"STR": 2}),
    "Falchion": Weapon("Falchion", "2d4", "slashing", ["two-handed", "heavy"], stats_bonus={"STR": 2}),
    "Trident": Weapon("Trident", "1d6", "piercing", ["versatile", "thrown"], stats_bonus={"STR": 1}),
    "Glaive": Weapon("Glaive", "2d6", "slashing", ["two-handed", "heavy"], stats_bonus={"STR": 2}),
    "Lucerne Hammer": Weapon("Lucerne Hammer", "2d6", "piercing", ["two-handed", "heavy"], stats_bonus={"STR": 2}),
    "Greataxe": Weapon("Greataxe", "2d6", "slashing", ["two-handed", "heavy"], stats_bonus={"STR": 3}),
    "Maul": Weapon("Maul", "2d10", "bludgeoning", ["two-handed", "heavy"], stats_bonus={"STR": 3}),
    "War Sickle": Weapon("War Sickle", "1d8", "slashing", ["versatile", "light"], stats_bonus={"STR": 1}),
    "Kris Dagger": Weapon("Kris Dagger", "1d4", "piercing", ["finesse", "light", "thrown"], stats_bonus={"DEX": 1}),
    "Broadsword": Weapon("Broadsword", "2d4", "slashing", ["two-handed", "versatile"], stats_bonus={"STR": 1}),
    "Cudgel": Weapon("Cudgel", "1d4", "bludgeoning", ["light"], stats_bonus={"STR": 1}),
    "Bone Club": Weapon("Bone Club", "1d6", "bludgeoning", ["light"], stats_bonus={"STR": 1}),
    "Anchor": Weapon("Anchor", "1d8", "bludgeoning", ["two-handed", "heavy"], stats_bonus={"STR": 1}),
    "Executioner's Axe": Weapon("Executioner's Axe", "1d10", "slashing", ["two-handed", "heavy"], stats_bonus={"STR": 2}),
    "Viper Fang": Weapon("Viper Fang", "1d6", "piercing", ["finesse", "light", "thrown"], stats_bonus={"DEX": 2}),
    "Sling": Weapon("Sling", "1d4", "bludgeoning", ["ranged", "light"], stats_bonus={"DEX": 1}),
    "Dart": Weapon("Dart", "1d4", "piercing", ["ranged", "light", "thrown"], stats_bonus={"DEX": 1}),
    "Javelin": Weapon("Javelin", "1d6", "piercing", ["thrown", "versatile"], stats_bonus={"DEX": 1}),
    "Light Crossbow": Weapon("Light Crossbow", "1d8", "piercing", ["ranged", "light"], stats_bonus={"DEX": 1}),
    "Heavy Crossbow": Weapon("Heavy Crossbow", "1d10", "piercing", ["ranged", "loading", "heavy"], stats_bonus={"STR": 1}),
    "Composite Bow": Weapon("Composite Bow", "1d8", "piercing", ["ranged", "heavy"], stats_bonus={"DEX": 2}),
    "Repeating Crossbow": Weapon("Repeating Crossbow", "1d10", "piercing", ["ranged", "loading"], stats_bonus={"DEX": 2}),
    "Ember Blade": Weapon("Ember Blade", "1d8", "fire_damage", ["versatile", "magic"], stats_bonus={"INT": 1}),
    "Frost Staff": Weapon("Frost Staff", "2d6", "cold", ["two-handed", "magic"], stats_bonus={"INT": 2}),
    "Storm Wand": Weapon("Storm Wand", "1d6", "lightning", ["magic", "ranged"], stats_bonus={"DEX": 1}),
    "Bone Wand": Weapon("Bone Wand", "1d6", "dark", ["magic", "ranged"], stats_bonus={"WIS": 1}),
    "Runed Dagger": Weapon("Runed Dagger", "1d4", "force", ["finesse", "light", "magic"], stats_bonus={"DEX": 2, "INT": 1}),

    # --- Extra armour and shields (added: 30) ---
    "Padded Armor": Armor("Padded Armor", 10, "light", stats_bonus={"CON": 1}),
    "Nomad Leather": Armor("Nomad Leather", 11, "light", stats_bonus={"DEX": 1}),
    "Doublet": Armor("Doublet", 12, "light", stats_bonus={"DEX": 1}),
    "Shadowcloth": Armor("Shadowcloth", 12, "light", None, ["magic"], stats_bonus={"DEX": 2}),
    "Wolf Hide Armor": Armor("Wolf Hide Armor", 12, "light", stats_bonus={"CON": 1, "DEX": 1}),
    "Robe of Silk": Armor("Robe of Silk", 10, "light", None, ["magic"], stats_bonus={"INT": 1}),
    "Mithral Leather": Armor("Mithral Leather", 13, "light", None, ["magic"], stats_bonus={"DEX": 1, "CON": 1}),
    "Elven Cloak Armor": Armor("Elven Cloak Armor", 12, "light", None, ["magic"], stats_bonus={"DEX": 2}),
    "Riveted Leather": Armor("Riveted Leather", 13, "medium", 2, stats_bonus={"CON": 1}),
    "Padded Mail": Armor("Padded Mail", 13, "medium", 2, stats_bonus={"DEX": 1}),
    "Ironweave Mail": Armor("Ironweave Mail", 14, "medium", 2, stats_bonus={"CON": 1}),
    "Bone Lacquer": Armor("Bone Lacquer", 14, "medium", 2, ["magic"], stats_bonus={"CON": 2}),
    "Goblinforged Mail": Armor("Goblinforged Mail", 14, "medium", 2, stats_bonus={"STR": 1, "CON": 1}),
    "Enchanted Hide": Armor("Enchanted Hide", 14, "medium", 2, ["magic"], stats_bonus={"CON": 1, "WIS": 1}),
    "Lamellar Armor": Armor("Lamellar Armor", 15, "medium", 2, stats_bonus={"CON": 1}),
    "Ward Mail": Armor("Ward Mail", 14, "medium", 2, ["magic"], stats_bonus={"DEX": 1}),
    "Banded Mail": Armor("Banded Mail", 15, "heavy"),
    "Steel Plate": Armor("Steel Plate", 17, "heavy", stats_bonus={"CON": 1}),
    "Obsidian Plate": Armor("Obsidian Plate", 17, "heavy", None, ["magic"], stats_bonus={"CON": 2}),
    "Mithral Plate": Armor("Mithral Plate", 18, "heavy", None, ["magic", "light"], stats_bonus={"CON": 1, "DEX": 1}),
    "Warden Plate": Armor("Warden Plate", 17, "heavy", stats_bonus={"STR": 1, "CON": 1}),
    "Dragonbone Plate": Armor("Dragonbone Plate", 18, "heavy", None, ["magic"], stats_bonus={"CON": 2}),
    "Titanforged Plate": Armor("Titanforged Plate", 18, "heavy", stats_bonus={"STR": 1, "CON": 1}),
    "Barrier Plate": Armor("Barrier Plate", 19, "heavy", None, ["magic"], stats_bonus={"CON": 1}),
    "Ancient Scale Plate": Armor("Ancient Scale Plate", 19, "heavy", None, ["magic"], stats_bonus={"CON": 2}),
    "Buckler": Armor("Buckler", 1, "shield", None, ["light"], stats_bonus={"DEX": 1}),
    "Bronze Shield": Armor("Bronze Shield", 2, "shield", stats_bonus={"CON": 1}),
    "Runed Shield": Armor("Runed Shield", 3, "shield", None, ["magic"], stats_bonus={"INT": 1, "WIS": 1}),
    "Warden's Bulwark": Armor("Warden's Bulwark", 5, "shield", None, ["two-handed"], stats_bonus={"CON": 2}),
    "Bulwark of Dawn": Armor("Bulwark of Dawn", 6, "shield", None, ["magic"], stats_bonus={"STR": 2, "CON": 2}),

    # --- Monster drops (quest materials) ---
    "Metal Fragments": Item("Metal Fragments", "Scrap metal wrenched from a goblin's gear.", "material"),
    "Web String": Item("Web String", "Silken strand, still faintly sticky.", "material"),
    "Slime Ball": Item("Slime Ball", "A wobbling blob that refuses to evaporate.", "material"),
    "Rotten Flesh": Item("Rotten Flesh", "Rank, but some alchemists pay for it.", "material"),
    "Bone": Item("Bone", "A clean femur. Someone was taller once.", "material"),
    "Fur": Item("Fur", "Coarse grey pelt, still warm.", "material"),
    "Plasma": Item("Plasma", "A finger of cold blue light. Handle carefully.", "material"),
}

# Every class starts with a full pack of healing potions.
STARTING_POTIONS = ["Healing Potion"] * 15

STARTING_GEAR = {
    "Fighter": {"weapon": "Longsword", "armor": "Chainmail", "items": list(STARTING_POTIONS)},
    "Rogue": {"weapon": "Dagger", "armor": "Leather", "items": list(STARTING_POTIONS)},
    "Wizard": {"weapon": "Magic Staff", "armor": None, "items": list(STARTING_POTIONS)},
    "Cleric": {"weapon": "Mace", "armor": "Plate", "items": list(STARTING_POTIONS)},
}

def get_item(name):
    return ITEMS.get(name)

def create_item(name):
    item = get_item(name)
    if not item:
        return None
    if item.category == "weapon":
        return Weapon(item.name, item.damage_dice, item.damage_type, item.properties.copy(), dict(item.stats_bonus))
    if item.category == "armor":
        return Armor(item.name, item.base_ac, item.armor_type, item.dex_limit, item.properties.copy(), dict(item.stats_bonus))
    if item.category == "item":
        return Item(item.name, item.description, item.effect, dict(item.stats_bonus))
    return None

# Monster drops used for quests: material -> the monster it comes from.
MATERIALS = {
    "Metal Fragments": "Goblin",
    "Web String": "Spider",
    "Slime Ball": "Slime",
    "Rotten Flesh": "Zombie",
    "Bone": "Skeleton",
    "Fur": "Wolf",
    "Plasma": "Ghost",
}


def is_material(item):
    """True for quest materials: not craftable, not sellable."""
    return item is not None and item.name in MATERIALS

