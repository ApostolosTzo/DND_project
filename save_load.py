import json
import os
from player import Player
from items import create_item

SAVES_DIR = "saves"

#===========================
# Save/Load System
#===========================
def _ensure_dir():
    if not os.path.exists(SAVES_DIR):
        os.makedirs(SAVES_DIR)

#===========================
# Save/Load Functions
#===========================
def _filename(save_name):
    _ensure_dir()
    return os.path.join(SAVES_DIR, f"{save_name}.json")

# save_game saves the player's state to a JSON file. 
# It takes a Player object and an optional save_name. 
# If no save_name is provided, it defaults to the player's name and level. 
# The function serializes the player's attributes, including
def save_game(player, save_name=None):
    if not save_name:
        save_name = f"{player.name}_Lv{player.level}"
    data = {
        "name": player.name,
        "race": player.race,
        "class_name": player.class_name,
        "level": player.level,
        "xp": player.xp,
        "gold": player.gold,
        "stats": player.stats,
        "hp": player.hp,
        "max_hp": player.max_hp,
        "weapon": player.weapon.name if player.weapon else None,
        "armor": player.armor.name if player.armor else None,
        "shield": player.shield.name if player.shield else None,
        "inventory": [item.name for item in player.inventory],
    }
    with open(_filename(save_name), "w") as f:
        json.dump(data, f, indent=2)
    return save_name

# load_game loads a player's state from a JSON file.
# It takes a save_name, reads the corresponding JSON file,
# and reconstructs a Player object with the saved attributes.
# The function also recreates the player's inventory and equipped items using the create_item function.
def load_game(save_name):
    with open(_filename(save_name), "r") as f:
        data = json.load(f)
    player = Player(data["name"], data["race"], data["class_name"], data["stats"])
    player.level = data["level"]
    player.xp = data["xp"]
    player.gold = data["gold"]
    player.hp = data["hp"]
    player.max_hp = data["max_hp"]
    player.inventory = []
    if data["weapon"]:
        player.equip_weapon(create_item(data["weapon"]))
    if data["armor"]:
        player.equip_armor(create_item(data["armor"]))
    if data["shield"]:
        player.shield = create_item(data["shield"])
        player.ac = player.calc_ac()
    for item_name in data["inventory"]:
        player.add_item(create_item(item_name))
    return player

# list_saves lists all available save files in the SAVES_DIR directory.
# It returns a list of tuples containing the save name, player
def list_saves():
    _ensure_dir()
    saves = []
    for fname in os.listdir(SAVES_DIR):
        if fname.endswith(".json"):
            name = fname[:-5]
            try:
                with open(os.path.join(SAVES_DIR, fname)) as f:
                    data = json.load(f)
                saves.append((name, data["name"], data["race"], data["class_name"], data["level"]))
            except:
                saves.append((name, name, "?", "?", 0))
    return saves
