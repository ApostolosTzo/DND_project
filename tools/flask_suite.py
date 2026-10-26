# Behavioural suite for the Flask build: drives the real game_server routes
# through the test client, mirroring the flows tools/js_suite.js exercises in
# the browser build - create, shop, fight, element riders, potions, inventory,
# saves.
#
#   py tools/flask_suite.py
#
# Exit code 0 when every check passes. This suite tests the Python build on
# its own; tools/parity_check.py guarantees both builds compute the same
# values for the same inputs, so green here + green there = both builds
# behave identically.
#
# Determinism: random.random()/random.randint() are frozen during character
# creation and combat (see pinned_rng). randInt(min,max) reads
# floor(r*(max-min+1))+min, so 0.999999 makes every roll its maximum and 0.5
# a middle roll - the exact numbers asserted below are computed from that
# rule. Saves go to a throwaway temp dir so the repo's saves/ is untouched
# and each run starts with an empty slot list.

import json
import os
import random
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# Saves must land in scratch, not in the repo. Patch the module global before
# any route can call save_game(); the helpers read it at call time.
import save_load
save_load.SAVES_DIR = tempfile.mkdtemp(prefix="flask_suite_saves_")

from game_server import app, gs, grant_xp
from enemy import Enemy
from items import ITEMS, create_item, two_handed_bonus

client = app.test_client()

passed = 0
failures = []


def check(desc, actual, expected):
    global passed
    if actual == expected:
        passed += 1
    else:
        failures.append(desc)
        print("FAIL " + desc)
        print("  expected: " + json.dumps(expected, default=repr))
        print("  actual:   " + json.dumps(actual, default=repr))


class pinned_rng:
    """Freeze random.random()/random.randint() to one value inside the block.

    randint(a, b) mirrors JS randInt: floor(value * (b - a + 1)) + a, so the
    same frozen value yields the same die face in both builds.
    """
    def __init__(self, value):
        self.value = value

    def __enter__(self):
        self._orig = (random.random, random.randint)
        v = self.value
        random.random = lambda: v
        random.randint = lambda a, b: int(v * (b - a + 1)) + a
        return self

    def __exit__(self, *exc):
        random.random, random.randint = self._orig
        return False


# A fresh game with a Fighter named Testor, every stat 19, standing in town.
def new_game(cls="Fighter"):
    with pinned_rng(0.999999):
        return client.post("/start", json={
            "name": "Testor",
            "race": "Human",
            "class": cls
        })


def has_item(name):
    return any(i.name == name for i in gs["player"].inventory)


def count_item(name):
    return sum(1 for i in gs["player"].inventory if i.name == name)


# --- boot ------------------------------------------------------------------
d = client.get("/state").get_json()
check("state: the app boots to the main menu", d["screen"], "main_menu")
d = client.get("/create_form").get_json()
check("create_form: four races and four classes",
      [len(d["races"]), len(d["classes"])], [4, 4])

# --- creation --------------------------------------------------------------
d = new_game().get_json()
check("create: lands in town", d["screen"], "town")
check("create: every stat is 19 (frozen RNG)", d["player"]["stats"],
      {"STR": 19, "DEX": 19, "CON": 19, "INT": 19, "WIS": 19, "CHA": 19})
check("create: Fighter HP is class 15 + CON+4", d["player"]["max_hp"], 19)
# Chainmail 14 + DEX mod +4, capped by the armour's dex_limit of 2.
check("create: Fighter AC is 14 + capped DEX", d["player"]["ac"], 16)
check("create: starts with a Longsword", d["player"]["weapon"], "Longsword")
check("create: starts in Chainmail", d["player"]["armor"], "Chainmail")
check("create: 15 starting potions in the bag",
      count_item("Healing Potion"), 15)
check("create: level 1, no gold",
      [d["player"]["level"], d["player"]["gold"]], [1, 0])

# --- shop: buy, class gate, gold gate, sell --------------------------------
new_game()
gs["player"].add_gold(500)

# Real flow: town -> Visit Shop -> Weaponsmith (index 1 of town's stalls).
d = client.post("/action", json={"choice": 1}).get_json()
check("shop: opens the stall list", d["screen"], "shop_select")
client.post("/action", json={"choice": 1})
check("shop: standing at the Weaponsmith", gs["shop_name"], "Weaponsmith")

d = client.post("/shop_buy", json={"item": "Longsword", "qty": 1}).get_json()
check("shop buy: deducts the listed price", d["player"]["gold"], 470)
check("shop buy: a second Longsword lands in the bag",
      count_item("Longsword"), 1)
check("shop buy: says what happened",
      d["log"][0], "Bought 1 \u00d7 Longsword for 30g!")

# The Wizard's stall sells Ember Blades - a Wizard-only weapon. A Fighter
# clicking the greyed-out row gets refused by /shop_buy itself, not UI.
client.post("/action", json={"choice": 1})   # shop -> stall list
client.post("/action", json={"choice": 4})   # index 4 = Wizard
check("shop: standing at the Wizard", gs["shop_name"], "Wizard")
d = client.post("/shop_buy", json={"item": "Ember Blade", "qty": 1}).get_json()
check("shop buy: another class's weapon is refused", d["log"][0],
      "Ember Blade is a Wizard weapon - not your class's weapon.")
check("shop buy: refusal costs no gold", d["player"]["gold"], 470)

# Not enough gold.
gs["player"].gold = 5
client.post("/action", json={"choice": 1})
client.post("/action", json={"choice": 1})   # back to the Weaponsmith
d = client.post("/shop_buy", json={"item": "Longsword", "qty": 1}).get_json()
check("shop buy: broke player hears about it", d["log"][0],
      "Not enough gold! Need 30g, you have 5g.")
check("shop buy: still broke", d["player"]["gold"], 5)

# Sell: 80% of the listed price, one item at a time.
gs["player"].add_item(create_item("Dagger"))
d = client.post("/sell", json={"item": "Dagger"}).get_json()
check("sell: pays 80% of shop price (30 -> 24)", d["player"]["gold"], 29)
check("sell: removes the item", has_item("Dagger"), False)
check("sell: says what happened", d["log"][0], "Sold Dagger for 24g.")

# --- combat: hit maths, weak multiplier, victory rewards -------------------
new_game()
with pinned_rng(0.999999):               # every roll at maximum
    d = client.post("/action", json={"choice": 0}).get_json()   # Fight
    check("combat: the fight opens", d["screen"], "combat")
    # The generator's pick is random; pin the monster so the maths below
    # is exact. Enemy construction itself is parity-checked elsewhere.
    gs["enemy"] = Enemy("Zombie", 1)
    d = client.post("/attack", json={"offhand": False}).get_json()

# The Longsword carries STR+1, so effective STR is 20 (+5). Max 1d8 (8)
# + 5 + 1 two-handed = 14, and the Zombie is weak to slashing: 14 x 1.5
# = 21. HP 22 -> 1.
check("combat: weak hit lands for 21", d["enemy"]["hp"], 1)
check("combat: floating damage number", d["last_damage"],
      {"amount": 21, "kind": "hit", "weak": True})
check("combat: the log explains the weakness",
      any("WEAK to slashing" in line for line in d["log"]), True)
# The Zombie swings back: d20 max 20 + 2 beats AC 16; d6 max 6 + 1 = 7.
check("combat: the monster retaliates", d["player"]["hp"], 12)

# Finish it: rewards are the Zombie's own drops (8 gold, 35 XP). The
# material drop needs random() < 0.75, so step down from RNG max first.
with pinned_rng(0.5):
    gs["enemy"].hp = 1
    d = client.post("/attack", json={"offhand": False}).get_json()
check("combat: victory clears the enemy", d["enemy"], None)
check("combat: loots the gold drop", d["player"]["gold"], 8)
check("combat: gains the XP reward", d["player"]["xp"], 35)
check("combat: collects the quest material",
      has_item("Rotten Flesh"), True)

# --- XP curve and level-up maths -------------------------------------------
new_game()
check("xp: level 1 needs 100", gs["player"].xp_to_next(), 100)
gs["player"].level = 7
check("xp: level 7 needs 700", gs["player"].xp_to_next(), 700)
gs["player"].level = 1

grant_xp(gs["player"], 100)              # exactly one level
p = gs["player"]
check("level up: level increments", p.level, 2)
check("level up: HP grows by hp_per_level (19 + 4)", p.max_hp, 23)
check("level up: HP fully restored", p.hp, 23)
check("level up: no leftover XP", p.xp, 0)
check("level up: finds level x 10 gold", p.gold, 20)
check("level up: earns a skill point", p.skill_points, 1)

# --- element rider: fire catches on a passing chance roll -------------------
# Fire weapons are the Wizard armory's (Ember Blade). INT 19 -> effective
# 20 with the blade's INT+1 -> chance 20% + 3% x 20 = 80%, capped 60%.
new_game("Wizard")
gs["player"].equip_weapon(create_item("Ember Blade"))
gs["enemy"] = Enemy("Zombie", 1)
with pinned_rng(0.5):                    # d20 reads 11 -> hits; 0.5 < 0.6
    d = client.post("/attack", json={"offhand": False}).get_json()
# The Ember Blade carries INT+1 (effective INT 20). The hit: 1d8 reads 5
# +4 STR (the blade is no finesse weapon) = 9, fire is neutral on the
# Zombie -> 22-9 = 13, then the burn ticks at the top of its turn: 1d4
# reads 3 +5 INT = 8 -> 5.
check("fire: the hit lands", gs["enemy"].hp, 5)
check("fire: ignites and is recorded", gs["enemy"].status["burn_rounds"], 1)
check("fire: burn damage scales on INT", gs["enemy"].status["burn_damage"], 8)
check("fire: the log says it caught",
      any("catches fire" in line for line in d["log"]), True)
check("fire: burning monster still swings (and misses AC 14)",
      d["player"]["hp"], 15)

# --- element rider: fire never catches on a failing roll --------------------
new_game("Wizard")
gs["player"].equip_weapon(create_item("Ember Blade"))
gs["enemy"] = Enemy("Zombie", 1)
with pinned_rng(0.999999):               # hits, but fails the 60% rider
    d = client.post("/attack", json={"offhand": False}).get_json()
check("fire: failing the chance roll leaves no burn",
      gs["enemy"].status["burn_rounds"], 0)
check("fire: the log says so",
      any("did not catch" in line for line in d["log"]), True)

# --- potions: combat list, heal, consume ------------------------------------
new_game()
client.post("/action", json={"choice": 0})   # Fight -> combat
gs["player"].hp = 1
d = client.post("/action", json={"choice": 0}).get_json()   # Use Item
check("combat: the Use Item screen opens", d["screen"], "combat_item")
check("potion: the strongest usable one is offered first",
      d["combat_items"][0], "Healing Potion")

d = client.post("/action", json={"choice": 0}).get_json()   # drink it
check("potion: heals its listed 10", gs["player"].hp, 11)
check("potion: one is consumed", count_item("Healing Potion"), 14)
check("potion: says what happened",
      any("Restored 10 HP" in line for line in d["log"]), True)

# At full HP the heal clamps to nothing (JS's bestUsablePotion would simply
# not offer it; Python's list stays but restores 0 HP).
gs["player"].hp = gs["player"].max_hp
client.post("/action", json={"choice": 0})   # Use Item again
d = client.post("/action", json={"choice": 0}).get_json()
check("potion: a full-HP drink restores nothing",
      any("Restored 0 HP" in line for line in d["log"]), True)

# --- two-handed weapons lock the off-hand -----------------------------------
new_game()
p = gs["player"]
# The starting bag is only potions; hand the suite its test gear.
for name in ("Shield", "Dagger", "Greatsword"):
    p.add_item(create_item(name))

d = client.post("/inventory_equip", json={"item": "Shield"}).get_json()
check("two-handed: shield refused while the Longsword is held",
      p.offhand, None)
check("two-handed: the game says why",
      isinstance(d["log"][0], str) and d["log"][0] != "", True)
check("two-handed: offhand_block_reason() is a string",
      isinstance(p.offhand_block_reason(), str), True)

# A one-handed weapon takes the main hand off the two-handed Longsword...
client.post("/inventory_equip", json={"item": "Dagger"})
check("two-handed: a one-handed weapon replaces the two-handed one",
      p.weapon.name, "Dagger")
check("two-handed: hand now free", p.offhand, None)

# ...so the shield fits, and a Greatsword upgrade stows it again.
client.post("/inventory_equip", json={"item": "Shield"})
check("two-handed: shield stows once a hand is free",
      p.offhand.name, "Shield")
client.post("/inventory_equip", json={"item": "Greatsword"})
check("two-handed: the shield is stowed, not lost", p.offhand, None)
check("two-handed: stowed shield goes to the bag",
      has_item("Shield"), True)
check("two-handed: Greatsword carries its +1 bonus",
      two_handed_bonus(p.weapon), 1)

# --- saving and loading round-trips the run --------------------------------
new_game()
d = client.get("/load_list").get_json()
check("load: an empty save slot reads as no saves",
      d["screen"], "main_menu")

gs["player"].add_gold(123)
gs["player"].hp = 5
d = client.post("/save", json={"name": "suite"}).get_json()
check("save: reports it", d["log"][0], "Game saved as 'suite'!")

gs["player"].gold = 0
gs["player"].hp = 1
d = client.get("/load_list").get_json()
check("load: the save is listed", d["screen"], "load_menu")
d = client.post("/action", json={"choice": 0}).get_json()
check("save/load: gold survives", d["player"]["gold"], 123)
check("save/load: wounded HP survives", d["player"]["hp"], 5)
check("save/load: back in town", d["screen"], "town")

# --- catalogue and world map -----------------------------------------------
items = client.get("/item_details").get_json()["items"]
check("catalogue: one entry per defined item", len(items), len(ITEMS))
ls = items["Longsword"]
check("catalogue: Longsword is a two-handed 1d8 slashing weapon",
      [ls["category"], ls["damage"], ls["type"], ls["two_handed"]],
      ["weapon", "1d8", "slashing", 1])
check("catalogue: Fighter may wield it", "Fighter" in ls["classes"], True)

d = client.get("/map_data").get_json()
check("map: four locations", len(d["locations"]), 4)
check("map: the run starts in town", d["current_location"], "town")
check("map: town links to both villages",
      d["locations"]["town"]["connects_to"], ["village1", "village2"])

d = client.post("/travel", json={"location": "dungeon"}).get_json()
check("travel: unreachable from town", d["log"][0],
      "You can't reach that location from here.")
d = client.post("/travel", json={"location": "village1"}).get_json()
check("travel: arrives at Village 1", d["log"][0],
      "You arrive at Village 1.")
check("travel: updates the location", d["current_location"], "village1")
d = client.post("/travel", json={"location": "village1"}).get_json()
check("travel: already there says so", d["log"][0],
      "You are already here.")
d = client.post("/travel", json={"location": "town"}).get_json()
check("travel: the road back works", d["current_location"], "town")

# --- report ----------------------------------------------------------------
print("")
if failures:
    print("FAILED: " + str(len(failures)) + " check(s), " +
          str(passed) + " passed")
    sys.exit(1)
print("all " + str(passed) + " checks passed")
