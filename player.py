# player.py - Character creation and management
#
# Contains:
#   RACES        - Race definitions with stat bonuses (Human, Elf, Dwarf, Halfling)
#   CLASSES      - Class definitions with HP and primary stat (Fighter, Rogue, Wizard, Cleric)
#   STAT_ORDER   - List of stat names in display order
#   Player       - Main player class (stats, inventory, equipment, HP, AC, sheet display)
#   create_character() - Full character creation flow: name → race → class → stats → gear


from dice import roll_4d6_drop_lowest
from ui import menu, prompt, clear_screen, show, press_any_key
from items import ITEMS, STARTING_GEAR, get_item, create_item

RACES = {
    "Human": {"desc": "Versatile and ambitious", "bonuses": {"STR": 1, "DEX": 1, "CON": 1, "INT": 1, "WIS": 1, "CHA": 1}},
    "Elf": {"desc": "Graceful and perceptive", "bonuses": {"DEX": 2, "INT": 1}},
    "Dwarf": {"desc": "Tough and resilient", "bonuses": {"CON": 2, "STR": 1}},
    "Halfling": {"desc": "Lucky and nimble", "bonuses": {"DEX": 2, "CHA": 1}},
}

CLASSES = {
    "Fighter": {"desc": "Master of martial combat", "hp": 10, "primary": "STR"},
    "Rogue": {"desc": "Sneaky and dextrous", "hp": 8, "primary": "DEX"},
    "Wizard": {"desc": "Wielder of arcane magic", "hp": 6, "primary": "INT"},
    "Cleric": {"desc": "Servant of the divine", "hp": 8, "primary": "WIS"},
}

STAT_ORDER = ["STR", "DEX", "CON", "INT", "WIS", "CHA"]

#==========================
# Player Class and Character Creation
#==========================


class Player:
    def __init__(self, name, race, class_name, stats):
        self.name = name
        self.race = race
        self.class_name = class_name
        self.level = 1
        self.xp = 0
        self.stats = stats
        self.max_hp = CLASSES[class_name]["hp"] + self.modifier("CON")
        self.hp = self.max_hp
        self.inventory = []
        self.weapon = None
        self.armor = None
        self.shield = None
        self.gold = 0
        self.current_save = None
        self.ac = self.calc_ac()

    def modifier(self, stat: str) -> int:
        return (self.stats[stat] - 10) // 2
    
    #===========================
    # Inventory and Equipment Management
    #==========================
    # AC Calculation
    #===========================

    def calc_ac(self):
        if self.armor:
            ac = self.armor.base_ac
            if self.armor.armor_type == "light":
                ac += self.modifier("DEX")
            elif self.armor.armor_type == "medium":
                ac += min(self.modifier("DEX"), 2)
        else:
            ac = 10 + self.modifier("DEX")
        if self.shield:
            ac += self.shield.base_ac
        return ac
    
    #===========================
    # Inventory Management
    #===========================

    def equip_weapon(self, weapon):
        self.weapon = weapon

    def equip_armor(self, armor):
        self.armor = armor
        self.ac = self.calc_ac()

    def add_item(self, item):
        self.inventory.append(item)

    def is_alive(self):
        return self.hp > 0

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)

    def add_gold(self, amount):
        self.gold += amount

    def spend_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    # ===========================
    # Leveling and Experience
    # ===========================
    
    def hp_per_level(self):
        base = CLASSES[self.class_name]["hp"]
        if base >= 10:
            return 4
        if base >= 8:
            return 3
        return 2

    # experience needed to reach the next level is 100 times the current level.
    def xp_to_next(self):
        return self.level * 100
    
    # Add experience points to the player and handle leveling up if enough XP is gained.
    def add_xp(self, amount):
        self.xp += amount
        while self.xp >= self.xp_to_next():
            self.xp -= self.xp_to_next()
            self.level_up()
            
    # Level up the player, increasing their level, max HP, and allowing for a stat increase every 4 levels.
    def level_up(self):
        old_con_mod = self.modifier("CON")
        self.level += 1
        gain = self.hp_per_level()
        self.max_hp += gain
        self.hp = self.max_hp
        gold_reward = self.level * 10
        self.add_gold(gold_reward)

        clear_screen()
        show(f"LEVEL UP! You are now level {self.level}!")
        show(f"HP increased by {gain}.")
        show(f"You found {gold_reward} gold!")
        show("")

        # Every 4 levels, the player can choose a stat to increase by 1. If the chosen stat is Constitution (CON) and its modifier increases, the player's max HP is also increased by 1.
        if self.level % 4 == 0:
            show("Choose a stat to increase by 1:\n")
            choice = menu("STAT BOOST", STAT_ORDER)
            chosen = STAT_ORDER[choice]
            self.stats[chosen] += 1
            if chosen == "CON" and self.modifier("CON") > old_con_mod:
                self.max_hp += 1
            clear_screen()
            show(f"{chosen} increased to {self.stats[chosen]}!")
            if self.current_save:
                from save_load import save_game
                save_game(self, self.current_save)
                show("Game autosaved!")
            press_any_key()

    #===========================
    # Character Sheet Display
    #===========================

    def sheet(self) -> str:
        lines = []
        lines.append(f"Name:  {self.name}")
        lines.append(f"Race:  {self.race}")
        lines.append(f"Class: {self.class_name} (Lv.{self.level})")
        lines.append(f"HP:    {self.hp}/{self.max_hp}")
        lines.append(f"AC:    {self.ac}")
        lines.append(f"Gold:  {self.gold}")
        weapon_name = self.weapon.name if self.weapon else "None"
        armor_name = self.armor.name if self.armor else "None"
        lines.append(f"Weapon: {weapon_name}")
        lines.append(f"Armor:  {armor_name}")
        lines.append("")
        for s in STAT_ORDER:
            mod = self.modifier(s)
            sign = "+" if mod >= 0 else ""
            lines.append(f"  {s}: {self.stats[s]:>2} ({sign}{mod})")
        return "\n".join(lines)


#===========================
# Character Creation Function
#===========================


def create_character() -> Player:
    clear_screen()
    show("=== CHARACTER CREATION ===\n")
    name = prompt("Enter your name:")
    if not name:
        name = "Adventurer"
    
    
    # Loops through every race in RACES, formatting each option as a display string that includes:
    # the race name,
    # its description,
    # and its stat bonuses.  

    race_options = []
    for r in RACES:
        bonus_str = ", ".join(f"{s}+{v}" for s, v in RACES[r]["bonuses"].items())
        race_options.append(f"{r:<10} {RACES[r]['desc']:<30} [{bonus_str}]")
    race_idx = menu("Choose your race", race_options)
    race = list(RACES.keys())[race_idx]
    
    
    # Loops through every class in CLASSES, formatting each option as a display string that includes:
    # the class name,
    # its description,
    # its hit points (hp),
    # and its primary stat.

    class_options = []
    for c in CLASSES:
        class_options.append(f"{c:<10} {CLASSES[c]['desc']:<30} [HP: {CLASSES[c]['hp']}, Primary: {CLASSES[c]['primary']}]")
    class_idx = menu("Choose your class", class_options)
    class_name = list(CLASSES.keys())[class_idx]
    
    #===========================
    # Stat Rolling and Assignment
    #===========================

    while True:
        raw_stats = [roll_4d6_drop_lowest() for _ in range(6)]
        stats = {}
        if race == "Human":
            for i, s in enumerate(STAT_ORDER):
                stats[s] = raw_stats[i] + 1
        else:
            for i, s in enumerate(STAT_ORDER):
                stats[s] = raw_stats[i]
            bonuses = RACES[race]["bonuses"]
            for s in bonuses:
                stats[s] += bonuses[s]

        player = Player(name, race, class_name, stats)
        
        #===========================
        # Starting Gear Assignment
        #===========================

        gear = STARTING_GEAR[class_name]
        if gear["weapon"]:
            player.equip_weapon(create_item(gear["weapon"]))
        if gear["armor"]:
            player.equip_armor(create_item(gear["armor"]))
        for item_name in gear["items"]:
            player.add_item(create_item(item_name))
            
        #===========================
        # Character Sheet Display and Confirmation
        #===========================

        stats_display = "\n".join(f"  {s}: {stats[s]:>2} ({'+' if player.modifier(s) >= 0 else ''}{player.modifier(s)})" for s in STAT_ORDER)
        choice = menu("Accept this character?", ["Accept", "Reroll stats", "Start over"], body=stats_display)
        if choice == 0:
            return player
        elif choice == 2:
            return create_character()

def make_character(name, race, class_name):
    raw_stats = [roll_4d6_drop_lowest() for _ in range(6)]
    stats = {}
    if race == "Human":
        for i, s in enumerate(STAT_ORDER):
            stats[s] = raw_stats[i] + 1
    else:
        for i, s in enumerate(STAT_ORDER):
            stats[s] = raw_stats[i]
        bonuses = RACES[race]["bonuses"]
        for s in bonuses:
            stats[s] += bonuses[s]

    player = Player(name, race, class_name, stats)
    gear = STARTING_GEAR[class_name]
    if gear["weapon"]:
        player.equip_weapon(create_item(gear["weapon"]))
    if gear["armor"]:
        player.equip_armor(create_item(gear["armor"]))
    for item_name in gear["items"]:
        player.add_item(create_item(item_name))
    return player
