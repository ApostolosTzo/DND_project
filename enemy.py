import random
from dice import roll

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
        self.xp_reward = t["xp"] * (level/2 )

    #===========================
    # Enemy Actions
    #===========================
    def display(self):
        return f"Lv.{self.level} {self.name}  HP: {self.hp}/{self.max_hp}  AC: {self.ac}"

    def gold_drop(self):
        return TEMPLATES[self.name]["gold"] * self.level

    def attack_damage(self):
        return roll(self.damage_dice) + self.damage_bonus

    def is_alive(self):
        return self.hp > 0

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
