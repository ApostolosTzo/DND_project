from flask import Flask, render_template, jsonify, request
from player import Player, create_character, make_character, STAT_ORDER, CLASSES, RACES
from items import ITEMS, create_item, get_item, is_material
from enemy import generate_enemy, generate_dungeon_enemy
from dice import roll
from save_load import save_game, load_game, list_saves, save_exists
from world_map import LOCATIONS
from quests import QUESTS, roll_quest_npcs, quests_for
from shop import SHOP_NPCS, sell_price

app = Flask(__name__)

# The town menu. Keep in step with templates/index.html handleClick().
TOWN_OPTIONS = ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"]
# No "Quit" on the main menu: it never did anything, and everything else in
# the game is reachable from the town screen's Quit option.
MENU_OPTIONS = ["New Game", "Load Game"]

gs = {
    "player": None,
    "enemy": None,
    "screen": "main_menu",
    "log": [],
    "pending_stat_boost": None,
    "pending_save_name": None,
    "current_location": None,
    "dungeon_floor": 0,
    "shop_mode": "buy",
    "quest_npcs": [],
    "quest_accepted": {},
    "quest_done": {},
    "quest_npc_index": 0,
    "return_to": None,
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
        "stats": p.stats,
        "effective_stats": p.effective_stats(),
        "stat_bonuses": p.get_equipment_stat_bonus(),
    }

def enemy_json(e):
    if not e:
        return None
    return {
        "name": e.name,
        "level": e.level,
        "hp": e.hp,
        "max_hp": e.max_hp,
        "ac": e.ac,
    }

# Function to respond with the current game state

def town_name():
    # Get the name of the current location based on the game state. 
    # If the current location is not set, default to "Town".
    loc = LOCATIONS.get(gs["current_location"])
    return loc["name"] if loc else "Town"

def respond(screen, title, body, options, extra=None):
    gs["screen"] = screen
    out = {
        "screen": screen,
        "title": title,
        "body": body,
        "options": options,
        "player": player_json(gs["player"]),
        "enemy": enemy_json(gs["enemy"]),
        "in_dungeon": gs["dungeon_floor"] > 0,
        "log": gs["log"],
        # Include the current location in the response
        "current_location": gs["current_location"],
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
    return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game"])

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

# Clears anything left over from a previous run: a live enemy, a half-finished
# dungeon crawl, a pending overwrite prompt or the last shop. Without this, a
# new game (or a loaded save) started while the previous run was inside the
# dungeon would silently inherit that state - no Flee option, and the world map
# would stay hidden.
def reset_run():
    gs["enemy"] = None
    gs["dungeon_floor"] = 0
    gs["pending_save_name"] = None
    gs["shop_name"] = None
    gs["shop_mode"] = "buy"
    # Fresh quest givers and a clean quest log for every new run.
    gs["quest_npcs"] = roll_quest_npcs()
    gs["quest_accepted"] = {}
    gs["quest_done"] = {}
    gs["quest_npc_index"] = 0
    gs["return_to"] = None

@app.route("/start", methods=["POST"])
def start_game():
    data = request.json
    name = data.get("name", "Adventurer")
    race = data.get("race", "Human")
    class_name = data.get("class", "Fighter")
    reset_run()
    gs["player"] = make_character(name, race, class_name)
    gs["screen"] = "town"
    gs["current_location"] = "town"
    gs["log"] = ["Welcome, adventurer!"]
    return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

# Function to handle player actions
# locations and their connections are defined in world_map.py
@app.route("/action", methods=["POST"])
def handle_action():
    data = request.json
    choice = data.get("choice", 0)

    # Determine the current screen and call the appropriate action handler
    
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
    elif gs["screen"] == "stat_allocation":
        return allocation_action(choice)
    elif gs["screen"] == "save_menu":
        gs["screen"] = "town"
        gs["log"] = []
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif gs["screen"] == "confirm_overwrite":
        if choice == 0:
            return force_save()
        gs["screen"] = "town"
        gs["pending_save_name"] = None
        gs["log"] = []
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif gs["screen"] == "load_menu":
        return load_action(choice)
    elif gs["screen"] == "quest_hub":
        return quest_hub_action(choice)
    elif gs["screen"] == "quest_npc":
        return quest_npc_action(gs.get("quest_npc_index", 0), choice)
    # Handle location travel
    elif gs["screen"] == "location":
        gs["screen"] = "town"
        gs["log"] = []
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif gs["screen"] == "dungeon":
        if choice == 0:
            return enter_dungeon()
        gs["screen"] = "town"
        gs["log"] = []
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif gs["screen"] == "dungeon_floor":
        return dungeon_floor_action(choice)
    elif gs["screen"] == "dungeon_victory":
        gs["dungeon_floor"] = 0
        gs["current_location"] = "village1"
        gs["screen"] = "town"
        gs["log"] = ["You return to Village 1, victorious!"]
        return respond("town", "Village 1", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif gs["screen"] == "game_over":
        gs["player"] = None
        gs["enemy"] = None
        gs["dungeon_floor"] = 0
        gs["screen"] = "main_menu"
        gs["log"] = []
        return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game"])

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
    return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

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
    return respond("town", "Saved!", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

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
        gs["screen"] = "shop_select"
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

    elif choice == 4:  # Quests
        return quest_hub_state()

    elif choice == 5:  # Quit
        gs["player"] = None
        gs["enemy"] = None
        gs["screen"] = "main_menu"
        gs["log"] = []
        return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game"])

    return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

#==============================
# ---- Combat ----
#=============================
def combat_state():
    e = gs["enemy"]
    p = gs["player"]
    body = f"{e.display()}\n\n{player_json(p)['name']}: HP {p.hp}/{p.max_hp}  AC {p.ac}"
    if gs["dungeon_floor"] > 0:
        return respond("combat", "COMBAT", body, ["Attack", "Use Item"])
    return respond("combat", "COMBAT", body, ["Attack", "Use Item", "Flee"])

def combat_action(choice):
    p = gs["player"]
    e = gs["enemy"]

    # Attack
    if choice == 0:  
        # The combat log accumulates: every exchange stays visible in the chat.
        result = web_player_attack(p, e)
        gs["log"].append(result)

        if not e.is_alive():
            return combat_reward("Victory!")

        result2 = web_enemy_attack(p, e)
        gs["log"].append(result2)

        if not p.is_alive():
            gs["screen"] = "game_over"
            return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"])

        return combat_state()
    
    # Use Item
    elif choice == 1:  
        consumables = [item for item in p.inventory if item.category == "item" and item != p.weapon and item != p.armor and item != p.shield]
        if not consumables:
            gs["log"].append("No potions to use!")
            return combat_state()

        grouped = {}
        for item in consumables:
            grouped.setdefault(item.name, []).append(item)
        names = list(grouped.keys())
        options = [f"{n} x{len(grouped[n])}" if len(grouped[n]) > 1 else n for n in names] + ["(Back)"]
        gs["screen"] = "combat_item"
        return respond("combat_item", "Use Item", "Choose an item:", options)

    # Flee (not allowed in dungeon)
    elif choice == 2:
        if gs["dungeon_floor"] > 0:
            gs["log"].append("You cannot flee from the dungeon!")
            return combat_state()
        if roll("1d20") >= 10:
            gs["enemy"] = None
            gs["screen"] = "town"
            gs["log"] = ["You fled successfully!"]
            return respond("town", "Fled!", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
        else:
            gs["log"].append("Failed to flee!")
            result2 = web_enemy_attack(p, e)
            gs["log"].append(result2)
            if not p.is_alive():
                gs["screen"] = "game_over"
                return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"])
            return combat_state()

    return combat_state()

# Use Item
def combat_item_action(choice):
    p = gs["player"]
    e = gs["enemy"]
    consumables = [item for item in p.inventory if item.category == "item" and item != p.weapon and item != p.armor and item != p.shield]
    grouped = {}
    for item in consumables:
        grouped.setdefault(item.name, []).append(item)
    names = list(grouped.keys())

    if choice >= len(names):
        gs["screen"] = "combat"
        return combat_state()

    item = grouped[names[choice]][0]
    if item.name == "Healing Potion":
        heal = 9
        p.hp = min(p.hp + heal, p.max_hp)
        p.remove_item(item)
        gs["log"].append(f"Drank Healing Potion! Restored {heal} HP.")
    elif item.name == "Greater Healing Potion":
        heal = 20
        p.hp = min(p.hp + heal, p.max_hp)
        p.remove_item(item)
        gs["log"].append(f"Drank Greater Healing Potion! Restored {heal} HP.")
    else:
        gs["log"].append(f"Cannot use {item.name} in combat yet.")

        result2 = web_enemy_attack(p, e)
        gs["log"].append(result2)

        if not p.is_alive():
            gs["screen"] = "game_over"
            return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"])

        gs["screen"] = "combat"
        return combat_state()

    gs["screen"] = "combat"
    return combat_state()

# Player Attack
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

# Enemy Attack
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

# Combat Reward
def combat_reward(title):
    p = gs["player"]
    e = gs["enemy"]
    gold = e.gold_drop()
    xp = e.xp_reward
    p.add_gold(gold)
    gs["log"] = [f"{e.name} defeated!", f"Looted {gold} gold!", f"Gained {xp} XP!"]

    if gs["dungeon_floor"] == 10:
        bonus_gold = 500
        bonus_xp = 500
        p.add_gold(bonus_gold)
        xp += bonus_xp
        gs["log"].append(f"Dungeon cleared! Bonus: {bonus_gold} gold, {bonus_xp} XP!")

    # Quest materials from the kill (bosses drop nothing yet).
    drop = e.roll_drop()
    if drop:
        material, count = drop
        for _ in range(count):
            p.add_item(create_item(material))
        gs["log"].append(f"Collected {count} × {material}!")

    grant_xp(p, xp)

    gs["enemy"] = None
    if p.skill_points > 0:
        return allocation_state()
    return after_combat()

# Add XP and run any level-ups it triggers.
def grant_xp(p, xp):
    p.xp += xp
    while p.xp >= p.xp_to_next():
        p.xp -= p.xp_to_next()
        handle_level_up()

# Level up handling
def handle_level_up():
    p = gs["player"]
    p.level += 1
    hp_gain = p.hp_per_level()
    p.max_hp += hp_gain
    p.hp = p.max_hp
    gold_r = p.level * 10
    p.add_gold(gold_r)
    gs["log"].append(f"LEVEL UP! Now level {p.level}! HP +{hp_gain}, +{gold_r} gold!")

    if p.level % 4 == 0:
        p.skill_points += 5
    else:
        p.skill_points += 1

# Stat Allocation
def allocation_state():
    p = gs["player"]
    body_lines = [f"{s}: {p.stats[s]}" for s in STAT_ORDER]
    return respond("stat_allocation", f"Allocate Skill Points ({p.skill_points} left)", "\n".join(body_lines), [f"[+] {s}" for s in STAT_ORDER])

def allocation_action(choice):
    p = gs["player"]
    if p.skill_points <= 0:
        return after_combat()
    chosen = STAT_ORDER[choice]
    old_con = p.modifier("CON")
    p.stats[chosen] += 1
    p.ac = p.calc_ac()
    if chosen == "CON":
        p.recalc_hp()
        # A CON point raises max HP and heals the character to full.
        p.hp = p.max_hp
    p.skill_points -= 1
    gs["log"] = [f"{chosen} increased to {p.stats[chosen]}!"]

    if p.skill_points <= 0:
        if p.current_save:
            save_game(p, p.current_save)
            gs["log"].append("Game autosaved!")
        return after_combat()
    return allocation_state()

#==============================
# ---- Quests (Town only) ----
#==============================
# Three repeatable quest givers live in Town. Accept a job, kill what they want,
# then bring the material back to the same NPC to collect gold and XP.

def _count_material(p, material):
    return sum(1 for item in p.inventory if item.name == material)

def _take_material(p, material, amount):
    taken = 0
    for item in list(p.inventory):
        if item.name == material and taken < amount:
            p.remove_item(item)
            taken += 1
    return taken

def quest_hub_state():
    p = gs["player"]
    if not p:
        return get_state()
    npcs = gs["quest_npcs"]
    options = []
    body = []
    for i, npc in enumerate(npcs):
        ready = 0
        for q in quests_for(i):
            key = f"{i}:{q['index']}"
            if gs["quest_accepted"].get(key) and _count_material(p, q["material"]) >= q["amount"]:
                ready += 1
        mark = f" — {ready} ready to hand in!" if ready else ""
        options.append(f"{npc['name']}{mark}")
        body.append(f"{npc['name']}: {len(quests_for(i))} standing job(s)")
    options.append("(Back)")
    return respond("quest_hub", "Quest Givers", "\n".join(body), options)

def quest_hub_action(choice):
    npcs = gs["quest_npcs"]
    if choice >= len(npcs):
        gs["return_to"] = None  # back to the town menu
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    gs["return_to"] = "quest_npc"
    gs["quest_npc_index"] = choice
    return quest_npc_state(choice)

def quest_npc_state(npc_index):
    p = gs["player"]
    if not p:
        return get_state()
    npcs = gs["quest_npcs"]
    if npc_index >= len(npcs):
        return quest_hub_state()
    gs["quest_npc_index"] = npc_index
    quests = quests_for(npc_index)
    options = []
    body = []
    for q in quests:
        key = f"{npc_index}:{q['index']}"
        have = _count_material(p, q["material"])
        accepted = gs["quest_accepted"].get(key, False)
        done = gs["quest_done"].get(key, 0)
        times = f" (handed in {done}×)" if done else ""
        body.append(f"{q['material']} ×{q['amount']}  →  {q['gold']}g, {q['xp']} XP{times}")
        if not accepted:
            options.append(f"[Accept] {q['material']} ×{q['amount']}")
        elif have >= q["amount"]:
            options.append(f"[Turn in] {q['material']} ×{q['amount']} (you have {have})")
        else:
            options.append(f"[Waiting] {q['material']} ×{q['amount']} — you have {have}")
    options.append("(Back)")
    return respond("quest_npc", npcs[npc_index]["name"], "\n".join(body), options,
                   extra={"quest_npc_index": npc_index})

def quest_npc_action(npc_index, choice):
    p = gs["player"]
    if not p:
        return get_state()
    quests = quests_for(npc_index)
    if choice >= len(quests):
        return quest_hub_state()
    q = quests[choice]
    key = f"{npc_index}:{q['index']}"

    if not gs["quest_accepted"].get(key):
        gs["quest_accepted"][key] = True
        gs["log"] = [f"You accepted: {q['material']} ×{q['amount']}"]
        return quest_npc_state(npc_index)

    have = _count_material(p, q["material"])
    if have < q["amount"]:
        gs["log"] = [f"You need {q['amount']} × {q['material']} (you have {have})."]
        return quest_npc_state(npc_index)

    _take_material(p, q["material"], q["amount"])
    p.add_gold(q["gold"])
    gs["quest_done"][key] = gs["quest_done"].get(key, 0) + 1
    gs["log"] = [
        f"Quest complete: {q['material']} ×{q['amount']}!",
        f"Paid {q['gold']} gold and {q['xp']} XP.",
    ]
    grant_xp(p, q["xp"])
    if p.skill_points > 0:
        return allocation_state()
    return quest_npc_state(npc_index)

#==============================
# ---- Shop ----
#==============================
from shop import SHOP_NPCS

# Shop State
def shop_state():
    loc_id = gs["current_location"] # Get the current location ID from the game state
    loc = LOCATIONS.get(loc_id, {}) # Get the current location data from LOCATIONS
    # Get the list of shops available at the current location, 
    # defaulting to all shops if none are specified
    shop_names = loc.get("shops", list(SHOP_NPCS.keys())) 
    # If there are no shops available at the current location, 
    # set the log message and return to the town screen
    if not shop_names: 
        gs["log"] = ["No shops here."]
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    return respond("shop_select", "Which shop?", "", shop_names + ["(Back)"])

# Shop Select Action
def shop_select_action(choice):
    loc_id = gs["current_location"]
    loc = LOCATIONS.get(loc_id, {})
    shop_names = loc.get("shops", list(SHOP_NPCS.keys()))
    # If the choice is out of bounds (e.g., "(Back)" option), return to town
    if choice >= len(shop_names): 
        gs["screen"] = "town"
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

    # If a valid shop is selected, set the current shop in the game state and show the shop interface
    shop_name = shop_names[choice]
    gs["shop_name"] = shop_name
    return show_shop(shop_name)

def shop_action(choice):
    if gs["dungeon_floor"] > 0:
        gs["screen"] = "dungeon_floor"
        return dungeon_floor_state()
    loc_id = gs["current_location"]
    loc = LOCATIONS.get(loc_id, {})
    shop_names = loc.get("shops", list(SHOP_NPCS.keys()))
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

    # Guard: a shop can list an item that items.py does not define (the two
    # catalogues can drift). Without this, create_item() returns None, None lands
    # in the inventory and the next inventory/shop render raises.
    if not get_item(item_name):
        gs["log"] = ["That item is not available."]
        return show_shop(shop_name)

    price = shop["items"][item_name]["price"]
    total = price * qty
    if p.spend_gold(total):
        for _ in range(qty):
            p.add_item(create_item(item_name))
        gs["log"] = [f"Bought {qty} × {item_name} for {total}g!"]
    else:
        gs["log"] = [f"Not enough gold! Need {total}g, you have {p.gold}g."]

    return show_shop(shop_name)

@app.route("/sell", methods=["POST"])
def sell_item():
    """Sell one item to the NPC you are standing at, at 20% under shop price."""
    p = gs["player"]
    if not p:
        return get_state()
    data = request.json
    item_name = data.get("item")
    price = sell_price(item_name)
    if not price:
        gs["log"] = ["Nobody wants to buy that."]
        return show_shop(gs.get("shop_name") or next(iter(SHOP_NPCS)))

    index = next((i for i, item in enumerate(p.inventory) if item.name == item_name), None)
    if index is not None:
        item = p.inventory.pop(index)
    elif p.weapon and p.weapon.name == item_name:
        item, p.weapon = p.weapon, None
    elif p.armor and p.armor.name == item_name:
        item, p.armor = p.armor, None
    elif p.shield and p.shield.name == item_name:
        item, p.shield = p.shield, None
    else:
        gs["log"] = ["You don't have that any more."]
        return show_shop(gs.get("shop_name") or next(iter(SHOP_NPCS)))

    # Selling equipped gear leaves you unequipped until you equip something else.
    if item is p.weapon or item is p.armor or item is p.shield:
        p.ac = p.calc_ac()
        p.recalc_hp()

    p.add_gold(price)
    gs["log"] = [f"Sold {item.name} for {price}g."]
    return show_shop(gs.get("shop_name") or next(iter(SHOP_NPCS)))

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
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

    item = grouped[names[choice]][0]

    if item.category == "weapon":
        if p.weapon:
            p.inventory.append(p.weapon)
        p.weapon = item
        p.remove_item(item)
        p.ac = p.calc_ac()
        p.recalc_hp()
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
        p.recalc_hp()
        gs["log"] = [f"Equipped {item.name}!"]
    elif item.category == "item":
        if item.name == "Healing Potion":
            heal = 9
            p.hp = min(p.hp + heal, p.max_hp)
            p.remove_item(item)
            gs["log"] = [f"Drank Healing Potion! Restored {heal} HP."]
        elif item.name == "Greater Healing Potion":
            heal = 20
            p.hp = min(p.hp + heal, p.max_hp)
            p.remove_item(item)
            gs["log"] = [f"Drank Greater Healing Potion! Restored {heal} HP."]
        else:
            gs["log"] = [f"Cannot use {item.name} yet."]

    return inventory_state()

# ---- Load Game ----
@app.route("/load_list")
def load_list():
    saves = list_saves()
    gs["screen"] = "load_menu"
    if not saves:
        return respond("main_menu", "No saves found", "", ["New Game", "Load Game"])
    options = [f"{s[1]} {s[2]} {s[3]} Lv.{s[4]}" for s in saves]
    return respond("load_menu", "Load Game", "", options + ["(Back)"])

def load_action(choice):
    saves = list_saves()
    if choice >= len(saves):
        gs["screen"] = "main_menu"
        gs["log"] = []
        return respond("main_menu", "DUNGEONS & DRAGONS", "", ["New Game", "Load Game"])

    name = saves[choice][0]
    player = load_game(name)
    reset_run()
    player.current_save = name
    gs["player"] = player
    gs["enemy"] = None
    gs["screen"] = "town"
    gs["current_location"] = "town"
    gs["log"] = [f"Loaded '{name}'!"]
    return respond("town", "Game Loaded!", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

#================================
# ---- Map ----
#================================
# This section handles the world map data and travel between locations. 
# The locations and their connections are defined in world_map.py.
@app.route("/map_data")
def map_data():
    current_id = gs["current_location"]
    return jsonify({
        "locations": {k: {"name": v["name"], "x": v["x"], "y": v["y"], "type": v["type"], "connects_to": v["connects_to"]} for k, v in LOCATIONS.items()},
        "current_location": current_id,
    })

# travel endpoint to move between locations
# The travel endpoint checks if the player can move to the target location 
# based on the current location and the connections defined in LOCATIONS. 
# It updates the game state accordingly and responds with the new location's information.

@app.route("/travel", methods=["POST"])
def travel():
    p = gs["player"]
    if not p:
        return get_state()
    data = request.json
    target_id = data.get("location")
    current_id = gs["current_location"] or "town"
    if target_id == current_id:
        gs["log"] = ["You are already here."]
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    current = LOCATIONS.get(current_id)
    if not current or target_id not in current["connects_to"]:
        gs["log"] = ["You can't reach that location from here."]
        return respond("town", town_name(), "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    target = LOCATIONS.get(target_id)
    if not target:
        return get_state()
    gs["current_location"] = target_id
    gs["log"] = [f"You arrive at {target['name']}."]
    if target["type"] in ("town", "village"):
        gs["screen"] = "town"
        return respond("town", target["name"], "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])
    elif target["type"] == "dungeon":
        gs["screen"] = "dungeon"
        return respond("dungeon", target["name"], "The entrance looms before you...", ["Enter", "(Back)"])
    else:
        gs["screen"] = "location"
        return respond("location", target["name"], "Nothing to do here yet.", ["(Back)"])

#================================
# ---- Dungeon ----
#================================

# Dungeon logic is handled here, 
# including entering the dungeon, progressing through floors, 
# and handling combat and rewards.
def enter_dungeon():
    gs["dungeon_floor"] = 1
    e = generate_dungeon_enemy(1, gs["player"].level)
    gs["enemy"] = e
    gs["log"] = ["You descend into the dungeon... Floor 1"]
    return dungeon_floor_state()

# Handle the state for each dungeon floor
def dungeon_floor_state():
    p = gs["player"]
    title = f"Dungeon - Floor {gs['dungeon_floor']}/10"
    e = gs["enemy"]
    if e and e.is_alive():
        body = f"{e.display()}\n\n{p.name}: HP {p.hp}/{p.max_hp}  AC {p.ac}"
        return respond("dungeon_floor", title, body, ["Attack"])
    else:
        body = "Floor cleared!"
        floor = gs["dungeon_floor"]
        if floor == 5:
            return respond("dungeon_floor", title, body, ["Visit Merchant", "Descend to Floor 6"])
        elif floor == 10:
            return respond("dungeon_floor", title, body, ["Visit Merchant", "Attack Boss"])
        else:
            return respond("dungeon_floor", title, body, [f"Descend to Floor {floor + 1}"])

# Handle actions on the dungeon floor, 
# including combat and merchant visits
def dungeon_floor_action(choice):
    e = gs["enemy"]
    floor = gs["dungeon_floor"]

    if e and e.is_alive():
        gs["screen"] = "combat"
        gs["log"] = []
        return combat_state()

    if floor == 5:
        if choice == 0:
            return dungeon_merchant()
        else:
            return advance_dungeon_floor()

    if floor == 10:
        if choice == 0:
            return dungeon_merchant()
        else:
            gs["screen"] = "combat"
            gs["log"] = ["The boss stands before you!"]
            return combat_state()

    return advance_dungeon_floor()

# Advance to the next dungeon floor, generating a new enemy
def advance_dungeon_floor():
    gs["dungeon_floor"] += 1
    floor = gs["dungeon_floor"]
    e = generate_dungeon_enemy(floor, gs["player"].level)
    gs["enemy"] = e
    gs["log"] = [f"You descend to Floor {floor}"]
    return dungeon_floor_state()

# After all combat/level-up/allocation is done, continue the game
def after_combat():
    # Quests put you back in front of the NPC you were talking to instead of
    # dropping you in the middle of Town.
    if gs.get("return_to") == "quest_npc":
        return quest_npc_state(gs.get("quest_npc_index", 0))
    if gs.get("return_to") == "quest_hub":
        return quest_hub_state()

    if gs["dungeon_floor"] > 0:
        if gs["dungeon_floor"] == 10:
            return respond("dungeon_victory", "DUNGEON CLEARED!", "You defeated the boss and conquered the dungeon!", ["Return to Village 1"])
        return dungeon_floor_state()
    gs["screen"] = "town"
    return respond("town", "Victory!", "What do you want to do?", ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"])

# Dungeon Merchant
def dungeon_merchant():
    gs["shop_name"] = "Potion Merchant"
    shop = SHOP_NPCS["Potion Merchant"]
    available = {n: d for n, d in shop["items"].items() if gs["player"].level >= d["min_level"]}
    items_list = [f"{n} ({d['price']}g)" for n, d in available.items()]
    gs["screen"] = "shop"
    return respond("shop", "Dungeon Merchant", "", items_list + ["(Back)"], extra={"shop_items": list(available.keys()), "shop_prices": [d["price"] for d in available.values()], "dungeon_shop": True})

if __name__ == "__main__":
    app.run(debug=True)