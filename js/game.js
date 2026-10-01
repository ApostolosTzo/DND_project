// game_server.py - The whole game state machine, ported to run in the browser.
//
// Every function returns the same plain object the Flask version returned as
// JSON, so the UI can render it directly. Game state lives in `gs`.

const gs = {
    player: null,
    enemy: null,
    screen: "main_menu",
    log: [],
    pending_save_name: null,
    current_location: null,
    dungeon_floor: 0,
    shop_name: null
};

const TOWN_OPTIONS = ["Fight", "Visit Shop", "Inventory", "Save Game", "Quit"];
// No "Quit" on the main menu: it never did anything, and everything else in
// the game is reachable from the town screen's Quit option.
const MENU_OPTIONS = ["New Game", "Load Game"];

// -----------------------------
// Response helpers
// -----------------------------

function playerJson(p) {
    if (!p) return null;
    return {
        name: p.name,
        race: p.race,
        "class": p.class_name,
        level: p.level,
        hp: p.hp,
        max_hp: p.max_hp,
        ac: p.ac,
        gold: p.gold,
        xp: p.xp,
        xp_to_next: p.xp_to_next(),
        weapon: p.weapon ? p.weapon.name : "None",
        armor: p.armor ? p.armor.name : "None",
        stats: Object.assign({}, p.stats),
        effective_stats: p.effective_stats(),
        stat_bonuses: p.get_equipment_stat_bonus()
    };
}

function townName() {
    const loc = LOCATIONS[gs.current_location];
    return loc ? loc.name : "Town";
}

// Every response syncs the server-side screen with the one the client shows.
function enemyJson(e) {
    if (!e) return null;
    return {
        name: e.name,
        level: e.level,
        hp: e.hp,
        max_hp: e.max_hp,
        ac: e.ac
    };
}

function respond(screen, title, body, options, extra) {
    gs.screen = screen;
    const out = {
        screen: screen,
        title: title,
        body: body,
        options: options,
        player: playerJson(gs.player),
        enemy: enemyJson(gs.enemy),
        in_dungeon: gs.dungeon_floor > 0,
        log: gs.log,
        current_location: gs.current_location
    };
    if (extra) {
        for (const key in extra) out[key] = extra[key];
    }
    return out;
}

function townRespond(title, body, log) {
    if (log !== undefined) gs.log = log;
    return respond("town", title, body, TOWN_OPTIONS);
}

function menuRespond() {
    return respond("main_menu", "DUNGEONS & DRAGONS", "", MENU_OPTIONS);
}

function getState() {
    gs.log = [];
    return menuRespond();
}

// Data for the character creation form.
function createForm() {
    return createFormData();
}

// -----------------------------
// Entry points
// -----------------------------

function startGame(data) {
    const name = (data && data.name) || "Adventurer";
    const race = (data && data.race) || "Human";
    const class_name = (data && data["class"]) || "Fighter";

    gs.player = makeCharacter(name, race, class_name);
    gs.enemy = null;
    gs.current_location = "town";
    gs.log = ["Welcome, adventurer!"];
    return townRespond(townName(), "What do you want to do?", gs.log);
}

// Routes a click on a menu option to the handler for the current screen.
function handleAction(choice) {
    switch (gs.screen) {
        case "town": return townAction(choice);
        case "combat": return combatAction(choice);
        case "combat_item": return combatItemAction(choice);
        case "shop_select": return shopSelectAction(choice);
        case "shop": return shopAction(choice);
        case "inventory": return inventoryAction(choice);
        case "stat_allocation": return allocationAction(choice);
        case "save_menu":
            gs.log = [];
            return townRespond(townName(), "What do you want to do?", []);
        case "confirm_overwrite":
            if (choice === 0) return forceSave();
            gs.pending_save_name = null;
            gs.log = [];
            return townRespond(townName(), "What do you want to do?", []);
        case "load_menu": return loadAction(choice);
        case "location":
            gs.log = [];
            return townRespond(townName(), "What do you want to do?", []);
        case "dungeon":
            if (choice === 0) return enterDungeon();
            gs.log = [];
            return townRespond(townName(), "What do you want to do?", []);
        case "dungeon_floor": return dungeonFloorAction(choice);
        case "dungeon_victory":
            gs.dungeon_floor = 0;
            gs.current_location = "village1";
            gs.log = ["You return to Village 1, victorious!"];
            return respond("town", "Village 1", "What do you want to do?", TOWN_OPTIONS);
        case "game_over":
            gs.player = null;
            gs.enemy = null;
            gs.dungeon_floor = 0;
            gs.log = [];
            return menuRespond();
    }
    return getState();
}

// -----------------------------
// Save / load
// -----------------------------

function save(name) {
    const p = gs.player;
    if (!p) return getState();
    if (name === undefined || name === null) name = p.name;

    if (saveExists(name)) {
        gs.pending_save_name = name;
        gs.log = ["Save '" + name + "' already exists. Overwrite?"];
        return respond("confirm_overwrite", "Overwrite Save?",
            "Save '" + name + "' already exists. Overwrite?", ["Yes", "No"]);
    }
    saveGame(p, name);
    p.current_save = name;
    gs.log = ["Game saved as '" + name + "'!"];
    return townRespond(townName(), "What do you want to do?", gs.log);
}

function forceSave() {
    const p = gs.player;
    if (!p || !gs.pending_save_name) return getState();
    const name = gs.pending_save_name;
    gs.pending_save_name = null;
    saveGame(p, name);
    p.current_save = name;
    gs.log = ["Game saved as '" + name + "'!"];
    return respond("town", "Saved!", "What do you want to do?", TOWN_OPTIONS);
}

function loadList() {
    const saves = listSaves();
    gs.screen = "load_menu";
    if (!saves.length) {
        return respond("main_menu", "No saves found", "", MENU_OPTIONS);
    }
    const options = saves.map((s) => s[1] + " " + s[2] + " " + s[3] + " Lv." + s[4]);
    return respond("load_menu", "Load Game", "", options.concat(["(Back)"]));
}

function loadAction(choice) {
    const saves = listSaves();
    if (choice >= saves.length) {
        gs.log = [];
        return menuRespond();
    }
    const name = saves[choice][0];
    const player = loadGame(name);
    if (!player) {
        gs.log = ["Could not load '" + name + "'."];
        return menuRespond();
    }
    player.current_save = name;
    gs.player = player;
    gs.enemy = null;
    gs.current_location = "town";
    gs.log = ["Loaded '" + name + "'!"];
    return respond("town", "Game Loaded!", "What do you want to do?", TOWN_OPTIONS);
}

// -----------------------------
// Town
// -----------------------------

function townAction(choice) {
    const p = gs.player;
    if (!p) return getState();

    if (choice === 0) { // Fight
        const e = generateEnemy(p.level);
        gs.enemy = e;
        gs.log = ["A wild " + e.name + " appears!"];
        return combatState();

    } else if (choice === 1) { // Shop
        gs.log = [];
        return shopState();

    } else if (choice === 2) { // Inventory
        gs.log = [];
        return inventoryState();

    } else if (choice === 3) { // Save
        const default_name = p.current_save || p.name;
        return respond("save_menu", "Save Game", "",
            ["Save as '" + default_name + "'", "(Back)"]);

    } else if (choice === 4) { // Quit
        gs.player = null;
        gs.enemy = null;
        gs.log = [];
        return menuRespond();
    }

    return townRespond(townName(), "What do you want to do?");
}

// -----------------------------
// Combat
// -----------------------------

function combatState() {
    const e = gs.enemy;
    const p = gs.player;
    const body = e.display() + "\n\n" + p.name + ": HP " + p.hp + "/" + p.max_hp + "  AC " + p.ac;
    if (gs.dungeon_floor > 0) {
        return respond("combat", "COMBAT", body, ["Attack", "Use Item"]);
    }
    return respond("combat", "COMBAT", body, ["Attack", "Use Item", "Flee"]);
}

function combatAction(choice) {
    const p = gs.player;
    const e = gs.enemy;

    // Attack
    if (choice === 0) {
        // The combat log accumulates: every exchange stays visible in the chat.
        gs.log.push(webPlayerAttack(p, e));

        if (!e.is_alive()) return combatReward("Victory!");

        gs.log.push(webEnemyAttack(p, e));

        if (!p.is_alive()) {
            return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"]);
        }

        return combatState();
    }

    // Use Item
    if (choice === 1) {
        const grouped = groupConsumables(p);
        const names = Object.keys(grouped);
        if (!names.length) {
            gs.log = ["No potions to use!"];
            return combatState();
        }
        const options = names.map((n) =>
            (grouped[n].length > 1 ? n + " x" + grouped[n].length : n)).concat(["(Back)"]);
        return respond("combat_item", "Use Item", "Choose an item:", options);
    }

    // Flee (not allowed in the dungeon)
    if (choice === 2) {
        if (gs.dungeon_floor > 0) {
            gs.log = ["You cannot flee from the dungeon!"];
            return combatState();
        }
        if (roll("1d20") >= 10) {
            gs.enemy = null;
            gs.log = ["You fled successfully!"];
            return townRespond("Fled!", "What do you want to do?", gs.log);
        }
        gs.log.push("Failed to flee!");
        gs.log.push(webEnemyAttack(p, e));
        if (!p.is_alive()) {
            return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"]);
        }
        return combatState();
    }

    return combatState();
}

// Consumables in the inventory, grouped by name (equipped items excluded).
function groupConsumables(p) {
    const grouped = {};
    p.inventory.forEach((item) => {
        if (item.category === "item" && item !== p.weapon && item !== p.armor && item !== p.shield) {
            (grouped[item.name] = grouped[item.name] || []).push(item);
        }
    });
    return grouped;
}

function combatItemAction(choice) {
    const p = gs.player;
    const e = gs.enemy;
    const grouped = groupConsumables(p);
    const names = Object.keys(grouped);

    if (choice >= names.length) {
        return combatState();
    }

    const item = grouped[names[choice]][0];
    if (item.name === "Healing Potion") {
        const heal = 9;
        p.hp = Math.min(p.hp + heal, p.max_hp);
        p.remove_item(item);
        gs.log.push("Drank Healing Potion! Restored " + heal + " HP.");
    } else if (item.name === "Greater Healing Potion") {
        const heal = 20;
        p.hp = Math.min(p.hp + heal, p.max_hp);
        p.remove_item(item);
        gs.log.push("Drank Greater Healing Potion! Restored " + heal + " HP.");
    } else {
        gs.log.push("Cannot use " + item.name + " in combat yet.");

        gs.log.push(webEnemyAttack(p, e));

        if (!p.is_alive()) {
            return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"]);
        }
        return combatState();
    }

    return combatState();
}

function webPlayerAttack(p, e) {
    let mod;
    if (p.weapon && p.weapon.properties.indexOf("finesse") !== -1) {
        mod = p.modifier("DEX");
    } else if (p.weapon && p.weapon.properties.indexOf("ranged") !== -1) {
        mod = p.modifier("DEX");
    } else {
        mod = p.modifier("STR");
    }

    const prof = Math.floor((p.level - 1) / 4) + 2;
    const atk = roll("1d20") + prof + mod;

    if (atk >= e.ac) {
        let dmg;
        if (p.weapon) {
            dmg = Math.max(roll(p.weapon.damage_dice) + mod, 1);
        } else {
            dmg = Math.max(1 + mod, 1);
        }
        e.take_damage(dmg);
        return "You hit the " + e.name + " for " + dmg + " damage! (d20 + " + prof +
            " + " + mod + " = " + atk + " vs AC " + e.ac + ")";
    }
    return "You missed! (d20 + " + prof + " + " + mod + " = " + atk + " vs AC " + e.ac + ")";
}

function webEnemyAttack(p, e) {
    const bonus = Math.floor(e.level / 2) + 2;
    const atk = roll("1d20") + bonus;

    if (atk >= p.ac) {
        const dmg = Math.max(e.attack_damage(), 1);
        p.hp -= dmg;
        if (p.hp < 0) p.hp = 0;
        return e.name + " hits you for " + dmg + " damage! (d20 + " + bonus +
            " = " + atk + " vs your AC " + p.ac + ")";
    }
    return e.name + " missed you! (d20 + " + bonus + " = " + atk + " vs your AC " + p.ac + ")";
}

function combatReward(title) {
    const p = gs.player;
    const e = gs.enemy;
    const gold = e.gold_drop();
    let xp = e.xp_reward;
    p.add_gold(gold);
    gs.log = [e.name + " defeated!", "Looted " + gold + " gold!", "Gained " + xp + " XP!"];

    if (gs.dungeon_floor === 10) {
        const bonus_gold = 500;
        const bonus_xp = 500;
        p.add_gold(bonus_gold);
        xp += bonus_xp;
        gs.log.push("Dungeon cleared! Bonus: " + bonus_gold + " gold, " + bonus_xp + " XP!");
    }

    p.xp += xp;
    while (p.xp >= p.xp_to_next()) {
        p.xp -= p.xp_to_next();
        handleLevelUp();
    }

    gs.enemy = null;
    if (p.skill_points > 0) return allocationState();
    return afterCombat();
}

function handleLevelUp() {
    const p = gs.player;
    p.level += 1;
    const hp_gain = p.hp_per_level();
    p.max_hp += hp_gain;
    p.hp = p.max_hp;
    const gold_r = p.level * 10;
    p.add_gold(gold_r);
    gs.log.push("LEVEL UP! Now level " + p.level + "! HP +" + hp_gain + ", +" + gold_r + " gold!");

    if (p.level % 4 === 0) {
        p.skill_points += 5;
    } else {
        p.skill_points += 1;
    }
}

// -----------------------------
// Skill point allocation
// -----------------------------

function allocationState() {
    const p = gs.player;
    const body_lines = STAT_ORDER.map((s) => s + ": " + p.stats[s]);
    return respond("stat_allocation",
        "Allocate Skill Points (" + p.skill_points + " left)",
        body_lines.join("\n"),
        STAT_ORDER.map((s) => "[+] " + s));
}

function allocationAction(choice) {
    const p = gs.player;
    if (p.skill_points <= 0) return afterCombat();

    const chosen = STAT_ORDER[choice];
    p.stats[chosen] += 1;
    p.ac = p.calc_ac();
    if (chosen === "CON") {
        p.recalc_hp();
        // A CON point raises max HP and heals the character to full.
        p.hp = p.max_hp;
    }
    p.skill_points -= 1;
    gs.log = [chosen + " increased to " + p.stats[chosen] + "!"];

    if (p.skill_points <= 0) {
        if (p.current_save) {
            saveGame(p, p.current_save);
            gs.log.push("Game autosaved!");
        }
        return afterCombat();
    }
    return allocationState();
}

// -----------------------------
// Shop
// -----------------------------

// Python: loc.get("shops", list(SHOP_NPCS.keys())) - the default only applies
// when the key is missing, so an explicitly empty list still means "no shops".
function locationShops() {
    const loc = LOCATIONS[gs.current_location];
    if (!loc || !Object.prototype.hasOwnProperty.call(loc, "shops")) {
        return Object.keys(SHOP_NPCS);
    }
    return loc.shops;
}

function shopState() {
    const shop_names = locationShops();
    if (!shop_names.length) {
        return townRespond(townName(), "What do you want to do?", ["No shops here."]);
    }
    gs.log = [];
    return respond("shop_select", "Which shop?", "", shop_names.concat(["(Back)"]));
}

function shopSelectAction(choice) {
    const shop_names = locationShops();
    if (choice >= shop_names.length) {
        return townRespond(townName(), "What do you want to do?");
    }
    const shop_name = shop_names[choice];
    gs.shop_name = shop_name;
    return showShop(shop_name);
}

function shopAction(choice) {
    if (gs.dungeon_floor > 0) {
        return dungeonFloorState();
    }
    return respond("shop_select", "Which shop?", "", locationShops().concat(["(Back)"]));
}

function shopBuy(item, qty) {
    const p = gs.player;
    const shop = SHOP_NPCS[gs.shop_name];
    if (!shop || !shop.items.hasOwnProperty(item)) {
        return showShop(gs.shop_name);
    }

    const price = shop.items[item].price;
    const total = price * qty;
    if (p.spend_gold(total)) {
        for (let i = 0; i < qty; i++) p.add_item(createItem(item));
        gs.log = ["Bought " + qty + " " + item + "(s) for " + total + "g!"];
    } else {
        gs.log = ["Not enough gold! Need " + total + "g, you have " + p.gold + "g."];
    }

    return showShop(gs.shop_name);
}

function showShop(shop_name) {
    const p = gs.player;
    const shop = SHOP_NPCS[shop_name];
    const available = {};
    Object.keys(shop.items).forEach((n) => {
        if (p.level >= shop.items[n].min_level) available[n] = shop.items[n];
    });
    const items_list = Object.keys(available).map((n) => n + " (" + available[n].price + "g)");
    return respond("shop", shop_name, "", items_list.concat(["(Back)"]), {
        shop_items: Object.keys(available),
        shop_prices: Object.keys(available).map((n) => available[n].price)
    });
}

// -----------------------------
// Inventory
// -----------------------------

// Storage entries (equipped items excluded), grouped by name, in order.
function groupStorage(p) {
    const grouped = {};
    p.inventory.forEach((item) => {
        if (item !== p.weapon && item !== p.armor && item !== p.shield) {
            (grouped[item.name] = grouped[item.name] || []).push(item);
        }
    });
    return grouped;
}

function inventoryState() {
    const p = gs.player;
    const lines = [];
    if (p.weapon) lines.push("Weapon: " + p.weapon.name);
    if (p.armor) lines.push("Armor: " + p.armor.name);
    if (p.shield) lines.push("Shield: " + p.shield.name);

    const grouped = groupStorage(p);
    const storage_lines = Object.keys(grouped).map((name) => {
        const items_list = grouped[name];
        return items_list.length > 1 ? name + " x" + items_list.length : name;
    });

    const body = "Equipped:\n  " + (lines.length ? lines.join("\n  ") : "None") +
        "\n\nStorage:\n  " + (storage_lines.length ? storage_lines.join("\n  ") : "(empty)");

    const options = storage_lines.length
        ? storage_lines.map((n) => "[Use] " + n).concat(["(Close)"])
        : ["(Close)"];

    return respond("inventory", "INVENTORY", body, options, {
        inv_items: Object.keys(grouped)
    });
}

function inventoryAction(choice) {
    const p = gs.player;
    const grouped = groupStorage(p);
    const names = Object.keys(grouped);

    if (!names.length || choice >= names.length) {
        return townRespond(townName(), "What do you want to do?");
    }

    const item = grouped[names[choice]][0];

    if (item.category === "weapon") {
        if (p.weapon) p.inventory.push(p.weapon);
        p.weapon = item;
        p.remove_item(item);
        p.ac = p.calc_ac();
        p.recalc_hp();
        gs.log = ["Equipped " + item.name + "!"];
    } else if (item.category === "armor") {
        if (item.armor_type === "shield") {
            if (p.shield) p.inventory.push(p.shield);
            p.shield = item;
        } else {
            if (p.armor) p.inventory.push(p.armor);
            p.armor = item;
        }
        p.remove_item(item);
        p.ac = p.calc_ac();
        p.recalc_hp();
        gs.log = ["Equipped " + item.name + "!"];
    } else if (item.category === "item") {
        if (item.name === "Healing Potion") {
            const heal = 9;
            p.hp = Math.min(p.hp + heal, p.max_hp);
            p.remove_item(item);
            gs.log = ["Drank Healing Potion! Restored " + heal + " HP."];
        } else if (item.name === "Greater Healing Potion") {
            const heal = 20;
            p.hp = Math.min(p.hp + heal, p.max_hp);
            p.remove_item(item);
            gs.log = ["Drank Greater Healing Potion! Restored " + heal + " HP."];
        } else {
            gs.log = ["Cannot use " + item.name + " yet."];
        }
    }

    return inventoryState();
}

// -----------------------------
// World map
// -----------------------------

function mapData() {
    return {
        locations: LOCATIONS,
        current_location: gs.current_location
    };
}

function travel(target_id) {
    const p = gs.player;
    if (!p) return getState();

    const current_id = gs.current_location || "town";
    if (target_id === current_id) {
        return townRespond(townName(), "What do you want to do?", ["You are already here."]);
    }
    const current = LOCATIONS[current_id];
    if (!current || current.connects_to.indexOf(target_id) === -1) {
        return townRespond(townName(), "What do you want to do?", ["You can't reach that location from here."]);
    }
    const target = LOCATIONS[target_id];
    if (!target) return getState();

    gs.current_location = target_id;
    gs.log = ["You arrive at " + target.name + "."];

    if (target.type === "town" || target.type === "village") {
        return respond("town", target.name, "What do you want to do?", TOWN_OPTIONS);
    }
    if (target.type === "dungeon") {
        return respond("dungeon", target.name, "The entrance looms before you...", ["Enter", "(Back)"]);
    }
    return respond("location", target.name, "Nothing to do here yet.", ["(Back)"]);
}

// -----------------------------
// Dungeon
// -----------------------------

function enterDungeon() {
    gs.dungeon_floor = 1;
    gs.enemy = generateDungeonEnemy(1, gs.player.level);
    gs.log = ["You descend into the dungeon... Floor 1"];
    return dungeonFloorState();
}

function dungeonFloorState() {
    const p = gs.player;
    const title = "Dungeon - Floor " + gs.dungeon_floor + "/10";
    const e = gs.enemy;

    if (e && e.is_alive()) {
        const body = e.display() + "\n\n" + p.name + ": HP " + p.hp + "/" + p.max_hp + "  AC " + p.ac;
        return respond("dungeon_floor", title, body, ["Attack"]);
    }

    const body = "Floor cleared!";
    const floor = gs.dungeon_floor;
    if (floor === 5) {
        return respond("dungeon_floor", title, body, ["Visit Merchant", "Descend to Floor 6"]);
    }
    if (floor === 10) {
        return respond("dungeon_floor", title, body, ["Visit Merchant", "Attack Boss"]);
    }
    return respond("dungeon_floor", title, body, ["Descend to Floor " + (floor + 1)]);
}

function dungeonFloorAction(choice) {
    const e = gs.enemy;
    const floor = gs.dungeon_floor;

    if (e && e.is_alive()) {
        gs.log = [];
        return combatState();
    }

    if (floor === 5) {
        if (choice === 0) return dungeonMerchant();
        return advanceDungeonFloor();
    }

    if (floor === 10) {
        if (choice === 0) return dungeonMerchant();
        gs.log = ["The boss stands before you!"];
        return combatState();
    }

    return advanceDungeonFloor();
}

function advanceDungeonFloor() {
    gs.dungeon_floor += 1;
    const floor = gs.dungeon_floor;
    gs.enemy = generateDungeonEnemy(floor, gs.player.level);
    gs.log = ["You descend to Floor " + floor];
    return dungeonFloorState();
}

function afterCombat() {
    if (gs.dungeon_floor > 0) {
        if (gs.dungeon_floor === 10) {
            return respond("dungeon_victory", "DUNGEON CLEARED!",
                "You defeated the boss and conquered the dungeon!",
                ["Return to Village 1"]);
        }
        return dungeonFloorState();
    }
    return respond("town", "Victory!", "What do you want to do?", TOWN_OPTIONS);
}

function dungeonMerchant() {
    gs.shop_name = "Potion Merchant";
    const shop = SHOP_NPCS["Potion Merchant"];
    const available = {};
    Object.keys(shop.items).forEach((n) => {
        if (gs.player.level >= shop.items[n].min_level) available[n] = shop.items[n];
    });
    const items_list = Object.keys(available).map((n) => n + " (" + available[n].price + "g)");
    return respond("shop", "Dungeon Merchant", "", items_list.concat(["(Back)"]), {
        shop_items: Object.keys(available),
        shop_prices: Object.keys(available).map((n) => available[n].price),
        dungeon_shop: true
    });
}

// Public API used by the UI.
const Game = {
    getState: getState,
    createForm: createForm,
    start: startGame,
    action: handleAction,
    save: save,
    forceSave: forceSave,
    loadList: loadList,
    shopBuy: shopBuy,
    mapData: mapData,
    travel: travel
};
