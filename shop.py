from ui import menu, show, clear_screen, prompt, press_any_key
from items import create_item, is_material

#===========================
# Shop System
#===========================

# NPCs pay 20% under the cheapest price the item sells for.
SELL_RATIO = 0.8


def sell_price(item_name):
    """What an NPC pays for one of these, or None if nobody sells it.

    Quest materials are never sellable - they are only worth turning in.
    """
    item = create_item(item_name)
    if item is None or is_material(item):
        return None
    prices = [shop["items"][item_name]["price"]
              for shop in SHOP_NPCS.values() if item_name in shop["items"]]
    if not prices:
        return None
    return int(min(prices) * SELL_RATIO)

SHOP_NPCS = {
    "Potion Merchant": {
        "items": {
            "Healing Potion": {"price": 15, "min_level": 1},
            "Greater Healing Potion": {"price": 50, "min_level": 5},
            "Superior Healing Potion": {"price": 300, "min_level": 15},
            "Grand Healing Potion": {"price": 1500, "min_level": 35},
            "Ultimate Healing Potion": {"price": 8000, "min_level": 70},
            #"Mana Potion": {"price": 30, "min_level": 3},
            #"Antidote": {"price": 20, "min_level": 1},
        }
    },
    # Every shield in the game is sold here and nowhere else.
    "Shield Smith": {
        "items": {
            "Buckler": {"price": 20, "min_level": 1},
            "Shield": {"price": 25, "min_level": 1},
            "Iron Shield": {"price": 55, "min_level": 2},
            "Bronze Shield": {"price": 45, "min_level": 2},
            "Tower Shield": {"price": 90, "min_level": 4},
            "Runed Shield": {"price": 150, "min_level": 5},
            "Magic Shield": {"price": 210, "min_level": 6},
            "Warden's Bulwark": {"price": 340, "min_level": 8},
            "Bulwark of Dawn": {"price": 480, "min_level": 10},
            "Dragon Shield": {"price": 620, "min_level": 11},
            "Aegis Shield": {"price": 900, "min_level": 13},
        }
    },
    "Weaponsmith": {
        "items": {
            "Dagger": {"price": 10, "min_level": 1},
            "Spear": {"price": 15, "min_level": 1},
            "Mace": {"price": 20, "min_level": 1},
            "Quarterstaff": {"price": 15, "min_level": 1},
            "Longsword": {"price": 30, "min_level": 1},
            "Battle Axe": {"price": 35, "min_level": 1},
            "War Hammer": {"price": 40, "min_level": 2},
            "Flail": {"price": 35, "min_level": 2},
            "Greatsword": {"price": 60, "min_level": 3},
                    "Shortsword": {"price": 25, "min_level": 1},
            "Sabre": {"price": 45, "min_level": 2},
            "Scimitar": {"price": 50, "min_level": 3},
            "Claymore": {"price": 90, "min_level": 4},
            "Falchion": {"price": 85, "min_level": 4},
            "Trident": {"price": 30, "min_level": 2},
            "Glaive": {"price": 95, "min_level": 5},
            "Lucerne Hammer": {"price": 110, "min_level": 5},
            "Greataxe": {"price": 130, "min_level": 6},
            "Maul": {"price": 140, "min_level": 7},
            "War Sickle": {"price": 55, "min_level": 3},
            "Kris Dagger": {"price": 70, "min_level": 4},
            "Broadsword": {"price": 75, "min_level": 4},
            "Cudgel": {"price": 12, "min_level": 1},
            "Bone Club": {"price": 18, "min_level": 1},
            "Anchor": {"price": 60, "min_level": 3},
            "Executioner's Axe": {"price": 100, "min_level": 5},
            "Viper Fang": {"price": 80, "min_level": 4},
            "Venom Dagger": {"price": 95, "min_level": 5},

            "Shortsword": {"price": 25, "min_level": 1},
            "Sabre": {"price": 45, "min_level": 2},
            "Scimitar": {"price": 50, "min_level": 3},
            "Claymore": {"price": 90, "min_level": 4},
            "Falchion": {"price": 85, "min_level": 4},
            "Trident": {"price": 30, "min_level": 2},
            "Glaive": {"price": 95, "min_level": 5},
            "Lucerne Hammer": {"price": 110, "min_level": 5},
            "Greataxe": {"price": 130, "min_level": 6},
            "Maul": {"price": 140, "min_level": 7},
            "War Sickle": {"price": 55, "min_level": 3},
            "Kris Dagger": {"price": 70, "min_level": 4},
            "Broadsword": {"price": 75, "min_level": 4},
            "Cudgel": {"price": 12, "min_level": 1},
            "Bone Club": {"price": 18, "min_level": 1},
            "Anchor": {"price": 60, "min_level": 3},
            "Executioner's Axe": {"price": 100, "min_level": 5},
            "Viper Fang": {"price": 80, "min_level": 4},

            "Shortsword": {"price": 25, "min_level": 1},
            "Sabre": {"price": 45, "min_level": 2},
            "Scimitar": {"price": 50, "min_level": 3},
            "Claymore": {"price": 90, "min_level": 4},
            "Falchion": {"price": 85, "min_level": 4},
            "Trident": {"price": 30, "min_level": 2},
            "Glaive": {"price": 95, "min_level": 5},
            "Lucerne Hammer": {"price": 110, "min_level": 5},
            "Greataxe": {"price": 130, "min_level": 6},
            "Maul": {"price": 140, "min_level": 7},
            "War Sickle": {"price": 55, "min_level": 3},
            "Kris Dagger": {"price": 70, "min_level": 4},
            "Broadsword": {"price": 75, "min_level": 4},
            "Cudgel": {"price": 12, "min_level": 1},
            "Bone Club": {"price": 18, "min_level": 1},
            "Anchor": {"price": 60, "min_level": 3},
            "Executioner's Axe": {"price": 100, "min_level": 5},
            "Viper Fang": {"price": 80, "min_level": 4},

            "Shortsword": {"price": 25, "min_level": 1},
            "Sabre": {"price": 45, "min_level": 2},
            "Scimitar": {"price": 50, "min_level": 3},
            "Claymore": {"price": 90, "min_level": 4},
            "Falchion": {"price": 85, "min_level": 4},
            "Trident": {"price": 30, "min_level": 2},
            "Glaive": {"price": 95, "min_level": 5},
            "Lucerne Hammer": {"price": 110, "min_level": 5},
            "Greataxe": {"price": 130, "min_level": 6},
            "Maul": {"price": 140, "min_level": 7},
            "War Sickle": {"price": 55, "min_level": 3},
            "Kris Dagger": {"price": 70, "min_level": 4},
            "Broadsword": {"price": 75, "min_level": 4},
            "Cudgel": {"price": 12, "min_level": 1},
            "Bone Club": {"price": 18, "min_level": 1},
            "Anchor": {"price": 60, "min_level": 3},
            "Executioner's Axe": {"price": 100, "min_level": 5},
            "Viper Fang": {"price": 80, "min_level": 4},

            "Shortsword": {"price": 25, "min_level": 1},
            "Sabre": {"price": 45, "min_level": 2},
            "Scimitar": {"price": 50, "min_level": 3},
            "Claymore": {"price": 90, "min_level": 4},
            "Falchion": {"price": 85, "min_level": 4},
            "Trident": {"price": 30, "min_level": 2},
            "Glaive": {"price": 95, "min_level": 5},
            "Lucerne Hammer": {"price": 110, "min_level": 5},
            "Greataxe": {"price": 130, "min_level": 6},
            "Maul": {"price": 140, "min_level": 7},
            "War Sickle": {"price": 55, "min_level": 3},
            "Kris Dagger": {"price": 70, "min_level": 4},
            "Broadsword": {"price": 75, "min_level": 4},
            "Cudgel": {"price": 12, "min_level": 1},
            "Bone Club": {"price": 18, "min_level": 1},
            "Anchor": {"price": 60, "min_level": 3},
            "Executioner's Axe": {"price": 100, "min_level": 5},
            "Viper Fang": {"price": 80, "min_level": 4},

}
    },
    "Armorer": {
        "items": {
            "Leather": {"price": 20, "min_level": 1},
            "Studded Leather": {"price": 45, "min_level": 2},
            "Hide": {"price": 30, "min_level": 1},
            "Chainmail": {"price": 100, "min_level": 1},
            "Scale Mail": {"price": 120, "min_level": 2},
            "Breastplate": {"price": 150, "min_level": 3},
            "Half Plate": {"price": 200, "min_level": 4},
            "Ring Mail": {"price": 80, "min_level": 1},
            "Plate": {"price": 300, "min_level": 4},
            "Splint": {"price": 350, "min_level": 5},
            "Titanium": {"price": 500, "min_level": 7},
            "Dragon Scale": {"price": 800, "min_level": 10},
                    "Padded Armor": {"price": 25, "min_level": 1},
            "Nomad Leather": {"price": 40, "min_level": 2},
            "Doublet": {"price": 70, "min_level": 3},
            "Shadowcloth": {"price": 190, "min_level": 6},
            "Wolf Hide Armor": {"price": 95, "min_level": 4},
            "Robe of Silk": {"price": 110, "min_level": 3},
            "Mithral Leather": {"price": 230, "min_level": 7},
            "Elven Cloak Armor": {"price": 210, "min_level": 6},
            "Riveted Leather": {"price": 55, "min_level": 2},
            "Padded Mail": {"price": 60, "min_level": 2},
            "Ironweave Mail": {"price": 165, "min_level": 5},
            "Bone Lacquer": {"price": 320, "min_level": 8},
            "Goblinforged Mail": {"price": 250, "min_level": 6},
            "Enchanted Hide": {"price": 285, "min_level": 7},
            "Lamellar Armor": {"price": 260, "min_level": 7},
            "Ward Mail": {"price": 240, "min_level": 6},
            "Banded Mail": {"price": 190, "min_level": 5},
            "Steel Plate": {"price": 390, "min_level": 8},
            "Obsidian Plate": {"price": 620, "min_level": 9},
            "Mithral Plate": {"price": 700, "min_level": 10},
            "Warden Plate": {"price": 520, "min_level": 9},
            "Dragonbone Plate": {"price": 760, "min_level": 10},
            "Titanforged Plate": {"price": 640, "min_level": 9},
            "Barrier Plate": {"price": 900, "min_level": 11},
            "Ancient Scale Plate": {"price": 1100, "min_level": 12},

            "Padded Armor": {"price": 25, "min_level": 1},
            "Nomad Leather": {"price": 40, "min_level": 2},
            "Doublet": {"price": 70, "min_level": 3},
            "Shadowcloth": {"price": 190, "min_level": 6},
            "Wolf Hide Armor": {"price": 95, "min_level": 4},
            "Robe of Silk": {"price": 110, "min_level": 3},
            "Mithral Leather": {"price": 230, "min_level": 7},
            "Elven Cloak Armor": {"price": 210, "min_level": 6},
            "Riveted Leather": {"price": 55, "min_level": 2},
            "Padded Mail": {"price": 60, "min_level": 2},
            "Ironweave Mail": {"price": 165, "min_level": 5},
            "Bone Lacquer": {"price": 320, "min_level": 8},
            "Goblinforged Mail": {"price": 250, "min_level": 6},
            "Enchanted Hide": {"price": 285, "min_level": 7},
            "Lamellar Armor": {"price": 260, "min_level": 7},
            "Ward Mail": {"price": 240, "min_level": 6},
            "Banded Mail": {"price": 190, "min_level": 5},
            "Steel Plate": {"price": 390, "min_level": 8},
            "Obsidian Plate": {"price": 620, "min_level": 9},
            "Mithral Plate": {"price": 700, "min_level": 10},
            "Warden Plate": {"price": 520, "min_level": 9},
            "Dragonbone Plate": {"price": 760, "min_level": 10},
            "Titanforged Plate": {"price": 640, "min_level": 9},
            "Barrier Plate": {"price": 900, "min_level": 11},
            "Ancient Scale Plate": {"price": 1100, "min_level": 12},

            "Padded Armor": {"price": 25, "min_level": 1},
            "Nomad Leather": {"price": 40, "min_level": 2},
            "Doublet": {"price": 70, "min_level": 3},
            "Shadowcloth": {"price": 190, "min_level": 6},
            "Wolf Hide Armor": {"price": 95, "min_level": 4},
            "Robe of Silk": {"price": 110, "min_level": 3},
            "Mithral Leather": {"price": 230, "min_level": 7},
            "Elven Cloak Armor": {"price": 210, "min_level": 6},
            "Riveted Leather": {"price": 55, "min_level": 2},
            "Padded Mail": {"price": 60, "min_level": 2},
            "Ironweave Mail": {"price": 165, "min_level": 5},
            "Bone Lacquer": {"price": 320, "min_level": 8},
            "Goblinforged Mail": {"price": 250, "min_level": 6},
            "Enchanted Hide": {"price": 285, "min_level": 7},
            "Lamellar Armor": {"price": 260, "min_level": 7},
            "Ward Mail": {"price": 240, "min_level": 6},
            "Banded Mail": {"price": 190, "min_level": 5},
            "Steel Plate": {"price": 390, "min_level": 8},
            "Obsidian Plate": {"price": 620, "min_level": 9},
            "Mithral Plate": {"price": 700, "min_level": 10},
            "Warden Plate": {"price": 520, "min_level": 9},
            "Dragonbone Plate": {"price": 760, "min_level": 10},
            "Titanforged Plate": {"price": 640, "min_level": 9},
            "Barrier Plate": {"price": 900, "min_level": 11},
            "Ancient Scale Plate": {"price": 1100, "min_level": 12},

            "Padded Armor": {"price": 25, "min_level": 1},
            "Nomad Leather": {"price": 40, "min_level": 2},
            "Doublet": {"price": 70, "min_level": 3},
            "Shadowcloth": {"price": 190, "min_level": 6},
            "Wolf Hide Armor": {"price": 95, "min_level": 4},
            "Robe of Silk": {"price": 110, "min_level": 3},
            "Mithral Leather": {"price": 230, "min_level": 7},
            "Elven Cloak Armor": {"price": 210, "min_level": 6},
            "Riveted Leather": {"price": 55, "min_level": 2},
            "Padded Mail": {"price": 60, "min_level": 2},
            "Ironweave Mail": {"price": 165, "min_level": 5},
            "Bone Lacquer": {"price": 320, "min_level": 8},
            "Goblinforged Mail": {"price": 250, "min_level": 6},
            "Enchanted Hide": {"price": 285, "min_level": 7},
            "Lamellar Armor": {"price": 260, "min_level": 7},
            "Ward Mail": {"price": 240, "min_level": 6},
            "Banded Mail": {"price": 190, "min_level": 5},
            "Steel Plate": {"price": 390, "min_level": 8},
            "Obsidian Plate": {"price": 620, "min_level": 9},
            "Mithral Plate": {"price": 700, "min_level": 10},
            "Warden Plate": {"price": 520, "min_level": 9},
            "Dragonbone Plate": {"price": 760, "min_level": 10},
            "Titanforged Plate": {"price": 640, "min_level": 9},
            "Barrier Plate": {"price": 900, "min_level": 11},
            "Ancient Scale Plate": {"price": 1100, "min_level": 12},

            "Padded Armor": {"price": 25, "min_level": 1},
            "Nomad Leather": {"price": 40, "min_level": 2},
            "Doublet": {"price": 70, "min_level": 3},
            "Shadowcloth": {"price": 190, "min_level": 6},
            "Wolf Hide Armor": {"price": 95, "min_level": 4},
            "Robe of Silk": {"price": 110, "min_level": 3},
            "Mithral Leather": {"price": 230, "min_level": 7},
            "Elven Cloak Armor": {"price": 210, "min_level": 6},
            "Riveted Leather": {"price": 55, "min_level": 2},
            "Padded Mail": {"price": 60, "min_level": 2},
            "Ironweave Mail": {"price": 165, "min_level": 5},
            "Bone Lacquer": {"price": 320, "min_level": 8},
            "Goblinforged Mail": {"price": 250, "min_level": 6},
            "Enchanted Hide": {"price": 285, "min_level": 7},
            "Lamellar Armor": {"price": 260, "min_level": 7},
            "Ward Mail": {"price": 240, "min_level": 6},
            "Banded Mail": {"price": 190, "min_level": 5},
            "Steel Plate": {"price": 390, "min_level": 8},
            "Obsidian Plate": {"price": 620, "min_level": 9},
            "Mithral Plate": {"price": 700, "min_level": 10},
            "Warden Plate": {"price": 520, "min_level": 9},
            "Dragonbone Plate": {"price": 760, "min_level": 10},
            "Titanforged Plate": {"price": 640, "min_level": 9},
            "Barrier Plate": {"price": 900, "min_level": 11},
            "Ancient Scale Plate": {"price": 1100, "min_level": 12},

}
    },
    "Archer": {
        "items": {
            "Shortbow": {"price": 25, "min_level": 1},
            "Longbow": {"price": 75, "min_level": 3},
            "Crossbow": {"price": 100, "min_level": 5},
            "Hand Crossbow": {"price": 50, "min_level": 2},
                    "Sling": {"price": 15, "min_level": 1},
            "Dart": {"price": 20, "min_level": 1},
            "Javelin": {"price": 35, "min_level": 2},
            "Light Crossbow": {"price": 65, "min_level": 3},
            "Heavy Crossbow": {"price": 140, "min_level": 6},
            "Composite Bow": {"price": 120, "min_level": 5},
            "Repeating Crossbow": {"price": 260, "min_level": 9},

            "Sling": {"price": 15, "min_level": 1},
            "Dart": {"price": 20, "min_level": 1},
            "Javelin": {"price": 35, "min_level": 2},
            "Light Crossbow": {"price": 65, "min_level": 3},
            "Heavy Crossbow": {"price": 140, "min_level": 6},
            "Composite Bow": {"price": 120, "min_level": 5},
            "Repeating Crossbow": {"price": 260, "min_level": 9},

            "Sling": {"price": 15, "min_level": 1},
            "Dart": {"price": 20, "min_level": 1},
            "Javelin": {"price": 35, "min_level": 2},
            "Light Crossbow": {"price": 65, "min_level": 3},
            "Heavy Crossbow": {"price": 140, "min_level": 6},
            "Composite Bow": {"price": 120, "min_level": 5},
            "Repeating Crossbow": {"price": 260, "min_level": 9},

            "Sling": {"price": 15, "min_level": 1},
            "Dart": {"price": 20, "min_level": 1},
            "Javelin": {"price": 35, "min_level": 2},
            "Light Crossbow": {"price": 65, "min_level": 3},
            "Heavy Crossbow": {"price": 140, "min_level": 6},
            "Composite Bow": {"price": 120, "min_level": 5},
            "Repeating Crossbow": {"price": 260, "min_level": 9},

            "Sling": {"price": 15, "min_level": 1},
            "Dart": {"price": 20, "min_level": 1},
            "Javelin": {"price": 35, "min_level": 2},
            "Light Crossbow": {"price": 65, "min_level": 3},
            "Heavy Crossbow": {"price": 140, "min_level": 6},
            "Composite Bow": {"price": 120, "min_level": 5},
            "Repeating Crossbow": {"price": 260, "min_level": 9},

}
    },
    "Wizard": {
        "items": {
            "Magic Staff": {"price": 30, "min_level": 1},
            "Wand": {"price": 40, "min_level": 1},
            "Arcane Staff": {"price": 120, "min_level": 4},
            "Wizard Robe": {"price": 80, "min_level": 2},
            "Arcane Ring": {"price": 200, "min_level": 5},
            "Lampada": {"price": 50, "min_level": 5},
                    "Ember Blade": {"price": 180, "min_level": 5},
            "Frost Staff": {"price": 340, "min_level": 8},
            "Storm Wand": {"price": 200, "min_level": 6},
            "Bone Wand": {"price": 150, "min_level": 5},
            "Runed Dagger": {"price": 150, "min_level": 5},
            "Plasma Wand": {"price": 230, "min_level": 6},

            "Ember Blade": {"price": 180, "min_level": 5},
            "Frost Staff": {"price": 340, "min_level": 8},
            "Storm Wand": {"price": 200, "min_level": 6},
            "Bone Wand": {"price": 150, "min_level": 5},
            "Runed Dagger": {"price": 150, "min_level": 5},

            "Ember Blade": {"price": 180, "min_level": 5},
            "Frost Staff": {"price": 340, "min_level": 8},
            "Storm Wand": {"price": 200, "min_level": 6},
            "Bone Wand": {"price": 150, "min_level": 5},
            "Runed Dagger": {"price": 150, "min_level": 5},

            "Ember Blade": {"price": 180, "min_level": 5},
            "Frost Staff": {"price": 340, "min_level": 8},
            "Storm Wand": {"price": 200, "min_level": 6},
            "Bone Wand": {"price": 150, "min_level": 5},
            "Runed Dagger": {"price": 150, "min_level": 5},

            "Ember Blade": {"price": 180, "min_level": 5},
            "Frost Staff": {"price": 340, "min_level": 8},
            "Storm Wand": {"price": 200, "min_level": 6},
            "Bone Wand": {"price": 150, "min_level": 5},
            "Runed Dagger": {"price": 150, "min_level": 5},

}
    },
}


#===========================
# Shop Interaction
#===========================

def open_shop(player, shop_name):
    shop = SHOP_NPCS[shop_name]
    # Filter items based on player's level
    available = {n: d for n, d in shop["items"].items() if player.level >= d["min_level"]}

    
    while True:
        # Display player's gold and storage items, grouped by name and quantity.
        storage_counts = {}
        for item in player.inventory:
            storage_counts[item.name] = storage_counts.get(item.name, 0) + 1
        # Also count equipped items in storage counts for display purposes.
        for eq in [player.weapon, player.armor, player.offhand]:
            if eq:
                storage_counts[eq.name] = storage_counts.get(eq.name, 0) + 1

        # Create a list of storage lines for display, showing quantity if more than one.
        storage_lines = []
        for name, count in sorted(storage_counts.items()):
            storage_lines.append(f"  {name} x{count}" if count > 1 else f"  {name}")
        storage_text = "\n".join(["Your Storage:"] + (storage_lines if storage_lines else ["  (empty)"]))
        
        # Create the menu body with player's gold and storage items.
        body = f"Gold: {player.gold}\n\n{storage_text}\n"

        item_names = list(available.keys())
        name_pad = max(len(n) for n in item_names) + 2 if item_names else 0
        options = [f"{n}{'.' * (name_pad - len(n))} {d['price']}g" for n, d in available.items()]
        options.append("(Leave)")

        choice = menu(shop_name, options, body=body)

        # If the player chooses to leave, exit the shop.
        if choice == len(item_names):
            return

        selected_name = item_names[choice]
        selected_price = available[selected_name]["price"]
        # Prompt the player for the quantity they want to buy, 
        # ensuring it's a valid positive integer.
        qty = prompt(f"How many {selected_name}(s)? ({selected_price}g each)")
        try:
            qty = int(qty)
            if qty < 1:
                continue
        except:
            continue
        
        # Calculate the total cost and check if the player has enough gold.
        total = selected_price * qty
        if player.spend_gold(total):
            for _ in range(qty):
                player.add_item(create_item(selected_name))
            clear_screen()
            show(f"Bought {qty} {selected_name}(s) for {total}g!")
            press_any_key()
        else:
            clear_screen()
            show(f"Not enough gold! Need {total}g, you have {player.gold}g.")
            press_any_key()
