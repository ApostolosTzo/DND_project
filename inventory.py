from ui import menu, show, clear_screen, press_any_key
from items import is_two_handed, is_potion, heal_amount


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
        if player.offhand:
            equipped_names.append(f"Off-hand: {player.offhand.name}")
        if player.hands_full():
            equipped_names.append("(both hands are full)")

        # Equipped items are displayed at the top, followed by storage items.
        # If no items are equipped, it shows "None".
        # Storage items are grouped by name and quantity.
        if equipped_names:
            header = "Equipped:\n" + "\n".join(f"  {e}" for e in equipped_names) + "\n\nStorage:"
        else:
            header = "Equipped:\n  None\n\nStorage:"

        # Filter out equipped items from the inventory to get storage items
        storage_items = [item for item in player.inventory
                         if item not in (player.weapon, player.armor, player.offhand)]

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
# Equipment slots
#===========================
def equip_target_for(player, item):
    """Which slot an item would go into when equipped.

    Weapons are the interesting case. A two-handed weapon always takes the
    main hand and hands the off-hand back; a one-handed weapon takes the main
    hand if it is free, otherwise the off-hand (that is how you end up
    dual-wielding), and only replaces the main hand once both hands are busy.
    Keeping the target in one place is what makes the "both hands full" check
    honest instead of cosmetic.
    """
    if item.category == "weapon":
        if is_two_handed(item):
            return "weapon"
        if not player.weapon:
            return "weapon"
        if is_two_handed(player.weapon):
            return "weapon"      # main hand owns both
        if not player.offhand:
            return "offhand"
        return "weapon"
    if item.category == "armor":
        if item.armor_type == "shield":
            return "offhand"
        return "armor"
    return None


def equip_refusal(player, item):
    """Why this item cannot be equipped right now, or None if it can."""
    slot = equip_target_for(player, item)
    if slot is None:
        return None
    if slot == "offhand" and not player.can_equip_offhand(item):
        return player.offhand_block_reason() or "That cannot go in your off-hand."
    return None


#===========================
# Item Actions
#===========================
def do_action(player, item):
    """Equips or uses one item, mirroring js/game.js inventoryEquip/Use."""
    refusal = equip_refusal(player, item)
    if refusal:
        clear_screen()
        show(refusal)
        press_any_key()
        return

    slot = equip_target_for(player, item)

    if slot == "weapon":
        if player.weapon:
            player.inventory.append(player.weapon)
        player.weapon = item
        stowed = player.stow_offhand() if is_two_handed(item) else None
        player.remove_item(item)
        player.ac = player.calc_ac()
        player.recalc_hp()
        clear_screen()
        show(f"Equipped {item.name}!")
        if stowed:
            show(f"{stowed.name} went back to storage.")
        press_any_key()

    elif slot == "armor":
        if player.armor:
            player.inventory.append(player.armor)
        player.armor = item
        player.remove_item(item)
        player.ac = player.calc_ac()
        player.recalc_hp()
        clear_screen()
        show(f"Equipped {item.name}!")
        press_any_key()

    elif slot == "offhand":
        old = player.offhand
        player.offhand = item
        if old:
            player.inventory.append(old)
        player.remove_item(item)
        player.ac = player.calc_ac()
        player.recalc_hp()
        clear_screen()
        show(f"Equipped {item.name} in your off-hand!")
        press_any_key()

    elif is_potion(item.name):
        before = player.hp
        heal = heal_amount(item.name)
        player.hp = min(player.hp + heal, player.max_hp)
        player.remove_item(item)
        clear_screen()
        show(f"Drank {item.name}! Restored {player.hp - before} HP ({heal} attempted).")
        press_any_key()

    else:
        clear_screen()
        show(f"Cannot use {item.name} yet.")
        press_any_key()
