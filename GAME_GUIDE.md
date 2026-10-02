# Player Guide

Everything a new player needs: how a character works, what every stat does, every
weapon and armour with the level it unlocks at, and every monster with its
weaknesses and resistances.

> **Generated from the game itself.** Every table below is read out of the
> catalogue, so it always matches what you can actually buy and fight. If a number
> here looks wrong, it is wrong in the game too.

---


---

| # | Section | What it covers |
|---|---|---|
| 1 | [Cheat sheet](#cheat-sheet) | the one screen worth printing: counters, elements, value picks, key numbers |
| 2 | [Your first five minutes](#your-first-five-minutes) | the shortest path from New Game to a level-up |
| 3 | [Races](#races) | bonuses and what each one is actually good for |
| 4 | [Classes](#classes) | HP curve, primary stat, starting weapon and armour |
| 5 | [Stats](#stats) | what each of the six does, plus the AC formula per armour type |
| 6 | [Combat](#combat) | the dice tray, damage numbers, and what costs a turn |
| 7 | [Two hands](#two-hands) | the slot rules, the half-damage off-hand swing, the two-handed bonus |
| 8 | [Damage types](#damage-types) | all nine, with what each does and which monsters resist it |
| 9 | [Elements](#elements) | all five riders: their chance, their scaling stat and their duration |
| 10 | [Enemies](#enemies) | all nine with HP, AC, damage, weaknesses, resistances and drops |
| 11 | [Progression to level 200](#progression-to-level-200) | the XP curve, the sixteen unlock tiers, and the prices |
| 12 | [Healing potions](#healing-potions) | all five tiers with unlock levels, healing and prices |
| 13 | [Weapon armories](#weapon-armories) | which class can wield what, and how the four weapon NPCs work |
| 14 | [Weapons](#weapons) | all 50 with dice, type, average damage, 2H bonus, element, price and level |
| 15 | [Armour](#armour) | all pieces with AC, type, DEX cap, stat bonus, price and level |
| 16 | [Shields](#shields) | every shield, its sell value, and where to buy one |
| 17 | [Other items](#other-items) | scrolls and the Arcane Ring |
| 18 | [Quest materials](#quest-materials) | the seven drops and which monster gives each one |
| 19 | [Shops](#shops) | which NPCs are in which location, and the level gate |
| 20 | [Quests](#quests) | repeatable jobs and the drop-to-giver mapping |
| 21 | [Quick reference](#quick-reference) | a question/answer table for the most common confusions |

---

## Cheat sheet

The one screen worth printing. Everything here is generated, so it cannot be stale.

**Damage types beat bigger numbers.** A hit against a weakness does **x1.5**; against a
resistance **x0.5**. A weapon you already own can be right against one monster and
useless against the next, so check the [counter chart](#the-counter-chart) before you
shop rather than after.

### Full weakness and resistance chart

| Monster | Weak to (x1.5) | Resists (x0.5) | HP | AC |
|---|---|---|---|---|
| **Zombie** | slashing, piercing | bludgeoning, force | 22 | 8 |
| **Skeleton** | bludgeoning, piercing | slashing, fire | 13 | 13 |
| **Spider** | fire, ice | piercing | 16 | 12 |
| **Wolf** | piercing | bludgeoning | 18 | 13 |
| **Goblin** | slashing | ice | 10 | 15 |
| **Slime** | fire, ice | bludgeoning, piercing, slashing | 20 | 7 |
| **Ghost** | force, ice | piercing, slashing | 18 | 11 |
| **Demon Lord** **(boss)** | ice, piercing | fire, dark, force | 60 | 15 |
| **Elder Dragon** **(boss)** | piercing, poison | fire, slashing | 75 | 18 |

### The five element riders

| Element | Chance | Scales on | Duration | Damage per round |
|---|---|---|---|---|
| **Fire** | 20% + 3% per INT, cap 60% | INT | 2 rounds | `1d4` + INT mod |
| **Ice** | 10% + 1% per 5 INT, cap 43% | INT | 1 round | none |
| **Poison** | 20% + 3% per DEX, cap 60% | DEX | **until it dies** | DEX mod |
| **Lightning** | 15% + 1% per 2 WIS, cap 50% | WIS | 2 rounds | `1d8` + WIS mod |
| **Dark** | **always** | STR | 3 rounds | `1d4` + 1 per 15 STR |

Four of the five have to **roll** to land, so the stat you have decides how often.
No two share a scaling stat, which means your build picks the one you can rely on.

### Hardest hitter per gold budget

The question when standing in a shop is *"I have this much gold, what is the best I
can get?"* — so the bands below are **budgets**, and each row is the weapon with the
highest average damage (plus the two-handed bonus) you can buy for no more than that.

Ranking by gold-per-point-of-damage instead sounds clever and is not: because prices
rise steeply with level, that ratio always nominates the cheapest tier in the band,
so a 3.5-average Bone Club beat a 6.5-average Executioner's Axe for "best value".

| Budget | Hardest hitter | Unlocks | Price | Avg + 2H |
|---|---|---|---|---|
| **up to 60g** | **Longsword** | L1 | 30g | 5.5 |
| | Mace | L1 | 30g | 3.5 |
| **up to 800g** | **Longsword** | L1 | 30g | 5.5 |
| | Battle Axe | L15 | 680g | 4.5 |
| **up to 6,000g** | **Broadsword** | L40 | 2,500g | 6 |
| | Falchion | L66 | 3,100g | 6 |
| **no limit (late game)** | **Maul** | L200 | 27,000g | 10 |
| | Venom Dagger | L200 | 27,000g | 10 |

Cheaper options are almost always a better *ratio*, but not more damage — and
damage is what ends a fight. Full breakdown in
[Which weapon should I actually buy?](#which-weapon-should-i-actually-buy).

### Numbers worth memorising

| | |
|---|---|
| Stat modifier | `floor((stat - 10) / 2)` — so 10-11 is 0, 12-13 is +1, 18-19 is +4 |
| XP to next level | `level x 100` |
| Gold on level up | `new level x 10` |
| Off-hand damage | `floor((main-hand dice + modifier) / 2)` |
| Selling price | 80% of the buy price |
| Material drop | 75% per kill, 1-3 pieces |
| Skill points | +1 per level, +5 more on every 4th level |
| Highest level | **200** — the last item in the game unlocks there |

### Three mistakes that cost runs

1. **Buying a bigger weapon instead of a smarter one.** Check the monster's
   resistances first; a resisted hit is halved.
2. **Forgetting that fire and ice have to roll.** You will swing a Frost Staff at a
   Spider and see it do nothing two times out of five. That is the design, not a bug.
3. **Spending CON late.** A CON skill point raises max HP *and* heals you to full, so
   it doubles as a potion. Buy them early.

---

## Your first five minutes

1. Pick a race and a class. **Every class starts with 15 Healing Potions** — use them, they are your safety net.
2. In Town you can **Fight**, **Visit Shop**, **Inventory**, **Save Game**, **Quests**.
3. Combat opens the **dice tray**: press **Roll** to attack. It shows the exact roll
   before you commit, and the dice land on the real result.
4. Kills level you up. Every level gives a **skill point** — spend it in **Allocate Skill
   Points**, which appears by itself after a kill.
5. **CON** skill points heal you to full. They are the best early purchase.
6. Save often — saves are per-browser and vanish if you clear site data.

**The single most useful thing to learn:** weapon damage types matter. A Skeleton
takes 50% extra from a bludgeoning weapon and half damage from a slashing one. The
same weapon is a great buy against one monster and a waste against another.

---

## Races

| Race | Bonuses | Notes |
|---|---|---|
| **Human** | CHA+1, CON+1, DEX+1, INT+1, STR+1, WIS+1 | **+1 to all six**, so there is no bias at all. |
| **Elf** | DEX+2, INT+2 | **DEX+2 and INT+2** — the best DEX and INT in the game. |
| **Dwarf** | CON+3, STR+2 | **CON+3** — by far the most HP — plus STR+2. |
| **Halfling** | CHA+1, DEX+2 | **DEX+2**, matching the Elf, plus CHA+1. |

Every race rolls 4d6-drop-lowest for its six stats and then adds these on top, so
how good a race feels depends on your rolls as well as your choice. What the
choice really decides is **which stat gets pushed** — and that matters more now
that each element scales off a different one:

| Race | Best for | Because |
|---|---|---|
| **Dwarf** | Fighter or Cleric | CON+3 is the most HP in the game, and heavy armour throws DEX away anyway |
| **Elf** | Rogue or Wizard | DEX+2 for armour class and finesse damage, INT+2 for fire and ice chance |
| **Halfling** | Rogue | DEX+2 on a small base is the cheapest way to hold AC up through the early game |
| **Human** | Anything | no bias, so take whichever class you actually want to play |
---

## Classes

| Class | HP at level 1 | HP per level | Primary | Starting weapon | Starting armour |
|---|---|---|---|---|---|
| **Fighter** | 15 + CON mod | 4 | STR | Longsword | Chainmail |
| **Rogue** | 13 + CON mod | 4 | DEX | Dagger | Leather |
| **Wizard** | 11 + CON mod | 4 | INT | Magic Staff | none |
| **Cleric** | 13 + CON mod | 4 | WIS | Mace | Plate |

- **Fighter** — Strongest HP, but starts **two-handed** — see [Two hands](#two-hands).
- **Rogue** — Starts with a one-handed Dagger, so a shield is available immediately.
- **Wizard** — Lowest HP. Magic weapons scale off INT.
- **Cleric** — Starts in Plate — a flat 17 AC, but DEX is ignored.

---

## Stats

| Stat | What it does |
|---|---|
| **STR** | Melee damage and attack rolls, unless the weapon is finesse or ranged. Also scales **dark** damage |
| **DEX** | Ranged and finesse damage, **Armour Class**, and the **poison** chance |
| **CON** | **Max HP** — `+1 HP per level` per modifier point. Buying a point also heals you to full |
| **INT** | The **fire** and **ice** application chance, and the fire damage per round |
| **WIS** | The **lightning** application chance and damage. Cleric spells are still to come, but WIS already pays |
| **CHA** | Nothing yet — the only stat with no mechanical use at all |

**All five element riders scale off a different stat**, and that is the main
reason to care which ones you raise: INT drives fire and ice, DEX drives poison,
WIS drives lightning and STR drives dark. See [Elements](#elements).
`modifier = floor((stat - 10) / 2)` — 10 and 11 are 0, 12-13 are +1, 18-19 are +4.

### Armour Class

| Armour type | DEX contribution |
|---|---|
| Light | Full DEX modifier |
| Medium | DEX modifier, **capped at +2** |
| Heavy | **Ignored** — the armour's own AC is all you get |
| Shield (off-hand) | Adds its AC on top of everything above |

A Cleric in Plate sits at a **flat 17** with no input from stats. Everyone else has to
reach 17 using armour, DEX and a shield.

### Levelling

| Event | Effect |
|---|---|
| XP to next level | `level x 100` |
| Highest level in the game | **200** — the last weapon, armour, shield and potion all unlock there |
| HP on level up | class HP per level **plus** `+1 per CON modifier point`, then healed to full |
| Gold on level up | `new level x 10` |
| Skill points | **+1** every level, **+5 extra** on levels 4, 8, 12, 16, ... |
| Spending a CON point | raises max HP **and heals you to full** |
| Kill reward | XP `base x (level/2) x 1.4`, gold `base x level x 1.6` |

The XP requirement is `level x 100` but rewards grow with level, so each level takes
*less* fighting than the last.

---

## Combat

### The dice tray

Your turn opens a tray showing the dice for **each** attack you can make, each with
a **Roll** button. Pressing it spins the dice, lands them on the real result, then
resolves the attack. You always know the die, the weapon and the modifier first.

| Dice shown | Means |
|---|---|
| `to hit 1d20 +N` | the attack roll, against the monster's AC |
| `damage NdX +N` | damage on a hit, before weaknesses |
| `half damage NdX +N` | the off-hand row, already halved |

A **miss** lands on `MISS` in grey and shows no damage number.

### Floating damage numbers

Damage rises over the monster's health bar as a number. A hit against a weakness
flashes **gold**. A miss shows **nothing** — not a zero.

### Your turn

| Action | Cost |
|---|---|
| Roll (main hand) | the whole turn — the monster retaliates |
| Roll (off-hand) | the whole turn — half damage, monster retaliates |
| Use Item | the whole turn; an **unusable** item still costs it |
| Flee | only outside the dungeon |

Because every action is a full turn, **the off-hand is a genuine choice**: about +50%
damage per round if your AC holds, and a much worse round if it does not.

### Using items

The Use Item list shows **everything** you carry, strongest healing potion first,
with quest materials and other unusable items listed but greyed out. Drinking a
potion does **not** return you to the main combat menu — you stay on the list until
you press Back.

---

## Two hands

You have **two hands and three slots**: main hand, off-hand, armour.

| In the main hand | What the off-hand accepts |
|---|---|
| Two-handed weapon | **Nothing** — the shield goes back in your bag |
| One-handed, off-hand empty | a shield, or a second one-handed weapon |
| One-handed, off-hand full | nothing |

Rules that catch people out:

- **A two-handed weapon sends your shield to storage by itself.** You do not lose it,
  but you are not wearing it either.
- **A shield is not a weapon.** It raises AC and adds its stat bonus, but gives no
  second attack.
- **A weapon in the off-hand attacks for half damage** — `floor((dice + modifier) / 2)`.
  It costs a whole turn: you give up the main-hand swing and the monster still
  retaliates. Roughly +50% damage per round if your AC holds up.
- **The Fighter starts with a two-handed Longsword** — so a new Fighter cannot equip a
  shield at all until they buy a one-handed weapon from another class's stall. See
  [If you are a Fighter and want a shield](#if-you-are-a-fighter-and-want-a-shield).

### Two-handed damage bonus

A two-handed weapon also hits harder. The bonus is a **rule over the dice**, not a
lookup table, so a rebalanced weapon keeps its bonus instead of silently losing it:

| Dice | Bonus |
|---|---|
| `1d4` | no bonus |
| `1d6` | no bonus |
| `1d8` | **+1** |
| `1d10` | **+1** |
| `1d12` | **+1** |
| `2d4` | **+1** |
| `2d6` | **+1** |
| `2d10` | **+2** |
| `2d12` | **+2** |

A flat `+N` on the dice does not change the bonus, because it is already part of the
damage: the Maul is `2d6+2`, which reads as two six-sided dice and gets **+1**.

### If you are a Fighter and want a shield

The Fighter's whole armory is heavy blades and polearms — there is **no**
one-handed Fighter weapon at any level, and the starting Longsword is two-handed, so a
shield is genuinely out of reach until you do one of these:

- Buy a **Dagger** from the Shadow Fence (the Rogue's stall) — anyone may buy from
  any stall, and it fits your free hand. This is the cheapest way out.
- Start a different class. The Rogue begins with a one-handed Dagger and can shield
  from the first fight.

This is a real gap in the class, not a puzzle — it is the first thing in
`PROGRESS.md`'s To Do list.

---

## Damage types

Every weapon has a damage type and every monster reacts to it. This is the most
important table in the game.

| Damage type | Effect |
|---|---|
| `slashing` | Blades. Skeletons and Goblins fold; Zombies and Ghosts shrug. |
| `bludgeoning` | Blunt. The answer to Skeletons; resisted by Slimes and Zombies. |
| `piercing` | Points and bites. The answer to Wolves, Zombies and Skeletons. |
| `fire` | **Rolls to ignite** the target. Weak against Spiders, Slimes and Skeletons. |
| `ice` | **Rolls to freeze** the target solid. Weak against Slimes, Ghosts, Spiders and the Demon Lord. |
| `lightning` | **Rolls to strike** the target. No monster weakness either way. |
| `dark` | **Always drains** the target. Resisted by the Demon Lord. |
| `force` | Arcane. Weak against Ghosts; resisted by Zombies and the Demon Lord. |
| `poison` | **Rolls to poison** the target. Weak against the Elder Dragon. |

A hit against a weakness does **x1.5** damage, against a resistance **x0**.

---

## Elements

Five damage types inflict a lasting effect, and **four of the five have to roll**
to land. That is the important rule: a rider is a bonus, not a promise, so the stat
you actually have decides how often it happens.

| Element | Applies | Chance | Scales on | Duration | Damage |
|---|---|---|---|---|---|
| **Fire** | rolls to ignite | 20% + 3% per INT, **cap 60%** | INT | 2 rounds | `1d4` + INT mod |
| **Ice** | rolls to freeze | 10% + 1% per 5 INT, **cap 43%** | INT | 1 round, 2 at INT 15+ | none |
| **Poison** | rolls to poison | 20% + 3% per DEX, **cap 60%** | DEX | **until it dies** | DEX mod, min 1 |
| **Lightning** | rolls to strike | 15% + 1% per 2 WIS, **cap 50%** | WIS | 2 rounds | `1d8` + WIS mod |
| **Dark** | **always** | no roll | STR | 3 rounds | `1d4` + 1 per 15 STR |

### What each one is worth

- **Ice steals a whole turn** and deals no damage, so it is the stingiest on
  purpose: +1% per **5** INT means only a dedicated caster closes the gap, and the
  43% cap keeps it strong rather than oppressive.
- **Poison never expires.** It is the only rider with no duration at all, which is
  why it beats the Elder Dragon alongside piercing despite being a small tick.
- **Lightning is the hardest-hitting of the short riders** (`1d8` per round against
  burn's `1d4`) and the only one that scales on WIS.
- **Dark is the only rider with no roll.** It is guaranteed, and it pays for that by
  being weak: a flat `1d4` at 10 STR, and only `1d4+2` at STR 30. It is the one element
  that rewards STR.

### The stat you need for each

No two elements share a scaling stat, so **your build decides which element you can
rely on**:

| Stat | Drives | Reaches its cap at |
|---|---|---|
| **INT** | fire, ice | fire caps at INT 13, ice at INT 160 |
| **DEX** | poison | DEX 13 |
| **WIS** | lightning | WIS 70 |
| **STR** | dark | never caps — it just keeps adding +1 per 15 |

Fire and ice cap at INT values you will have early. Lightning needs WIS 70 and ice
needs INT 160 
— both are genuinely deep investments by level 200.

### When a roll fails

A miss says so and costs nothing else:

> *The fire did not catch.* / *The ice did not freeze it.* / *The poison did not take.*
> / *The lightning misses.*

Dark has no such branch, because dark always applies.

### Which weapons carry an element

| Element | Weapons |
|---|---|
| **fire** | **Ember Blade**, **Lampada** |
| **ice** | **Frost Staff** |
| **lightning** | **Storm Wand** |
| **dark** | **Bone Wand** |
| **poison** | **Plasma Wand**, **Venom Dagger** |

> **Poison scales off DEX, so a poison weapon rewards you for having DEX.** The
> Venom Dagger grants DEX+3, which raises both its hit chance *and* how fast the
> poison ticks. Fire and ice scale off INT, WIS drives lightning, and dark is the
> only element that wants STR.

Damage-over-time resolves at the **top of the monster's turn**, before it can attack,
so a monster can die to its own burning and that still counts as your kill. Freeze
is different: it removes the turn outright, so nothing ticks while it lasts.

---

## Enemies

Seven regular monsters plus two bosses, at **level 1**. HP grows `+6 per level`, AC
every 3 levels, damage gains a die every 4 levels and a flat bonus every 2.

| Monster | HP | AC | Damage | Weak to (x1.5) | Resists (x0) | Drops |
|---|---|---|---|---|---|---|
| **Zombie** | 22 | 8 | `1d6` + 1 | slashing, piercing | bludgeoning, force | Rotten Flesh |
| **Skeleton** | 13 | 13 | `1d6` + 2 | bludgeoning, piercing | slashing, fire | Bone |
| **Spider** | 16 | 12 | `1d4` + 1 | fire, ice | piercing | Web String |
| **Wolf** | 18 | 13 | `1d6` + 2 | piercing | bludgeoning | Fur |
| **Goblin** | 10 | 15 | `1d4` + 1 | slashing | ice | Metal Fragments |
| **Slime** | 20 | 7 | `1d6` + 0 | fire, ice | bludgeoning, piercing, slashing | Slime Ball |
| **Ghost** | 18 | 11 | `1d8` + 2 | force, ice | piercing, slashing | Plasma |
| **Demon Lord** **(boss)** | 60 | 15 | `1d10` + 5 | ice, piercing | fire, dark, force | — |
| **Elder Dragon** **(boss)** | 75 | 18 | `1d12` + 6 | piercing, poison | fire, slashing | — |

### The counter chart

Read this as *what to equip*, not as trivia. Both columns are read straight out of
the vulnerability table, so this cannot disagree with the enemy table above it. The
last column is the **hardest hitter** of that type — when you are countering, that is
what you want in your hand, not the cheapest thing that technically qualifies.

| Monster | Bring this (x1.5) | Avoid (x0.5) | Best weapon for it |
|---|---|---|---|
| **Zombie** | piercing, slashing | bludgeoning, force | **Spear** 130g (L6) |
| **Skeleton** | piercing, bludgeoning | slashing, fire | **Spear** 130g (L6) |
| **Spider** | ice, fire | piercing | **Frost Staff** 27,000g (L200) — _nothing cheaper exists yet_ |
| **Wolf** | piercing | bludgeoning | **Spear** 130g (L6) |
| **Goblin** | slashing | ice | **Longsword** 30g (L1) |
| **Slime** | ice, fire | slashing, bludgeoning, piercing | **Frost Staff** 27,000g (L200) — _nothing cheaper exists yet_ |
| **Ghost** | ice, force | slashing, piercing | **Frost Staff** 27,000g (L200) — _nothing cheaper exists yet_ |
| **Demon Lord** | piercing, ice | fire, force, dark | **Spear** 130g (L6) |
| **Elder Dragon** | piercing, poison | slashing, fire | **Spear** 130g (L6) |

Everything below is computed from that same table rather than written by hand:

- **piercing is the broadest answer** — a weakness on 5 of the 9 monsters.
  **ice** follows at 4, then **fire** at 2.
- **slashing is the most commonly resisted** — 4 monsters shrug off it, so the weapon
  you already own may be much worse than useless against a large slice of the
  bestiary.
- **Slime is resisted by 3 types** (bludgeoning, piercing, slashing) — the most locked-down monster in the game.
  It still has weaknesses, so the damage type still matters there — but there is
  less room to pick.
- **Demon Lord, Elder Dragon resist fire, dark or force** — the elemental weapons that shine against the
  overworld are actively bad there. Read the boss row before you reach floor 10.
- A resisted hit still deals **at least 1 damage**, so the wrong weapon is never
  literally nothing — it is just a much worse use of your turn.

### Rewards at level 1

| Monster | XP | Gold |
|---|---|---|
| **Zombie** | 35 | 8 |
| **Skeleton** | 35 | 9 |
| **Spider** | 35 | 6 |
| **Wolf** | 35 | 9 |
| **Goblin** | 21 | 12 |
| **Slime** | 28 | 4 |
| **Ghost** | 56 | 16 |
| **Demon Lord** | 140 | 80 |
| **Elder Dragon** | 175 | 128 |

Rewards scale with **level**, not with difficulty: XP is `base x (level/2) x 1.4` and
gold is `base x level x 1.6`. A level-20 Wolf pays twenty times the gold of a
level-1 Wolf, so **fighting slightly above your level is always the right economic
choice** — and the overworld enemies are capped at your own level anyway.

### Bosses

Both appear only on **dungeon floor 10**, at `your level + 2`.

| Boss | Weak to | Resists |
|---|---|---|
| **Demon Lord** | ice, piercing | fire, dark, force |
| **Elder Dragon** | piercing, poison | fire, slashing |

They drop no materials yet. By level 70 you have far more HP than they do, so the
floor-10 boss becomes a damage check rather than a survival check.

---

## Progression to level 200

The game runs to **level 200**. Every weapon, armour, shield and potion sits on one
of sixteen unlock tiers, and the gaps between tiers *grow* as you climb — early you
get something new every few levels, later each rung has to be earned.

| Tier | Level | Tier | Level | Tier | Level | Tier | Level |
|---|---|---|---|---|---|---|---|
| 1 | **1** | 2 | **3** | 3 | **6** | 4 | **10** |
| 5 | **15** | 6 | **22** | 7 | **30** | 8 | **40** |
| 9 | **52** | 10 | **66** | 11 | **82** | 12 | **100** |
| 13 | **120** | 14 | **142** | 15 | **166** | 16 | **200** |

### How prices follow the ladder

Prices are **derived**, not typed in by hand. An item costs roughly `TIER_MULT`
levels' worth of income at its own tier, and level N pays 10*N gold:

```
price = 10 * tier_level * TIER_MULT * rel
rel   = 1.0x for the cheapest item at that tier
        3.0x for the strongest, so every rung has a budget option and a flagship
```

Real examples from the Armorer, which has the most stock at each tier:

| Tier level | Budget option | Mid | Flagship |
|---|---|---|---|
| **L1** | 10 Banded Mail | 22 Leather | 30 Ring Mail |
| **L15** | 230 Half Plate | 450 Plate | 680 Wolf Hide Armor |
| **L52** | 1,200 Enchanted Hide | 2,900 Mithral Leather | 3,700 Titanium |
| **L100** | 3,200 Obsidian Plate | 6,400 Titanforged Plate | 9,600 Warden Plate |
| **L200** | 16,250 Ancient Scale Plate | _the only item at this tier_ | 16,250 Ancient Scale Plate |

What that means in play:

- **Level 1 to 15** you can buy upgrades with a couple of kills' worth of gold.
- **Level 52** a new tier costs about as much as the four levels below it earned.
- **Level 200** the top items cost around 15 levels of income, so they are a
  deliberate purchase rather than an automatic one.

Because the ladder is a formula, moving the whole game is one edit: change
`UNLOCK_TIERS` in `shop.py` (and its mirror in `js/shop.js`) and every item
re-levels and re-prices itself.

---

## Healing potions

| Potion | Restores | Unlocks | Price |
|---|---|---|---|
| **Healing Potion** | 10 HP | level 1 | 15g |
| **Greater Healing Potion** | 55 HP | level 25 | 200g |
| **Superior Healing Potion** | 120 HP | level 60 | 1500g |
| **Grand Healing Potion** | 220 HP | level 120 | 8000g |
| **Ultimate Healing Potion** | 360 HP | level 200 | 30000g |

All come from the **Potion Merchant** in Town, Village 1 and Village 2, and from the
dungeon merchant on floors 5 and 10. They stack — the shop gives you a quantity
stepper for exactly that reason.

**Every class starts with 15 Healing Potions.** At level 1 your maximum HP is only
11-16, so a Healing Potion (10 HP) is a genuine emergency button rather than a waste.

### Why the heals scale with the levels

Maximum HP grows linearly — roughly 2 per level for a Wizard, 3 for a Rogue or
Cleric, 4 for a Fighter. A flat 20 HP potion that was a third of a level-5 character
is a rounding error at level 60, so each tier is tuned to about **55% of the max HP
of an average class** at the level it unlocks:

| Tier | Level | Heals | Fighter max HP | % of Fighter | Wizard max HP | % of Wizard |
|---|---|---|---|---|---|---|
| **Healing Potion** | 1 | 10 | 15 | 67% | 11 | 91% |
| **Greater Healing Potion** | 25 | 55 | 111 | 50% | 59 | 93% |
| **Superior Healing Potion** | 60 | 120 | 251 | 48% | 129 | 93% |
| **Grand Healing Potion** | 120 | 220 | 491 | 45% | 249 | 88% |
| **Ultimate Healing Potion** | 200 | 360 | 811 | 44% | 409 | 88% |

So a big potion is always worth drinking for a Wizard — it overheals, which
is normal and harmless — and is still a solid chunk of a Fighter's health bar.
The ladder ends where the character does: the Ultimate Potion unlocks at level 200,
alongside the last weapon and the last plate.

---

## Weapon armories

Each class has **its own weapon stall**, plus a copy of the universal kit. You can
walk into any stall in Town — the class only decides what is **greyed out**, never
whether the door is open.

| Stall | Class | Sells |
|---|---|---|
| **Weaponsmith** | Fighter | Anchor, Battle Axe, Broadsword, Claymore..., plus the universal kit |
| **Shadow Fence** | Rogue | Bone Club, Dagger, Kris Dagger, Rapier..., plus the universal kit |
| **Wizard** | Wizard | Arcane Staff, Ember Blade, Frost Staff, Lampada..., plus the universal kit |
| **Temple** | Cleric | Bone Wand, Flail, Mace, Quarterstaff..., plus the universal kit |

Browsing someone else's stall shows their gear greyed out with a
*"not your class's weapon"* note. The item still opens, so you can compare the
stats, but there is no Buy button and the server refuses the purchase if you ask.

### What each class can wield

| Class | Weapons | Notes |
|---|---|---|
| **Fighter** | 16 | Heavy blades, axes and polearms. The only class with a two-handed opener. |
| **Rogue** | 9 | Finesse blades and thrown daggers. The lightest armour on the ladder. |
| **Wizard** | 7 | Staves and elemental wands — the whole fire/ice/lightning/poison range. |
| **Cleric** | 5 | Maces, flails and the Bone Wand. The smallest armory in the game. |
| **any class** | 12 | Bows, darts, crossbows and the plain Wand |

**The universal kit is why a Fighter can use a wand or a bow.** Bows, darts,
crossbows and the plain Wand are tagged `ALL_CLASSES`, so they are stocked by all
four stalls and never greyed out. Only another class's *signature* weapons are.

`Runed Dagger` is the one weapon two classes share — a rogue's blade and a
wizard's focus — so it appears in both the Shadow Fence and the Wizard stall.

### Per-class ladder

**Weaponsmith** (the Fighter)

| Level | Weapons | |
|---|---|---|
| **1** | Longsword | **3** | Cudgel |
| **6** | Spear | **10** | Trident |
| **15** | Battle Axe | **22** | War Sickle |
| **30** | Anchor | **40** | Broadsword |
| **66** | Falchion | **82** | Executioner's Axe |
| **100** | Claymore | **120** | Glaive |
| **142** | Greatsword | **166** | Lucerne Hammer |
| **200** | Greataxe, Maul |  | |

**Shadow Fence** (the Rogue)

| Level | Weapons | |
|---|---|---|
| **1** | Dagger | **3** | Bone Club |
| **10** | Shortsword | **22** | Rapier |
| **40** | Sabre | **66** | Scimitar |
| **82** | Kris Dagger | **120** | Viper Fang |
| **166** | Runed Dagger | **200** | Venom Dagger |

**Wizard** (the Wizard)

| Level | Weapons | |
|---|---|---|
| **1** | Magic Staff | **3** | Lampada |
| **15** | Storm Wand | **30** | Ember Blade |
| **66** | Plasma Wand | **100** | Arcane Staff |
| **166** | Runed Dagger | **200** | Frost Staff |

**Temple** (the Cleric)

| Level | Weapons | |
|---|---|---|
| **1** | Mace | **3** | Quarterstaff |
| **30** | Bone Wand | **100** | Flail |
| **200** | War Hammer |  | |

Every armory has something at level 1 and something at level 200, so no class is
ever stranded without an upgrade — although the Cleric's is the thinnest of
the four, which is worth knowing if you are planning a long Cleric run.

---

## Weapons

Cheapest first. **Avg** is the average damage roll *before* your modifier and before
the two-handed bonus — it is the number to compare when deciding what to buy.

| Weapon | Damage | Type | Avg | 2H | Element | Class | Props | Stat | Shop | Lvl | Price |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Wand** | `1d4` | force | 2.5 | — | — | any | ranged | — | Temple | L1 | 10g |
| **Dagger** | `1d4` | piercing | 2.5 | — | — | Rog | finesse, light, thrown | DEX+1 | Shadow Fence | L1 | 30g |
| **Mace** | `1d6` | bludgeoning | 3.5 | — | — | Cle | versatile | STR+1 | Temple | L1 | 30g |
| **Magic Staff** | `1d6` | bludgeoning | 3.5 | — | — | Wiz | versatile | — | Wizard | L1 | 30g |
| **Longsword** | `1d8` | slashing | 4.5 | +1 | — | Fig | two-handed, versatile | STR+1 | Weaponsmith | L1 | 30g |
| **Cudgel** | `1d4` | bludgeoning | 2.5 | — | — | Fig | light | STR+1 | Weaponsmith | L3 | 33g |
| **Dart** | `1d4` | piercing | 2.5 | — | — | any | ranged, light, thrown | DEX+1 | Temple | L3 | 33g |
| **Quarterstaff** | `1d6` | bludgeoning | 3.5 | — | — | Cle | versatile | STR+1 | Temple | L3 | 100g |
| **Lampada** | `1d6` | fire | 3.5 | — | fire | Wiz | versatile | — | Wizard | L3 | 100g |
| **Bone Club** | `1d6` | bludgeoning | 3.5 | — | — | Rog | light | STR+1 | Shadow Fence | L3 | 100g |
| **Spear** | `1d6` | piercing | 3.5 | — | — | Fig | versatile, thrown | STR+1 | Weaponsmith | L6 | 130g |
| **Sling** | `1d4` | bludgeoning | 2.5 | — | — | any | ranged, light | DEX+1 | Temple | L10 | 240g |
| **Hand Crossbow** | `1d6` | piercing | 3.5 | — | — | any | ranged, light | DEX+1 | Temple | L15 | 410g |
| **Shortsword** | `1d6` | slashing | 3.5 | — | — | Rog | versatile | STR+1 | Shadow Fence | L10 | 410g |
| **Trident** | `1d6` | piercing | 3.5 | — | — | Fig | versatile, thrown | STR+1 | Weaponsmith | L10 | 410g |
| **Javelin** | `1d6` | piercing | 3.5 | — | — | any | thrown, versatile | DEX+1 | Temple | L22 | 670g |
| **Storm Wand** | `1d6` | lightning | 3.5 | — | lightning | Wiz | ranged | DEX+1 | Wizard | L15 | 680g |
| **Battle Axe** | `1d8` | slashing | 4.5 | — | — | Fig | versatile | STR+1 | Weaponsmith | L15 | 680g |
| **Bone Wand** | `1d6` | dark | 3.5 | — | dark | Cle | ranged | WIS+1 | Temple | L30 | 1050g |
| **Anchor** | `1d8` | bludgeoning | 4.5 | +1 | — | Fig | two-handed, heavy | STR+1 | Weaponsmith | L30 | 1050g |
| **Ember Blade** | `1d8` | fire | 4.5 | — | fire | Wiz | versatile | INT+1 | Wizard | L30 | 1050g |
| **Rapier** | `1d8` | piercing | 4.5 | — | — | Rog | finesse | DEX+1 | Shadow Fence | L22 | 1100g |
| **War Sickle** | `1d8` | slashing | 4.5 | — | — | Fig | versatile, light | STR+1 | Weaponsmith | L22 | 1100g |
| **Shortbow** | `1d6` | piercing | 3.5 | — | — | any | two-handed, ranged | DEX+1 | Temple | L40 | 1500g |
| **Light Crossbow** | `1d8` | piercing | 4.5 | — | — | any | ranged, light | DEX+1 | Temple | L52 | 2200g |
| **Kris Dagger** | `2d4` | piercing | 5 | — | — | Rog | finesse, light, thrown | DEX+1 | Shadow Fence | L82 | 2400g |
| **Sabre** | `1d8` | slashing | 4.5 | — | — | Rog | finesse | DEX+1 | Shadow Fence | L40 | 2500g |
| **Broadsword** | `2d4` | slashing | 5 | +1 | — | Fig | two-handed, versatile | STR+1 | Weaponsmith | L40 | 2500g |
| **Plasma Wand** | `1d6` | poison | 3.5 | — | poison | Wiz | ranged | INT+1 | Wizard | L66 | 3100g |
| **Scimitar** | `1d8` | slashing | 4.5 | — | — | Rog | finesse, light | DEX+1 | Shadow Fence | L66 | 3100g |
| **Falchion** | `2d4` | slashing | 5 | +1 | — | Fig | two-handed, heavy | STR+2 | Weaponsmith | L66 | 3100g |
| **Flail** | `1d8` | bludgeoning | 4.5 | — | — | Cle | versatile | STR+1 | Temple | L100 | 3200g |
| **Viper Fang** | `1d6` | piercing | 3.5 | — | — | Rog | finesse, light, thrown | DEX+2 | Shadow Fence | L120 | 4200g |
| **Heavy Crossbow** | `1d10` | piercing | 5.5 | — | — | any | ranged, loading, heavy | STR+1 | Temple | L82 | 4300g |
| **Executioner's Axe** | `1d10` | slashing | 5.5 | +1 | — | Fig | two-handed, heavy | STR+2 | Weaponsmith | L82 | 7100g |
| **Longbow** | `1d8` | piercing | 4.5 | +1 | — | any | two-handed, ranged, heavy | DEX+1 | Temple | L120 | 7600g |
| **War Hammer** | `1d10` | bludgeoning | 5.5 | — | — | Cle | versatile | STR+1 | Temple | L200 | 9000g |
| **Arcane Staff** | `1d8` | force | 4.5 | +1 | — | Wiz | two-handed | INT+1 | Wizard | L100 | 9600g |
| **Composite Bow** | `1d8` | piercing | 4.5 | — | — | any | ranged, heavy | DEX+2 | Temple | L100 | 9600g |
| **Claymore** | `2d6` | slashing | 7 | +1 | — | Fig | two-handed, heavy | STR+2 | Weaponsmith | L100 | 9600g |
| **Greatsword** | `2d6` | slashing | 7 | +1 | — | Fig | two-handed, heavy | STR+2 | Weaponsmith | L142 | 9700g |
| **Repeating Crossbow** | `1d10` | piercing | 5.5 | — | — | any | ranged, loading | DEX+2 | Temple | L166 | 12250g |
| **Glaive** | `2d6` | slashing | 7 | +1 | — | Fig | two-handed, heavy | STR+2 | Weaponsmith | L120 | 12500g |
| **Greataxe** | `2d6` | slashing | 7 | +1 | — | Fig | two-handed, heavy | STR+3 | Weaponsmith | L200 | 18000g |
| **Lucerne Hammer** | `2d6` | piercing | 7 | +1 | — | Fig | two-handed, heavy | STR+2 | Weaponsmith | L166 | 20500g |
| **Runed Dagger** | `2d4+2` | force | 7 | — | — | Rog/Wiz | finesse, light | DEX+2, INT+1 | Wizard | L166 | 20500g |
| **Crossbow** | `1d10` | piercing | 5.5 | +1 | — | any | two-handed, ranged, loading | DEX+1 | Temple | L200 | 27000g |
| **Frost Staff** | `2d6` | ice | 7 | +1 | ice | Wiz | two-handed | INT+2 | Wizard | L200 | 27000g |
| **Maul** | `2d6+2` | bludgeoning | 9 | +1 | — | Fig | two-handed, heavy | STR+3 | Weaponsmith | L200 | 27000g |
| **Venom Dagger** | `2d4+5` | poison | 10 | — | poison | Rog | finesse, light, thrown | DEX+3 | Shadow Fence | L200 | 27000g |

**Reading the table**

- **2H** is the extra damage a two-handed weapon adds to every hit.
- **Element** means it inflicts a lasting effect on hit — see [Elements](#elements).
- **finesse** uses DEX instead of STR; **ranged** also uses DEX.
- **light** weapons can go in the off-hand. **heavy** ones cannot.
- A weapon with no shop cannot be bought — drops and quest rewards only.

---

### Which weapon should I actually buy?

There is no single right answer, because the shops sell two different things:
**damage** and **stat bonuses**. They are priced differently and they are not
interchangeable, so here are both rather than one misleading ranking.

#### 1. The hardest hitter available at your level

This is the one that ends fights. For each unlock tier, the highest average damage
(the roll plus the two-handed bonus) you can buy when that tier opens:

| Unlocks | Hardest hitter | Price | Avg + 2H | Also good |
|---|---|---|---|---|
| **L1** | **Longsword** | 30g | 5.5 | Mace, Magic Staff |
| **L3** | **Bone Club** | 100g | 3.5 | Lampada, Quarterstaff |
| **L6** | **Spear** | 130g | 3.5 | — |
| **L10** | **Shortsword** | 410g | 3.5 | Trident, Sling |
| **L15** | **Battle Axe** | 680g | 4.5 | Hand Crossbow, Storm Wand |
| **L22** | **Rapier** | 1,100g | 4.5 | War Sickle, Javelin |
| **L30** | **Anchor** | 1,050g | 5.5 | Ember Blade, Bone Wand |
| **L40** | **Broadsword** | 2,500g | 6 | Sabre, Shortbow |
| **L52** | **Light Crossbow** | 2,200g | 4.5 | — |
| **L66** | **Falchion** | 3,100g | 6 | Scimitar, Plasma Wand |
| **L82** | **Executioner's Axe** | 7,100g | 6.5 | Heavy Crossbow, Kris Dagger |
| **L100** | **Claymore** | 9,600g | 8 | Arcane Staff, Flail |
| **L120** | **Glaive** | 12,500g | 8 | Longbow, Viper Fang |
| **L142** | **Greatsword** | 9,700g | 8 | — |
| **L166** | **Lucerne Hammer** | 20,500g | 8 | Runed Dagger, Repeating Crossbow |
| **L200** | **Maul** | 27,000g | 10 | Venom Dagger, Greataxe |

Notice how often the answer barely changes between tiers. The catalogue is
deliberately flat in its damage curve — **the stat bonus is where the real
progression is**, which is why the second table matters more than the first.

#### 2. The best ratio, per tier

Within a single tier this is meaningful: it finds the cheapest way to reach a given
damage. **Across** tiers it is not, because prices climb steeply with level, so the
ratio always nominates the cheapest thing in the band. Read it per row, never down
the column.

| Unlocks | Best ratio | Price | Avg + 2H | Gold per point |
|---|---|---|---|---|
| **L1** | **Wand** | 10g | 2.5 | 4.0 |
| **L3** | **Cudgel** | 33g | 2.5 | 13.2 |
| **L6** | **Spear** | 130g | 3.5 | 37.1 |
| **L10** | **Sling** | 240g | 2.5 | 96.0 |
| **L15** | **Hand Crossbow** | 410g | 3.5 | 117.1 |
| **L22** | **Javelin** | 670g | 3.5 | 191.4 |
| **L30** | **Anchor** | 1,050g | 5.5 | 190.9 |
| **L40** | **Broadsword** | 2,500g | 6 | 416.7 |
| **L52** | **Light Crossbow** | 2,200g | 4.5 | 488.9 |
| **L66** | **Falchion** | 3,100g | 6 | 516.7 |
| **L82** | **Kris Dagger** | 2,400g | 5 | 480.0 |
| **L100** | **Flail** | 3,200g | 4.5 | 711.1 |
| **L120** | **Viper Fang** | 4,200g | 3.5 | 1200.0 |
| **L142** | **Greatsword** | 9,700g | 8 | 1212.5 |
| **L166** | **Repeating Crossbow** | 12,250g | 5.5 | 2227.3 |
| **L200** | **War Hammer** | 9,000g | 5.5 | 1636.4 |

**Stat bonuses are worth more than damage, and that is the real progression here.**
DEX+2 raises your attack roll, your damage *and* your armour class at the same time,
so 2 points of a stat routinely beats 2 points of damage. The buffed dagger line is
the clearest example: the Venom Dagger grants DEX+3, which lifts its own damage, its
hit chance and your AC — and it poisons on top.

**And check the resistances before committing to any of this.** The tables above
rank raw damage. Against a monster that resists your damage type you want the
opposite pick, which is what [the counter chart](#the-counter-chart) is for.

---

## Armour

| Armour | AC | Type | DEX cap | Stat | Shop | Lvl | Price |
|---|---|---|---|---|---|---|---|
| **Banded Mail** | 15 | heavy | — | — | Armorer | L1 | 10g |
| **Chainmail** | 14 | medium | 2 | — | Armorer | L1 | 14g |
| **Hide** | 13 | medium | 2 | — | Armorer | L1 | 18g |
| **Leather** | 11 | light | full | — | Armorer | L1 | 22g |
| **Padded Armor** | 10 | light | full | CON+1 | Armorer | L1 | 26g |
| **Ring Mail** | 14 | heavy | — | — | Armorer | L1 | 30g |
| **Nomad Leather** | 11 | light | full | DEX+1 | Armorer | L3 | 33g |
| **Padded Mail** | 13 | medium | 2 | DEX+1 | Armorer | L3 | 46g |
| **Riveted Leather** | 13 | medium | 2 | CON+1 | Armorer | L3 | 59g |
| **Scale Mail** | 14 | medium | 2 | — | Armorer | L3 | 75g |
| **Studded Leather** | 12 | light | full | DEX+1 | Armorer | L3 | 85g |
| **Wizard Robe** | 10 | light | full | INT+9 | Armorer | L3 | 100g |
| **Breastplate** | 14 | medium | 2 | — | Armorer | L10 | 135g |
| **Half Plate** | 15 | medium | 2 | — | Armorer | L15 | 230g |
| **Doublet** | 12 | light | full | DEX+1 | Armorer | L10 | 270g |
| **Ironweave Mail** | 14 | medium | 2 | CON+1 | Armorer | L22 | 370g |
| **Robe of Silk** | 10 | light | full | INT+1 | Armorer | L10 | 410g |
| **Plate** | 17 | heavy | — | — | Armorer | L15 | 450g |
| **Wolf Hide Armor** | 12 | light | full | CON+1, DEX+1 | Armorer | L15 | 680g |
| **Elven Cloak Armor** | 12 | light | full | DEX+2 | Armorer | L40 | 850g |
| **Splint** | 17 | heavy | — | — | Armorer | L22 | 1100g |
| **Enchanted Hide** | 14 | medium | 2 | CON+1, WIS+1 | Armorer | L52 | 1200g |
| **Goblinforged Mail** | 14 | medium | 2 | CON+1, STR+1 | Armorer | L40 | 1400g |
| **Shadowcloth** | 12 | light | full | DEX+2 | Armorer | L40 | 1950g |
| **Lamellar Armor** | 15 | medium | 2 | CON+1 | Armorer | L52 | 2050g |
| **Bone Lacquer** | 14 | medium | 2 | CON+2 | Armorer | L82 | 2400g |
| **Ward Mail** | 14 | medium | 2 | DEX+1 | Armorer | L40 | 2500g |
| **Mithral Leather** | 13 | light | full | CON+1, DEX+1 | Armorer | L52 | 2900g |
| **Obsidian Plate** | 17 | heavy | — | CON+2 | Armorer | L100 | 3200g |
| **Titanium** | 18 | heavy | — | — | Armorer | L52 | 3700g |
| **Dragon Scale** | 19 | heavy | — | CON+8 | Armorer | L120 | 4200g |
| **Titanforged Plate** | 18 | heavy | — | CON+1, STR+1 | Armorer | L100 | 6400g |
| **Steel Plate** | 17 | heavy | — | CON+1 | Armorer | L82 | 7100g |
| **Dragonbone Plate** | 18 | heavy | — | CON+2 | Armorer | L120 | 8400g |
| **Warden Plate** | 17 | heavy | — | CON+1, STR+1 | Armorer | L100 | 9600g |
| **Barrier Plate** | 19 | heavy | — | CON+1 | Armorer | L166 | 12250g |
| **Mithral Plate** | 18 | heavy | — | CON+1, DEX+1 | Armorer | L120 | 12500g |
| **Ancient Scale Plate** | 19 | heavy | — | CON+2 | Armorer | L200 | 16250g |

### Armour analysis

Compare **effective AC**, not the printed number. Assuming a +4 DEX modifier (DEX 18)
and no shield:

| Type | Best example | Effective AC with DEX 18 | Rule |
|---|---|---|---|
| light | Mithral Leather (base 13) | **17** | full DEX |
| medium | Half Plate (base 15) | **17** | DEX capped at +2 |
| heavy | Barrier Plate (base 19) | **19** | DEX ignored |

Two conclusions:

- **Heavy armour is a trap until about level 6-7**, because you are discarding a DEX
  bonus you have not outgrown. Plate at a flat 17 is the level-8 breakpoint.
- **Light armour with a stat bonus can beat medium outright.** Mithral Leather grants
  DEX+1 *and* CON+1 — a permanent HP gain as well as AC.

---

## Shields

**Every shield is sold by the Shield Smith** in Town and Village 1, and nowhere else.
A shield goes in the **off-hand** — you cannot equip one while holding a two-handed weapon.

| Shield | AC | Stat | Props | Lvl | Price | Sells for |
|---|---|---|---|---|---|---|
| **Buckler** | +1 | DEX+1 | light | L1 | 10g | 8g |
| **Shield** | +2 | — | — | L1 | 30g | 24g |
| **Bronze Shield** | +2 | CON+1 | — | L3 | 33g | 26g |
| **Iron Shield** | +3 | DEX+3, STR+1 | — | L3 | 100g | 80g |
| **Runed Shield** | +3 | INT+1, WIS+1 | magic | L22 | 670g | 536g |
| **Tower Shield** | +4 | DEX+2, STR+2 | — | L15 | 410g | 328g |
| **Magic Shield** | +5 | INT+2, WIS+2 | — | L30 | 1050g | 840g |
| **Warden's Bulwark** | +5 | CON+2 | two-handed | L66 | 3100g | 2480g |
| **Dragon Shield** | +6 | CON+4, DEX+4, STR+4 | — | L142 | 9700g | 7760g |
| **Bulwark of Dawn** | +6 | CON+2, STR+2 | magic | L100 | 5800g | 4640g |
| **Aegis Shield** | +7 | CON+5, DEX+5, STR+5 | — | L200 | 16250g | 13000g |

The **Dragon Shield** and **Aegis Shield** are strongest on paper, but their bonuses
only pay off if you have the stat to spend — late-game buys, not early ones.

---

## Other items

| Item | Effect | Notes |
|---|---|---|
| **Arcane Ring** | A ring humming with magic | Equippable INT+1. No AC, no damage. |
| **Scroll of Fireball** | Deals fire damage (future use) | **Not usable yet.** Reserved for a future spell. |
| **Scroll of Healing** | Heals ally (future use) | **Not usable yet.** |

---

## Quest materials

These drop from monsters and are **not sellable** — they exist only to hand to a
quest giver. Spawn is **75% per kill**, dropping **1-3** pieces.

| Material | Dropped by | Quest giver wants |
|---|---|---|
| **Plasma** | Ghost | Town |
| **Metal Fragments** | Goblin | Town |
| **Bone** | Skeleton | Town |
| **Slime Ball** | Slime | Town |
| **Web String** | Spider | Town |
| **Fur** | Wolf | Town |
| **Rotten Flesh** | Zombie | Town |

Drops are per-monster, so the three quest givers always ask for three different
materials. Fighting variety beats farming one camp.

---

## Shops

| Location | NPCs |
|---|---|
| **Town** | Potion Merchant, Weaponsmith, Shadow Fence, Temple, Wizard, Armorer, Shield Smith |
| **Village 1** | Potion Merchant, Weaponsmith, Shadow Fence, Armorer, Shield Smith |
| **Village 2** | Potion Merchant |
| **Dungeon** | _none — this is the dungeon_ |

| NPC | Class | Stock | Span |
|---|---|---|---|
| **Potion Merchant** | _everyone_ | 5 items | L1 — L200 |
| **Shield Smith** | _everyone_ | 11 items | L1 — L200 |
| **Weaponsmith** | Fighter | 28 items | L1 — L200 |
| **Shadow Fence** | Rogue | 22 items | L1 — L200 |
| **Wizard** | Wizard | 21 items | L1 — L200 |
| **Temple** | Cleric | 17 items | L1 — L200 |
| **Armorer** | _everyone_ | 38 items | L1 — L200 |

Stock is **gated by level**: a shop only shows items at or below your level. The
gates are the `Lvl` column in the tables above, and they are what the derived
ladder in [Progression to level 200](#progression-to-level-200) produces.

The four weapon stalls also **grey out another class's stock** — see
[Weapon armories](#weapon-armories). The Armorer, Shield Smith and Potion Merchant
serve everyone and never grey anything out.

### Selling

Any NPC buys anything they stock at **80% of the buy price**
(the *Sells for* column). You can sell equipped gear, including your weapon or
armour — the game warns you first if it would leave that slot empty.

**Quest materials cannot be sold at all.** Turn them in instead.

---

## Quests

Three quest givers in **Town**, named randomly each run. Each offers **repeatable**
jobs: bring N of a material, get gold and XP, and the job goes back on the board.

Because each monster drops a different material, the three givers always ask for
three different things — fighting variety pays better than farming one camp.

Quests are the most reliable early gold and XP, and the materials come from monsters
you are fighting anyway.

---

## Quick reference

| Question | Answer |
|---|---|
| How do I attack? | Press **Roll** in the dice tray |
| Why is there no Attack button? | The dice tray replaced it |
| Can I use a shield? | Yes, in the **off-hand**, with a one-handed weapon |
| Why can I not equip that shield? | You are holding a two-handed weapon |
| What does this monster drop? | See the [enemy table](#enemies) |
| What should I fight? | Anything at or slightly above your level |
| Best stat to buy? | **CON** early (heals you to full), then **STR** or **DEX** |
| Where do I sell? | Any NPC, at 20% under |
| Where do I turn in materials? | The quest givers in **Town** |
| How do I get better damage? | Match the monster's **weakness**, not just a bigger number |
| What unlocks at level 15 / 35 / 70? | Superior / Grand / Ultimate Healing Potions |
| Do potions sell? | Yes, at the Potion Merchant in 1/5/10/20 quantities |

---

_Generated from the game catalogue by `py tools/gen_game_guide.py`. Re-run it after
any balance change and commit the result._
