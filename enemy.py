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

# Status effects. Burn and freeze are short and driven by INT; poison sticks
# until it kills.
BURN_ROUNDS = 2
BURN_DIE = "1d4"
FREEZE_INT_THRESHOLD = 15    # at or above this INT, a freeze lasts 2 rounds
FREEZE_MIN_ROUNDS = 1
FREEZE_MAX_ROUNDS = 2
POISON_BASE_CHANCE = 0.20    # +3% per point of DEX
POISON_CHANCE_PER_DEX = 0.03
POISON_MAX_CHANCE = 0.60
# Poison is never "wearing off" - it runs until the creature is dead.
POISON_MAX_ROUNDS = 999


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
        }

    def status_text(self):
        """e.g. "Frozen (1), Burning (2), Poisoned" - empty when clean."""
        s = self.status
        parts = []
        if s["freeze_rounds"] > 0:
            parts.append(f"Frozen ({s['freeze_rounds']})")
        if s["burn_rounds"] > 0:
            parts.append(f"Burning ({s['burn_rounds']})")
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

        Fire and ice scale with INT, poison with DEX. Returns a log fragment.
        """
        if not element or player is None:
            return ""
        s = self.status

        if element == "fire":
            s["burn_rounds"] = BURN_ROUNDS
            int_mod = player.modifier("INT")
            s["burn_damage"] = max(1, roll(BURN_DIE) + max(0, int_mod))
            return (f" It catches fire ({s['burn_damage']}/round "
                    f"for {BURN_ROUNDS} rounds)!")

        if element == "ice":
            rounds = (FREEZE_MAX_ROUNDS if player.effective_stats()["INT"] >= FREEZE_INT_THRESHOLD
                      else FREEZE_MIN_ROUNDS)
            s["freeze_rounds"] = max(s["freeze_rounds"], rounds)
            plural = "s" if rounds > 1 else ""
            return f" It is frozen for {rounds} round{plural}!"

        if element == "poison":
            dex = player.effective_stats()["DEX"]
            chance = min(POISON_MAX_CHANCE, POISON_BASE_CHANCE + POISON_CHANCE_PER_DEX * dex)
            if random.random() >= chance:
                return " The poison did not take."
            s["poison_rounds"] = POISON_MAX_ROUNDS
            s["poison_damage"] = max(1, player.modifier("DEX"))
            return f" It is poisoned ({s['poison_damage']}/round until it dies)!"

        return ""

    def tick_status(self):
        """One round of damage-over-time. Returns log lines."""
        s = self.status
        lines = []
        if s["burn_rounds"] > 0:
            self.take_damage(s["burn_damage"])
            s["burn_rounds"] -= 1
            lines.append(f"{self.name} burns for {s['burn_damage']} damage.")
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
