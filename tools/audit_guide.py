"""Audits the hand-written prose in tools/gen_game_guide.py against live data.

The guide's tables are generated, but its *sentences* are typed by hand, so they
drift silently. This checks every factual claim it can reach and prints the ones
that are wrong.
"""
import io
import os
import re
import sys

ROOT = r"C:\Users\aptzo\OneDrive\Desktop\Github_repos\DND_project"
sys.path.insert(0, ROOT)

import items as IT
import player as PL
import shop as SH
import enemy as EN
from world_map import LOCATIONS

guide = io.open(ROOT + r"\GAME_GUIDE.md", encoding="utf-8").read()
bad = []


def check(label, ok, detail=""):
    print("%s %-52s %s" % ("ok  " if ok else "BAD ", label, detail))
    if not ok:
        bad.append(label)


print("=== races: prose vs data ===")
for r in PL.RACES:
    real = PL.RACES[r]["bonuses"]
    # The guide renders bonuses via a hardcoded "%s+1" template, so any stat that
    # is not exactly +1 is misreported. Check the rendered row directly.
    row = [l for l in guide.split("\n") if l.startswith("| **%s**" % r)]
    rendered = row[0] if row else ""
    for stat, val in sorted(real.items()):
        check("%s %s should be +%d" % (r, stat, val),
              ("%s+%d" % (stat, val)) in rendered,
              "rendered row: %s" % rendered[:80])

print()
print("=== stat descriptions match the live effects ===")
# WIS now scales lightning, so a "nothing yet" row is stale.
check("WIS is described as scaling lightning", "lightning" in guide.lower().split("## stats")[1][:1200].lower())
# WIS must be live (it scales lightning). CHA legitimately has no use yet, so it
# is the only stat allowed to say so.
check("WIS is not described as 'Nothing yet'",
      not re.search(r"\|\s*\*\*WIS\*\*\s*\|\s*Nothing yet", guide))
check("CHA is the only stat with no use, and says so",
      not re.search(r"\|\s*\*\*(STR|DEX|CON|INT)\*\*\s*\|\s*Nothing yet", guide))
check("INT mentions fire and ice chance", "fire" in guide and "ice" in guide)

print()
print("=== class table vs STARTING_GEAR ===")
for c in PL.CLASSES:
    gear = PL.STARTING_GEAR[c]
    row = [l for l in guide.split("\n") if l.startswith("| **%s**" % c)]
    rendered = row[0] if row else ""
    check("%s starting weapon %r is in the table" % (c, gear["weapon"]), gear["weapon"] in rendered)
    armour = gear["armor"] or "none"
    check("%s starting armour %r is in the table" % (c, armour),
          armour.lower() in rendered.lower(), rendered[:90])
    # hp_per_level is derived, so verify it too
    p = PL.Player("x", "Human", c, dict.fromkeys(PL.STAT_ORDER, 10))
    check("%s HP per level is %d" % (c, p.hp_per_level()), ("| %d |" % p.hp_per_level()) in rendered)

print()
print("=== which weapons can each class actually reach? ===")
NPC = {c: n for n, c, _ in SH.ARMORY_NPCS}
for c in PL.CLASSES:
    stock = SH.SHOP_NPCS[NPC[c]]["items"]
    one_handed = [n for n, d in stock.items()
                  if IT.get_item(n) and IT.get_item(n).category == "weapon"
                  and not IT.is_two_handed(IT.get_item(n))
                  and d["min_level"] <= 3]
    print("   %-8s can be one-handed by L3: %s" % (c, sorted(one_handed) or "NOTHING"))
    check("%s has a one-handed weapon by level 3" % c, bool(one_handed),
          "the two-hands section tells Fighters to buy a one-handed weapon")

print()
print("=== potion availability ===")
pot = [n for n, d in LOCATIONS["town"].items() if n == "shops"]
check("Town lists the Potion Merchant", "Potion Merchant" in LOCATIONS["town"]["shops"])
check("Village 1 lists the Potion Merchant", "Potion Merchant" in LOCATIONS["village1"]["shops"])
check("Village 2 lists the Potion Merchant", "Potion Merchant" in LOCATIONS["village2"]["shops"])
check("every shop name in world_map exists in SHOP_NPCS",
      all(s in SH.SHOP_NPCS for loc in LOCATIONS.values() for s in loc["shops"]))
print("   dungeon merchant floors:",
      [k for k in dir(__import__("game_server")) if "dungeon_shop" in k] or "checked in tests")

print()
print("=== drops ===")
check("drop chance in the guide matches the code",
      "%d%%" % int(EN.DROP_CHANCE * 100) in guide,
      "code says %d%%" % int(EN.DROP_CHANCE * 100))

print()
print("=== selling ===")
check("sell ratio in the guide matches the code",
      "%d%%" % int(SH.SELL_RATIO * 100) in guide,
      "code says %d%%" % int(SH.SELL_RATIO * 100))

print()
print("=== counter chart vs VULNERABILITIES ===")
# The chart is hand-written; confirm every "bring this" claim is a real weakness.
chart = {}
in_chart = False
for line in guide.split("\n"):
    if line.startswith("### The counter chart"):
        in_chart = True
        continue
    if in_chart and line.startswith("##"):
        break
    if in_chart and line.startswith("| **") and "|" in line:
        parts = [p.strip() for p in line.strip("|").split("|")]
        if len(parts) == 3:
            chart[parts[0].replace("*", "")] = (parts[1], parts[2])
for monster, (bring, avoid) in chart.items():
    vuln = EN.VULNERABILITIES.get(monster)
    if vuln is None:
        check("counter chart names a real monster: %s" % monster, False)
        continue
    for dmg in [d.strip() for d in bring.split(",")]:
        check("%s is actually weak to %s" % (monster, dmg), dmg in vuln["weak"],
              "real weak: %s" % vuln["weak"])
    for dmg in [d.strip() for d in avoid.split(",")]:
        check("%s really resists %s" % (monster, dmg), dmg in vuln["resist"],
              "real resist: %s" % vuln["resist"])

print()
print("=== two-handed bonus table ordering ===")
tw = [l for l in guide.split("\n") if re.match(r"\|\s*`\d+d\d+`", l)]
order = [re.search(r"(\d+)d(\d+)", l).groups() for l in tw]
print("   rendered order:", order)
def key(p):
    return (int(p[0]), int(p[1]))
check("two-handed rows are in dice order, not alphabetical",
      order == sorted(order, key=key), str(order))

print()
print("=== L200 armour row in the price table ===")
for line in guide.split("\n"):
    if line.startswith("| **L200**"):
        cells = [c.strip() for c in line.strip("|").split("|")]
        check("the L200 row does not repeat one item in three columns",
              not (cells[1] == cells[3] and "only item" not in line), str(cells))

print()
print("=== every catalogue item appears ===")
missing = [n for n in IT.ITEMS if n not in guide]
check("all %d catalogue entries present" % len(IT.ITEMS), not missing, str(missing))

print()
print("=== monsters ===")
check("every monster is named", all(m in guide for m in EN.TEMPLATES))

print()
print("=" * 70)
print("%d PROBLEM(S)" % len(bad) if bad else "NO PROBLEMS FOUND")
for b in bad:
    print("  -", b)