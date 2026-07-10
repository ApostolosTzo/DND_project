from ui import menu, show, clear_screen, press_any_key
from dice import roll

#===========================
# Inventory Management
#===========================
def open_inventory(player):
    while True:
        equipped_names = []
        if player.weapon:
            equipped_names.append(f"Weapon: {player.weapon.name}")
        if player.armor:
            equipped_names.append(f"Armor:  {player.armor.name}")
        if player.shield:
            equipped_names.append(f"Shield: {player.shield.name}")
        
        
        # Equipped items are displayed at the top, followed by storage items. 
        # If no items are equipped, it shows "None". 
        # Storage items are grouped by name and quantity.
        if equipped_names:
            header = "Equipped:\n" + "\n".join(f"  {e}" for e in equipped_names) + "\n\nStorage:"
        else:
            header = "Equipped:\n  None\n\nStorage:"
        
        
        # Filter out equipped items from the inventory to get storage items
        storage_items = [item for item in player.inventory
                            if item != player.weapon and item != player.armor and item != player.shield]

        grouped = {}
        for item in storage_items:
            grouped.setdefault(item.name, []).append(item)

        # Create a list of display names for the grouped items, 
        # showing quantity if more than one
        display_names = []
        for name, items in grouped.items():
            if len(items) > 1:
                display_names.append(f"{name} x{len(items)}")
            else:
                display_names.append(name)

        # If there are no storage items, show "(Empty)". 
        # Otherwise, show the grouped item names and a "(Close)" option at the end.
        options = ["(Empty)"] if not display_names else display_names + ["(Close)"]

        choice = menu("Inventory", options, body=header)

        if not display_names:
            return

        if choice == len(display_names):
            return

        selected_name = list(grouped.keys())[choice]
        selected = grouped[selected_name][0]
        do_action(player, selected)


#===========================
# Item Actions
#===========================

def do_action(player, item):
    if item.category == "weapon":
        if player.weapon:
            player.inventory.append(player.weapon)
        player.weapon = item
        player.remove_item(item)
        player.ac = player.calc_ac()
        player.recalc_hp()
        clear_screen()
        show(f"Equipped {item.name}!")
        press_any_key()

    elif item.category == "armor":
        if item.armor_type == "shield":
            if player.shield:
                player.inventory.append(player.shield)
            player.shield = item
        else:
            if player.armor:
                player.inventory.append(player.armor)
            player.armor = item
        player.remove_item(item)
        player.ac = player.calc_ac()
        player.recalc_hp()
        clear_screen()
        show(f"Equipped {item.name}!")
        press_any_key()

    elif item.category == "item":
        if item.name == "Healing Potion":
            heal = 9
            player.hp = min(player.hp + heal, player.max_hp)
            player.remove_item(item)
            clear_screen()
            show(f"Drank Healing Potion! Restored {heal} HP.")
            press_any_key()
        elif item.name == "Greater Healing Potion":
            heal = 20
            player.hp = min(player.hp + heal, player.max_hp)
            player.remove_item(item)
            clear_screen()
            show(f"Drank Greater Healing Potion! Restored {heal} HP.")
            press_any_key()
        else:
            clear_screen()
            show(f"Cannot use {item.name} yet.")
            press_any_key()
