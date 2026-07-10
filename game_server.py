from flask import Flask, render_template, jsonify, request
from player import Player, create_character, make_character, STAT_ORDER, CLASSES, RACES
from items import ITEMS, create_item
from enemy import generate_enemy
from dice import roll
from save_load import save_game, load_game, list_saves, save_exists

app = Flask(__name__)

gs = {
    "player": None,
    "enemy": None,
    "screen": "main_menu",
    "log": [],
    "pending_stat_boost": None,
    "pending_save_name": None,
}

def player_json(p):
    if not p:
        return None
    return {
        "name": p.name,
        "race": p.race,
        "class": p.class_name,
        "level": p.level,
        "hp": p.hp,
        "max_hp": p.max_hp,
        "ac": p.ac,
        "gold": p.gold,
        "xp": p.xp,
        "xp_to_next": p.xp_to_next(),
        "weapon": p.weapon.name if p.weapon else "None",
        "armor": p.armor.name if p.armor else "None",
    }

def respond(screen, title, body, options, extra=None):
    out = {
        "screen": screen,
        "title": title,
        "body": body,
        "options": options,
        "player": player_json(gs["player"]),
        "log": gs["log"],
    }
    if extra:
        out.update(extra)
    return jsonify(out)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/state")
def get_state():
    gs["log"] = []
    return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game", "Quit"])

@app.route("/create_form")
def create_form():
    race_list = []
    for r in RACES:
        bonuses = RACES[r]["bonuses"]
        bonus_str = ", ".join(f"{s}+{v}" for s, v in bonuses.items())
        race_list.append((r, f"{r} - {RACES[r]['desc']}", bonus_str))
    class_list = []
    for c in CLASSES:
        class_list.append((c, f"{c} - {CLASSES[c]['desc']}", CLASSES[c]["hp"], CLASSES[c]["primary"]))
    return jsonify({"races": race_list, "classes": class_list})

@app.route("/start", methods=["POST"])
def start_game():
    data = request.json
    name = data.get("name", "Adventurer")
    race = data.get("race", "Human")
    class_name = data.get("class", "Fighter")
    gs["player"] = make_character(name, race, class_name)
    gs["screen"] = "town"
    gs["log"] = ["Welcome, adventurer!"]
    return respond("town", "Town", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])

@app.route("/action", methods=["POST"])
def handle_action():
    data = request.json
    choice = data.get("choice", 0)

    if gs["screen"] == "town":
        return town_action(choice)
    elif gs["screen"] == "combat":
        return combat_action(choice)
    elif gs["screen"] == "combat_item":
        return combat_item_action(choice)
    elif gs["screen"] == "shop_select":
        return shop_select_action(choice)
    elif gs["screen"] == "shop":
        return shop_action(choice)
    elif gs["screen"] == "inventory":
        return inventory_action(choice)
    elif gs["screen"] == "stat_boost":
        return stat_boost_action(choice)
    elif gs["screen"] == "save_menu":
        gs["screen"] = "town"
        gs["log"] = []
        return respond("town", "Town", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])
    elif gs["screen"] == "confirm_overwrite":
        if choice == 0:
            return force_save()
        gs["screen"] = "town"
        gs["pending_save_name"] = None
        gs["log"] = []
        return respond("town", "Town", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])
    elif gs["screen"] == "load_menu":
        return load_action(choice)
    elif gs["screen"] == "game_over":
        gs["player"] = None
        gs["enemy"] = None
        gs["screen"] = "main_menu"
        gs["log"] = []
        return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game", "Quit"])

    return get_state()

@app.route("/save", methods=["POST"])
def do_save():
    p = gs["player"]
    if not p:
        return get_state()
    data = request.json
    name = data.get("name", p.name)
    if save_exists(name):
        gs["screen"] = "confirm_overwrite"
        gs["pending_save_name"] = name
        gs["log"] = [f"Save '{name}' already exists. Overwrite?"]
        return respond("confirm_overwrite", "Overwrite Save?", f"Save '{name}' already exists. Overwrite?", ["Yes", "No"])
    save_game(p, name)
    p.current_save = name
    gs["log"] = [f"Game saved as '{name}'!"]
    return respond("town", "Town", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])

@app.route("/force_save", methods=["POST"])
def force_save():
    p = gs["player"]
    if not p or not gs["pending_save_name"]:
        return get_state()
    name = gs["pending_save_name"]
    gs["pending_save_name"] = None
    save_game(p, name)
    p.current_save = name
    gs["screen"] = "town"
    gs["log"] = [f"Game saved as '{name}'!"]
    return respond("town", "Saved!", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])

# ---- Town ----
def town_action(choice):
    p = gs["player"]
    if not p:
        return get_state()

    if choice == 0:  # Fight
        e = generate_enemy(p.level)
        gs["enemy"] = e
        gs["screen"] = "combat"
        gs["log"] = [f"A wild {e.name} appears!"]
        return combat_state()

    elif choice == 1:  # Shop
        gs["screen"] = "shop"
        gs["log"] = []
        return shop_state()

    elif choice == 2:  # Inventory
        gs["screen"] = "inventory"
        gs["log"] = []
        return inventory_state()

    elif choice == 3:  # Save
        gs["screen"] = "save_menu"
        default = p.current_save or p.name
        return respond("save_menu", "Save Game", "", [f"Save as '{default}'", "(Back)"])

    elif choice == 4:  # Quit
        gs["player"] = None
        gs["enemy"] = None
        gs["screen"] = "main_menu"
        gs["log"] = []
        return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game", "Quit"])

    return respond("town", "Town", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])

# ---- Combat ----
def combat_state():
    e = gs["enemy"]
    p = gs["player"]
    body = f"{e.display()}\n\n{player_json(p)['name']}: HP {p.hp}/{p.max_hp}  AC {p.ac}"
    return respond("combat", "COMBAT", body, ["Attack", "Use Item", "Flee"])

def combat_action(choice):
    p = gs["player"]
    e = gs["enemy"]

    if choice == 0:  # Attack
        result = web_player_attack(p, e)
        gs["log"] = [result]

        if not e.is_alive():
            return combat_reward("Victory!")

        result2 = web_enemy_attack(p, e)
        gs["log"].append(result2)

        if not p.is_alive():
            gs["screen"] = "game_over"
            return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"])

        return combat_state()

    elif choice == 1:  # Use Item
        consumables = [item for item in p.inventory if item.category == "item" and item != p.weapon and item != p.armor and item != p.shield]
        if not consumables:
            gs["log"] = ["No potions to use!"]
            return combat_state()

        gs["screen"] = "combat_item"
        return respond("combat_item", "Use Item", "Choose an item:", [f"{i.name}" for i in consumables] + ["(Back)"])

    elif choice == 2:  # Flee
        if roll("1d20") >= 10:
            gs["enemy"] = None
            gs["screen"] = "town"
            gs["log"] = ["You fled successfully!"]
            return respond("town", "Fled!", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])
        else:
            gs["log"] = ["Failed to flee!"]
            result2 = web_enemy_attack(p, e)
            gs["log"].append(result2)
            if not p.is_alive():
                gs["screen"] = "game_over"
                return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"])
            return combat_state()

    return combat_state()

def combat_item_action(choice):
    p = gs["player"]
    e = gs["enemy"]
    consumables = [item for item in p.inventory if item.category == "item" and item != p.weapon and item != p.armor and item != p.shield]

    if choice >= len(consumables):
        gs["screen"] = "combat"
        return combat_state()

    item = consumables[choice]
    if item.name == "Healing Potion":
        heal = 9
        p.hp = min(p.hp + heal, p.max_hp)
        p.remove_item(item)
        gs["log"] = [f"Drank Healing Potion! Restored {heal} HP."]

        result2 = web_enemy_attack(p, e)
        gs["log"].append(result2)

        if not p.is_alive():
            gs["screen"] = "game_over"
            return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"])

        gs["screen"] = "combat"
        return combat_state()

    gs["screen"] = "combat"
    return combat_state()

def web_player_attack(p, e):
    if p.weapon and "finesse" in p.weapon.properties:
        mod = p.modifier("DEX")
    elif p.weapon and "ranged" in p.weapon.properties:
        mod = p.modifier("DEX")
    else:
        mod = p.modifier("STR")

    prof = (p.level - 1) // 4 + 2
    atk = roll("1d20") + prof + mod

    if atk >= e.ac:
        dmg = max(roll(p.weapon.damage_dice) + mod, 1) if p.weapon else max(1 + mod, 1)
        e.take_damage(dmg)
        return f"You hit the {e.name} for {dmg} damage! (d20 + {prof} + {mod} = {atk} vs AC {e.ac})"
    else:
        return f"You missed! (d20 + {prof} + {mod} = {atk} vs AC {e.ac})"

def web_enemy_attack(p, e):
    bonus = e.level // 2 + 2
    atk = roll("1d20") + bonus

    if atk >= p.ac:
        dmg = max(e.attack_damage(), 1)
        p.hp -= dmg
        if p.hp < 0:
            p.hp = 0
        return f"{e.name} hits you for {dmg} damage! (d20 + {bonus} = {atk} vs your AC {p.ac})"
    else:
        return f"{e.name} missed you! (d20 + {bonus} = {atk} vs your AC {p.ac})"

def combat_reward(title):
    p = gs["player"]
    e = gs["enemy"]
    gold = e.gold_drop()
    xp = e.xp_reward
    p.add_gold(gold)
    gs["log"] = [f"{e.name} defeated!", f"Looted {gold} gold!", f"Gained {xp} XP!"]

    # Handle XP / level-up
    p.xp += xp
    while p.xp >= p.xp_to_next():
        stat_boost = handle_level_up()
        if stat_boost:
            gs["screen"] = "stat_boost"
            return respond("stat_boost", f"LEVEL UP! You are now level {p.level}!", "Choose a stat to increase by 1:", STAT_ORDER)

    gs["enemy"] = None
    gs["screen"] = "town"
    return respond("town", title, "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])

def handle_level_up():
    p = gs["player"]
    old_con = p.modifier("CON")
    p.level += 1
    hp_gain = p.hp_per_level()
    p.max_hp += hp_gain
    p.hp = p.max_hp
    gold_r = p.level * 10
    p.add_gold(gold_r)
    gs["log"].append(f"LEVEL UP! Now level {p.level}! HP +{hp_gain}, +{gold_r} gold!")

    if p.level % 4 == 0:
        return p.level
    return None

def stat_boost_action(choice):
    p = gs["player"]
    old_con = p.modifier("CON")
    chosen = STAT_ORDER[choice]
    p.stats[chosen] += 1
    p.ac = p.calc_ac()
    if chosen == "CON" and p.modifier("CON") > old_con:
        p.max_hp += 1
    gs["log"].append(f"{chosen} increased to {p.stats[chosen]}!")

    # Autosave
    if p.current_save:
        save_game(p, p.current_save)
        gs["log"].append("Game autosaved!")

    # Process any pending XP (multiple level-ups)
    while p.xp >= p.xp_to_next():
        stat_boost = handle_level_up()
        if stat_boost:
            gs["screen"] = "stat_boost"
            return respond("stat_boost", f"LEVEL UP! You are now level {p.level}!", "Choose a stat to increase by 1:", STAT_ORDER)

    gs["enemy"] = None
    gs["screen"] = "town"
    return respond("town", "Character Updated!", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])

# ---- Shop ----
from shop import SHOP_NPCS

def shop_state():
    shop_names = list(SHOP_NPCS.keys())
    return respond("shop_select", "Which shop?", "", shop_names + ["(Back)"])

def shop_select_action(choice):
    shop_names = list(SHOP_NPCS.keys())
    if choice >= len(shop_names):
        gs["screen"] = "town"
        return respond("town", "Town", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])

    shop_name = shop_names[choice]
    gs["shop_name"] = shop_name
    return show_shop(shop_name)

def shop_action(choice):
    # Called when user selects an item or Back inside a specific shop
    # choice is the index of the option selected
    # Last option is always "(Back)"
    shop_names = list(SHOP_NPCS.keys())
    gs["screen"] = "shop_select"
    return respond("shop_select", "Which shop?", "", shop_names + ["(Back)"])

@app.route("/shop_buy", methods=["POST"])
def shop_buy():
    p = gs["player"]
    data = request.json
    item_name = data["item"]
    qty = data["qty"]
    shop_name = gs["shop_name"]
    shop = SHOP_NPCS.get(shop_name)
    if not shop or item_name not in shop["items"]:
        return show_shop(shop_name)

    price = shop["items"][item_name]["price"]
    total = price * qty
    if p.spend_gold(total):
        for _ in range(qty):
            p.add_item(create_item(item_name))
        gs["log"] = [f"Bought {qty} {item_name}(s) for {total}g!"]
    else:
        gs["log"] = [f"Not enough gold! Need {total}g, you have {p.gold}g."]

    return show_shop(shop_name)

def show_shop(shop_name):
    p = gs["player"]
    shop = SHOP_NPCS[shop_name]
    available = {n: d for n, d in shop["items"].items() if p.level >= d["min_level"]}
    items_list = [f"{n} ({d['price']}g)" for n, d in available.items()]
    return respond("shop", shop_name, "", items_list + ["(Back)"], extra={"shop_items": list(available.keys()), "shop_prices": [d["price"] for d in available.values()]})

# ---- Inventory ----
def inventory_state():
    p = gs["player"]
    lines = []
    if p.weapon:
        lines.append(f"Weapon: {p.weapon.name}")
    if p.armor:
        lines.append(f"Armor: {p.armor.name}")
    if p.shield:
        lines.append(f"Shield: {p.shield.name}")

    storage = [item for item in p.inventory if item != p.weapon and item != p.armor and item != p.shield]
    grouped = {}
    for item in storage:
        grouped.setdefault(item.name, []).append(item)

    storage_lines = []
    for name, items_list in grouped.items():
        storage_lines.append(f"{name} x{len(items_list)}" if len(items_list) > 1 else name)

    body = "Equipped:\n  " + ("\n  ".join(lines) if lines else "None") + "\n\nStorage:\n  " + ("\n  ".join(storage_lines) if storage_lines else "(empty)")
    gs["screen"] = "inventory"
    options = [f"[Use] {n}" for n in storage_lines] + ["(Close)"] if storage_lines else ["(Close)"]
    return respond("inventory", "INVENTORY", body, options, extra={"inv_items": [name for name in grouped.keys()]})

def inventory_action(choice):
    p = gs["player"]
    storage = [item for item in p.inventory if item != p.weapon and item != p.armor and item != p.shield]
    grouped = {}
    for item in storage:
        grouped.setdefault(item.name, []).append(item)

    names = list(grouped.keys())
    if not names or choice >= len(names):
        gs["screen"] = "town"
        return respond("town", "Town", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])

    item = grouped[names[choice]][0]

    if item.category == "weapon":
        if p.weapon:
            p.inventory.append(p.weapon)
        p.weapon = item
        p.remove_item(item)
        gs["log"] = [f"Equipped {item.name}!"]
    elif item.category == "armor":
        if item.armor_type == "shield":
            if p.shield:
                p.inventory.append(p.shield)
            p.shield = item
        else:
            if p.armor:
                p.inventory.append(p.armor)
            p.armor = item
        p.remove_item(item)
        p.ac = p.calc_ac()
        gs["log"] = [f"Equipped {item.name}!"]
    elif item.category == "item":
        if item.name == "Healing Potion":
            heal = 9
            p.hp = min(p.hp + heal, p.max_hp)
            p.remove_item(item)
            gs["log"] = [f"Drank Healing Potion! Restored {heal} HP."]

    return inventory_state()

# ---- Load Game ----
@app.route("/load_list")
def load_list():
    saves = list_saves()
    gs["screen"] = "load_menu"
    if not saves:
        return respond("main_menu", "No saves found", "", ["New Game", "Load Game", "Quit"])
    options = [f"{s[1]} {s[2]} {s[3]} Lv.{s[4]}" for s in saves]
    return respond("load_menu", "Load Game", "", options + ["(Back)"])

def load_action(choice):
    saves = list_saves()
    if choice >= len(saves):
        gs["screen"] = "main_menu"
        gs["log"] = []
        return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game", "Quit"])

    name = saves[choice][0]
    player = load_game(name)
    player.current_save = name
    gs["player"] = player
    gs["enemy"] = None
    gs["screen"] = "town"
    gs["log"] = [f"Loaded '{name}'!"]
    return respond("town", "Game Loaded!", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"])

if __name__ == "__main__":
    app.run(debug=True)
