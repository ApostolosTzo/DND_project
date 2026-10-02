"""Generates GAME_GUIDE.md from the live game catalogue.

Every table in the guide is read straight out of items.py / shop.py / enemy.py /
player.py / world_map.py, so the guide cannot drift from the game: re-run this
after any balance change and commit the result.

    py tools/gen_game_guide.py

Run it from anywhere; it locates the repository itself.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from items import (ITEMS, MATERIALS, POTION_HEAL, POTION_MIN_LEVEL,
                   TWO_HANDED_BONUS, is_two_handed, two_handed_bonus,
                   damage_type, element_of, is_potion, two_handed_bonus_for,
                   WEAPON_CLASSES, ALL_CLASSES)
from shop import (SHOP_NPCS, SELL_RATIO, UNLOCK_TIERS, ARMORY_NPCS, NPC_CLASS)
from enemy import (TEMPLATES, VULNERABILITIES, DROPS, BOSS_NAMES,
                   XP_REWARD_MULTIPLIER, GOLD_REWARD_MULTIPLIER,
                   WEAK_MULTIPLIER, RESIST_MULTIPLIER,
                   BURN_ROUNDS, BURN_DIE,
                   BURN_BASE_CHANCE, BURN_CHANCE_PER_INT, BURN_MAX_CHANCE,
                   FREEZE_INT_THRESHOLD, FREEZE_MIN_ROUNDS, FREEZE_MAX_ROUNDS,
                   FREEZE_BASE_CHANCE, FREEZE_INT_PER_POINT,
                   FREEZE_CHANCE_PER_INT_BLOCK, FREEZE_MAX_CHANCE,
                   POISON_BASE_CHANCE, POISON_CHANCE_PER_DEX, POISON_MAX_CHANCE,
                   POISON_MAX_ROUNDS,
                   LIGHTNING_ROUNDS, LIGHTNING_DIE,
                   LIGHTNING_BASE_CHANCE, LIGHTNING_WIS_PER_POINT,
                   LIGHTNING_CHANCE_PER_WIS_BLOCK, LIGHTNING_MAX_CHANCE,
                   DARK_ROUNDS, DARK_DIE, DARK_STR_PER_POINT,
                   DARK_DAMAGE_PER_STR_BLOCK,
                   DROP_CHANCE, DROP_MIN, DROP_MAX)
from player import RACES, CLASSES, STAT_ORDER
import player as player_mod
from world_map import LOCATIONS

OUT = os.path.join(ROOT, "GAME_GUIDE.md")
L = []

# Where the body starts. Everything written before this index is the preamble,
# and the table of contents is spliced in between - the TOC is derived from the
# headings themselves, so adding a section needs no second edit here.
BODY_START = [0]


def slug(heading):
    """GitHub-flavoured heading anchor.

    GitHub lowercases the heading, turns every space into a dash and drops the
    punctuation, so "Which weapon should I actually buy?" anchors to
    "#which-weapon-should-i-actually-buy". Getting this wrong produces a TOC that
    renders but never scrolls anywhere, which is worse than no TOC.
    """
    out = []
    for ch in heading.lower().strip():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_":
            out.append("-")
    return "".join(out).strip("-")


def build_toc():
    """A linked contents list, generated from the sections themselves.

    Read in the same order the document is emitted, so the numbering always
    matches what the reader actually sees.
    """
    rows = ["| # | Section | What it covers |",
            "|---|---|---|"]
    for n, sec in enumerate(ordered_sections(), 1):
        rows.append("| %d | [%s](#%s) | %s |"
                    % (n, sec["title"], slug(sec["title"]),
                       TOC_BLURBS.get(sec["title"], "")))
    return rows

EM = "\u2014"
MDASH = "\u2014"
DOTS = "\u00b7"

_PROBE = player_mod.Player("probe", "Human", "Fighter", dict.fromkeys(STAT_ORDER, 10))


def hp_per_level(class_name):
    return _PROBE.hp_per_level()


# One line of "what you will find here" per section, used only by the table of
# contents. A heading with no entry still appears in the TOC, just unblurred.
TOC_BLURBS = {
    "Cheat sheet": "the one screen worth printing: counters, elements, value picks, key numbers",
    "Your first five minutes": "the shortest path from New Game to a level-up",
    "Progression to level 200": "the XP curve, the sixteen unlock tiers, and the prices",
    "Races": "bonuses and what each one is actually good for",
    "Classes": "HP curve, primary stat, starting weapon and armour",
    "Stats": "what each of the six does, plus the AC formula per armour type",
    "Two hands": "the slot rules, the half-damage off-hand swing, the two-handed bonus",
    "Healing potions": "all five tiers with unlock levels, healing and prices",
    "Weapon armories": "which class can wield what, and how the four weapon NPCs work",
    "Weapons": "all 50 with dice, type, average damage, 2H bonus, element, price and level",
    "Which weapon should I actually buy?": "gold-per-point-of-damage ranking by price band",
    "Armour": "all pieces with AC, type, DEX cap, stat bonus, price and level",
    "Armour analysis": "effective AC at DEX 18, and why heavy armour is a trap early",
    "Shields": "every shield, its sell value, and where to buy one",
    "Other items": "scrolls and the Arcane Ring",
    "Quest materials": "the seven drops and which monster gives each one",
    "Damage types": "all nine, with what each does and which monsters resist it",
    "Elements": "all five riders: their chance, their scaling stat and their duration",
    "Enemies": "all nine with HP, AC, damage, weaknesses, resistances and drops",
    "The counter chart": "what to bring and what to avoid, per monster",
    "Bosses": "floor-10 only, with their weaknesses and resistances",
    "Combat": "the dice tray, damage numbers, and what costs a turn",
    "Shops": "which NPCs are in which location, and the level gate",
    "Quests": "repeatable jobs and the drop-to-giver mapping",
    "Quick reference": "a question/answer table for the most common confusions",
}


def em(template, *args):
    """Format a template that may contain {EM}.

    Written because "..." + EM + " %d" % (x,) silently does the wrong thing:
    % binds tighter than +, so only the last literal gets formatted. Replacing the
    marker first and using str.format for everything else removes that whole trap.
    """
    return template.replace("{EM}", EM).format(*args)


# Sections are buffered separately and emitted in `order`, not in the order they
# are written. That keeps this file readable top to bottom - it still builds each
# table where it logically belongs - while letting the finished guide be ordered
# for someone reading it from the start.
SECTIONS = []
_current = {"title": None, "order": 0, "lines": []}


def begin(title, order):
    """Start a new top-level section."""
    global _current
    _current = {"title": title, "order": order, "lines": []}
    SECTIONS.append(_current)


def w(line=""):
    _current["lines"].append(line)


def ordered_sections():
    """Sections in reading order.

    Ties keep the order they were written in, so two sections sharing an order
    come out the way the file reads rather than alphabetically.
    """
    return sorted(SECTIONS, key=lambda s: (s["order"], SECTIONS.index(s)))



def avg(dice):
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


SELL = {}
for _npc, _data in SHOP_NPCS.items():
    for _item, _d in _data["items"].items():
        SELL[_item] = (_npc, _d["price"], _d["min_level"])


def price_cell(n):
    return "%dg" % SELL[n][1] if n in SELL else MDASH


def level_cell(n):
    return "L%d" % SELL[n][2] if n in SELL else MDASH


def npc_cell(n):
    return SELL[n][0] if n in SELL else MDASH


def bonus_text(item):
    if not item.stats_bonus:
        return ""
    return ", ".join("%s+%d" % (k, v) for k, v in sorted(item.stats_bonus.items()))


def stats_at(tpl, level):
    return (tpl["hp"] + (level - 1) * 6,
            tpl["ac"] + (level - 1) // 3,
            "%d%s" % ((level - 1) // 4 + 1, tpl["dice"]),
            tpl["bonus"] + (level - 1) // 2,
            int(tpl["xp"] * (level / 2) * XP_REWARD_MULTIPLIER),
            int(tpl["gold"] * level * GOLD_REWARD_MULTIPLIER))


# ==================================================================== preamble
# Everything above the first section. Collected into PREAMBLE rather than written
# through w(), because w() now routes into the current section's buffer.
PREAMBLE = [
    "# Player Guide",
    "",
    "Everything a new player needs: how a character works, what every stat does, every",
    "weapon and armour with the level it unlocks at, and every monster with its",
    "weaknesses and resistances.",
    "",
    "> **Generated from the game itself.** Every table below is read out of the",
    "> catalogue, so it always matches what you can actually buy and fight. If a number",
    "> here looks wrong, it is wrong in the game too.",
    "",
    "---",
    "",
    "<<CHEATSHEET>>",
    "",
    "---",
    "",
]

# ==================================================================== cheat sheet
begin("Cheat sheet", 10)
w()
w("The one screen worth printing. Everything here is generated, so it cannot be stale.")
w()
w("**Damage types beat bigger numbers.** A hit against a weakness does **x%.1f**; against a"
  % WEAK_MULTIPLIER)
w("resistance **x%.1f**. A weapon you already own can be right against one monster and"
  % RESIST_MULTIPLIER)
w("useless against the next, so check the [counter chart](#the-counter-chart) before you")
w("shop rather than after.")
w()
w("### Full weakness and resistance chart")
w()
w("| Monster | Weak to (x%.1f) | Resists (x%.1f) | HP | AC |"
  % (WEAK_MULTIPLIER, RESIST_MULTIPLIER))
w("|---|---|---|---|---|")
for _name in TEMPLATES:
    _hp, _ac, _dice, _bonus, _xp, _gold = stats_at(TEMPLATES[_name], 1)
    _v = VULNERABILITIES.get(_name, {"weak": [], "resist": []})
    w("| **%s**%s | %s | %s | %d | %d |"
      % (_name, " **(boss)**" if _name in BOSS_NAMES else "",
         ", ".join(_v["weak"]) or MDASH, ", ".join(_v["resist"]) or MDASH, _hp, _ac))
w()
w("### The five element riders")
w()
w("| Element | Chance | Scales on | Duration | Damage per round |")
w("|---|---|---|---|---|")
w("| **Fire** | %d%% + %d%% per INT, cap %d%% | INT | %d rounds | `%s` + INT mod |"
  % (int(BURN_BASE_CHANCE * 100), int(BURN_CHANCE_PER_INT * 100),
     int(BURN_MAX_CHANCE * 100), BURN_ROUNDS, BURN_DIE))
w("| **Ice** | %d%% + %d%% per %d INT, cap %d%% | INT | %d round | none |"
  % (int(FREEZE_BASE_CHANCE * 100), int(FREEZE_CHANCE_PER_INT_BLOCK * 100),
     FREEZE_INT_PER_POINT, int(FREEZE_MAX_CHANCE * 100), FREEZE_MIN_ROUNDS))
w("| **Poison** | %d%% + %d%% per DEX, cap %d%% | DEX | **until it dies** | DEX mod |"
  % (int(POISON_BASE_CHANCE * 100), int(POISON_CHANCE_PER_DEX * 100),
     int(POISON_MAX_CHANCE * 100)))
w("| **Lightning** | %d%% + %d%% per %d WIS, cap %d%% | WIS | %d rounds | `%s` + WIS mod |"
  % (int(LIGHTNING_BASE_CHANCE * 100), int(LIGHTNING_CHANCE_PER_WIS_BLOCK * 100),
     LIGHTNING_WIS_PER_POINT, int(LIGHTNING_MAX_CHANCE * 100),
     LIGHTNING_ROUNDS, LIGHTNING_DIE))
w("| **Dark** | **always** | STR | %d rounds | `%s` + 1 per %d STR |"
  % (DARK_ROUNDS, DARK_DIE, DARK_STR_PER_POINT))
w()
w("Four of the five have to **roll** to land, so the stat you have decides how often.")
w("No two share a scaling stat, which means your build picks the one you can rely on.")
w()
w("### Hardest hitter per gold budget")
w()
w("The question when standing in a shop is *\"I have this much gold, what is the best I")
w("can get?\"* " + EM + " so the bands below are **budgets**, and each row is the weapon with the")
w("highest average damage (plus the two-handed bonus) you can buy for no more than that.")
w()
w("Ranking by gold-per-point-of-damage instead sounds clever and is not: because prices")
w("rise steeply with level, that ratio always nominates the cheapest tier in the band,")
w("so a 3.5-average Bone Club beat a 6.5-average Executioner's Axe for \"best value\".")
w()
w("| Budget | Hardest hitter | Unlocks | Price | Avg + 2H |")
w("|---|---|---|---|---|")
for _budget, _label in [(60, "up to 60g"), (800, "up to 800g"),
                        (6000, "up to 6,000g"), (10 ** 12, "no limit (late game)")]:
    _rows = []
    for _n, _i in ITEMS.items():
        if _i.category != "weapon" or _n not in SELL:
            continue
        _p = SELL[_n][1]
        if _p > _budget:
            continue
        _eff = avg(_i.damage_dice) + two_handed_bonus(_i)
        _rows.append((-_eff, _p, _n, SELL[_n][2]))
    if not _rows:
        continue
    _rows.sort()
    _neg, _p, _n, _lv = _rows[0]
    w("| **%s** | **%s** | L%d | %s | %g |"
      % (_label, _n, _lv, "{:,}g".format(_p), -_neg))
    if len(_rows) > 1:
        _neg2, _p2, _n2, _lv2 = _rows[1]
        w("| | %s | L%d | %s | %g |" % (_n2, _lv2, "{:,}g".format(_p2), -_neg2))
w()
w("Cheaper options are almost always a better *ratio*, but not more damage " + EM + " and")
w("damage is what ends a fight. Full breakdown in")
w("[Which weapon should I actually buy?](#which-weapon-should-i-actually-buy).")
w()
w("### Numbers worth memorising")
w()
w("| | |")
w("|---|---|")
w("| Stat modifier | `floor((stat - 10) / 2)` " + EM + " so 10-11 is 0, 12-13 is +1, 18-19 is +4 |")
w("| XP to next level | `level x 100` |")
w("| Gold on level up | `new level x 10` |")
w("| Off-hand damage | `floor((main-hand dice + modifier) / 2)` |")
w("| Selling price | %d%% of the buy price |" % int(SELL_RATIO * 100))
w("| Material drop | %d%% per kill, 1-%d pieces |" % (int(DROP_CHANCE * 100), DROP_MAX))
w("| Skill points | +1 per level, +5 more on every 4th level |")
w("| Highest level | **200** " + EM + " the last item in the game unlocks there |")
w()
w("### Three mistakes that cost runs")
w()
w("1. **Buying a bigger weapon instead of a smarter one.** Check the monster's")
w("   resistances first; a resisted hit is halved.")
w("2. **Forgetting that fire and ice have to roll.** You will swing a Frost Staff at a")
w("   Spider and see it do nothing two times out of five. That is the design, not a bug.")
w("3. **Spending CON late.** A CON skill point raises max HP *and* heals you to full, so")
w("   it doubles as a potion. Buy them early.")
w()
w("---")
w()

# ==================================================================== start
begin("Your first five minutes", 20)
w()
w("1. Pick a race and a class. **Every class starts with 15 Healing Potions** " + EM + " use them, they are your safety net.")
w("2. In Town you can **Fight**, **Visit Shop**, **Inventory**, **Save Game**, **Quests**.")
w("3. Combat opens the **dice tray**: press **Roll** to attack. It shows the exact roll")
w("   before you commit, and the dice land on the real result.")
w("4. Kills level you up. Every level gives a **skill point** " + EM + " spend it in **Allocate Skill")
w("   Points**, which appears by itself after a kill.")
w("5. **CON** skill points heal you to full. They are the best early purchase.")
w("6. Save often " + EM + " saves are per-browser and vanish if you clear site data.")
w()
w("**The single most useful thing to learn:** weapon damage types matter. A Skeleton")
w("takes 50% extra from a bludgeoning weapon and half damage from a slashing one. The")
w("same weapon is a great buy against one monster and a waste against another.")
w()
w("---")
w()

# ==================================================================== races
begin("Races", 30)
w()
w("| Race | Bonuses | Notes |")
w("|---|---|---|")
# The bonuses are read straight out of RACES, never formatted from a template.
# An earlier version rendered every stat as "+1", which quietly reported the
# Dwarf's CON+3 and the Elf's DEX+2 as +1 and made the whole table a lie.
RACE_NOTES = {
    "Human": "**+1 to all six**, so there is no bias at all.",
    "Elf": "**DEX+2 and INT+2** " + EM + " the best DEX and INT in the game.",
    "Dwarf": "**CON+3** " + EM + " by far the most HP " + EM + " plus STR+2.",
    "Halfling": "**DEX+2**, matching the Elf, plus CHA+1.",
}
for r in RACES:
    bonuses = ", ".join("%s+%d" % (k, v) for k, v in sorted(RACES[r]["bonuses"].items()))
    w("| **%s** | %s | %s |" % (r, bonuses, RACE_NOTES.get(r, RACES[r]["desc"])))
w()
w("Every race rolls 4d6-drop-lowest for its six stats and then adds these on top, so")
w("how good a race feels depends on your rolls as well as your choice. What the")
w("choice really decides is **which stat gets pushed** " + EM + " and that matters more now")
w("that each element scales off a different one:")
w()
w("| Race | Best for | Because |")
w("|---|---|---|")
RACE_ROLE = [
    ("Dwarf", "Fighter or Cleric",
     "CON+3 is the most HP in the game, and heavy armour throws DEX away anyway"),
    ("Elf", "Rogue or Wizard",
     "DEX+2 for armour class and finesse damage, INT+2 for fire and ice chance"),
    ("Halfling", "Rogue",
     "DEX+2 on a small base is the cheapest way to hold AC up through the early game"),
    ("Human", "Anything",
     "no bias, so take whichever class you actually want to play"),
]
for _race, _role, _why in RACE_ROLE:
    w("| **%s** | %s | %s |" % (_race, _role, _why))
w("---")
w()

# ==================================================================== classes
begin("Classes", 40)
w()
w("| Class | HP at level 1 | HP per level | Primary | Starting weapon | Starting armour |")
w("|---|---|---|---|---|---|")
GEAR = player_mod.STARTING_GEAR
GEAR_NOTE = {
    "Fighter": "Strongest HP, but starts **two-handed** " + EM + " see [Two hands](#two-hands).",
    "Rogue": "Starts with a one-handed Dagger, so a shield is available immediately.",
    "Wizard": "Lowest HP. Magic weapons scale off INT.",
    "Cleric": "Starts in Plate " + EM + " a flat 17 AC, but DEX is ignored.",
}
for c in CLASSES:
    gear = GEAR[c]
    w("| **%s** | %d + CON mod | %d | %s | %s | %s |"
      % (c, CLASSES[c]["hp"], hp_per_level(c), CLASSES[c]["primary"],
         gear["weapon"], gear["armor"] or "none"))
w()
for c in CLASSES:
    w("- **%s** %s %s" % (c, EM, GEAR_NOTE[c]))
w()
w("---")
w()

# ==================================================================== stats
begin("Stats", 50)
w()
w("| Stat | What it does |")
w("|---|---|")
w("| **STR** | Melee damage and attack rolls, unless the weapon is finesse or ranged. Also scales **dark** damage |")
w("| **DEX** | Ranged and finesse damage, **Armour Class**, and the **poison** chance |")
w("| **CON** | **Max HP** " + EM + " `+1 HP per level` per modifier point. Buying a point also heals you to full |")
w("| **INT** | The **fire** and **ice** application chance, and the fire damage per round |")
w("| **WIS** | The **lightning** application chance and damage. Cleric spells are still to come, but WIS already pays |")
w("| **CHA** | Nothing yet " + EM + " the only stat with no mechanical use at all |")
w()
w("**All five element riders scale off a different stat**, and that is the main")
w("reason to care which ones you raise: INT drives fire and ice, DEX drives poison,")
w("WIS drives lightning and STR drives dark. See [Elements](#elements).")
w("`modifier = floor((stat - 10) / 2)` " + "—" + " 10 and 11 are 0, 12-13 are +1, 18-19 are +4.")
w()
w("### Armour Class")
w()
w("| Armour type | DEX contribution |")
w("|---|---|")
w("| Light | Full DEX modifier |")
w("| Medium | DEX modifier, **capped at +2** |")
w("| Heavy | **Ignored** " + EM + " the armour's own AC is all you get |")
w("| Shield (off-hand) | Adds its AC on top of everything above |")
w()
w("A Cleric in Plate sits at a **flat 17** with no input from stats. Everyone else has to")
w("reach 17 using armour, DEX and a shield.")
w()
w("### Levelling")
w()
w("| Event | Effect |")
w("|---|---|")
w("| XP to next level | `level x 100` |")
w("| Highest level in the game | **200** " + EM + " the last weapon, armour, shield and potion all unlock there |")
w("| HP on level up | class HP per level **plus** `+1 per CON modifier point`, then healed to full |")
w("| Gold on level up | `new level x 10` |")
w("| Skill points | **+1** every level, **+5 extra** on levels 4, 8, 12, 16, ... |")
w("| Spending a CON point | raises max HP **and heals you to full** |")
w("| Kill reward | XP `base x (level/2) x %.1f`, gold `base x level x %.1f` |"
  % (XP_REWARD_MULTIPLIER, GOLD_REWARD_MULTIPLIER))
w()
w("The XP requirement is `level x 100` but rewards grow with level, so each level takes")
w("*less* fighting than the last.")
w()
w("---")
w()

# ==================================================================== ladder
begin("Progression to level 200", 110)
w()
w("The game runs to **level 200**. Every weapon, armour, shield and potion sits on one")
w("of sixteen unlock tiers, and the gaps between tiers *grow* as you climb " + EM + " early you")
w("get something new every few levels, later each rung has to be earned.")
w()
w("| Tier | Level | Tier | Level | Tier | Level | Tier | Level |")
w("|---|---|---|---|---|---|---|---|")
for _r in range(4):
    _cells = []
    for _c in range(4):
        _i = _r * 4 + _c
        _cells.append("%d | **%d**" % (_i + 1, UNLOCK_TIERS[_i]) if _i < len(UNLOCK_TIERS) else " | ")
    w("| " + " | ".join(_cells) + " |")
w()
w("### How prices follow the ladder")
w()
w("Prices are **derived**, not typed in by hand. An item costs roughly `TIER_MULT`")
w("levels' worth of income at its own tier, and level N pays 10*N gold:")
w()
w("```")
w("price = 10 * tier_level * TIER_MULT * rel")
w("rel   = 1.0x for the cheapest item at that tier")
w("        3.0x for the strongest, so every rung has a budget option and a flagship")
w("```")
w()
w("Real examples from the Armorer, which has the most stock at each tier:")
w()
w("| Tier level | Budget option | Mid | Flagship |")
w("|---|---|---|---|")
for _lv in (1, 15, 52, 100, 200):
    _found = sorted((d["price"], n) for n, d in SHOP_NPCS["Armorer"]["items"].items()
                    if d["min_level"] == _lv)
    if not _found:
        continue

    def _cell(_pair):
        return "%s %s" % ("{:,}".format(_pair[0]), _pair[1])

    if len(_found) == 1:
        # A tier with a single item has no spread to show, and printing the same
        # number three times would read as a bug rather than as the fact.
        w("| **L%d** | %s | _the only item at this tier_ | %s |"
          % (_lv, _cell(_found[0]), _cell(_found[0])))
    else:
        w("| **L%d** | %s | %s | %s |"
          % (_lv, _cell(_found[0]), _cell(_found[len(_found) // 2]), _cell(_found[-1])))
w()
w("What that means in play:")
w()
w("- **Level 1 to 15** you can buy upgrades with a couple of kills' worth of gold.")
w("- **Level 52** a new tier costs about as much as the four levels below it earned.")
w("- **Level 200** the top items cost around 15 levels of income, so they are a")
w("  deliberate purchase rather than an automatic one.")
w()
w("Because the ladder is a formula, moving the whole game is one edit: change")
w("`UNLOCK_TIERS` in `shop.py` (and its mirror in `js/shop.js`) and every item")
w("re-levels and re-prices itself.")
w()
w("---")
w()

# ==================================================================== hands
begin("Two hands", 70)
w()
w("You have **two hands and three slots**: main hand, off-hand, armour.")
w()
w("| In the main hand | What the off-hand accepts |")
w("|---|---|")
w("| Two-handed weapon | **Nothing** " + EM + " the shield goes back in your bag |")
w("| One-handed, off-hand empty | a shield, or a second one-handed weapon |")
w("| One-handed, off-hand full | nothing |")
w()
w("Rules that catch people out:")
w()
w("- **A two-handed weapon sends your shield to storage by itself.** You do not lose it,")
w("  but you are not wearing it either.")
w("- **A shield is not a weapon.** It raises AC and adds its stat bonus, but gives no")
w("  second attack.")
w("- **A weapon in the off-hand attacks for half damage** " + EM + " `floor((dice + modifier) / 2)`.")
w("  It costs a whole turn: you give up the main-hand swing and the monster still")
w("  retaliates. Roughly +50% damage per round if your AC holds up.")
w("- **The Fighter starts with a two-handed Longsword** " + EM + " so a new Fighter cannot equip a")
w("  shield at all until they buy a one-handed weapon from another class's stall. See")
w("  [If you are a Fighter and want a shield](#if-you-are-a-fighter-and-want-a-shield).")
w()
w("### Two-handed damage bonus")
w()
w("A two-handed weapon also hits harder. The bonus is a **rule over the dice**, not a")
w("lookup table, so a rebalanced weapon keeps its bonus instead of silently losing it:")
w()
w("| Dice | Bonus |")
w("|---|---|")


def _dice_sort(d):
    """Sort '1d8' before '2d4', and 1d10 before 1d12.

    Plain string sorting gave 1d10, 1d12, 1d4, 1d6, 1d8..., which reads as noise.
    """
    _n, _s = d.split("d")
    return (int(_n), int(_s))


for dice in sorted(TWO_HANDED_BONUS, key=_dice_sort):
    b = two_handed_bonus_for(dice)
    w("| `%s` | %s |" % (dice, ("**+%d**" % b) if b else "no bonus"))
w()
w("A flat `+N` on the dice does not change the bonus, because it is already part of the")
w("damage: the Maul is `2d6+2`, which reads as two six-sided dice and gets **+1**.")
w()
w("### If you are a Fighter and want a shield")
w()
w("The Fighter's whole armory is heavy blades and polearms " + EM + " there is **no**")
w("one-handed Fighter weapon at any level, and the starting Longsword is two-handed, so a")
w("shield is genuinely out of reach until you do one of these:")
w()
w("- Buy a **Dagger** from the Shadow Fence (the Rogue's stall) " + EM + " anyone may buy from")
w("  any stall, and it fits your free hand. This is the cheapest way out.")
w("- Start a different class. The Rogue begins with a one-handed Dagger and can shield")
w("  from the first fight.")
w()
w("This is a real gap in the class, not a puzzle " + EM + " it is the first thing in")
w("`PROGRESS.md`'s To Do list.")
w()
w("---")
w()

# ==================================================================== potions
begin("Healing potions", 120)
w()
w("| Potion | Restores | Unlocks | Price |")
w("|---|---|---|---|")
for name, amount in sorted(POTION_HEAL.items(), key=lambda kv: kv[1]):
    w("| **%s** | %d HP | level %d | %s |"
      % (name, amount, POTION_MIN_LEVEL.get(name, 1), price_cell(name)))
w()
w("All come from the **Potion Merchant** in Town, Village 1 and Village 2, and from the")
w("dungeon merchant on floors 5 and 10. They stack " + EM + " the shop gives you a quantity")
w("stepper for exactly that reason.")
w()
w("**Every class starts with 15 Healing Potions.** At level 1 your maximum HP is only")
w("11-16, so a Healing Potion (%d HP) is a genuine emergency button rather than a waste."
  % POTION_HEAL["Healing Potion"])
w()
w("### Why the heals scale with the levels")
w()
w("Maximum HP grows linearly " + EM + " roughly 2 per level for a Wizard, 3 for a Rogue or")
w("Cleric, 4 for a Fighter. A flat 20 HP potion that was a third of a level-5 character")
w("is a rounding error at level 60, so each tier is tuned to about **55% of the max HP")
w("of an average class** at the level it unlocks:")
w()
w("| Tier | Level | Heals | Fighter max HP | % of Fighter | Wizard max HP | % of Wizard |")
w("|---|---|---|---|---|---|---|")
for _p, _lv in sorted(POTION_MIN_LEVEL.items(), key=lambda kv: kv[1]):
    _f = 15 + 4 * (_lv - 1)          # Fighter: 15 base, 4 HP per level
    _wiz = 11 + 2 * (_lv - 1)        # Wizard: 11 base, 2 HP per level
    w("| **%s** | %d | %d | %d | %d%% | %d | %d%% |"
      % (_p, _lv, POTION_HEAL[_p], _f, round(100 * POTION_HEAL[_p] / _f),
         _wiz, round(100 * POTION_HEAL[_p] / _wiz)))
w()
w("So a big potion is always worth drinking for a Wizard " + EM + " it overheals, which")
w("is normal and harmless " + EM + " and is still a solid chunk of a Fighter's health bar.")
w("The ladder ends where the character does: the Ultimate Potion unlocks at level 200,")
w("alongside the last weapon and the last plate.")
w()
w("---")
w()

# ==================================================================== armories
begin("Weapon armories", 130)
w()
w("Each class has **its own weapon stall**, plus a copy of the universal kit. You can")
w("walk into any stall in Town " + EM + " the class only decides what is **greyed out**, never")
w("whether the door is open.")
w()
w("| Stall | Class | Sells |")
w("|---|---|---|")
for _npc, _cls, _note in ARMORY_NPCS:
    _own = sorted(n for n in SHOP_NPCS[_npc]["items"]
                  if WEAPON_CLASSES.get(n, ALL_CLASSES) == [_cls])
    w("| **%s** | %s | %s, plus the universal kit |"
      % (_npc, _cls, ", ".join(_own[:4]) + ("..." if len(_own) > 4 else "")))
w()
w("Browsing someone else's stall shows their gear greyed out with a")
w("*\"not your class's weapon\"* note. The item still opens, so you can compare the")
w("stats, but there is no Buy button and the server refuses the purchase if you ask.")
w()
w("### What each class can wield")
w()
w("| Class | Weapons | Notes |")
w("|---|---|---|")
ARM_NOTE = {
    "Fighter": "Heavy blades, axes and polearms. The only class with a two-handed opener.",
    "Rogue": "Finesse blades and thrown daggers. The lightest armour on the ladder.",
    "Wizard": "Staves and elemental wands " + EM + " the whole fire/ice/lightning/poison range.",
    "Cleric": "Maces, flails and the Bone Wand. The smallest armory in the game.",
}
for _cls in ALL_CLASSES:
    _own = sorted(n for n in WEAPON_CLASSES if WEAPON_CLASSES[n] == [_cls])
    w("| **%s** | %d | %s |" % (_cls, len(_own), ARM_NOTE[_cls]))
w("| **any class** | %d | Bows, darts, crossbows and the plain Wand |"
  % len([n for n in WEAPON_CLASSES if WEAPON_CLASSES[n] == ALL_CLASSES]))
w()
w("**The universal kit is why a Fighter can use a wand or a bow.** Bows, darts,")
w("crossbows and the plain Wand are tagged `ALL_CLASSES`, so they are stocked by all")
w("four stalls and never greyed out. Only another class's *signature* weapons are.")
w()
w("`Runed Dagger` is the one weapon two classes share " + EM + " a rogue's blade and a")
w("wizard's focus " + EM + " so it appears in both the Shadow Fence and the Wizard stall.")
w()
w("### Per-class ladder")
w()
for _npc, _cls, _note in ARMORY_NPCS:
    w("**%s** (the %s)" % (_npc, _cls))
    w()
    w("| Level | Weapons | |")
    w("|---|---|---|")
    _rows = []
    for _n, _d in SHOP_NPCS[_npc]["items"].items():
        if _d["min_level"] > 200:
            continue
        _own = WEAPON_CLASSES.get(_n, ALL_CLASSES) != ALL_CLASSES
        if _own:
            _rows.append((_d["min_level"], _n))
    _by_level = {}
    for _lv, _n in _rows:
        _by_level.setdefault(_lv, []).append(_n)
    _levels = sorted(_by_level)
    for _i in range(0, len(_levels), 2):
        _a = _levels[_i]
        _left = "**%d** | %s" % (_a, ", ".join(sorted(_by_level[_a])))
        if _i + 1 < len(_levels):
            _b = _levels[_i + 1]
            _right = "**%d** | %s |" % (_b, ", ".join(sorted(_by_level[_b])))
        else:
            _right = " | |"
        w("| " + _left + " | " + _right)
    w()
w("Every armory has something at level 1 and something at level 200, so no class is")
w("ever stranded without an upgrade " + EM + " although the Cleric's is the thinnest of")
w("the four, which is worth knowing if you are planning a long Cleric run.")
w()
w("---")
w()

# ==================================================================== weapons
weapons = [(n, i) for n, i in ITEMS.items() if i.category == "weapon"]
weapons.sort(key=lambda kv: (SELL.get(kv[0], (None, 10 ** 6, 0))[1], avg(kv[1].damage_dice)))

begin("Weapons", 140)
w()
w("Cheapest first. **Avg** is the average damage roll *before* your modifier and before")
w("the two-handed bonus " + EM + " it is the number to compare when deciding what to buy.")
w()
w("| Weapon | Damage | Type | Avg | 2H | Element | Class | Props | Stat | Shop | Lvl | Price |")
w("|---|---|---|---|---|---|---|---|---|---|---|---|")
for n, i in weapons:
    th = two_handed_bonus(i)
    elem = element_of(i)
    cls = WEAPON_CLASSES.get(n, ALL_CLASSES)
    w("| **%s** | `%s` | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        n, i.damage_dice, damage_type(i.damage_type), ("%g" % avg(i.damage_dice)),
        ("+%d" % th) if th else MDASH,
        elem if elem else MDASH,
        ("any" if cls == ALL_CLASSES else "/".join(c[:3] for c in cls)),
        ", ".join(p for p in i.properties if p != "magic") if i.properties else MDASH,
        bonus_text(i) or MDASH, npc_cell(n), level_cell(n), price_cell(n)))
w()
w("**Reading the table**")
w()
w("- **2H** is the extra damage a two-handed weapon adds to every hit.")
w("- **Element** means it inflicts a lasting effect on hit " + EM + " see [Elements](#elements).")
w("- **finesse** uses DEX instead of STR; **ranged** also uses DEX.")
w("- **light** weapons can go in the off-hand. **heavy** ones cannot.")
w("- A weapon with no shop cannot be bought " + EM + " drops and quest rewards only.")
w()
w("---")
w()

# ==================================================================== analysis
w("### Which weapon should I actually buy?")
w()
w("There is no single right answer, because the shops sell two different things:")
w("**damage** and **stat bonuses**. They are priced differently and they are not")
w("interchangeable, so here are both rather than one misleading ranking.")
w()
w("#### 1. The hardest hitter available at your level")
w()
w("This is the one that ends fights. For each unlock tier, the highest average damage")
w("(the roll plus the two-handed bonus) you can buy when that tier opens:")
w()
w("| Unlocks | Hardest hitter | Price | Avg + 2H | Also good |")
w("|---|---|---|---|---|")
for _tier in range(len(UNLOCK_TIERS)):
    _lv = UNLOCK_TIERS[_tier]
    _rows = []
    for _n, _i in weapons:
        if _n not in SELL or SELL[_n][2] != _lv:
            continue
        _rows.append((-(avg(_i.damage_dice) + two_handed_bonus(_i)), SELL[_n][1], _n))
    if not _rows:
        continue
    _rows.sort()
    _best = _rows[0]
    _also = ", ".join(_r[2] for _r in _rows[1:3])
    w("| **L%d** | **%s** | %s | %g | %s |"
      % (_lv, _best[2], "{:,}g".format(_best[1]), -_best[0], _also or MDASH))
w()
w("Notice how often the answer barely changes between tiers. The catalogue is")
w("deliberately flat in its damage curve " + EM + " **the stat bonus is where the real")
w("progression is**, which is why the second table matters more than the first.")
w()
w("#### 2. The best ratio, per tier")
w()
w("Within a single tier this is meaningful: it finds the cheapest way to reach a given")
w("damage. **Across** tiers it is not, because prices climb steeply with level, so the")
w("ratio always nominates the cheapest thing in the band. Read it per row, never down")
w("the column.")
w()
w("| Unlocks | Best ratio | Price | Avg + 2H | Gold per point |")
w("|---|---|---|---|---|")
for _tier in range(len(UNLOCK_TIERS)):
    _lv = UNLOCK_TIERS[_tier]
    _rows = []
    for _n, _i in weapons:
        if _n not in SELL or SELL[_n][2] != _lv:
            continue
        _eff = avg(_i.damage_dice) + two_handed_bonus(_i)
        _rows.append((SELL[_n][1] / max(_eff, 0.5), _n, SELL[_n][1], _eff))
    if not _rows:
        continue
    _rows.sort()
    _b = _rows[0]
    w("| **L%d** | **%s** | %s | %g | %.1f |"
      % (_lv, _b[1], "{:,}g".format(_b[2]), _b[3], _b[0]))
w()
w("**Stat bonuses are worth more than damage, and that is the real progression here.**")
w("DEX+2 raises your attack roll, your damage *and* your armour class at the same time,")
w("so 2 points of a stat routinely beats 2 points of damage. The buffed dagger line is")
w("the clearest example: the Venom Dagger grants DEX+3, which lifts its own damage, its")
w("hit chance and your AC " + EM + " and it poisons on top.")
w()
w("**And check the resistances before committing to any of this.** The tables above")
w("rank raw damage. Against a monster that resists your damage type you want the")
w("opposite pick, which is what [the counter chart](#the-counter-chart) is for.")
w()
w("---")
w()

# ==================================================================== armour
armours = [(n, i) for n, i in ITEMS.items()
           if i.category == "armor" and i.armor_type != "shield"]
armours.sort(key=lambda kv: (SELL.get(kv[0], (None, 10 ** 6, 0))[1], kv[1].base_ac))

begin("Armour", 150)
w()
w("| Armour | AC | Type | DEX cap | Stat | Shop | Lvl | Price |")
w("|---|---|---|---|---|---|---|---|")
for n, i in armours:
    w("| **%s** | %d | %s | %s | %s | %s | %s | %s |" % (
        n, i.base_ac, i.armor_type,
        ("%d" % i.dex_limit) if i.dex_limit is not None else (MDASH if i.armor_type == "heavy" else "full"),
        bonus_text(i) or MDASH, npc_cell(n), level_cell(n), price_cell(n)))
w()
w("### Armour analysis")
w()
w("Compare **effective AC**, not the printed number. Assuming a +4 DEX modifier (DEX 18)")
w("and no shield:")
w()
w("| Type | Best example | Effective AC with DEX 18 | Rule |")
w("|---|---|---|---|")
for kind, example, rule in (("light", "Mithral Leather", "full DEX"),
                            ("medium", "Half Plate", "DEX capped at +2"),
                            ("heavy", "Barrier Plate", "DEX ignored")):
    it = ITEMS.get(example)
    if not it:
        continue
    eff = {"light": it.base_ac + 4, "medium": it.base_ac + 2, "heavy": it.base_ac}[kind]
    w("| %s | %s (base %d) | **%d** | %s |" % (kind, example, it.base_ac, eff, rule))
w()
w("Two conclusions:")
w()
w("- **Heavy armour is a trap until about level 6-7**, because you are discarding a DEX")
w("  bonus you have not outgrown. Plate at a flat 17 is the level-8 breakpoint.")
w("- **Light armour with a stat bonus can beat medium outright.** Mithral Leather grants")
w("  DEX+1 *and* CON+1 " + EM + " a permanent HP gain as well as AC.")
w()
w("---")
w()

# ==================================================================== shields
shields = [(n, i) for n, i in ITEMS.items()
           if i.category == "armor" and i.armor_type == "shield"]
shields.sort(key=lambda kv: kv[1].base_ac)

begin("Shields", 160)
w()
w("**Every shield is sold by the Shield Smith** in Town and Village 1, and nowhere else.")
w("A shield goes in the **off-hand** " + EM + " you cannot equip one while holding a two-handed weapon.")
w()
w("| Shield | AC | Stat | Props | Lvl | Price | Sells for |")
w("|---|---|---|---|---|---|---|")
for n, i in shields:
    sell = int(SELL[n][1] * SELL_RATIO) if n in SELL else None
    w("| **%s** | +%d | %s | %s | %s | %s | %s |" % (
        n, i.base_ac, bonus_text(i) or MDASH, ", ".join(i.properties) if i.properties else MDASH,
        level_cell(n), price_cell(n), ("%dg" % sell) if sell else MDASH))
w()
w("The **Dragon Shield** and **Aegis Shield** are strongest on paper, but their bonuses")
w("only pay off if you have the stat to spend " + EM + " late-game buys, not early ones.")
w()
w("---")
w()

# ==================================================================== misc items
begin("Other items", 170)
w()
w("| Item | Effect | Notes |")
w("|---|---|---|")
NOTE = {
    "Arcane Ring": "Equippable INT+1. No AC, no damage.",
    "Scroll of Fireball": "**Not usable yet.** Reserved for a future spell.",
    "Scroll of Healing": "**Not usable yet.**",
}
for n, i in sorted((n, i) for n, i in ITEMS.items()
                  if i.category == "item" and not is_potion(n) and n not in MATERIALS):
    w("| **%s** | %s | %s |" % (n, i.description, NOTE.get(n, "")))
w()
w("---")
w()

# ==================================================================== materials
begin("Quest materials", 180)
w()
w("These drop from monsters and are **not sellable** " + EM + " they exist only to hand to a")
w("quest giver. Spawn is **%d%% per kill**, dropping **%d-%d** pieces."
  % (int(DROP_CHANCE * 100), DROP_MIN, DROP_MAX))
w()
w("| Material | Dropped by | Quest giver wants |")
w("|---|---|---|")
for mat, monster in sorted(MATERIALS.items(), key=lambda kv: kv[1]):
    w("| **%s** | %s | Town |" % (mat, monster))
w()
w("Drops are per-monster, so the three quest givers always ask for three different")
w("materials. Fighting variety beats farming one camp.")
w()
w("---")
w()

# ==================================================================== types
begin("Damage types", 80)
w()
w("Every weapon has a damage type and every monster reacts to it. This is the most")
w("important table in the game.")
w()
w("| Damage type | Effect |")
w("|---|---|")
DT_NOTE = {
    "slashing": "Blades. Skeletons and Goblins fold; Zombies and Ghostes shrug.",
    "bludgeoning": "Blunt. The answer to Skeletons; resisted by Slimes and Zombies.",
    "piercing": "Points and bites. The answer to Wolves, Zombies and Skeletons.",
    "fire": "**Rolls to ignite** the target. Weak against Spiders, Slimes and Skeletons.",
    "ice": "**Rolls to freeze** the target solid. Weak against Slimes, Ghosts, Spiders and the Demon Lord.",
    "lightning": "**Rolls to strike** the target. No monster weakness either way.",
    "dark": "**Always drains** the target. Resisted by the Demon Lord.",
    "force": "Arcane. Weak against Ghosts; resisted by Zombies and the Demon Lord.",
    "poison": "**Rolls to poison** the target. Weak against the Elder Dragon.",
}
DT_NOTE["slashing"] = DT_NOTE["slashing"].replace("Ghostes", "Ghosts")
for t in ["slashing", "bludgeoning", "piercing", "fire", "ice", "lightning", "dark", "force", "poison"]:
    w("| `%s` | %s |" % (t, DT_NOTE[t]))
w()
w("A hit against a weakness does **x%.1f** damage, against a resistance **x%.1s**."
  % (WEAK_MULTIPLIER, RESIST_MULTIPLIER))
w()
w("---")
w()

# ==================================================================== elements
begin("Elements", 90)
w()
w("Five damage types inflict a lasting effect, and **four of the five have to roll**")
w("to land. That is the important rule: a rider is a bonus, not a promise, so the stat")
w("you actually have decides how often it happens.")
w()
w("| Element | Applies | Chance | Scales on | Duration | Damage |")
w("|---|---|---|---|---|---|")
w("| **Fire** | rolls to ignite | %d%% + %d%% per INT, **cap %d%%** | INT | %d rounds | `%s` + INT mod |"
  % (int(BURN_BASE_CHANCE * 100), int(BURN_CHANCE_PER_INT * 100),
     int(BURN_MAX_CHANCE * 100), BURN_ROUNDS, BURN_DIE))
w("| **Ice** | rolls to freeze | %d%% + %d%% per %d INT, **cap %d%%** | INT | %d round, %d at INT %d+ | none |"
  % (int(FREEZE_BASE_CHANCE * 100), int(FREEZE_CHANCE_PER_INT_BLOCK * 100),
     FREEZE_INT_PER_POINT, int(FREEZE_MAX_CHANCE * 100),
     FREEZE_MIN_ROUNDS, FREEZE_MAX_ROUNDS, FREEZE_INT_THRESHOLD))
w("| **Poison** | rolls to poison | %d%% + %d%% per DEX, **cap %d%%** | DEX | **until it dies** | DEX mod, min 1 |"
  % (int(POISON_BASE_CHANCE * 100), int(POISON_CHANCE_PER_DEX * 100),
     int(POISON_MAX_CHANCE * 100)))
w("| **Lightning** | rolls to strike | %d%% + %d%% per %d WIS, **cap %d%%** | WIS | %d rounds | `%s` + WIS mod |"
  % (int(LIGHTNING_BASE_CHANCE * 100), int(LIGHTNING_CHANCE_PER_WIS_BLOCK * 100),
     LIGHTNING_WIS_PER_POINT, int(LIGHTNING_MAX_CHANCE * 100),
     LIGHTNING_ROUNDS, LIGHTNING_DIE))
w("| **Dark** | **always** | no roll | STR | %d rounds | `%s` + 1 per %d STR |"
  % (DARK_ROUNDS, DARK_DIE, DARK_STR_PER_POINT))
w()
w("### What each one is worth")
w()
w("- **Ice steals a whole turn** and deals no damage, so it is the stingiest on")
w("  purpose: +1%% per **%d** INT means only a dedicated caster closes the gap, and the"
  % FREEZE_INT_PER_POINT)
w("  %d%% cap keeps it strong rather than oppressive." % int(FREEZE_MAX_CHANCE * 100))
w("- **Poison never expires.** It is the only rider with no duration at all, which is")
w("  why it beats the Elder Dragon alongside piercing despite being a small tick.")
w("- **Lightning is the hardest-hitting of the short riders** (`%s` per round against"
  % LIGHTNING_DIE)
w("  burn's `%s`) and the only one that scales on WIS." % BURN_DIE)
w("- **Dark is the only rider with no roll.** It is guaranteed, and it pays for that by")
w("  being weak: a flat `%s` at 10 STR, and only `%s` at STR 30. It is the one element"
  % (DARK_DIE, DARK_DIE + "+2"))
w("  that rewards STR.")
w()
w("### The stat you need for each")
w()
w("No two elements share a scaling stat, so **your build decides which element you can")
w("rely on**:")
w()
w("| Stat | Drives | Reaches its cap at |")
w("|---|---|---|")
_ice_cap_int = int((FREEZE_MAX_CHANCE - FREEZE_BASE_CHANCE)
                   / FREEZE_CHANCE_PER_INT_BLOCK) * FREEZE_INT_PER_POINT
_bolt_cap_wis = int((LIGHTNING_MAX_CHANCE - LIGHTNING_BASE_CHANCE)
                    / LIGHTNING_CHANCE_PER_WIS_BLOCK) * LIGHTNING_WIS_PER_POINT
w("| **INT** | fire, ice | fire caps at INT %d, ice at INT %d |"
  % (int((BURN_MAX_CHANCE - BURN_BASE_CHANCE) / BURN_CHANCE_PER_INT), _ice_cap_int))
w("| **DEX** | poison | DEX %d |"
  % int((POISON_MAX_CHANCE - POISON_BASE_CHANCE) / POISON_CHANCE_PER_DEX))
w("| **WIS** | lightning | WIS %d |" % _bolt_cap_wis)
w("| **STR** | dark | never caps " + EM + " it just keeps adding +1 per %d |" % DARK_STR_PER_POINT)
w()
w("Fire and ice cap at INT values you will have early. Lightning needs WIS %d and ice"
  % _bolt_cap_wis)
w("needs INT %d " % _ice_cap_int)
w(MDASH + " both are genuinely deep investments by level 200.")
w()
w("### When a roll fails")
w()
w("A miss says so and costs nothing else:")
w()
w("> *The fire did not catch.* / *The ice did not freeze it.* / *The poison did not take.*")
w("> / *The lightning misses.*")
w()
w("Dark has no such branch, because dark always applies.")
w()
w("### Which weapons carry an element")
w()
BY_ELEM = {}
for n, i in ITEMS.items():
    if i.category == "weapon":
        e = element_of(i)
        if e:
            BY_ELEM.setdefault(e, []).append(n)
w("| Element | Weapons |")
w("|---|---|")
for e in ("fire", "ice", "lightning", "dark", "poison"):
    w("| **%s** | %s |" % (e, ", ".join("**%s**" % x for x in sorted(BY_ELEM.get(e, []))) or MDASH))
w()
w("> **Poison scales off DEX, so a poison weapon rewards you for having DEX.** The")
w("> Venom Dagger grants DEX+3, which raises both its hit chance *and* how fast the")
w("> poison ticks. Fire and ice scale off INT, WIS drives lightning, and dark is the")
w("> only element that wants STR.")
w()
w("Damage-over-time resolves at the **top of the monster's turn**, before it can attack,")
w("so a monster can die to its own burning and that still counts as your kill. Freeze")
w("is different: it removes the turn outright, so nothing ticks while it lasts.")
w()
w("---")
w()

# ==================================================================== enemies
begin("Enemies", 100)
w()
w("Seven regular monsters plus two bosses, at **level 1**. HP grows `+6 per level`, AC")
w("every 3 levels, damage gains a die every 4 levels and a flat bonus every 2.")
w()
w("| Monster | HP | AC | Damage | Weak to (x%.1f) | Resists (x%.1s) | Drops |"
  % (WEAK_MULTIPLIER, RESIST_MULTIPLIER))
w("|---|---|---|---|---|---|---|")
for name in TEMPLATES:
    hp, ac, dice, bonus, xp, gold = stats_at(TEMPLATES[name], 1)
    vuln = VULNERABILITIES.get(name, {"weak": [], "resist": []})
    w("| **%s**%s | %d | %d | `%s` + %d | %s | %s | %s |" % (
        name, " **(boss)**" if name in BOSS_NAMES else "", hp, ac, dice, bonus,
        ", ".join(vuln["weak"]) or MDASH, ", ".join(vuln["resist"]) or MDASH,
        DROPS.get(name) or MDASH))
w()
w("### The counter chart")
w()
w("Read this as *what to equip*, not as trivia. Both columns are read straight out of")
w("the vulnerability table, so this cannot disagree with the enemy table above it. The")
w("last column is the **hardest hitter** of that type " + EM + " when you are countering, that is")
w("what you want in your hand, not the cheapest thing that technically qualifies.")
w()
w("| Monster | Bring this (x%.1f) | Avoid (x%.1f) | Best weapon for it |"
  % (WEAK_MULTIPLIER, RESIST_MULTIPLIER))
w("|---|---|---|---|")

# How broadly each damage type works, so the most generally useful answer is
# listed first rather than whatever order the table happens to be in.
_WEAK_COUNT = {}
_RESIST_COUNT = {}
for _m, _v in VULNERABILITIES.items():
    for _d in _v["weak"]:
        _WEAK_COUNT[_d] = _WEAK_COUNT.get(_d, 0) + 1
    for _d in _v["resist"]:
        _RESIST_COUNT[_d] = _RESIST_COUNT.get(_d, 0) + 1

# Which weapon to actually swing at a given damage type.
#
# Three rules were tried and two of them were wrong:
#
#   cheapest        -> answered "bring a 1d4 Dagger" for everything, at every level
#   gold per point  -> same problem, because the ratio always favours the cheapest
#   hardest hitter  -> answered "bring a L166 Lucerne Hammer", also at every level
#
# What a player actually wants is "what can I be holding at the level I am at". So
# the first choice is the strongest weapon of that type available by the early
# game (tier 4, level 15). If a damage type has nothing that early - ice and
# poison both do not - it falls back to the hardest hitter and says so, because
# "there is no cheap Ice weapon" is genuinely useful to know.
_EARLY_TIER = 4
_BY_TYPE = {}
for _n, _i in ITEMS.items():
    if _i.category != "weapon" or _n not in SELL:
        continue
    _t = damage_type(_i.damage_type)
    _price = SELL[_n][1]
    _level = SELL[_n][2]
    _tier = UNLOCK_TIERS.index(_level)
    _eff = avg(_i.damage_dice) + two_handed_bonus(_i)
    _early = _tier <= _EARLY_TIER
    # Ranked by damage within the early band; the hardest hitter overall is kept
    # separately as the fallback.
    _cand = (0 if _early else 1, -_eff, _price, _n, _level)
    if _t not in _BY_TYPE or _cand < _BY_TYPE[_t]:
        _BY_TYPE[_t] = _cand

for _name in TEMPLATES:
    _vuln = VULNERABILITIES.get(_name, {"weak": [], "resist": []})
    _weak = sorted(_vuln["weak"], key=lambda d: (-_WEAK_COUNT.get(d, 0), d))
    _resist = sorted(_vuln["resist"], key=lambda d: (-_RESIST_COUNT.get(d, 0), d))
    _weapon = "_nothing is weak to it_"
    if _weak and _weak[0] in _BY_TYPE:
        _band, _neg, _price, _wname, _wlevel = _BY_TYPE[_weak[0]]
        _weapon = "**%s** %s (L%d)" % (_wname, "{:,}g".format(_price), _wlevel)
        if _band == 1:
            _weapon += " " + EM + " _nothing cheaper exists yet_"
    elif _weak:
        _weapon = "_no buyable weapon does this_"
    else:
        _weapon = "_nothing is weak to it_"
    w("| **%s** | %s | %s | %s |"
      % (_name, ", ".join(_weak) or MDASH, ", ".join(_resist) or MDASH, _weapon))
w()
w("Everything below is computed from that same table rather than written by hand:")
w()
_all_weak = sorted(_WEAK_COUNT.items(), key=lambda kv: (-kv[1], kv[0]))
_all_resist = sorted(_RESIST_COUNT.items(), key=lambda kv: (-kv[1], kv[0]))
w(em("- **{0} is the broadest answer** {EM} a weakness on {1} of the {2} monsters.",
     _all_weak[0][0], _all_weak[0][1], len(VULNERABILITIES)))
w("  **{0}** follows at {1}, then **{2}** at {3}."
  .format(_all_weak[1][0], _all_weak[1][1], _all_weak[2][0], _all_weak[2][1]))
w(em("- **{0} is the most commonly resisted** {EM} {1} monsters shrug off it, so the weapon",
     _all_resist[0][0], _all_resist[0][1]))
w("  you already own may be much worse than useless against a large slice of the")
w("  bestiary.")
_most_resisted = max(VULNERABILITIES.items(), key=lambda kv: len(kv[1]["resist"]))
w(em("- **{0} is resisted by {1} types** ({2}) {EM} the most locked-down monster in the game.",
     _most_resisted[0], len(_most_resisted[1]["resist"]),
     ", ".join(_most_resisted[1]["resist"])))
w("  It still has weaknesses, so the damage type still matters there " + EM + " but there is")
w("  less room to pick.")
_boss_resist = [b for b in BOSS_NAMES
                if b in VULNERABILITIES
                and set(VULNERABILITIES[b]["resist"]) & {"fire", "dark", "force"}]
if _boss_resist:
    w(em("- **{0} {1} fire, dark or force** {EM} the elemental weapons that shine against the",
         ", ".join(_boss_resist), "resist" if len(_boss_resist) > 1 else "resists"))
    w("  overworld are actively bad there. Read the boss row before you reach floor 10.")
w("- A resisted hit still deals **at least 1 damage**, so the wrong weapon is never")
w("  literally nothing " + EM + " it is just a much worse use of your turn.")
w()
w("### Rewards at level 1")
w()
w("| Monster | XP | Gold |")
w("|---|---|---|")
for name in TEMPLATES:
    _, _, _, _, xp, gold = stats_at(TEMPLATES[name], 1)
    w("| **%s** | %d | %d |" % (name, xp, gold))
w()
w("Rewards scale with **level**, not with difficulty: XP is `base x (level/2) x %.1f` and"
  % XP_REWARD_MULTIPLIER)
w("gold is `base x level x %.1f`. A level-20 Wolf pays twenty times the gold of a"
  % GOLD_REWARD_MULTIPLIER)
w("level-1 Wolf, so **fighting slightly above your level is always the right economic")
w("choice** " + EM + " and the overworld enemies are capped at your own level anyway.")
w()
w("### Bosses")
w()
w("Both appear only on **dungeon floor 10**, at `your level + 2`.")
w()
w("| Boss | Weak to | Resists |")
w("|---|---|---|")
for b in BOSS_NAMES:
    vuln = VULNERABILITIES.get(b, {"weak": [], "resist": []})
    w("| **%s** | %s | %s |" % (b, ", ".join(vuln["weak"]), ", ".join(vuln["resist"])))
w()
w("They drop no materials yet. By level 70 you have far more HP than they do, so the")
w("floor-10 boss becomes a damage check rather than a survival check.")
w()
w("---")
w()

# ==================================================================== combat
begin("Combat", 60)
w()
w("### The dice tray")
w()
w("Your turn opens a tray showing the dice for **each** attack you can make, each with")
w("a **Roll** button. Pressing it spins the dice, lands them on the real result, then")
w("resolves the attack. You always know the die, the weapon and the modifier first.")
w()
w("| Dice shown | Means |")
w("|---|---|")
w("| `to hit 1d20 +N` | the attack roll, against the monster's AC |")
w("| `damage NdX +N` | damage on a hit, before weaknesses |")
w("| `half damage NdX +N` | the off-hand row, already halved |")
w()
w("A **miss** lands on `MISS` in grey and shows no damage number.")
w()
w("### Floating damage numbers")
w()
w("Damage rises over the monster's health bar as a number. A hit against a weakness")
w("flashes **gold**. A miss shows **nothing** " + EM + " not a zero.")
w()
w("### Your turn")
w()
w("| Action | Cost |")
w("|---|---|")
w("| Roll (main hand) | the whole turn " + MDASH + " the monster retaliates |")
w("| Roll (off-hand) | the whole turn " + MDASH + " half damage, monster retaliates |")
w("| Use Item | the whole turn; an **unusable** item still costs it |")
w("| Flee | only outside the dungeon |")
w()
w("Because every action is a full turn, **the off-hand is a genuine choice**: about +50%")
w("damage per round if your AC holds, and a much worse round if it does not.")
w()
w("### Using items")
w()
w("The Use Item list shows **everything** you carry, strongest healing potion first,")
w("with quest materials and other unusable items listed but greyed out. Drinking a")
w("potion does **not** return you to the main combat menu " + EM + " you stay on the list until")
w("you press Back.")
w()
w("---")
w()

# ==================================================================== shops
begin("Shops", 190)
w()
w("| Location | NPCs |")
w("|---|---|")
for loc in LOCATIONS.values():
    shops = loc.get("shops", [])
    w("| **%s** | %s |" % (loc["name"],
                           ", ".join(shops) if shops else "_none " + EM + " this is the dungeon_"))
w()
w("| NPC | Class | Stock | Span |")
w("|---|---|---|---|")
for npc, data in SHOP_NPCS.items():
    levels = [d["min_level"] for d in data["items"].values()]
    cls = data["class"] or "_everyone_"
    w("| **%s** | %s | %d items | L%d %s L%d |"
      % (npc, cls, len(data["items"]), min(levels), EM, max(levels)))
w()
w("Stock is **gated by level**: a shop only shows items at or below your level. The")
w("gates are the `Lvl` column in the tables above, and they are what the derived")
w("ladder in [Progression to level 200](#progression-to-level-200) produces.")
w()
w("The four weapon stalls also **grey out another class's stock** " + EM + " see")
w("[Weapon armories](#weapon-armories). The Armorer, Shield Smith and Potion Merchant")
w("serve everyone and never grey anything out.")
w()
w("### Selling")
w()
w("Any NPC buys anything they stock at **%d%% of the buy price**" % int(SELL_RATIO * 100))
w("(the *Sells for* column). You can sell equipped gear, including your weapon or")
w("armour " + EM + " the game warns you first if it would leave that slot empty.")
w()
w("**Quest materials cannot be sold at all.** Turn them in instead.")
w()
w("---")
w()

# ==================================================================== quests
begin("Quests", 200)
w()
w("Three quest givers in **Town**, named randomly each run. Each offers **repeatable**")
w("jobs: bring N of a material, get gold and XP, and the job goes back on the board.")
w()
w("Because each monster drops a different material, the three givers always ask for")
w("three different things " + EM + " fighting variety pays better than farming one camp.")
w()
w("Quests are the most reliable early gold and XP, and the materials come from monsters")
w("you are fighting anyway.")
w()
w("---")
w()

# ==================================================================== quick ref
begin("Quick reference", 210)
w()
w("| Question | Answer |")
w("|---|---|")
w("| How do I attack? | Press **Roll** in the dice tray |")
w("| Why is there no Attack button? | The dice tray replaced it |")
w("| Can I use a shield? | Yes, in the **off-hand**, with a one-handed weapon |")
w("| Why can I not equip that shield? | You are holding a two-handed weapon |")
w("| What does this monster drop? | See the [enemy table](#enemies) |")
w("| What should I fight? | Anything at or slightly above your level |")
w("| Best stat to buy? | **CON** early (heals you to full), then **STR** or **DEX** |")
w("| Where do I sell? | Any NPC, at 20% under |")
w("| Where do I turn in materials? | The quest givers in **Town** |")
w("| How do I get better damage? | Match the monster's **weakness**, not just a bigger number |")
w("| What unlocks at level 15 / 35 / 70? | Superior / Grand / Ultimate Healing Potions |")
w("| Do potions sell? | Yes, at the Potion Merchant in 1/5/10/20 quantities |")
w()
w("---")
w()
w("_Generated from the game catalogue by `py tools/gen_game_guide.py`. Re-run it after")
w("any balance change and commit the result._")

# ==================================================================== write
# Emit the preamble, then the table of contents, then the sections in reading
# order. The TOC is derived from the sections, so it cannot fall out of step with
# them.
_preamble = [ln for ln in PREAMBLE if ln != "<<CHEATSHEET>>"]
_ordered = ordered_sections()
_body = []
for _sec in _ordered:
    _body.append("## " + _sec["title"])
    _body.extend(_sec["lines"])
text = "\n".join(_preamble + build_toc() + ["", "---", ""] + _body) + "\n"
io.open(OUT, "w", encoding="utf-8", newline="\n").write(text)
print("GAME_GUIDE.md written: %d lines, %d sections"
      % (len(text.split("\n")), len(_ordered)))
