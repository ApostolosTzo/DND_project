class Weapon:
    def __init__(self, name, damage_dice, damage_type, properties=None):
        self.name = name
        self.damage_dice = damage_dice
        self.damage_type = damage_type
        self.properties = properties or []
        self.category = "weapon"

class Armor:
    def __init__(self, name, base_ac, armor_type, dex_limit=None, properties=None):
        self.name = name
        self.base_ac = base_ac
        self.armor_type = armor_type
        self.dex_limit = dex_limit
        self.properties = properties or []
        self.category = "armor"

class Item:
    def __init__(self, name, description, effect=None):
        self.name = name
        self.description = description
        self.effect = effect
        self.category = "item"

ITEMS = {
    
    # Weapons
    "Longsword": Weapon("Longsword", "1d8", "slashing", ["versatile"]),
    "Shortbow": Weapon("Shortbow", "1d6", "piercing", ["two-handed", "ranged"]),
    "Dagger": Weapon("Dagger", "1d4", "piercing", ["finesse", "light", "thrown"]),
    "Magic Staff": Weapon("Magic Staff", "1d6", "bludgeoning", ["versatile", "magic"]),
    "Mace": Weapon("Mace", "1d6", "bludgeoning", ["versatile"]),
    "Lampada": Weapon("Lampada", "1d6", "fire_damage", ["versatile", "magic"]),
    
    # Armor
    "Leather": Armor("Leather", 11, "light"),
    "Chainmail": Armor("Chainmail", 14, "medium", 2),
    "Plate": Armor("Plate", 17, "heavy"),
    "Titanium": Armor("Titanium", 18, "heavy"),
    "Dragon Scale": Armor("Dragon Scale", 19, "heavy"),
    "Shield": Armor("Shield", 2, "shield"),
    
    # Items
    "Healing Potion": Item("Healing Potion", "Restores 9 HP", "heal"),
}

STARTING_GEAR = {
    "Fighter": {"weapon": "Longsword", "armor": "Chainmail", "items": ["Healing Potion", "Healing Potion", "Healing Potion","Healing Potion", "Healing Potion", "Healing Potion"]},
    "Rogue": {"weapon": "Dagger", "armor": "Leather", "items": ["Healing Potion", "Healing Potion", "Healing Potion","Healing Potion", "Healing Potion", "Healing Potion"]},
    "Wizard": {"weapon": "Magic Staff", "armor": None, "items": ["Healing Potion", "Healing Potion", "Healing Potion","Healing Potion", "Healing Potion", "Healing Potion"]},
    "Cleric": {"weapon": "Mace", "armor": "Plate", "items": ["Healing Potion", "Healing Potion", "Healing Potion","Healing Potion", "Healing Potion", "Healing Potion"]},
}

def get_item(name):
    return ITEMS.get(name)

def create_item(name):
    item = get_item(name)
    if not item:
        return None
    if item.category == "weapon":
        return Weapon(item.name, item.damage_dice, item.damage_type, item.properties.copy())
    if item.category == "armor":
        return Armor(item.name, item.base_ac, item.armor_type, item.dex_limit, item.properties.copy())
    if item.category == "item":
        return Item(item.name, item.description, item.effect)
    return None
