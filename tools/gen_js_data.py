"""Emit js/game_data.js from the Python catalogue.

**Python is the single source of truth for game data.** This script reads the
imported modules - items, shop, enemy, player, world_map - and serialises every
shared constant into one generated file that the PWA loads before anything
else:

    py tools/gen_js_data.py     # regenerate after any data change

Why this exists
---------------
Before it, every table lived twice: once in Python and once hand-mirrored in
js/*.js, policed by a parity check that could only catch drift *after* it
happened - and routinely missed it (race bonuses drifted silently for a whole
session because nothing compared them). Now the JS side aliases GAME_DATA and
the mirror cannot drift at all: there is only one copy.

What lands in GAME_DATA
-----------------------
Only *data* - the tables and constants. Logic (combat, the two-handed rule,
element ticking, class gating) stays hand-written on both sides, because it is
small, test-covered, and genuinely different code in each language.

Key names keep their Python spelling exactly (snake_case), so the mapping from
module attribute to GAME_DATA key is 1:1 and checkable - see tools/parity_check.py,
which re-imports everything and diffs it against the emitted file.

Determinism
-----------
dicts preserve insertion order, floats round-trip through json, and non-ASCII
is escaped, so two runs on the same source always produce byte-identical
output. tools/parity_check.py fails if this file is stale.
"""
import io
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import items as IT          # noqa: E402
import shop as SH           # noqa: E402
import enemy as EN          # noqa: E402
import player as PL         # noqa: E402
from world_map import LOCATIONS  # noqa: E402

OUT = os.path.join(ROOT, "js", "game_data.js")


def item_to_data(item):
    """One catalogue entry, shaped exactly like the JS constructor needs.

    Only the fields each category actually carries - a weapon has no base_ac
    and a potion has no dice - so the emitted file is the catalogue and
    nothing else.
    """
    d = {"name": item.name, "category": item.category}
    if item.category == "weapon":
        d["damage_dice"] = item.damage_dice
        d["damage_type"] = item.damage_type
        d["properties"] = list(item.properties)
        d["stats_bonus"] = dict(item.stats_bonus)
    elif item.category == "armor":
        d["base_ac"] = item.base_ac
        d["armor_type"] = item.armor_type
        d["dex_limit"] = item.dex_limit
        d["properties"] = list(item.properties)
        d["stats_bonus"] = dict(item.stats_bonus)
    else:  # "item"
        d["description"] = item.description
        d["effect"] = item.effect
        d["stats_bonus"] = dict(item.stats_bonus)
    return d


def build():
    data = {}

    # ---- items.py --------------------------------------------------------
    data["items"] = {name: item_to_data(item) for name, item in IT.ITEMS.items()}
    data["starting_potions"] = list(IT.STARTING_POTIONS)
    data["starting_gear"] = {
        c: {"weapon": g["weapon"], "armor": g["armor"], "items": list(g["items"])}
        for c, g in IT.STARTING_GEAR.items()
    }
    data["potion_heal"] = dict(IT.POTION_HEAL)
    data["potion_min_level"] = dict(IT.POTION_MIN_LEVEL)
    data["materials"] = dict(IT.MATERIALS)
    data["damage_type_aliases"] = dict(IT.DAMAGE_TYPE_ALIASES)
    data["damage_types"] = list(IT.DAMAGE_TYPES)
    data["element_status"] = dict(IT.ELEMENT_STATUS)
    data["two_handed_bonus"] = dict(IT.TWO_HANDED_BONUS)
    data["all_classes"] = list(IT.ALL_CLASSES)
    # list() per entry, so a shared ALL_CLASSES list never aliases the same
    # JS array across a dozen weapons.
    data["weapon_classes"] = {n: list(c) for n, c in IT.WEAPON_CLASSES.items()}

    # ---- player.py -------------------------------------------------------
    data["races"] = {
        r: {"desc": d["desc"], "bonuses": dict(d["bonuses"])}
        for r, d in PL.RACES.items()
    }
    data["classes"] = {
        c: ({"desc": d["desc"], "hp": d["hp"], "primary": d["primary"],
             "bonuses": dict(d["bonuses"])} if "bonuses" in d
            else {"desc": d["desc"], "hp": d["hp"], "primary": d["primary"]})
        for c, d in PL.CLASSES.items()
    }
    data["stat_order"] = list(PL.STAT_ORDER)

    # ---- shop.py ---------------------------------------------------------
    # The DERIVED stock, so the whole tier/price/spread machinery can be
    # deleted from js/shop.js. Insertion order is the display order.
    data["shops"] = {
        npc: {"class": shop["class"], "note": shop["note"],
              "items": {n: {"price": d["price"], "min_level": d["min_level"]}
                        for n, d in shop["items"].items()}}
        for npc, shop in SH.SHOP_NPCS.items()
    }
    data["unlock_tiers"] = list(SH.UNLOCK_TIERS)
    data["tier_base"] = SH.TIER_BASE
    data["tier_mult"] = list(SH.TIER_MULT)
    data["sell_ratio"] = SH.SELL_RATIO
    data["armory_npcs"] = [[npc, cls, note] for npc, cls, note in SH.ARMORY_NPCS]

    # ---- enemy.py --------------------------------------------------------
    data["templates"] = {n: dict(t) for n, t in EN.TEMPLATES.items()}
    data["boss_names"] = list(EN.BOSS_NAMES)
    data["vulnerabilities"] = {
        n: {"weak": list(v["weak"]), "resist": list(v["resist"])}
        for n, v in EN.VULNERABILITIES.items()
    }
    data["weak_multiplier"] = EN.WEAK_MULTIPLIER
    data["resist_multiplier"] = EN.RESIST_MULTIPLIER
    data["drops"] = dict(EN.DROPS)
    data["drop_chance"] = EN.DROP_CHANCE
    data["drop_min"] = EN.DROP_MIN
    data["drop_max"] = EN.DROP_MAX
    data["xp_reward_multiplier"] = EN.XP_REWARD_MULTIPLIER
    data["gold_reward_multiplier"] = EN.GOLD_REWARD_MULTIPLIER
    # The element constants keep their exact Python names so the JS aliases
    # are 1:1 and diffable - no restructuring to get wrong.
    data["element_rules"] = {
        "BURN_ROUNDS": EN.BURN_ROUNDS,
        "BURN_DIE": EN.BURN_DIE,
        "BURN_BASE_CHANCE": EN.BURN_BASE_CHANCE,
        "BURN_CHANCE_PER_INT": EN.BURN_CHANCE_PER_INT,
        "BURN_MAX_CHANCE": EN.BURN_MAX_CHANCE,
        "FREEZE_BASE_CHANCE": EN.FREEZE_BASE_CHANCE,
        "FREEZE_INT_PER_POINT": EN.FREEZE_INT_PER_POINT,
        "FREEZE_CHANCE_PER_INT_BLOCK": EN.FREEZE_CHANCE_PER_INT_BLOCK,
        "FREEZE_MAX_CHANCE": EN.FREEZE_MAX_CHANCE,
        "FREEZE_INT_THRESHOLD": EN.FREEZE_INT_THRESHOLD,
        "FREEZE_MIN_ROUNDS": EN.FREEZE_MIN_ROUNDS,
        "FREEZE_MAX_ROUNDS": EN.FREEZE_MAX_ROUNDS,
        "POISON_BASE_CHANCE": EN.POISON_BASE_CHANCE,
        "POISON_CHANCE_PER_DEX": EN.POISON_CHANCE_PER_DEX,
        "POISON_MAX_CHANCE": EN.POISON_MAX_CHANCE,
        "POISON_MAX_ROUNDS": EN.POISON_MAX_ROUNDS,
        "LIGHTNING_ROUNDS": EN.LIGHTNING_ROUNDS,
        "LIGHTNING_DIE": EN.LIGHTNING_DIE,
        "LIGHTNING_BASE_CHANCE": EN.LIGHTNING_BASE_CHANCE,
        "LIGHTNING_WIS_PER_POINT": EN.LIGHTNING_WIS_PER_POINT,
        "LIGHTNING_CHANCE_PER_WIS_BLOCK": EN.LIGHTNING_CHANCE_PER_WIS_BLOCK,
        "LIGHTNING_MAX_CHANCE": EN.LIGHTNING_MAX_CHANCE,
        "DARK_ROUNDS": EN.DARK_ROUNDS,
        "DARK_DIE": EN.DARK_DIE,
        "DARK_STR_PER_POINT": EN.DARK_STR_PER_POINT,
        "DARK_DAMAGE_PER_STR_BLOCK": EN.DARK_DAMAGE_PER_STR_BLOCK,
    }

    # ---- world_map.py ----------------------------------------------------
    data["locations"] = {
        k: {"name": v["name"], "x": v["x"], "y": v["y"], "type": v["type"],
            "connects_to": list(v["connects_to"]), "shops": list(v.get("shops", []))}
        for k, v in LOCATIONS.items()
    }

    return data


HEADER = """// GENERATED FILE - do not edit by hand.
//
// Every table below is read straight out of the Python catalogue (items.py,
// shop.py, enemy.py, player.py, world_map.py) by tools/gen_js_data.py. Python
// is the single source of truth for game data; the js/*.js modules alias these
// values instead of mirroring them, so the two builds cannot drift.
//
// To change a price, a dice string, a monster or a race bonus: edit the Python
// file, then run  py tools/gen_js_data.py  and re-run the test suites.
//
// Logic (combat maths, the two-handed rule, element ticking, class gating)
// deliberately stays hand-written on both sides - only data is generated.
"""


def render():
    """The exact file contents for the current Python sources.

    Called by main() to write and by tools/parity_check.py to verify, so the
    freshness check can never disagree with the generator about what the output
    should be.
    """
    return _serialize(build())


def _serialize(data):
    body = json.dumps(data, indent=1, ensure_ascii=True)
    return HEADER + "\nconst GAME_DATA = " + body + ";\n"


def main():
    data = build()
    text = _serialize(data)
    io.open(OUT, "w", encoding="utf-8", newline="\n").write(text)

    stats = [
        ("items", len(data["items"])),
        ("shops", len(data["shops"])),
        ("shop entries", sum(len(s["items"]) for s in data["shops"].values())),
        ("races", len(data["races"])),
        ("classes", len(data["classes"])),
        ("monsters", len(data["templates"])),
        ("locations", len(data["locations"])),
        ("element constants", len(data["element_rules"])),
    ]
    print("js/game_data.js written: %d bytes" % len(text))
    for label, n in stats:
        print("  %-16s %d" % (label, n))


if __name__ == "__main__":
    main()
