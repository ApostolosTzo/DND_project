"""Do the two builds still agree? Run this after any data or logic change.

    py tools/parity_check.py

Two checks, both failing loudly:

1. **js/game_data.js freshness** - regenerates the file in memory from the
   Python modules and byte-compares it against what is on disk. A mismatch
   means someone edited data without running `py tools/gen_js_data.py`.

2. **Logic parity** - Python and JavaScript independently implement the same
   small rules (the two-handed bonus, damage-type canonicalisation, class
   gating, sell prices, enemy maths, character construction, element riders).
   This script feeds *identical* inputs to both implementations and diffs the
   outputs case by case. The JavaScript half runs in Node (tools/js_probe.js)
   against the exact scripts the browser loads.

Data is generated now, so drift there is structurally impossible; this suite
exists for the hand-written logic, where drift is only humanly preventable.
"""
import io
import json
import os
import random
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, ROOT)

import gen_js_data as GEN     # noqa: E402
import items as IT            # noqa: E402
import shop as SH             # noqa: E402
import enemy as EN            # noqa: E402
import player as PL           # noqa: E402

# Results as {group: [(description, python_value, js_value), ...]}.
RESULTS = {}


def add(group, desc, py_val, js_val):
    RESULTS.setdefault(group, []).append((desc, py_val, js_val))


# ---------------------------------------------------------------------------
# Case grids - built from the Python catalogue so both halves test the exact
# same inputs.
# ---------------------------------------------------------------------------

def build_cases():
    cases = {}

    # Two-handed bonus: every NdX shape plus the strings a rebalance might
    # produce ("2d6+2", "1d6-") and things that are not dice at all.
    dice = []
    for count in ["", "0", "1", "2", "3", "4", "01"]:
        for sides in ["2", "4", "6", "8", "10", "12", "20", "100"]:
            dice.append(count + "d" + sides)
    dice += ["d6", "2d6+2", "1d8-1", "1d20+3", "1d100", "4d20", "10d6",
             "garbage", "", "d", "3", "3d", "d20x", " 2d6 ", "2 d6",
             "-1d6", "1d6-", "1D8", None, 0]
    cases["dice"] = dice

    cases["damage_type"] = [
        None, "", 0, "fire_damage", "cold", "fire", "ice", "lightning",
        "dark", "force", "poison", "slashing", "bludgeoning", "piercing",
        "Piercing", "Fire", "light", "physical",
    ]

    item_names = list(IT.ITEMS.keys())
    # element_of's contract is a *weapon* (its parameter is named as much), and
    # every caller in both builds guards for that. Python would raise on an
    # armour instance while JavaScript would shrug and return null, so feeding
    # it armour would test a case the game never plays - weapons, None and an
    # unknown name are the shapes it actually sees.
    weapon_names = [n for n, i in IT.ITEMS.items() if i.category == "weapon"]
    cases["element_names"] = weapon_names + [None, "Bogus Blade"]
    cases["potion_inputs"] = item_names + [None, "", "Bread"]
    cases["sell_inputs"] = item_names + [None, "Bogus"]
    cases["usable"] = {
        "items": item_names + [None],
        "classes": list(IT.ALL_CLASSES),
    }

    cases["enemy"] = {
        "templates": list(EN.TEMPLATES.keys()),
        "levels": [1, 2, 3, 4, 7, 10, 50, 200],
    }

    # Weak/resist application: the template only decides how much HP is left
    # to chew through, so a handful of them covers the multipliers, and the
    # amount list deliberately includes odd numbers - those are where Python's
    # round-half-even and JavaScript's Math.round disagree on .5 results.
    apply_types = list(IT.DAMAGE_TYPES) + [None, "fire_damage"]
    cases["apply"] = [
        {"name": name, "amount": amount, "type": t}
        for name in ["Zombie", "Slime", "Ghost", "Demon Lord"]
        for amount in list(range(1, 13)) + [13, 17, 25, 26, 33, 50, 100]
        for t in apply_types
    ]

    stat_sets = {
        "base": {s: 10 for s in PL.STAT_ORDER},
        "fighter": {"STR": 18, "DEX": 13, "CON": 16, "INT": 8, "WIS": 12, "CHA": 9},
        "caster": {"STR": 10, "DEX": 10, "CON": 10, "INT": 19, "WIS": 19, "CHA": 10},
        "rogue": {"STR": 15, "DEX": 18, "CON": 12, "INT": 10, "WIS": 10, "CHA": 10},
        "min": {s: 3 for s in PL.STAT_ORDER},
    }
    cases["_stat_sets"] = stat_sets

    # The same equipment sequence for every race/class/stat combination: it
    # walks through a shield, a two-handed stow, a refused off-hand, armour
    # swaps and an armour removal.
    steps = [
        ["weapon", "Dagger"],
        ["offhand", "Shield"],
        ["weapon", "Greatsword"],   # two-handed: the shield must stow
        ["offhand", "Dagger"],      # refused: hands are full
        ["armor", "Chainmail"],
        ["weapon", "Longsword"],    # two-handed property as well
        ["offhand", "Shield"],      # refused again
        ["weapon", "Dagger"],
        ["offhand", "Tower Shield"],
        ["armor", "Wizard Robe"],
        ["armor", None],
    ]
    cases["players"] = [
        {"name": "Tester", "race": race, "cls": cls,
         "stats": dict(stats), "steps": steps}
        for stats in stat_sets.values()
        for race in PL.RACES
        for cls in PL.CLASSES
    ]
    cases["_player_labels"] = [
        "%s/%s" % (race, cls)
        for stats in stat_sets.values()
        for race in PL.RACES
        for cls in PL.CLASSES
    ]
    cases["_steps"] = steps

    # Element riders under a frozen RNG: 0 forces every chance roll to succeed
    # (and every die to its minimum), 0.999999 forces every chance roll to
    # fail. Dark has no roll, so it must ignore the RNG entirely.
    cases["elements"] = [
        {"element": el, "stats": dict(stats), "rng": rng}
        for el in ["fire", "ice", "poison", "lightning", "dark"]
        for stats_name in ["base", "caster", "rogue"]
        for stats in [stat_sets[stats_name]]
        for rng in [0.0, 0.999999]
    ]
    cases["_element_labels"] = [
        "%s/%s/rng=%s" % (el, sn, rng)
        for el in ["fire", "ice", "poison", "lightning", "dark"]
        for sn in ["base", "caster", "rogue"]
        for rng in [0.0, 0.999999]
    ]
    return cases


# ---------------------------------------------------------------------------
# Python-side expected values
# ---------------------------------------------------------------------------

class _FixedRNG(object):
    """Pin random.random() and random.randint() while inside the block.

    enemy.inflict_element rolls for the rider and then rolls the rider's die.
    Freezing both to a constant makes the result order-independent, and the
    frozen value is interpreted exactly the way JavaScript's randInt reads
    Math.random: floor(value * (max - min + 1)) + min. So 0 makes every chance
    roll succeed and every die read its minimum, while 0.999999 makes chance
    rolls fail and dice read their maximum - identically on both sides.
    """

    def __init__(self, value):
        self.value = value
        self._orig = None

    def __enter__(self):
        self._orig = (random.random, random.randint)
        value = self.value
        random.random = lambda: value
        random.randint = lambda a, b: int(value * (b - a + 1)) + a
        return self

    def __exit__(self, *exc):
        random.random, random.randint = self._orig
        return False


def py_player(case):
    p = PL.Player(case["name"], case["race"], case["cls"], dict(case["stats"]))
    # snap[0] is the freshly built character; each later entry is the state
    # after one equipment step. The JavaScript probe builds the same shape.
    snap = [[p.max_hp, p.hp, p.ac, p.hp_per_level(), p.xp_to_next(), p.sheet()]]
    for op, arg in case["steps"]:
        item = IT.create_item(arg)
        if op == "weapon":
            p.equip_weapon(item)
        elif op == "offhand":
            p.equip_offhand(item)
        elif op == "armor":
            p.equip_armor(item)
        snap.append([
            p.max_hp, p.hp, p.ac,
            p.offhand.name if p.offhand else None,
            len(p.inventory),
            p.hands_full(),
            p.weapon.name if p.weapon else None,
            p.armor.name if p.armor else None,
        ])
    return snap


def py_element(case):
    with _FixedRNG(case["rng"]):
        p = PL.Player("Tester", "Human", "Wizard", dict(case["stats"]))
        e = EN.Enemy("Zombie", 1)
        note = e.inflict_element(case["element"], p)
        return [note, e.status, e.status_text()]


def run_python(cases):
    for d in cases["dice"]:
        add("two_handed_bonus", repr(d), IT.two_handed_bonus_for(d), None)
    for n in cases["damage_type"]:
        add("damage_type", repr(n), IT.damage_type(n), None)
    for n in cases["potion_inputs"]:
        add("heal_amount", repr(n), IT.heal_amount(n), None)
        add("is_potion", repr(n), IT.is_potion(n), None)
    for n in cases["sell_inputs"]:
        add("sell_price", repr(n), SH.sell_price(n), None)
    for n in cases["element_names"]:
        add("element_of", repr(n), IT.element_of(IT.create_item(n)), None)
    for n in cases["usable"]["items"]:
        for cls in cases["usable"]["classes"]:
            add("usable_by", "%s for %s" % (n, cls),
                IT.usable_by(IT.create_item(n), cls), None)

    for name in cases["enemy"]["templates"]:
        for level in cases["enemy"]["levels"]:
            e = EN.Enemy(name, level)
            add("enemy", "%s@lv%d" % (name, level), {
                "max_hp": e.max_hp, "ac": e.ac, "damage_dice": e.damage_dice,
                "damage_bonus": e.damage_bonus, "xp_reward": e.xp_reward,
                "gold_drop": e.gold_drop(), "weak_to": e.weak_to,
                "resists": e.resists,
            }, None)

    for c in cases["apply"]:
        e = EN.Enemy(c["name"], 1)
        total, note = e.apply_damage(c["amount"], c["type"])
        add("apply", "%s amount=%d type=%s" % (c["name"], c["amount"], c["type"]),
            [total, note, e.hp], None)

    for case, label in zip(cases["players"], cases["_player_labels"]):
        snap = py_player(case)
        for i, step in enumerate([None] + cases["_steps"]):
            desc = label if step is None else "%s after %s(%s)" % (label, step[0], step[1])
            add("player", desc, snap[i], None)

    for case, label in zip(cases["elements"], cases["_element_labels"]):
        add("element_rider", label, py_element(case), None)


def merge_js(cases, js):
    """Attach the probe's values to the Python ones, in generation order."""
    pairs = [
        ("two_handed_bonus", js["two_handed"]),
        ("damage_type", js["damage_type"]),
        ("heal_amount", js["heal"]),
        ("is_potion", js["is_potion"]),
        ("sell_price", js["sell"]),
        ("element_of", js["element_of"]),
        ("usable_by", js["usable"]),
    ]
    for group, values in pairs:
        rows = RESULTS[group]
        assert len(rows) == len(values), (group, len(rows), len(values))
        for i, v in enumerate(values):
            d, py_v, _ = rows[i]
            rows[i] = (d, py_v, v)

    rows = RESULTS["enemy"]
    i = 0
    for name in cases["enemy"]["templates"]:
        for j, level in enumerate(cases["enemy"]["levels"]):
            d, py_v, _ = rows[i]
            rows[i] = (d, py_v, js["enemy"][name][j])
            i += 1

    rows = RESULTS["apply"]
    assert len(rows) == len(js["apply"])
    for i, v in enumerate(js["apply"]):
        d, py_v, _ = rows[i]
        rows[i] = (d, py_v, v)

    rows = RESULTS["player"]
    flat = []
    for case, snap in zip(cases["players"], js["players"]):
        for v in snap:
            flat.append(v)
    assert len(rows) == len(flat), (len(rows), len(flat))
    for i, v in enumerate(flat):
        d, py_v, _ = rows[i]
        rows[i] = (d, py_v, v)

    rows = RESULTS["element_rider"]
    assert len(rows) == len(js["elements"])
    for i, v in enumerate(js["elements"]):
        d, py_v, _ = rows[i]
        rows[i] = (d, py_v, v)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def report(fresh_ok, fresh_detail):
    print("=== 1. js/game_data.js freshness ===")
    if fresh_ok:
        print("OK   " + fresh_detail)
    else:
        print("FAIL " + fresh_detail)
    print("")
    print("=== 2. logic parity (Python vs JavaScript) ===")

    failures = 0 if fresh_ok else 1
    for group, rows in RESULTS.items():
        bad = [(d, py_v, js_v) for d, py_v, js_v in rows if py_v != js_v]
        if not bad:
            print("OK   %-15s %d cases" % (group, len(rows)))
            continue
        failures += 1
        print("FAIL %-15s %d/%d cases differ" % (group, len(bad), len(rows)))
        for d, py_v, js_v in bad[:5]:
            print("       %s" % d)
            print("         python: %r" % (py_v,))
            print("         js:     %r" % (js_v,))
        if len(bad) > 5:
            print("       ... and %d more" % (len(bad) - 5))
    print("")
    if failures:
        print("FAILED (%d group(s))" % failures)
        return 1
    print("all groups agree")
    return 0


def main():
    # --- 1. freshness -----------------------------------------------------
    expected = GEN.render()
    path = os.path.join(ROOT, "js", "game_data.js")
    try:
        with io.open(path, encoding="utf-8", newline="") as f:
            actual = f.read()
    except IOError as exc:
        print("cannot read js/game_data.js: %s" % exc)
        return 1
    fresh_ok = expected == actual
    fresh_detail = ("js/game_data.js is up to date (%d bytes)" % len(actual)
                    if fresh_ok else
                    "js/game_data.js is STALE - run: py tools/gen_js_data.py")

    # --- 2. logic parity ---------------------------------------------------
    cases = build_cases()
    run_python(cases)

    scratch = os.path.join(tempfile.gettempdir(), "opencode")
    if not os.path.isdir(scratch):
        os.makedirs(scratch)
    cases_path = os.path.join(scratch, "parity_cases.json")
    probe_path = os.path.join(HERE, "js_probe.js")
    with io.open(cases_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(cases, f)

    try:
        proc = subprocess.run(
            ["node", probe_path, cases_path, ROOT],
            capture_output=True, encoding="utf-8", errors="replace")
    except OSError as exc:
        print("cannot run node: %s" % exc)
        return 2

    if proc.returncode != 0:
        print("js_probe.js failed (exit %d):" % proc.returncode)
        print(proc.stderr.strip())
        return 2
    try:
        js = json.loads(proc.stdout)
    except ValueError as exc:
        print("js_probe.js produced unreadable JSON (%s):" % exc)
        print(proc.stdout[:2000])
        print(proc.stderr[:2000])
        return 2

    merge_js(cases, js)
    return report(fresh_ok, fresh_detail)


if __name__ == "__main__":
    sys.exit(main())
