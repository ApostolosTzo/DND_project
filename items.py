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
        return Weapon(item.name, item.damage_dice, item.damage_type, item.properties.copy(), dict(item.stats_bonus))
    if item.category == "armor":
        return Armor(item.name, item.base_ac, item.armor_type, item.dex_limit, item.properties.copy(), dict(item.stats_bonus))
    if item.category == "item":
        return Item(item.name, item.description, item.effect, dict(item.stats_bonus))
    return None
