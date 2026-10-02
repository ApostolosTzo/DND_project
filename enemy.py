import random
from dice import roll
from items import element_of, damage_type

#===========================
# Enemy Class and Generation
#===========================

TEMPLATES = {
    "Zombie": {"hp": 22, "ac": 8, "dice": "d6", "bonus": 1, "xp": 50, "gold": 5},
    "Skeleton": {"hp": 13, "ac": 13, "dice": "d6", "bonus": 2, "xp": 50, "gold": 6},
    "Spider": {"hp": 16, "ac": 12, "dice": "d4", "bonus": 1, "xp": 50, "gold": 4},
    "Wolf": {"hp": 18, "ac": 13, "dice": "d6", "bonus": 2, "xp": 50, "gold": 6},
    "Goblin": {"hp": 10, "ac": 15, "dice": "d4", "bonus": 1, "xp": 30, "gold": 8},
    "Slime": {"hp": 20, "ac": 7, "dice": "d6", "bonus": 0, "xp": 40, "gold": 3},
    "Ghost": {"hp": 18, "ac": 11, "dice": "d8", "bonus": 2, "xp": 80, "gold": 10},
    "Demon Lord": {"hp": 60, "ac": 15, "dice": "d10", "bonus": 5, "xp": 200, "gold": 50},
    "Elder Dragon": {"hp": 75, "ac": 18, "dice": "d12", "bonus": 6, "xp": 250, "gold": 80},
}

# Rewards are multiplied by these before being rounded to whole numbers.
XP_REWARD_MULTIPLIER = 1.4    # +40% XP
GOLD_REWARD_MULTIPLIER = 1.6  # +60% gold

# Monster -> the quest material it drops.
# Demon Lord and Elder Dragon deliberately drop nothing yet.
DROPS = {
    "Goblin": "Metal Fragments",
    "Spider": "Web String",
    "Slime": "Slime Ball",
    "Zombie": "Rotten Flesh",
    "Skeleton": "Bone",
    "Wolf": "Fur",
    "Ghost": "Plasma",
}

# Chance a kill drops anything, and how many pieces it is worth.
DROP_CHANCE = 0.75
DROP_MIN = 1
DROP_MAX = 3

BOSS_NAMES = ["Demon Lord", "Elder Dragon"]

# Damage types each monster is weak or hard against. This is what makes weapon
# damage types matter: the same longsword that barely scratches a Zombie cuts a
# Skeleton open, because skeletons are all bone.
VULNERABILITIES = {
    "Zombie": {"weak": ["slashing", "piercing"], "resist": ["bludgeoning", "force"]},
    "Skeleton": {"weak": ["bludgeoning", "piercing"], "resist": ["slashing", "fire"]},
    "Spider": {"weak": ["fire", "ice"], "resist": ["piercing"]},
    "Wolf": {"weak": ["piercing"], "resist": ["bludgeoning"]},
    "Goblin": {"weak": ["slashing"], "resist": ["ice"]},
    "Slime": {"weak": ["fire", "ice"], "resist": ["bludgeoning", "piercing", "slashing"]},
    "Ghost": {"weak": ["force", "ice"], "resist": ["piercing", "slashing"]},
    "Demon Lord": {"weak": ["ice", "piercing"], "resist": ["fire", "dark", "force"]},
    "Elder Dragon": {"weak": ["piercing", "poison"], "resist": ["fire", "slashing"]},
}

# How much damage a hit does when the monster is weak / resistant to its type.
WEAK_MULTIPLIER = 1.5
RESIST_MULTIPLIER = 0.5

# ---- Element effects ------------------------------------------------------------
# Five damage types inflict a lasting effect, and every one of them is *rolled
# for* except dark. That is deliberate: a weapon should be a good investment,
# not a guaranteed effect, so the stat that matters to you decides how often the
# rider actually lands.
#
# Each effect names the stat it scales on, and no two of them share a stat - INT
# drives fire and ice, DEX drives poison, WIS drives lightning and STR drives
# dark. That means your build picks which element you can rely on.
#
#   fire      roll to ignite     20% + 3% per INT, capped at 60%
#   ice       roll to freeze     10% + 1% per 5 INT, capped at 43%
#   poison    roll to poison     20% + 3% per DEX, capped at 60%
#   lightning roll to strike     15% + 1% per 2 WIS, capped at 50%
#   dark      always applies     no chance, but scales on STR instead
#
# Ice is the stingiest on purpose: freezing removes the target's entire turn,
# so a 43% cap keeps it strong rather than overpowered, and +1% per *5* INT
# means only a dedicated caster closes the gap.

# --- Fire: catches, then burns for two rounds
BURN_ROUNDS = 2
BURN_DIE = "1d4"
BURN_BASE_CHANCE = 0.20
BURN_CHANCE_PER_INT = 0.03
BURN_MAX_CHANCE = 0.60

# --- Ice: no damage at all, but the target loses its whole turn
FREEZE_BASE_CHANCE = 0.10
FREEZE_INT_PER_POINT = 5      # one extra point of chance per this much INT
FREEZE_CHANCE_PER_INT_BLOCK = 0.01
FREEZE_MAX_CHANCE = 0.43
FREEZE_INT_THRESHOLD = 15     # at or above this INT, a freeze lasts 2 rounds
FREEZE_MIN_ROUNDS = 1
FREEZE_MAX_ROUNDS = 2

# --- Poison: the mirror of fire, but on DEX, and it never wears off
POISON_BASE_CHANCE = 0.20
POISON_CHANCE_PER_DEX = 0.03
POISON_MAX_CHANCE = 0.60
# Poison is never "wearing off" - it runs until the creature is dead.
POISON_MAX_ROUNDS = 999

# --- Lightning: the WIS effect, and the hardest-hitting of the short riders
LIGHTNING_ROUNDS = 2
LIGHTNING_DIE = "1d8"
LIGHTNING_BASE_CHANCE = 0.15
LIGHTNING_WIS_PER_POINT = 2    # one extra point of chance per this much WIS
LIGHTNING_CHANCE_PER_WIS_BLOCK = 0.01
LIGHTNING_MAX_CHANCE = 0.50

# --- Dark: the odd one out. No roll at all, and it scales on STR.
# 1d4 + 1 for every 15 points of STR, so it starts at a flat 1d4 on a 10 STR
# character and only reaches 1d4+2 at STR 30.
DARK_ROUNDS = 3
DARK_DIE = "1d4"
DARK_STR_PER_POINT = 15       # one extra point of damage per this much STR
DARK_DAMAGE_PER_STR_BLOCK = 1


class Enemy:
    def __init__(self, name, level):
        self.name = name
        self.level = level
        t = TEMPLATES[name]

        self.max_hp = t["hp"] + (level - 1) * 6
        self.hp = self.max_hp
        self.ac = t["ac"] + (level - 1) // 3
        num_dice = (level - 1) // 4 + 1
        self.damage_dice = f"{num_dice}{t['dice']}"
        self.damage_bonus = t["bonus"] + (level - 1) // 2
        # int() keeps the reward a whole number - without it floating point
        # would show things like "35.000000000000004 XP" in the log.
        self.xp_reward = int(t["xp"] * (level / 2) * XP_REWARD_MULTIPLIER)

        vuln = VULNERABILITIES.get(name, {"weak": [], "resist": []})
        self.weak_to = list(vuln["weak"])
        self.resists = list(vuln["resist"])
        self.clear_status()

    #===========================
    # Status effects
    #===========================
    def clear_status(self):
        """Resets the status track.

        Called on spawn and before each new fight so a poisoned corpse can never
        bleed its condition into the next monster.
        """
        self.status = {
            "burn_rounds": 0,
            "burn_damage": 0,
            "freeze_rounds": 0,
            "poison_rounds": 0,
            "poison_damage": 0,
            "strike_rounds": 0,
            "strike_damage": 0,
            "drain_rounds": 0,
            "drain_damage": 0,
        }

    def status_text(self):
        """e.g. "Frozen (1), Burning (2), Poisoned" - empty when clean."""
        s = self.status
        parts = []
        if s["freeze_rounds"] > 0:
            parts.append(f"Frozen ({s['freeze_rounds']})")
        if s["burn_rounds"] > 0:
            parts.append(f"Burning ({s['burn_rounds']})")
        if s["strike_rounds"] > 0:
            parts.append(f"Struck ({s['strike_rounds']})")
        if s["drain_rounds"] > 0:
            parts.append(f"Draining ({s['drain_rounds']})")
        if s["poison_rounds"] > 0:
            parts.append("Poisoned")
        return ", ".join(parts)

    def is_frozen(self):
        return self.status["freeze_rounds"] > 0

    def damage_multiplier(self, type_name):
        """1.5x weak, 0.5x resistant, 1x otherwise."""
        if not type_name:
            return 1
        if type_name in self.weak_to:
            return WEAK_MULTIPLIER
        if type_name in self.resists:
            return RESIST_MULTIPLIER
        return 1

    def apply_damage(self, amount, type_name):
        """Deal damage of a type and return (total_damage, log_note).

        Always at least 1, so a resisted hit still registers as a hit rather
        than silently doing nothing.
        """
        mult = self.damage_multiplier(type_name)
        total = max(1, round(amount * mult))
        self.take_damage(total)
        note = ""
        if mult == WEAK_MULTIPLIER:
            note = f" - WEAK to {type_name} (x1.5)"
        elif mult == RESIST_MULTIPLIER:
            note = f" - resists {type_name} (x0.5)"
        return total, note

    def inflict_element(self, element, player):
        """Apply the element a weapon carries. `player` scales it.

        Each element has its own chance roll and its own stat - see the block of
        constants above. A failed roll says so and costs nothing. Returns a log
        fragment, or "" when the weapon carries no element.
        """
        if not element or player is None:
            return ""
        s = self.status
        stats = player.effective_stats()

        if element == "fire":
            chance = min(BURN_MAX_CHANCE,
                         BURN_BASE_CHANCE + BURN_CHANCE_PER_INT * stats["INT"])
            if random.random() >= chance:
                return " The fire did not catch."
            s["burn_rounds"] = BURN_ROUNDS
            s["burn_damage"] = max(1, roll(BURN_DIE) + max(0, player.modifier("INT")))
            return (f" It catches fire ({s['burn_damage']}/round "
                    f"for {BURN_ROUNDS} rounds)!")

        if element == "ice":
            chance = min(FREEZE_MAX_CHANCE,
                         FREEZE_BASE_CHANCE
                         + FREEZE_CHANCE_PER_INT_BLOCK * (stats["INT"] // FREEZE_INT_PER_POINT))
            if random.random() >= chance:
                return " The ice did not freeze it."
            rounds = (FREEZE_MAX_ROUNDS if stats["INT"] >= FREEZE_INT_THRESHOLD
                      else FREEZE_MIN_ROUNDS)
            s["freeze_rounds"] = max(s["freeze_rounds"], rounds)
            plural = "s" if rounds > 1 else ""
            return f" It is frozen for {rounds} round{plural}!"

        if element == "poison":
            chance = min(POISON_MAX_CHANCE,
                         POISON_BASE_CHANCE + POISON_CHANCE_PER_DEX * stats["DEX"])
            if random.random() >= chance:
                return " The poison did not take."
            s["poison_rounds"] = POISON_MAX_ROUNDS
            s["poison_damage"] = max(1, player.modifier("DEX"))
            return f" It is poisoned ({s['poison_damage']}/round until it dies)!"

        if element == "lightning":
            chance = min(LIGHTNING_MAX_CHANCE,
                         LIGHTNING_BASE_CHANCE
                         + LIGHTNING_CHANCE_PER_WIS_BLOCK
                         * (stats["WIS"] // LIGHTNING_WIS_PER_POINT))
            if random.random() >= chance:
                return " The lightning misses."
            s["strike_rounds"] = LIGHTNING_ROUNDS
            s["strike_damage"] = max(1, roll(LIGHTNING_DIE) + max(0, player.modifier("WIS")))
            return (f" It is struck by lightning ({s['strike_damage']}/round "
                    f"for {LIGHTNING_ROUNDS} rounds)!")

        if element == "dark":
            # Dark has no chance roll on purpose - it is the one rider that is
            # guaranteed, and it pays for that by being weak and STR-scaled.
            s["drain_rounds"] = DARK_ROUNDS
            s["drain_damage"] = max(
                1, roll(DARK_DIE) + DARK_DAMAGE_PER_STR_BLOCK * (stats["STR"] // DARK_STR_PER_POINT))
            return (f" It is drained of life ({s['drain_damage']}/round "
                    f"for {DARK_ROUNDS} rounds)!")

        return ""

    def tick_status(self):
        """One round of damage-over-time. Returns log lines."""
        s = self.status
        lines = []
        if s["burn_rounds"] > 0:
            self.take_damage(s["burn_damage"])
            s["burn_rounds"] -= 1
            lines.append(f"{self.name} burns for {s['burn_damage']} damage.")
        if s["strike_rounds"] > 0:
            self.take_damage(s["strike_damage"])
            s["strike_rounds"] -= 1
            lines.append(f"{self.name} is struck for {s['strike_damage']} damage.")
        if s["drain_rounds"] > 0:
            self.take_damage(s["drain_damage"])
            s["drain_rounds"] -= 1
            lines.append(f"{self.name} is drained for {s['drain_damage']} damage.")
        if s["poison_rounds"] > 0:
            self.take_damage(s["poison_damage"])
            s["poison_rounds"] -= 1
            lines.append(f"{self.name} suffers {s['poison_damage']} poison damage.")
        if s["freeze_rounds"] > 0:
            s["freeze_rounds"] -= 1
        return lines

    #===========================
    # Enemy Actions
    #===========================
    def display(self):
        return f"Lv.{self.level} {self.name}  HP: {self.hp}/{self.max_hp}  AC: {self.ac}"

    def gold_drop(self):
        return int(TEMPLATES[self.name]["gold"] * self.level * GOLD_REWARD_MULTIPLIER)

    def attack_damage(self):
        return roll(self.damage_dice) + self.damage_bonus

    def is_alive(self):
        return self.hp > 0

    def roll_drop(self):
        """Quest material dropped on death, or None.

        Returns the material name and how many pieces dropped, e.g.
        ("Plasma", 2), so the caller can add them to the inventory.
        """
        material = DROPS.get(self.name)
        if not material:
            return None
        if random.random() >= DROP_CHANCE:
            return None
        return material, random.randint(DROP_MIN, DROP_MAX)

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

#===========================
# Enemy Generation
#===========================
def generate_enemy(player_level):
    # Generate an enemy based on the player's level.
    # The enemy's level is randomly chosen to be within 2 levels of the player's level
    if player_level <= 2:
        enemy_level = 1
    else:
        enemy_level = random.randint(player_level - 2, player_level)

    name = random.choice([t for t in TEMPLATES if t not in BOSS_NAMES])
    return Enemy(name, enemy_level)

BOSS_NAMES = ["Demon Lord", "Elder Dragon"]

def generate_dungeon_enemy(floor, player_level):
    if floor == 10:
        name = random.choice(BOSS_NAMES)
        enemy_level = player_level + 2
    else:
        name = random.choice([t for t in TEMPLATES if t not in BOSS_NAMES])
        enemy_level = player_level + floor // 2
    return Enemy(name, enemy_level)
