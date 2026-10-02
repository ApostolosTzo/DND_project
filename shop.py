"""NPC shops: who stocks what, at what price, and at what level.

**This module derives its stock; it does not hard-code it.** The previous version
was a literal dict in which the same weapon appeared five times inside one NPC.
Python silently keeps the last duplicate key, so those repeats were invisible
dead weight: a reader could edit what looked like the live entry and change
nothing at all.

Stock is now computed at import time from the catalogue in items.py:

* Every item lands on one of sixteen **unlock tiers**, running from level 1 to
  level 200. UNLOCK_TIERS is the single place to change the whole game.
* Each class gets its **own themed NPC**, and every armory also stocks the
  universal ranged kit, so a Fighter can walk into the Wizard's stall and still
  buy a bow.
* Prices follow the tier. An item costs roughly TIER_MULT levels' worth of
  income at that level (level N pays 10*N gold), multiplied by where it sits
  within its own rung - 1.0x for the cheapest there, 3.0x for the strongest.

Because the dict is built from ITEMS rather than typed out, a new weapon added
to items.py appears in the right stall at the right level with a sane price,
and the browser mirror in js/shop.js can be checked against it directly.
"""
import math

from items import (ITEMS, WEAPON_CLASSES, ALL_CLASSES, POTION_MIN_LEVEL,
                   is_potion, create_item, two_handed_bonus, element_of)
from player import STARTING_GEAR

# NPCs pay 20% under the cheapest price an item sells for.
SELL_RATIO = 0.8

# -----------------------------
# The unlock ladder: 1 -> 200
# -----------------------------
# The game runs to level 200, so the ladder spreads across the whole range with
# growing gaps: 2, 3, 4, 5, 7, 8, 10, 12, 14, 16, 18, 20, 22, 24, 34. Early on
# you get something new every few levels; later each rung has to be earned.
UNLOCK_TIERS = [1, 3, 6, 10, 15, 22, 30, 40, 52, 66, 82, 100, 120, 142, 166, 200]

# How many levels of income an item on that rung costs. Level N pays 10*N gold,
# so TIER_BASE * level * TIER_MULT is the price of the rung's cheapest item and
# the rel multiplier (1.0x - 3.0x) spreads the rest of the rung above it.
TIER_BASE = 10.0
TIER_MULT = [1.0, 1.1, 1.2, 1.35, 1.5, 1.7, 1.9, 2.1, 2.35, 2.6, 2.9, 3.2, 3.5, 3.8, 4.1, 4.5]

# How much a weapon's element is worth when ranking it for a rung. Ice and
# poison outrank the rest because one removes the target's turn and the other
# never expires.
ELEMENT_VALUE = {"ice": 2.0, "poison": 2.5, "lightning": 1.5, "fire": 1.0, "dark": 1.0}

# -----------------------------
# The four armories
# -----------------------------
# (NPC name, class, tagline shown as the shop's greeting)
#
# Bows, darts, crossbows and the plain Wand are tagged ALL_CLASSES in
# items.WEAPON_CLASSES and are therefore stocked by all four of these. That is
# what makes "a Fighter can use a wand or a bow" true without a special case:
# the universal kit is never greyed out, only someone else's armory is.
ARMORY_NPCS = [
    ("Weaponsmith", "Fighter", "Blades, axes and polearms."),
    ("Shadow Fence", "Rogue", "Finesse weapons and thrown daggers."),
    ("Wizard", "Wizard", "Staves and elemental wands."),
    ("Temple", "Cleric", "Maces, flails and divine tools."),
]

# Potions are priced by hand rather than by rung: the healing curve is not
# linear, and a formula would flatten the interesting jumps.
POTION_PRICES = {
    "Healing Potion": 15,
    "Greater Healing Potion": 200,
    "Superior Healing Potion": 1500,
    "Grand Healing Potion": 8000,
    "Ultimate Healing Potion": 30000,
}

# Armour and shields keep the ORIGINAL hand-tuned level order, stretched onto
# the new ladder rather than re-derived. Their stat bonuses are large and uneven
# (Wizard Robe INT+9, Dragon Scale CON+8), so any computed power score would
# reorder pieces that were placed deliberately.
OLD_ARMOUR_LEVELS = {
    "Leather": 1, "Studded Leather": 2, "Hide": 1, "Chainmail": 1, "Scale Mail": 2,
    "Breastplate": 3, "Half Plate": 4, "Ring Mail": 1, "Plate": 4, "Splint": 5,
    "Titanium": 7, "Dragon Scale": 10, "Padded Armor": 1, "Nomad Leather": 2,
    "Doublet": 3, "Shadowcloth": 6, "Wolf Hide Armor": 4, "Robe of Silk": 3,
    "Mithral Leather": 7, "Elven Cloak Armor": 6, "Riveted Leather": 2, "Padded Mail": 2,
    "Ironweave Mail": 5, "Bone Lacquer": 8, "Goblinforged Mail": 6, "Enchanted Hide": 7,
    "Lamellar Armor": 7, "Ward Mail": 6, "Banded Mail": 1, "Steel Plate": 8,
    "Obsidian Plate": 9, "Mithral Plate": 10, "Warden Plate": 9, "Dragonbone Plate": 10,
    "Titanforged Plate": 9, "Barrier Plate": 11, "Ancient Scale Plate": 12,
    # Sold by the Wizard's stall rather than the Armorer, but it is still armour.
    "Wizard Robe": 2,
}
OLD_SHIELD_LEVELS = {
    "Buckler": 1, "Shield": 1, "Iron Shield": 2, "Bronze Shield": 2, "Tower Shield": 4,
    "Runed Shield": 5, "Magic Shield": 6, "Warden's Bulwark": 8, "Bulwark of Dawn": 10,
    "Dragon Shield": 11, "Aegis Shield": 13,
}
OLD_LEVEL_MAX = {"armour": 12, "shields": 13}

# Odds and ends that are neither weapon nor armour, sold by a named NPC.
# Prices and gates are explicit because there is nothing to derive them from.
EXTRA_STOCK = {
    "Wizard": {
        "Arcane Ring": {"price": 2400, "min_level": 66},
    },
}


# -----------------------------
# Deriving the stock
# -----------------------------
def _avg_dice(dice):
    """Average damage of an NdX+Y string."""
    s = str(dice)
    bonus = 0
    if "+" in s:
        s, b = s.split("+")
        bonus = int(b)
    elif "-" in s:
        s, b = s.split("-")
        bonus = -int(b)
    n, x = s.split("d")
    return int(n) * (int(x) + 1) / 2.0 + bonus


def _weapon_score(item):
    """Rough power ranking, used only to sort items within a rung.

    Armour has no meaningful score here - it is ordered by its hand-tuned level
    instead - so anything that is not a weapon ranks 0 and falls back to name.
    """
    if item.category != "weapon":
        return 0.0
    return (_avg_dice(item.damage_dice)
            + 2 * two_handed_bonus(item)
            + 1.5 * sum(item.stats_bonus.values())
            + ELEMENT_VALUE.get(element_of(item), 0.0))


def _round_half_up(v):
    """Round half away from zero, the way JavaScript's Math.round does.

    Python's built-in round() is round-half-to-even, so round(12.5) is 12 while
    Math.round(12.5) is 13. Every rounding in this module decides an unlock
    level or a price, so a one-off difference would leave the browser mirror's
    shop out of sync with this one - which is exactly what it did before this
    helper existed.
    """
    v = float(v)
    return int(math.floor(v + 0.5)) if v >= 0 else -int(math.floor(-v + 0.5))


def _round_price(v):
    """Snap to a price players read as a deliberate number, not a computed one."""
    v = max(5.0, float(v))
    if v >= 10000:
        step = 250
    elif v >= 2500:
        step = 100
    elif v >= 800:
        step = 50
    elif v >= 200:
        step = 10
    elif v >= 60:
        step = 5
    else:
        step = 1
    return _round_half_up(v / step) * step


def _price_for(tier, rel):
    return _round_price(TIER_BASE * UNLOCK_TIERS[tier] * TIER_MULT[tier] * rel)


def _spread(ranked):
    """Rank -> rung, spread evenly across the whole ladder."""
    n = len(ranked)
    if n == 0:
        return {}
    if n == 1:
        return {ranked[0]: 0}
    last = len(UNLOCK_TIERS) - 1
    return {name: _round_half_up(rank / (n - 1) * last)
            for rank, name in enumerate(ranked)}


def _map_old_level(old, old_max):
    """Stretch the original 1..old_max ladder onto the full UNLOCK_TIERS."""
    last = len(UNLOCK_TIERS) - 1
    frac = (max(1, old) - 1) / float(max(1, old_max - 1))
    return _round_half_up(frac * last)


def _build():
    """Compute the per-NPC stock lists and the {item: (price, min_level)} map."""
    groups = {}
    for name, item in ITEMS.items():
        if item.category != "weapon":
            continue
        classes = WEAPON_CLASSES.get(name, ALL_CLASSES)
        if classes == ALL_CLASSES:
            groups.setdefault("Universal", []).append(name)
        else:
            for c in classes:
                groups.setdefault(c, []).append(name)

    tiers = {}
    # The universal kit lands on the same rung in every stall, so a Crossbow
    # never costs a different level depending on who you buy it from.
    tiers.update(_spread(sorted(groups["Universal"],
                                key=lambda n: (_weapon_score(ITEMS[n]), n))))
    for _npc, cls, _note in ARMORY_NPCS:
        # A class's starting weapon is always rung 0: a Fighter handed a
        # Longsword at level 1 must be able to buy a replacement Longsword at
        # level 1. The rest of the armory is spread over rungs 1..15.
        opener = STARTING_GEAR[cls]["weapon"]
        rest = sorted((n for n in groups[cls] if n != opener),
                      key=lambda n: (_weapon_score(ITEMS[n]), n))
        tiers[opener] = 0
        for name, tier in _spread(rest).items():
            tiers[name] = min(len(UNLOCK_TIERS) - 1, tier + 1)
    for name, old in OLD_ARMOUR_LEVELS.items():
        tiers[name] = _map_old_level(old, OLD_LEVEL_MAX["armour"])
    for name, old in OLD_SHIELD_LEVELS.items():
        tiers[name] = _map_old_level(old, OLD_LEVEL_MAX["shields"])

    armour = [n for n, i in ITEMS.items()
              if i.category == "armor" and i.armor_type != "shield"]
    shields = [n for n, i in ITEMS.items()
               if i.category == "armor" and i.armor_type == "shield"]

    stock = {}
    for npc, cls, _note in ARMORY_NPCS:
        stock[npc] = sorted(set(groups[cls]) | set(groups["Universal"]),
                            key=lambda n: (tiers[n], _weapon_score(ITEMS[n]), n))
    stock["Armorer"] = sorted(armour, key=lambda n: (tiers[n], n))
    stock["Shield Smith"] = sorted(shields, key=lambda n: (tiers[n], n))
    for npc, extras in EXTRA_STOCK.items():
        for name in extras:
            stock[npc] = sorted(set(stock[npc]) | {name},
                                key=lambda n: (extras[n]["min_level"] if n in extras
                                               else tiers[n],
                                               _weapon_score(ITEMS[n]) if n in tiers else 0, n))

    prices = {}
    for npc, names in stock.items():
        extras = EXTRA_STOCK.get(npc, {})
        buckets = {}
        for n in names:
            if n in extras:
                continue
            buckets.setdefault(tiers[n], []).append(n)
        for tier, group in buckets.items():
            group = sorted(group, key=lambda n: (_weapon_score(ITEMS[n]), n))
            m = len(group)
            for i, n in enumerate(group):
                # 1.0x for the cheapest at this rung, 3.0x for the strongest, so
                # every rung offers a budget option as well as a flagship.
                rel = 1.8 if m == 1 else 1.0 + 2.0 * i / (m - 1)
                prices[n] = _price_for(tier, rel)

    levels = {n: UNLOCK_TIERS[t] for n, t in tiers.items()}
    return stock, prices, levels


_STOCK, _PRICES, _LEVELS = _build()


def _weapons(**entries):
    """Expand {"price": p, "min_level": l} for every item in a stock list."""
    return dict(entries)


def _stock_items(names, npc):
    """Expand a stock list into {name: {price, min_level}}.

    One pass, so the dict keeps the order of `names` - which is the order the
    shop displays. Building extras first and updating afterwards would silently
    pin them to the top of the list no matter what level they unlock at.
    """
    extras = EXTRA_STOCK.get(npc, {})
    return {n: (extras[n] if n in extras
                else {"price": _PRICES[n], "min_level": _LEVELS[n]})
            for n in names}


SHOP_NPCS = {
    "Potion Merchant": {
        "class": None,
        "note": "Potions for every level.",
        "items": {n: {"price": POTION_PRICES[n], "min_level": POTION_MIN_LEVEL[n]}
                  for n in sorted(POTION_PRICES, key=lambda x: POTION_MIN_LEVEL[x])},
    },
    "Shield Smith": {
        "class": None,
        "note": "Every shield in the game is sold here and nowhere else.",
        "items": _stock_items(_STOCK["Shield Smith"], "Shield Smith"),
    },
}

for _npc, _cls, _note in ARMORY_NPCS:
    SHOP_NPCS[_npc] = {
        "class": _cls,
        "note": _note,
        "items": _stock_items(_STOCK[_npc], _npc),
    }

SHOP_NPCS["Armorer"] = {
    "class": None,
    "note": "Body armour, light to heavy.",
    "items": _stock_items(_STOCK["Armorer"], "Armorer"),
}

# Which class an NPC caters to, or None when it serves everybody.
NPC_CLASS = {npc: data["class"] for npc, data in SHOP_NPCS.items()}
NPC_NOTE = {npc: data["note"] for npc, data in SHOP_NPCS.items()}


# ---------------------------
# Queries
# ---------------------------
def sell_price(item_name):
    """What an NPC pays for one of these, or None if nobody sells it.

    NPCs pay 20% under the cheapest price the item sells for, so an item stocked
    by two stalls is sold to the shop that values it least.
    """
    item = create_item(item_name)
    if item is None:
        return None
    prices = [shop["items"][item_name]["price"]
              for shop in SHOP_NPCS.values() if item_name in shop["items"]]
    if not prices:
        return None
    return int(min(prices) * SELL_RATIO)


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
