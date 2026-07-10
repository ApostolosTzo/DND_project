from ui import menu, show, clear_screen, prompt, press_any_key
from items import create_item

#===========================
# Shop System
#===========================

SHOP_NPCS = {
    "Potion Merchant": {
        "items": {
            "Healing Potion": {"price": 15, "min_level": 1},
        }
    },
    "Weaponsmith": {
        "items": {
            "Dagger": {"price": 10, "min_level": 1},
            "Shortbow": {"price": 25, "min_level": 1},
            "Mace": {"price": 20, "min_level": 1},
            "Longsword": {"price": 30, "min_level": 1},
        }
    },
    "Armorer": {
        "items": {
            "Leather": {"price": 20, "min_level": 1},
            "Chainmail": {"price": 100, "min_level": 1},
            "Shield": {"price": 25, "min_level": 1},
            "Plate": {"price": 300, "min_level": 4},
            "Titanium": {"price": 500, "min_level": 7},
            "Dragon Scale": {"price": 800, "min_level": 10},
        }
    },
    "Arcane Vendor": {
        "items": {
            "Magic Staff": {"price": 30, "min_level": 1},
            "Lampada": {"price": 50, "min_level": 5},
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
        for eq in [player.weapon, player.armor, player.shield]:
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
