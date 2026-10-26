// GENERATED FILE - do not edit by hand.
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

const GAME_DATA = {
 "items": {
  "Longsword": {
   "name": "Longsword",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "slashing",
   "properties": [
    "two-handed",
    "versatile"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Greatsword": {
   "name": "Greatsword",
   "category": "weapon",
   "damage_dice": "2d6",
   "damage_type": "slashing",
   "properties": [
    "two-handed",
    "heavy"
   ],
   "stats_bonus": {
    "STR": 2
   }
  },
  "Battle Axe": {
   "name": "Battle Axe",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "slashing",
   "properties": [
    "versatile"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "War Hammer": {
   "name": "War Hammer",
   "category": "weapon",
   "damage_dice": "1d10",
   "damage_type": "bludgeoning",
   "properties": [
    "versatile"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Mace": {
   "name": "Mace",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "bludgeoning",
   "properties": [
    "versatile"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Flail": {
   "name": "Flail",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "bludgeoning",
   "properties": [
    "versatile"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Spear": {
   "name": "Spear",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "piercing",
   "properties": [
    "versatile",
    "thrown"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Rapier": {
   "name": "Rapier",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "piercing",
   "properties": [
    "finesse"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Dagger": {
   "name": "Dagger",
   "category": "weapon",
   "damage_dice": "1d4",
   "damage_type": "piercing",
   "properties": [
    "finesse",
    "light",
    "thrown"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Quarterstaff": {
   "name": "Quarterstaff",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "bludgeoning",
   "properties": [
    "versatile"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Shortbow": {
   "name": "Shortbow",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "piercing",
   "properties": [
    "two-handed",
    "ranged"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Longbow": {
   "name": "Longbow",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "piercing",
   "properties": [
    "two-handed",
    "ranged",
    "heavy"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Crossbow": {
   "name": "Crossbow",
   "category": "weapon",
   "damage_dice": "1d10",
   "damage_type": "piercing",
   "properties": [
    "two-handed",
    "ranged",
    "loading"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Hand Crossbow": {
   "name": "Hand Crossbow",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "piercing",
   "properties": [
    "ranged",
    "light"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Magic Staff": {
   "name": "Magic Staff",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "bludgeoning",
   "properties": [
    "versatile",
    "magic"
   ],
   "stats_bonus": {}
  },
  "Arcane Staff": {
   "name": "Arcane Staff",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "force",
   "properties": [
    "two-handed",
    "magic"
   ],
   "stats_bonus": {
    "INT": 1
   }
  },
  "Wand": {
   "name": "Wand",
   "category": "weapon",
   "damage_dice": "1d4",
   "damage_type": "force",
   "properties": [
    "magic",
    "ranged"
   ],
   "stats_bonus": {}
  },
  "Lampada": {
   "name": "Lampada",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "fire_damage",
   "properties": [
    "versatile",
    "magic"
   ],
   "stats_bonus": {}
  },
  "Leather": {
   "name": "Leather",
   "category": "armor",
   "base_ac": 11,
   "armor_type": "light",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {}
  },
  "Studded Leather": {
   "name": "Studded Leather",
   "category": "armor",
   "base_ac": 12,
   "armor_type": "light",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Hide": {
   "name": "Hide",
   "category": "armor",
   "base_ac": 13,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [],
   "stats_bonus": {}
  },
  "Chainmail": {
   "name": "Chainmail",
   "category": "armor",
   "base_ac": 14,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [],
   "stats_bonus": {}
  },
  "Scale Mail": {
   "name": "Scale Mail",
   "category": "armor",
   "base_ac": 14,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [],
   "stats_bonus": {}
  },
  "Breastplate": {
   "name": "Breastplate",
   "category": "armor",
   "base_ac": 14,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [],
   "stats_bonus": {}
  },
  "Half Plate": {
   "name": "Half Plate",
   "category": "armor",
   "base_ac": 15,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [],
   "stats_bonus": {}
  },
  "Ring Mail": {
   "name": "Ring Mail",
   "category": "armor",
   "base_ac": 14,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {}
  },
  "Plate": {
   "name": "Plate",
   "category": "armor",
   "base_ac": 17,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {}
  },
  "Splint": {
   "name": "Splint",
   "category": "armor",
   "base_ac": 17,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {}
  },
  "Titanium": {
   "name": "Titanium",
   "category": "armor",
   "base_ac": 18,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {}
  },
  "Dragon Scale": {
   "name": "Dragon Scale",
   "category": "armor",
   "base_ac": 19,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "CON": 8
   }
  },
  "Shield": {
   "name": "Shield",
   "category": "armor",
   "base_ac": 2,
   "armor_type": "shield",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {}
  },
  "Iron Shield": {
   "name": "Iron Shield",
   "category": "armor",
   "base_ac": 3,
   "armor_type": "shield",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "STR": 1,
    "DEX": 3
   }
  },
  "Tower Shield": {
   "name": "Tower Shield",
   "category": "armor",
   "base_ac": 4,
   "armor_type": "shield",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "STR": 2,
    "DEX": 2
   }
  },
  "Magic Shield": {
   "name": "Magic Shield",
   "category": "armor",
   "base_ac": 5,
   "armor_type": "shield",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "INT": 2,
    "WIS": 2
   }
  },
  "Dragon Shield": {
   "name": "Dragon Shield",
   "category": "armor",
   "base_ac": 6,
   "armor_type": "shield",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "STR": 4,
    "DEX": 4,
    "CON": 4
   }
  },
  "Aegis Shield": {
   "name": "Aegis Shield",
   "category": "armor",
   "base_ac": 7,
   "armor_type": "shield",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "STR": 5,
    "DEX": 5,
    "CON": 5
   }
  },
  "Wizard Robe": {
   "name": "Wizard Robe",
   "category": "armor",
   "base_ac": 10,
   "armor_type": "light",
   "dex_limit": null,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "INT": 9
   }
  },
  "Healing Potion": {
   "name": "Healing Potion",
   "category": "item",
   "description": "Restores 10 HP.",
   "effect": "heal",
   "stats_bonus": {}
  },
  "Greater Healing Potion": {
   "name": "Greater Healing Potion",
   "category": "item",
   "description": "Restores 55 HP.",
   "effect": "heal",
   "stats_bonus": {}
  },
  "Superior Healing Potion": {
   "name": "Superior Healing Potion",
   "category": "item",
   "description": "Restores 120 HP.",
   "effect": "heal",
   "stats_bonus": {}
  },
  "Grand Healing Potion": {
   "name": "Grand Healing Potion",
   "category": "item",
   "description": "Restores 220 HP.",
   "effect": "heal",
   "stats_bonus": {}
  },
  "Ultimate Healing Potion": {
   "name": "Ultimate Healing Potion",
   "category": "item",
   "description": "Restores 360 HP.",
   "effect": "heal",
   "stats_bonus": {}
  },
  "Scroll of Fireball": {
   "name": "Scroll of Fireball",
   "category": "item",
   "description": "Deals fire damage (future use)",
   "effect": "scroll_fireball",
   "stats_bonus": {}
  },
  "Scroll of Healing": {
   "name": "Scroll of Healing",
   "category": "item",
   "description": "Heals ally (future use)",
   "effect": "scroll_heal",
   "stats_bonus": {}
  },
  "Arcane Ring": {
   "name": "Arcane Ring",
   "category": "item",
   "description": "A ring humming with magic",
   "effect": null,
   "stats_bonus": {
    "INT": 1
   }
  },
  "Shortsword": {
   "name": "Shortsword",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "slashing",
   "properties": [
    "versatile"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Sabre": {
   "name": "Sabre",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "slashing",
   "properties": [
    "finesse"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Scimitar": {
   "name": "Scimitar",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "slashing",
   "properties": [
    "finesse",
    "light"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Claymore": {
   "name": "Claymore",
   "category": "weapon",
   "damage_dice": "2d6",
   "damage_type": "slashing",
   "properties": [
    "two-handed",
    "heavy"
   ],
   "stats_bonus": {
    "STR": 2
   }
  },
  "Falchion": {
   "name": "Falchion",
   "category": "weapon",
   "damage_dice": "2d4",
   "damage_type": "slashing",
   "properties": [
    "two-handed",
    "heavy"
   ],
   "stats_bonus": {
    "STR": 2
   }
  },
  "Trident": {
   "name": "Trident",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "piercing",
   "properties": [
    "versatile",
    "thrown"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Glaive": {
   "name": "Glaive",
   "category": "weapon",
   "damage_dice": "2d6",
   "damage_type": "slashing",
   "properties": [
    "two-handed",
    "heavy"
   ],
   "stats_bonus": {
    "STR": 2
   }
  },
  "Lucerne Hammer": {
   "name": "Lucerne Hammer",
   "category": "weapon",
   "damage_dice": "2d6",
   "damage_type": "piercing",
   "properties": [
    "two-handed",
    "heavy"
   ],
   "stats_bonus": {
    "STR": 2
   }
  },
  "Greataxe": {
   "name": "Greataxe",
   "category": "weapon",
   "damage_dice": "2d6",
   "damage_type": "slashing",
   "properties": [
    "two-handed",
    "heavy"
   ],
   "stats_bonus": {
    "STR": 3
   }
  },
  "Maul": {
   "name": "Maul",
   "category": "weapon",
   "damage_dice": "2d6+2",
   "damage_type": "bludgeoning",
   "properties": [
    "two-handed",
    "heavy"
   ],
   "stats_bonus": {
    "STR": 3
   }
  },
  "War Sickle": {
   "name": "War Sickle",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "slashing",
   "properties": [
    "versatile",
    "light"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Kris Dagger": {
   "name": "Kris Dagger",
   "category": "weapon",
   "damage_dice": "2d4",
   "damage_type": "piercing",
   "properties": [
    "finesse",
    "light",
    "thrown"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Broadsword": {
   "name": "Broadsword",
   "category": "weapon",
   "damage_dice": "2d4",
   "damage_type": "slashing",
   "properties": [
    "two-handed",
    "versatile"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Cudgel": {
   "name": "Cudgel",
   "category": "weapon",
   "damage_dice": "1d4",
   "damage_type": "bludgeoning",
   "properties": [
    "light"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Bone Club": {
   "name": "Bone Club",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "bludgeoning",
   "properties": [
    "light"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Anchor": {
   "name": "Anchor",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "bludgeoning",
   "properties": [
    "two-handed",
    "heavy"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Executioner's Axe": {
   "name": "Executioner's Axe",
   "category": "weapon",
   "damage_dice": "1d10",
   "damage_type": "slashing",
   "properties": [
    "two-handed",
    "heavy"
   ],
   "stats_bonus": {
    "STR": 2
   }
  },
  "Viper Fang": {
   "name": "Viper Fang",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "piercing",
   "properties": [
    "finesse",
    "light",
    "thrown"
   ],
   "stats_bonus": {
    "DEX": 2
   }
  },
  "Sling": {
   "name": "Sling",
   "category": "weapon",
   "damage_dice": "1d4",
   "damage_type": "bludgeoning",
   "properties": [
    "ranged",
    "light"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Dart": {
   "name": "Dart",
   "category": "weapon",
   "damage_dice": "1d4",
   "damage_type": "piercing",
   "properties": [
    "ranged",
    "light",
    "thrown"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Javelin": {
   "name": "Javelin",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "piercing",
   "properties": [
    "thrown",
    "versatile"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Light Crossbow": {
   "name": "Light Crossbow",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "piercing",
   "properties": [
    "ranged",
    "light"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Heavy Crossbow": {
   "name": "Heavy Crossbow",
   "category": "weapon",
   "damage_dice": "1d10",
   "damage_type": "piercing",
   "properties": [
    "ranged",
    "loading",
    "heavy"
   ],
   "stats_bonus": {
    "STR": 1
   }
  },
  "Composite Bow": {
   "name": "Composite Bow",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "piercing",
   "properties": [
    "ranged",
    "heavy"
   ],
   "stats_bonus": {
    "DEX": 2
   }
  },
  "Repeating Crossbow": {
   "name": "Repeating Crossbow",
   "category": "weapon",
   "damage_dice": "1d10",
   "damage_type": "piercing",
   "properties": [
    "ranged",
    "loading"
   ],
   "stats_bonus": {
    "DEX": 2
   }
  },
  "Ember Blade": {
   "name": "Ember Blade",
   "category": "weapon",
   "damage_dice": "1d8",
   "damage_type": "fire_damage",
   "properties": [
    "versatile",
    "magic"
   ],
   "stats_bonus": {
    "INT": 1
   }
  },
  "Frost Staff": {
   "name": "Frost Staff",
   "category": "weapon",
   "damage_dice": "2d6",
   "damage_type": "cold",
   "properties": [
    "two-handed",
    "magic"
   ],
   "stats_bonus": {
    "INT": 2
   }
  },
  "Storm Wand": {
   "name": "Storm Wand",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "lightning",
   "properties": [
    "magic",
    "ranged"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Bone Wand": {
   "name": "Bone Wand",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "dark",
   "properties": [
    "magic",
    "ranged"
   ],
   "stats_bonus": {
    "WIS": 1
   }
  },
  "Runed Dagger": {
   "name": "Runed Dagger",
   "category": "weapon",
   "damage_dice": "2d4+2",
   "damage_type": "force",
   "properties": [
    "finesse",
    "light",
    "magic"
   ],
   "stats_bonus": {
    "DEX": 2,
    "INT": 1
   }
  },
  "Venom Dagger": {
   "name": "Venom Dagger",
   "category": "weapon",
   "damage_dice": "2d4+5",
   "damage_type": "poison",
   "properties": [
    "finesse",
    "light",
    "thrown"
   ],
   "stats_bonus": {
    "DEX": 3
   }
  },
  "Plasma Wand": {
   "name": "Plasma Wand",
   "category": "weapon",
   "damage_dice": "1d6",
   "damage_type": "poison",
   "properties": [
    "magic",
    "ranged"
   ],
   "stats_bonus": {
    "INT": 1
   }
  },
  "Padded Armor": {
   "name": "Padded Armor",
   "category": "armor",
   "base_ac": 10,
   "armor_type": "light",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "CON": 1
   }
  },
  "Nomad Leather": {
   "name": "Nomad Leather",
   "category": "armor",
   "base_ac": 11,
   "armor_type": "light",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Doublet": {
   "name": "Doublet",
   "category": "armor",
   "base_ac": 12,
   "armor_type": "light",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Shadowcloth": {
   "name": "Shadowcloth",
   "category": "armor",
   "base_ac": 12,
   "armor_type": "light",
   "dex_limit": null,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "DEX": 2
   }
  },
  "Wolf Hide Armor": {
   "name": "Wolf Hide Armor",
   "category": "armor",
   "base_ac": 12,
   "armor_type": "light",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "CON": 1,
    "DEX": 1
   }
  },
  "Robe of Silk": {
   "name": "Robe of Silk",
   "category": "armor",
   "base_ac": 10,
   "armor_type": "light",
   "dex_limit": null,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "INT": 1
   }
  },
  "Mithral Leather": {
   "name": "Mithral Leather",
   "category": "armor",
   "base_ac": 13,
   "armor_type": "light",
   "dex_limit": null,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "DEX": 1,
    "CON": 1
   }
  },
  "Elven Cloak Armor": {
   "name": "Elven Cloak Armor",
   "category": "armor",
   "base_ac": 12,
   "armor_type": "light",
   "dex_limit": null,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "DEX": 2
   }
  },
  "Riveted Leather": {
   "name": "Riveted Leather",
   "category": "armor",
   "base_ac": 13,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [],
   "stats_bonus": {
    "CON": 1
   }
  },
  "Padded Mail": {
   "name": "Padded Mail",
   "category": "armor",
   "base_ac": 13,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Ironweave Mail": {
   "name": "Ironweave Mail",
   "category": "armor",
   "base_ac": 14,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [],
   "stats_bonus": {
    "CON": 1
   }
  },
  "Bone Lacquer": {
   "name": "Bone Lacquer",
   "category": "armor",
   "base_ac": 14,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "CON": 2
   }
  },
  "Goblinforged Mail": {
   "name": "Goblinforged Mail",
   "category": "armor",
   "base_ac": 14,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [],
   "stats_bonus": {
    "STR": 1,
    "CON": 1
   }
  },
  "Enchanted Hide": {
   "name": "Enchanted Hide",
   "category": "armor",
   "base_ac": 14,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "CON": 1,
    "WIS": 1
   }
  },
  "Lamellar Armor": {
   "name": "Lamellar Armor",
   "category": "armor",
   "base_ac": 15,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [],
   "stats_bonus": {
    "CON": 1
   }
  },
  "Ward Mail": {
   "name": "Ward Mail",
   "category": "armor",
   "base_ac": 14,
   "armor_type": "medium",
   "dex_limit": 2,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Banded Mail": {
   "name": "Banded Mail",
   "category": "armor",
   "base_ac": 15,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {}
  },
  "Steel Plate": {
   "name": "Steel Plate",
   "category": "armor",
   "base_ac": 17,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "CON": 1
   }
  },
  "Obsidian Plate": {
   "name": "Obsidian Plate",
   "category": "armor",
   "base_ac": 17,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "CON": 2
   }
  },
  "Mithral Plate": {
   "name": "Mithral Plate",
   "category": "armor",
   "base_ac": 18,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [
    "magic",
    "light"
   ],
   "stats_bonus": {
    "CON": 1,
    "DEX": 1
   }
  },
  "Warden Plate": {
   "name": "Warden Plate",
   "category": "armor",
   "base_ac": 17,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "STR": 1,
    "CON": 1
   }
  },
  "Dragonbone Plate": {
   "name": "Dragonbone Plate",
   "category": "armor",
   "base_ac": 18,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "CON": 2
   }
  },
  "Titanforged Plate": {
   "name": "Titanforged Plate",
   "category": "armor",
   "base_ac": 18,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "STR": 1,
    "CON": 1
   }
  },
  "Barrier Plate": {
   "name": "Barrier Plate",
   "category": "armor",
   "base_ac": 19,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "CON": 1
   }
  },
  "Ancient Scale Plate": {
   "name": "Ancient Scale Plate",
   "category": "armor",
   "base_ac": 19,
   "armor_type": "heavy",
   "dex_limit": null,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "CON": 2
   }
  },
  "Buckler": {
   "name": "Buckler",
   "category": "armor",
   "base_ac": 1,
   "armor_type": "shield",
   "dex_limit": null,
   "properties": [
    "light"
   ],
   "stats_bonus": {
    "DEX": 1
   }
  },
  "Bronze Shield": {
   "name": "Bronze Shield",
   "category": "armor",
   "base_ac": 2,
   "armor_type": "shield",
   "dex_limit": null,
   "properties": [],
   "stats_bonus": {
    "CON": 1
   }
  },
  "Runed Shield": {
   "name": "Runed Shield",
   "category": "armor",
   "base_ac": 3,
   "armor_type": "shield",
   "dex_limit": null,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "INT": 1,
    "WIS": 1
   }
  },
  "Warden's Bulwark": {
   "name": "Warden's Bulwark",
   "category": "armor",
   "base_ac": 5,
   "armor_type": "shield",
   "dex_limit": null,
   "properties": [
    "two-handed"
   ],
   "stats_bonus": {
    "CON": 2
   }
  },
  "Bulwark of Dawn": {
   "name": "Bulwark of Dawn",
   "category": "armor",
   "base_ac": 6,
   "armor_type": "shield",
   "dex_limit": null,
   "properties": [
    "magic"
   ],
   "stats_bonus": {
    "STR": 2,
    "CON": 2
   }
  },
  "Metal Fragments": {
   "name": "Metal Fragments",
   "category": "item",
   "description": "Scrap metal wrenched from a goblin's gear.",
   "effect": "material",
   "stats_bonus": {}
  },
  "Web String": {
   "name": "Web String",
   "category": "item",
   "description": "Silken strand, still faintly sticky.",
   "effect": "material",
   "stats_bonus": {}
  },
  "Slime Ball": {
   "name": "Slime Ball",
   "category": "item",
   "description": "A wobbling blob that refuses to evaporate.",
   "effect": "material",
   "stats_bonus": {}
  },
  "Rotten Flesh": {
   "name": "Rotten Flesh",
   "category": "item",
   "description": "Rank, but some alchemists pay for it.",
   "effect": "material",
   "stats_bonus": {}
  },
  "Bone": {
   "name": "Bone",
   "category": "item",
   "description": "A clean femur. Someone was taller once.",
   "effect": "material",
   "stats_bonus": {}
  },
  "Fur": {
   "name": "Fur",
   "category": "item",
   "description": "Coarse grey pelt, still warm.",
   "effect": "material",
   "stats_bonus": {}
  },
  "Plasma": {
   "name": "Plasma",
   "category": "item",
   "description": "A finger of cold blue light. Handle carefully.",
   "effect": "material",
   "stats_bonus": {}
  }
 },
 "starting_potions": [
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion",
  "Healing Potion"
 ],
 "starting_gear": {
  "Fighter": {
   "weapon": "Longsword",
   "armor": "Chainmail",
   "items": [
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion"
   ]
  },
  "Rogue": {
   "weapon": "Dagger",
   "armor": "Leather",
   "items": [
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion"
   ]
  },
  "Wizard": {
   "weapon": "Magic Staff",
   "armor": null,
   "items": [
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion"
   ]
  },
  "Cleric": {
   "weapon": "Mace",
   "armor": "Plate",
   "items": [
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion",
    "Healing Potion"
   ]
  }
 },
 "potion_heal": {
  "Healing Potion": 10,
  "Greater Healing Potion": 55,
  "Superior Healing Potion": 120,
  "Grand Healing Potion": 220,
  "Ultimate Healing Potion": 360
 },
 "potion_min_level": {
  "Healing Potion": 1,
  "Greater Healing Potion": 25,
  "Superior Healing Potion": 60,
  "Grand Healing Potion": 120,
  "Ultimate Healing Potion": 200
 },
 "materials": {
  "Metal Fragments": "Goblin",
  "Web String": "Spider",
  "Slime Ball": "Slime",
  "Rotten Flesh": "Zombie",
  "Bone": "Skeleton",
  "Fur": "Wolf",
  "Plasma": "Ghost"
 },
 "damage_type_aliases": {
  "fire_damage": "fire",
  "cold": "ice"
 },
 "damage_types": [
  "slashing",
  "bludgeoning",
  "piercing",
  "fire",
  "ice",
  "lightning",
  "dark",
  "force",
  "poison"
 ],
 "element_status": {
  "fire": "burn",
  "ice": "freeze",
  "poison": "poison",
  "lightning": "strike",
  "dark": "drain"
 },
 "two_handed_bonus": {
  "1d4": 0,
  "1d6": 0,
  "1d8": 1,
  "1d10": 1,
  "1d12": 1,
  "2d4": 1,
  "2d6": 1,
  "2d10": 2,
  "2d12": 2
 },
 "all_classes": [
  "Fighter",
  "Rogue",
  "Wizard",
  "Cleric"
 ],
 "weapon_classes": {
  "Longsword": [
   "Fighter"
  ],
  "Greatsword": [
   "Fighter"
  ],
  "Battle Axe": [
   "Fighter"
  ],
  "Spear": [
   "Fighter"
  ],
  "Trident": [
   "Fighter"
  ],
  "Glaive": [
   "Fighter"
  ],
  "Lucerne Hammer": [
   "Fighter"
  ],
  "Executioner's Axe": [
   "Fighter"
  ],
  "Greataxe": [
   "Fighter"
  ],
  "Maul": [
   "Fighter"
  ],
  "Claymore": [
   "Fighter"
  ],
  "Falchion": [
   "Fighter"
  ],
  "Broadsword": [
   "Fighter"
  ],
  "Anchor": [
   "Fighter"
  ],
  "War Sickle": [
   "Fighter"
  ],
  "Cudgel": [
   "Fighter"
  ],
  "Rapier": [
   "Rogue"
  ],
  "Dagger": [
   "Rogue"
  ],
  "Shortsword": [
   "Rogue"
  ],
  "Sabre": [
   "Rogue"
  ],
  "Scimitar": [
   "Rogue"
  ],
  "Kris Dagger": [
   "Rogue"
  ],
  "Viper Fang": [
   "Rogue"
  ],
  "Venom Dagger": [
   "Rogue"
  ],
  "Bone Club": [
   "Rogue"
  ],
  "Runed Dagger": [
   "Rogue",
   "Wizard"
  ],
  "Magic Staff": [
   "Wizard"
  ],
  "Arcane Staff": [
   "Wizard"
  ],
  "Lampada": [
   "Wizard"
  ],
  "Ember Blade": [
   "Wizard"
  ],
  "Frost Staff": [
   "Wizard"
  ],
  "Storm Wand": [
   "Wizard"
  ],
  "Plasma Wand": [
   "Wizard"
  ],
  "Quarterstaff": [
   "Cleric"
  ],
  "War Hammer": [
   "Cleric"
  ],
  "Mace": [
   "Cleric"
  ],
  "Flail": [
   "Cleric"
  ],
  "Bone Wand": [
   "Cleric"
  ],
  "Shortbow": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ],
  "Longbow": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ],
  "Sling": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ],
  "Dart": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ],
  "Javelin": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ],
  "Hand Crossbow": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ],
  "Light Crossbow": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ],
  "Crossbow": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ],
  "Composite Bow": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ],
  "Heavy Crossbow": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ],
  "Repeating Crossbow": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ],
  "Wand": [
   "Fighter",
   "Rogue",
   "Wizard",
   "Cleric"
  ]
 },
 "races": {
  "Human": {
   "desc": "Versatile and ambitious",
   "bonuses": {
    "STR": 1,
    "DEX": 1,
    "CON": 1,
    "INT": 1,
    "WIS": 1,
    "CHA": 1
   }
  },
  "Elf": {
   "desc": "Graceful and perceptive",
   "bonuses": {
    "DEX": 2,
    "INT": 2
   }
  },
  "Dwarf": {
   "desc": "Tough and resilient",
   "bonuses": {
    "CON": 3,
    "STR": 2
   }
  },
  "Halfling": {
   "desc": "Lucky and nimble",
   "bonuses": {
    "DEX": 2,
    "CHA": 1
   }
  }
 },
 "classes": {
  "Fighter": {
   "desc": "Master of martial combat",
   "hp": 15,
   "primary": "STR",
   "bonuses": {
    "STR": 2
   }
  },
  "Rogue": {
   "desc": "Sneaky and dextrous",
   "hp": 13,
   "primary": "DEX",
   "bonuses": {
    "DEX": 2
   }
  },
  "Wizard": {
   "desc": "Wielder of arcane magic",
   "hp": 11,
   "primary": "INT",
   "bonuses": {
    "INT": 2
   }
  },
  "Cleric": {
   "desc": "Servant of the divine",
   "hp": 13,
   "primary": "WIS",
   "bonuses": {
    "WIS": 2
   }
  }
 },
 "stat_order": [
  "STR",
  "DEX",
  "CON",
  "INT",
  "WIS",
  "CHA"
 ],
 "shops": {
  "Potion Merchant": {
   "class": null,
   "note": "Potions for every level.",
   "items": {
    "Healing Potion": {
     "price": 15,
     "min_level": 1
    },
    "Greater Healing Potion": {
     "price": 200,
     "min_level": 25
    },
    "Superior Healing Potion": {
     "price": 1500,
     "min_level": 60
    },
    "Grand Healing Potion": {
     "price": 8000,
     "min_level": 120
    },
    "Ultimate Healing Potion": {
     "price": 30000,
     "min_level": 200
    }
   }
  },
  "Shield Smith": {
   "class": null,
   "note": "Every shield in the game is sold here and nowhere else.",
   "items": {
    "Buckler": {
     "price": 10,
     "min_level": 1
    },
    "Shield": {
     "price": 30,
     "min_level": 1
    },
    "Bronze Shield": {
     "price": 33,
     "min_level": 3
    },
    "Iron Shield": {
     "price": 100,
     "min_level": 3
    },
    "Tower Shield": {
     "price": 410,
     "min_level": 15
    },
    "Runed Shield": {
     "price": 670,
     "min_level": 22
    },
    "Magic Shield": {
     "price": 1050,
     "min_level": 30
    },
    "Warden's Bulwark": {
     "price": 3100,
     "min_level": 66
    },
    "Bulwark of Dawn": {
     "price": 5800,
     "min_level": 100
    },
    "Dragon Shield": {
     "price": 9700,
     "min_level": 142
    },
    "Aegis Shield": {
     "price": 16250,
     "min_level": 200
    }
   }
  },
  "Weaponsmith": {
   "class": "Fighter",
   "note": "Blades, axes and polearms.",
   "items": {
    "Wand": {
     "price": 10,
     "min_level": 1
    },
    "Longsword": {
     "price": 30,
     "min_level": 1
    },
    "Cudgel": {
     "price": 33,
     "min_level": 3
    },
    "Dart": {
     "price": 33,
     "min_level": 3
    },
    "Spear": {
     "price": 130,
     "min_level": 6
    },
    "Sling": {
     "price": 240,
     "min_level": 10
    },
    "Trident": {
     "price": 410,
     "min_level": 10
    },
    "Hand Crossbow": {
     "price": 410,
     "min_level": 15
    },
    "Battle Axe": {
     "price": 680,
     "min_level": 15
    },
    "Javelin": {
     "price": 670,
     "min_level": 22
    },
    "War Sickle": {
     "price": 1100,
     "min_level": 22
    },
    "Anchor": {
     "price": 1050,
     "min_level": 30
    },
    "Shortbow": {
     "price": 1500,
     "min_level": 40
    },
    "Broadsword": {
     "price": 2500,
     "min_level": 40
    },
    "Light Crossbow": {
     "price": 2200,
     "min_level": 52
    },
    "Falchion": {
     "price": 3100,
     "min_level": 66
    },
    "Heavy Crossbow": {
     "price": 4300,
     "min_level": 82
    },
    "Executioner's Axe": {
     "price": 7100,
     "min_level": 82
    },
    "Composite Bow": {
     "price": 9600,
     "min_level": 100
    },
    "Claymore": {
     "price": 9600,
     "min_level": 100
    },
    "Longbow": {
     "price": 7600,
     "min_level": 120
    },
    "Glaive": {
     "price": 12500,
     "min_level": 120
    },
    "Greatsword": {
     "price": 9700,
     "min_level": 142
    },
    "Repeating Crossbow": {
     "price": 12250,
     "min_level": 166
    },
    "Lucerne Hammer": {
     "price": 20500,
     "min_level": 166
    },
    "Crossbow": {
     "price": 27000,
     "min_level": 200
    },
    "Greataxe": {
     "price": 18000,
     "min_level": 200
    },
    "Maul": {
     "price": 27000,
     "min_level": 200
    }
   }
  },
  "Shadow Fence": {
   "class": "Rogue",
   "note": "Finesse weapons and thrown daggers.",
   "items": {
    "Wand": {
     "price": 10,
     "min_level": 1
    },
    "Dagger": {
     "price": 30,
     "min_level": 1
    },
    "Dart": {
     "price": 33,
     "min_level": 3
    },
    "Bone Club": {
     "price": 100,
     "min_level": 3
    },
    "Sling": {
     "price": 240,
     "min_level": 10
    },
    "Shortsword": {
     "price": 410,
     "min_level": 10
    },
    "Hand Crossbow": {
     "price": 410,
     "min_level": 15
    },
    "Javelin": {
     "price": 670,
     "min_level": 22
    },
    "Rapier": {
     "price": 1100,
     "min_level": 22
    },
    "Shortbow": {
     "price": 1500,
     "min_level": 40
    },
    "Sabre": {
     "price": 2500,
     "min_level": 40
    },
    "Light Crossbow": {
     "price": 2200,
     "min_level": 52
    },
    "Scimitar": {
     "price": 3100,
     "min_level": 66
    },
    "Kris Dagger": {
     "price": 2400,
     "min_level": 82
    },
    "Heavy Crossbow": {
     "price": 4300,
     "min_level": 82
    },
    "Composite Bow": {
     "price": 9600,
     "min_level": 100
    },
    "Viper Fang": {
     "price": 4200,
     "min_level": 120
    },
    "Longbow": {
     "price": 7600,
     "min_level": 120
    },
    "Repeating Crossbow": {
     "price": 12250,
     "min_level": 166
    },
    "Runed Dagger": {
     "price": 20500,
     "min_level": 166
    },
    "Crossbow": {
     "price": 27000,
     "min_level": 200
    },
    "Venom Dagger": {
     "price": 27000,
     "min_level": 200
    }
   }
  },
  "Wizard": {
   "class": "Wizard",
   "note": "Staves and elemental wands.",
   "items": {
    "Wand": {
     "price": 10,
     "min_level": 1
    },
    "Magic Staff": {
     "price": 30,
     "min_level": 1
    },
    "Dart": {
     "price": 33,
     "min_level": 3
    },
    "Lampada": {
     "price": 100,
     "min_level": 3
    },
    "Sling": {
     "price": 240,
     "min_level": 10
    },
    "Hand Crossbow": {
     "price": 410,
     "min_level": 15
    },
    "Storm Wand": {
     "price": 680,
     "min_level": 15
    },
    "Javelin": {
     "price": 670,
     "min_level": 22
    },
    "Ember Blade": {
     "price": 1050,
     "min_level": 30
    },
    "Shortbow": {
     "price": 1500,
     "min_level": 40
    },
    "Light Crossbow": {
     "price": 2200,
     "min_level": 52
    },
    "Plasma Wand": {
     "price": 3100,
     "min_level": 66
    },
    "Heavy Crossbow": {
     "price": 4300,
     "min_level": 82
    },
    "Composite Bow": {
     "price": 9600,
     "min_level": 100
    },
    "Arcane Staff": {
     "price": 9600,
     "min_level": 100
    },
    "Longbow": {
     "price": 7600,
     "min_level": 120
    },
    "Repeating Crossbow": {
     "price": 12250,
     "min_level": 166
    },
    "Runed Dagger": {
     "price": 20500,
     "min_level": 166
    },
    "Crossbow": {
     "price": 27000,
     "min_level": 200
    },
    "Frost Staff": {
     "price": 27000,
     "min_level": 200
    },
    "Arcane Ring": {
     "price": 2400,
     "min_level": 66
    }
   }
  },
  "Temple": {
   "class": "Cleric",
   "note": "Maces, flails and divine tools.",
   "items": {
    "Wand": {
     "price": 10,
     "min_level": 1
    },
    "Mace": {
     "price": 30,
     "min_level": 1
    },
    "Dart": {
     "price": 33,
     "min_level": 3
    },
    "Quarterstaff": {
     "price": 100,
     "min_level": 3
    },
    "Sling": {
     "price": 240,
     "min_level": 10
    },
    "Hand Crossbow": {
     "price": 410,
     "min_level": 15
    },
    "Javelin": {
     "price": 670,
     "min_level": 22
    },
    "Bone Wand": {
     "price": 1050,
     "min_level": 30
    },
    "Shortbow": {
     "price": 1500,
     "min_level": 40
    },
    "Light Crossbow": {
     "price": 2200,
     "min_level": 52
    },
    "Heavy Crossbow": {
     "price": 4300,
     "min_level": 82
    },
    "Flail": {
     "price": 3200,
     "min_level": 100
    },
    "Composite Bow": {
     "price": 9600,
     "min_level": 100
    },
    "Longbow": {
     "price": 7600,
     "min_level": 120
    },
    "Repeating Crossbow": {
     "price": 12250,
     "min_level": 166
    },
    "War Hammer": {
     "price": 9000,
     "min_level": 200
    },
    "Crossbow": {
     "price": 27000,
     "min_level": 200
    }
   }
  },
  "Armorer": {
   "class": null,
   "note": "Body armour, light to heavy.",
   "items": {
    "Banded Mail": {
     "price": 10,
     "min_level": 1
    },
    "Chainmail": {
     "price": 14,
     "min_level": 1
    },
    "Hide": {
     "price": 18,
     "min_level": 1
    },
    "Leather": {
     "price": 22,
     "min_level": 1
    },
    "Padded Armor": {
     "price": 26,
     "min_level": 1
    },
    "Ring Mail": {
     "price": 30,
     "min_level": 1
    },
    "Nomad Leather": {
     "price": 33,
     "min_level": 3
    },
    "Padded Mail": {
     "price": 46,
     "min_level": 3
    },
    "Riveted Leather": {
     "price": 59,
     "min_level": 3
    },
    "Scale Mail": {
     "price": 75,
     "min_level": 3
    },
    "Studded Leather": {
     "price": 85,
     "min_level": 3
    },
    "Wizard Robe": {
     "price": 100,
     "min_level": 3
    },
    "Breastplate": {
     "price": 135,
     "min_level": 10
    },
    "Doublet": {
     "price": 270,
     "min_level": 10
    },
    "Robe of Silk": {
     "price": 410,
     "min_level": 10
    },
    "Half Plate": {
     "price": 230,
     "min_level": 15
    },
    "Plate": {
     "price": 450,
     "min_level": 15
    },
    "Wolf Hide Armor": {
     "price": 680,
     "min_level": 15
    },
    "Ironweave Mail": {
     "price": 370,
     "min_level": 22
    },
    "Splint": {
     "price": 1100,
     "min_level": 22
    },
    "Elven Cloak Armor": {
     "price": 850,
     "min_level": 40
    },
    "Goblinforged Mail": {
     "price": 1400,
     "min_level": 40
    },
    "Shadowcloth": {
     "price": 1950,
     "min_level": 40
    },
    "Ward Mail": {
     "price": 2500,
     "min_level": 40
    },
    "Enchanted Hide": {
     "price": 1200,
     "min_level": 52
    },
    "Lamellar Armor": {
     "price": 2050,
     "min_level": 52
    },
    "Mithral Leather": {
     "price": 2900,
     "min_level": 52
    },
    "Titanium": {
     "price": 3700,
     "min_level": 52
    },
    "Bone Lacquer": {
     "price": 2400,
     "min_level": 82
    },
    "Steel Plate": {
     "price": 7100,
     "min_level": 82
    },
    "Obsidian Plate": {
     "price": 3200,
     "min_level": 100
    },
    "Titanforged Plate": {
     "price": 6400,
     "min_level": 100
    },
    "Warden Plate": {
     "price": 9600,
     "min_level": 100
    },
    "Dragon Scale": {
     "price": 4200,
     "min_level": 120
    },
    "Dragonbone Plate": {
     "price": 8400,
     "min_level": 120
    },
    "Mithral Plate": {
     "price": 12500,
     "min_level": 120
    },
    "Barrier Plate": {
     "price": 12250,
     "min_level": 166
    },
    "Ancient Scale Plate": {
     "price": 16250,
     "min_level": 200
    }
   }
  }
 },
 "unlock_tiers": [
  1,
  3,
  6,
  10,
  15,
  22,
  30,
  40,
  52,
  66,
  82,
  100,
  120,
  142,
  166,
  200
 ],
 "tier_base": 10.0,
 "tier_mult": [
  1.0,
  1.1,
  1.2,
  1.35,
  1.5,
  1.7,
  1.9,
  2.1,
  2.35,
  2.6,
  2.9,
  3.2,
  3.5,
  3.8,
  4.1,
  4.5
 ],
 "sell_ratio": 0.8,
 "armory_npcs": [
  [
   "Weaponsmith",
   "Fighter",
   "Blades, axes and polearms."
  ],
  [
   "Shadow Fence",
   "Rogue",
   "Finesse weapons and thrown daggers."
  ],
  [
   "Wizard",
   "Wizard",
   "Staves and elemental wands."
  ],
  [
   "Temple",
   "Cleric",
   "Maces, flails and divine tools."
  ]
 ],
 "templates": {
  "Zombie": {
   "hp": 22,
   "ac": 8,
   "dice": "d6",
   "bonus": 1,
   "xp": 50,
   "gold": 5
  },
  "Skeleton": {
   "hp": 13,
   "ac": 13,
   "dice": "d6",
   "bonus": 2,
   "xp": 50,
   "gold": 6
  },
  "Spider": {
   "hp": 16,
   "ac": 12,
   "dice": "d4",
   "bonus": 1,
   "xp": 50,
   "gold": 4
  },
  "Wolf": {
   "hp": 18,
   "ac": 13,
   "dice": "d6",
   "bonus": 2,
   "xp": 50,
   "gold": 6
  },
  "Goblin": {
   "hp": 10,
   "ac": 15,
   "dice": "d4",
   "bonus": 1,
   "xp": 30,
   "gold": 8
  },
  "Slime": {
   "hp": 20,
   "ac": 7,
   "dice": "d6",
   "bonus": 0,
   "xp": 40,
   "gold": 3
  },
  "Ghost": {
   "hp": 18,
   "ac": 11,
   "dice": "d8",
   "bonus": 2,
   "xp": 80,
   "gold": 10
  },
  "Demon Lord": {
   "hp": 60,
   "ac": 15,
   "dice": "d10",
   "bonus": 5,
   "xp": 200,
   "gold": 50
  },
  "Elder Dragon": {
   "hp": 75,
   "ac": 18,
   "dice": "d12",
   "bonus": 6,
   "xp": 250,
   "gold": 80
  }
 },
 "boss_names": [
  "Demon Lord",
  "Elder Dragon"
 ],
 "vulnerabilities": {
  "Zombie": {
   "weak": [
    "slashing",
    "piercing"
   ],
   "resist": [
    "bludgeoning",
    "force"
   ]
  },
  "Skeleton": {
   "weak": [
    "bludgeoning",
    "piercing"
   ],
   "resist": [
    "slashing",
    "fire"
   ]
  },
  "Spider": {
   "weak": [
    "fire",
    "ice"
   ],
   "resist": [
    "piercing"
   ]
  },
  "Wolf": {
   "weak": [
    "piercing"
   ],
   "resist": [
    "bludgeoning"
   ]
  },
  "Goblin": {
   "weak": [
    "slashing"
   ],
   "resist": [
    "ice"
   ]
  },
  "Slime": {
   "weak": [
    "fire",
    "ice"
   ],
   "resist": [
    "bludgeoning",
    "piercing",
    "slashing"
   ]
  },
  "Ghost": {
   "weak": [
    "force",
    "ice"
   ],
   "resist": [
    "piercing",
    "slashing"
   ]
  },
  "Demon Lord": {
   "weak": [
    "ice",
    "piercing"
   ],
   "resist": [
    "fire",
    "dark",
    "force"
   ]
  },
  "Elder Dragon": {
   "weak": [
    "piercing",
    "poison"
   ],
   "resist": [
    "fire",
    "slashing"
   ]
  }
 },
 "weak_multiplier": 1.5,
 "resist_multiplier": 0.5,
 "drops": {
  "Goblin": "Metal Fragments",
  "Spider": "Web String",
  "Slime": "Slime Ball",
  "Zombie": "Rotten Flesh",
  "Skeleton": "Bone",
  "Wolf": "Fur",
  "Ghost": "Plasma"
 },
 "drop_chance": 0.75,
 "drop_min": 1,
 "drop_max": 3,
 "xp_reward_multiplier": 1.4,
 "gold_reward_multiplier": 1.6,
 "element_rules": {
  "BURN_ROUNDS": 2,
  "BURN_DIE": "1d4",
  "BURN_BASE_CHANCE": 0.2,
  "BURN_CHANCE_PER_INT": 0.03,
  "BURN_MAX_CHANCE": 0.6,
  "FREEZE_BASE_CHANCE": 0.1,
  "FREEZE_INT_PER_POINT": 5,
  "FREEZE_CHANCE_PER_INT_BLOCK": 0.01,
  "FREEZE_MAX_CHANCE": 0.43,
  "FREEZE_INT_THRESHOLD": 15,
  "FREEZE_MIN_ROUNDS": 1,
  "FREEZE_MAX_ROUNDS": 2,
  "POISON_BASE_CHANCE": 0.2,
  "POISON_CHANCE_PER_DEX": 0.03,
  "POISON_MAX_CHANCE": 0.6,
  "POISON_MAX_ROUNDS": 999,
  "LIGHTNING_ROUNDS": 2,
  "LIGHTNING_DIE": "1d8",
  "LIGHTNING_BASE_CHANCE": 0.15,
  "LIGHTNING_WIS_PER_POINT": 2,
  "LIGHTNING_CHANCE_PER_WIS_BLOCK": 0.01,
  "LIGHTNING_MAX_CHANCE": 0.5,
  "DARK_ROUNDS": 3,
  "DARK_DIE": "1d4",
  "DARK_STR_PER_POINT": 15,
  "DARK_DAMAGE_PER_STR_BLOCK": 1
 },
 "locations": {
  "town": {
   "name": "Town",
   "x": 80,
   "y": 180,
   "type": "town",
   "connects_to": [
    "village1",
    "village2"
   ],
   "shops": [
    "Potion Merchant",
    "Weaponsmith",
    "Shadow Fence",
    "Temple",
    "Wizard",
    "Armorer",
    "Shield Smith"
   ]
  },
  "village1": {
   "name": "Village 1",
   "x": 380,
   "y": 310,
   "type": "village",
   "connects_to": [
    "town",
    "dungeon"
   ],
   "shops": [
    "Potion Merchant",
    "Weaponsmith",
    "Shadow Fence",
    "Armorer",
    "Shield Smith"
   ]
  },
  "village2": {
   "name": "Village 2",
   "x": 380,
   "y": 50,
   "type": "village",
   "connects_to": [
    "town"
   ],
   "shops": [
    "Potion Merchant"
   ]
  },
  "dungeon": {
   "name": "Dungeon",
   "x": 470,
   "y": 310,
   "type": "dungeon",
   "connects_to": [
    "village1"
   ],
   "shops": []
  }
 }
};
