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
    shop_name: null,
    shop_mode: "buy",
    quest_npcs: [],
    quest_accepted: {},
    quest_done: {},
    quest_npc_index: 0,
    return_to: null
};

const TOWN_OPTIONS = ["Fight", "Visit Shop", "Inventory", "Save Game", "Quests", "Quit"];
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
        offhand: p.offhand ? p.offhand.name : "None",
        hands_full: p.hands_full(),
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

// Clears anything left over from a previous run: a live enemy, a half-finished
// dungeon crawl, a pending overwrite prompt or the last shop. Without this, a
// new game (or a loaded save) started while the previous run was inside the
// dungeon would silently inherit that state - no Flee option, and the world map
// would stay hidden.
function resetRun() {
    gs.enemy = null;
    gs.dungeon_floor = 0;
    gs.pending_save_name = null;
    gs.shop_name = null;
    gs.shop_mode = "buy";
    // Fresh quest givers and a clean quest log for every new run.
    gs.quest_npcs = rollQuestNpcs();
    gs.quest_accepted = {};
    gs.quest_done = {};
    gs.quest_npc_index = 0;
    gs.return_to = null;
}

function startGame(data) {
    const name = (data && data.name) || "Adventurer";
    const race = (data && data.race) || "Human";
    const class_name = (data && data["class"]) || "Fighter";

    resetRun();
    gs.player = makeCharacter(name, race, class_name);
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
        case "quest_hub": return questHubAction(choice);
        case "quest_npc": return questNpcAction(gs.quest_npc_index || 0, choice);
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
    resetRun();
    player.current_save = name;
    gs.player = player;
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

    } else if (choice === 4) { // Quests
        return questHubState();

    } else if (choice === 5) { // Quit
        gs.player = null;
        gs.enemy = null;
        gs.log = [];
        return menuRespond();
    }

    return townRespond(townName(), "What do you want to do?");
}

//=============================
// Quests (Town only)
//=============================
// Three repeatable quest givers live in Town. Accept a job, kill what they
// want, then bring the material back to the same NPC for gold and XP.

function countMaterial(p, material) {
    let n = 0;
    p.inventory.forEach((item) => { if (item.name === material) n++; });
    return n;
}

function takeMaterial(p, material, amount) {
    let taken = 0;
    for (let i = p.inventory.length - 1; i >= 0 && taken < amount; i--) {
        if (p.inventory[i].name === material) {
            p.inventory.splice(i, 1);
            taken++;
        }
    }
    return taken;
}

// Where to go once a level-up is finished. Quests put you back in front of the
// NPC you were talking to instead of dropping you in the middle of Town.
function afterQuestOrCombat() {
    if (gs.return_to === "quest_npc") return questNpcState(gs.quest_npc_index);
    if (gs.return_to === "quest_hub") return questHubState();
    return afterCombat();
}

function questHubState() {
    const p = gs.player;
    if (!p) return getState();
    const options = [];
    const body = [];
    gs.quest_npcs.forEach((npc, i) => {
        let ready = 0;
        questsFor(i).forEach((q) => {
            const key = i + ":" + q.index;
            if (gs.quest_accepted[key] && countMaterial(p, q.material) >= q.amount) ready++;
        });
        options.push(npc.name + (ready ? " — " + ready + " ready to hand in!" : ""));
        body.push(npc.name + ": " + questsFor(i).length + " standing job(s)");
    });
    options.push("(Back)");
    return respond("quest_hub", "Quest Givers", body.join("\n"), options);
}

function questHubAction(choice) {
    if (choice >= gs.quest_npcs.length) {
        gs.return_to = null;   // back to the town menu
        return townRespond(townName(), "What do you want to do?");
    }
    gs.return_to = "quest_npc";
    gs.quest_npc_index = choice;
    return questNpcState(choice);
}

function questNpcState(npcIndex) {
    const p = gs.player;
    if (!p) return getState();
    if (npcIndex >= gs.quest_npcs.length) return questHubState();
    gs.quest_npc_index = npcIndex;
    const quests = questsFor(npcIndex);
    const options = [];
    const body = [];
    quests.forEach((q) => {
        const key = npcIndex + ":" + q.index;
        const have = countMaterial(p, q.material);
        const done = gs.quest_done[key] || 0;
        body.push(q.material + " ×" + q.amount + "  →  " + q.gold + "g, " + q.xp + " XP" +
            (done ? " (handed in " + done + "×)" : ""));
        if (!gs.quest_accepted[key]) {
            options.push("[Accept] " + q.material + " ×" + q.amount);
        } else if (have >= q.amount) {
            options.push("[Turn in] " + q.material + " ×" + q.amount + " (you have " + have + ")");
        } else {
            options.push("[Waiting] " + q.material + " ×" + q.amount + " — you have " + have);
        }
    });
    options.push("(Back)");
    return respond("quest_npc", gs.quest_npcs[npcIndex].name, body.join("\n"), options,
        { quest_npc_index: npcIndex });
}

function questNpcAction(npcIndex, choice) {
    const p = gs.player;
    if (!p) return getState();
    const quests = questsFor(npcIndex);
    if (choice >= quests.length) return questHubState();
    const q = quests[choice];
    const key = npcIndex + ":" + q.index;

    if (!gs.quest_accepted[key]) {
        gs.quest_accepted[key] = true;
        gs.log = ["You accepted: " + q.material + " ×" + q.amount];
        return questNpcState(npcIndex);
    }

    const have = countMaterial(p, q.material);
    if (have < q.amount) {
        gs.log = ["You need " + q.amount + " × " + q.material + " (you have " + have + ")."];
        return questNpcState(npcIndex);
    }

    takeMaterial(p, q.material, q.amount);
    p.add_gold(q.gold);
    gs.quest_done[key] = (gs.quest_done[key] || 0) + 1;
    gs.log = [
        "Quest complete: " + q.material + " ×" + q.amount + "!",
        "Paid " + q.gold + " gold and " + q.xp + " XP."
    ];
    grantXp(p, q.xp);
    if (p.skill_points > 0) return allocationState();
    return questNpcState(npcIndex);
}

// -----------------------------
// Combat
// -----------------------------

function combatState() {
    const e = gs.enemy;
    const p = gs.player;
    const status = e.status_text();
    const body = e.display() + (status ? "\n" + status : "") +
        "\n\n" + p.name + ": HP " + p.hp + "/" + p.max_hp + "  AC " + p.ac;
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

        // Burn and poison bite before the monster gets to swing back.
        enemyStatusTurn(p, e).forEach((line) => gs.log.push(line));
        if (!p.is_alive()) {
            return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"]);
        }
        if (!e.is_alive()) return combatReward("Victory!");

        gs.log.push(webEnemyAttack(p, e));

        if (!p.is_alive()) {
            return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"]);
        }

        return combatState();
    }

    // Use Item
    if (choice === 1) {
        const items = combatItemList(p);
        if (!items.length) {
            gs.log = ["You have nothing to use!"];
            return combatState();
        }
        const options = items.map((item) => combatItemLabel(item)).concat(["(Back)"]);
        return respond("combat_item", "Use Item",
            "Choose an item — strongest healing potion first. Nothing here can be used in combat yet is listed greyed out.",
            options, { combat_items: items.map((i) => i.name) });
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

// Everything the player could reach for mid-fight, best healing potion first.
// Quest materials and other drops used to be hidden here, which made the list
// look empty right after a monster dropped something useful.
function combatItemList(p) {
    const counts = {};
    p.inventory.forEach((item) => {
        if (item === p.weapon || item === p.armor || item === p.offhand) return;
        (counts[item.name] = counts[item.name] || []).push(item);
    });

    const grouped = Object.keys(counts).map((name) => ({
        name: name,
        item: counts[name][0],
        count: counts[name].length,
        heal: isPotion(name) ? healAmount(name) : 0
    }));

    grouped.sort(function (a, b) {
        // Usable healing first, strongest first.
        if (a.heal && b.heal) return b.heal - a.heal;
        if (a.heal) return -1;
        if (b.heal) return 1;
        // Then the rest alphabetically so the list does not jump around.
        return a.name < b.name ? -1 : (a.name > b.name ? 1 : 0);
    });
    return grouped;
}

function combatItemLabel(entry) {
    return entry.count > 1 ? entry.name + " x" + entry.count : entry.name;
}

// Only healing potions work in combat; everything else is shown but refused.
function itemUsableInCombat(name) {
    return isPotion(name);
}

function useItemInCombat(name) {
    const p = gs.player;
    const heal = healAmount(name);
    if (!heal) return { ok: false, message: "Cannot use " + name + " in combat yet." };

    const idx = p.inventory.findIndex((i) => i.name === name);
    if (idx === -1) return { ok: false, message: "You don't have " + name + " any more." };

    const before = p.hp;
    p.hp = Math.min(p.hp + heal, p.max_hp);
    p.inventory.splice(idx, 1);
    return {
        ok: true,
        message: "Drank " + name + "! Restored " + (p.hp - before) + " HP (" +
            heal + " attempted)."
    };
}

function combatItemAction(choice) {
    const p = gs.player;
    const e = gs.enemy;
    const items = combatItemList(p);

    // (Back) is the only thing that leaves this screen - using an item leaves
    // you standing here so the fight does not jump back to the main menu.
    if (choice >= items.length) {
        return combatState();
    }

    const entry = items[choice];
    const result = useItemInCombat(entry.name);

    if (result.ok) {
        gs.log.push(result.message);
        if (!e.is_alive()) return combatReward("Victory!");
        // Stay on the Use Item screen; the player presses Back when ready.
        return combatItemState();
    }

    gs.log.push(result.message);
    gs.log.push(webEnemyAttack(p, e));
    if (!p.is_alive()) {
        return respond("game_over", "GAME OVER", "You have died...", ["Return to Menu"]);
    }
    return combatItemState();
}

// The Use Item screen, rebuilt from scratch after every use.
function combatItemState() {
    const p = gs.player;
    const items = combatItemList(p);
    if (!items.length) {
        gs.log.push("You have nothing left to use.");
        return combatState();
    }
    const options = items.map((item) => combatItemLabel(item)).concat(["(Back)"]);
    return respond("combat_item", "Use Item",
        "Choose an item — strongest healing potion first. Nothing here can be used in combat yet is listed greyed out.",
        options, { combat_items: items.map((i) => i.name) });
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
        let dmg = 0;
        const heavy = twoHandedBonus(p.weapon);
        if (p.weapon) {
            dmg = Math.max(roll(p.weapon.damage_dice) + mod + heavy, 1);
        } else {
            dmg = Math.max(1 + mod, 1);
        }
        // The weapon's damage type decides how hard this lands: skeletons
        // crumble to bludgeoning, slimes shrug off steel.
        const type = p.weapon ? damageType(p.weapon.damage_type) : null;
        const result = e.apply_damage(dmg, type);
        const element = elementOf(p.weapon);
        const effect = e.inflict_element(element, p);

        let line = "You hit the " + e.name + " for " + result.total + " damage!" +
            result.note + " (d20 + " + prof + " + " + mod + " = " + atk + " vs AC " + e.ac + ")";
        if (heavy > 0) line += " +" + heavy + " two-handed";
        if (effect) line += effect;
        return line;
    }
    return "You missed! (d20 + " + prof + " + " + mod + " = " + atk + " vs AC " + e.ac + ")";
}

function webEnemyAttack(p, e) {
    // A frozen monster loses its whole turn.
    if (e.is_frozen()) {
        e.status.freeze_rounds -= 1;
        const left = Math.max(0, e.status.freeze_rounds);
        return e.name + " is frozen solid and cannot attack!" +
            (left ? " (" + left + " round" + (left > 1 ? "s" : "") + " left)" : "");
    }

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

// Burns and poison resolve at the top of the monster's turn, before it acts.
function enemyStatusTurn(p, e) {
    const lines = e.tick_status();
    if (!p.is_alive()) return lines;
    return lines;
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

    // Quest materials from the kill (bosses drop nothing yet).
    const drop = e.roll_drop();
    if (drop) {
        for (let i = 0; i < drop[1]; i++) p.add_item(createItem(drop[0]));
        gs.log.push("Collected " + drop[1] + " × " + drop[0] + "!");
    }

    grantXp(p, xp);

    gs.enemy = null;
    if (p.skill_points > 0) return allocationState();
    return afterCombat();
}

// Add XP and run any level-ups it triggers.
function grantXp(p, xp) {
    p.xp += xp;
    while (p.xp >= p.xp_to_next()) {
        p.xp -= p.xp_to_next();
        handleLevelUp();
    }
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
        return afterQuestOrCombat();
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

    // Guard: a shop can list an item that js/items.js does not define (the two
    // catalogues can drift). Without this, createItem() returns null, null lands
    // in the inventory and the next inventory/shop render throws.
    if (!getItem(item)) {
        gs.log = ["That item is not available."];
        return showShop(gs.shop_name);
    }

    const price = shop.items[item].price;
    const total = price * qty;
    if (p.spend_gold(total)) {
        for (let i = 0; i < qty; i++) p.add_item(createItem(item));
        gs.log = ["Bought " + qty + " × " + item + " for " + total + "g!"];
    } else {
        gs.log = ["Not enough gold! Need " + total + "g, you have " + p.gold + "g."];
    }

    return showShop(gs.shop_name);
}

function sellItem(name) {
    // Sell one item to the NPC you are standing at, at 20% under shop price.
    // Equipped gear can be sold too - the caller warns first when it is the
    // last weapon/armour of its kind, which leaves you with nothing equipped.
    const p = gs.player;
    if (!p) return getState();
    const price = sellPrice(name);
    const back = () => showShop(gs.shop_name || Object.keys(SHOP_NPCS)[0]);

    if (!price) {
        gs.log = ["Nobody wants to buy that."];
        return back();
    }

    const index = p.inventory.findIndex((item) => item.name === name);
    let item;
    if (index !== -1) {
        item = p.inventory.splice(index, 1)[0];
    } else if (p.weapon && p.weapon.name === name) {
        item = p.weapon; p.weapon = null;
    } else if (p.armor && p.armor.name === name) {
        item = p.armor; p.armor = null;
    } else if (p.offhand && p.offhand.name === name) {
        item = p.offhand; p.offhand = null;
    } else {
        gs.log = ["You don't have that any more."];
        return back();
    }

    if (item === p.weapon || item === p.armor || item === p.offhand) {
        p.ac = p.calc_ac();
        p.recalc_hp();
    }

    p.add_gold(price);
    gs.log = ["Sold " + item.name + " for " + price + "g."];
    return back();
}

function showShop(shop_name) {
    const p = gs.player;
    const shop = SHOP_NPCS[shop_name];
    const available = {};
    Object.keys(shop.items).forEach((n) => {
        if (p.level >= shop.items[n].min_level) available[n] = shop.items[n];
    });
    const names = Object.keys(available);
    const items_list = names.map((n) => n + " (" + available[n].price + "g)");
    return respond("shop", shop_name, "", items_list.concat(["(Back)"]), {
        shop_items: names,
        shop_prices: names.map((n) => available[n].price),
        // Only potions get the quantity stepper; everything else is one tap.
        shop_potions: names.map((n) => isPotion(n))
    });
}

// -----------------------------
// Inventory
// -----------------------------

// Storage entries (equipped items excluded), grouped by name, in order.
function groupStorage(p) {
    const grouped = {};
    p.inventory.forEach((item) => {
        if (item !== p.weapon && item !== p.armor && item !== p.offhand) {
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
    if (p.offhand) lines.push("Off-hand: " + p.offhand.name);
    if (p.hands_full()) lines.push("(both hands are full)");

    const grouped = groupStorage(p);
    const storage_lines = Object.keys(grouped).map((name) => {
        const items_list = grouped[name];
        return items_list.length > 1 ? name + " x" + items_list.length : name;
    });

    const body = "Equipped:\n  " + (lines.length ? lines.join("\n  ") : "None") +
        "\n\nStorage:\n  " + (storage_lines.length ? storage_lines.join("\n  ") : "(empty)");

    const options = storage_lines.length ? storage_lines.concat(["(Close)"]) : ["(Close)"];

    return respond("inventory", "INVENTORY", body, options, {
        inv_items: Object.keys(grouped)
    });
}

// Selecting an entry no longer equips or drinks anything on the spot - the UI
// opens a detail panel under it and the player presses Equip or Use there.
function inventoryAction(choice) {
    const p = gs.player;
    const names = Object.keys(groupStorage(p));
    if (!names.length || choice >= names.length) {
        return townRespond(townName(), "What do you want to do?");
    }
    return inventoryState();
}

// Which slot an item would go into when equipped, and whether it is allowed.
//
// Weapons are the interesting case. A two-handed weapon always takes the main
// hand and hands the off-hand back; a one-handed weapon takes the main hand if
// it is free, otherwise the off-hand (that is how you end up dual-wielding),
// and only replaces the main hand once both hands are busy. Keeping the target
// in one place is what makes the "both hands full" check honest instead of
// cosmetic.
function equipTargetFor(p, item) {
    if (item.category === "weapon") {
        if (isTwoHanded(item)) return "weapon";
        if (!p.weapon) return "weapon";
        if (isTwoHanded(p.weapon)) return "weapon";   // main hand owns both
        if (!p.offhand) return "offhand";
        return "weapon";
    }
    if (item.category === "armor") {
        if (item.armor_type === "shield") return "offhand";
        return "armor";
    }
    return null;
}

function equipRefusal(p, item) {
    const slot = equipTargetFor(p, item);
    if (!slot) return null;
    if (slot === "offhand" && !p.can_equip_offhand(item)) {
        return p.offhand_block_reason() || "That cannot go in your off-hand.";
    }
    return null;
}

// Moves one item out of storage and into its slot. Weapons and armour swap
// with whatever was there; a two-handed weapon hands the off-hand back.
function inventoryEquip(name) {
    const p = gs.player;
    const idx = p.inventory.findIndex((i) => i.name === name);
    if (idx === -1) {
        gs.log = ["You don't have " + name + " any more."];
        return inventoryState();
    }
    const item = p.inventory[idx];

    const refusal = equipRefusal(p, item);
    if (refusal) {
        gs.log = [refusal];
        return inventoryState();
    }

    const slot = equipTargetFor(p, item);
    p.inventory.splice(idx, 1);

    if (slot === "weapon") {
        if (p.weapon) p.inventory.push(p.weapon);
        p.weapon = item;
        const stowed = isTwoHanded(item) && p.offhand;
        if (stowed) {
            p.offhand = null;
            p.inventory.push(stowed);
        }
        p.ac = p.calc_ac();
        p.recalc_hp();
        gs.log = ["Equipped " + item.name + "!" +
            (stowed ? " " + stowed.name + " went back to storage." : "")];
    } else if (slot === "armor") {
        if (p.armor) p.inventory.push(p.armor);
        p.armor = item;
        p.ac = p.calc_ac();
        p.recalc_hp();
        gs.log = ["Equipped " + item.name + "!"];
    } else if (slot === "offhand") {
        const old = p.offhand;
        p.offhand = item;
        if (old) p.inventory.push(old);
        p.ac = p.calc_ac();
        p.recalc_hp();
        gs.log = ["Equipped " + item.name + (old ? " in your off-hand." : " in your off-hand!")];
    } else {
        p.inventory.splice(idx, 0, item);
        gs.log = ["You cannot equip " + item.name + "."];
    }

    return inventoryState();
}

// Drinks a potion out of combat. Deliberately separate from the combat path so
// the two never drift on how much a potion is worth.
function inventoryUse(name) {
    const p = gs.player;
    const idx = p.inventory.findIndex((i) => i.name === name);
    if (idx === -1) {
        gs.log = ["You don't have " + name + " any more."];
        return inventoryState();
    }
    if (!isPotion(name)) {
        gs.log = ["Cannot use " + name + " yet."];
        return inventoryState();
    }
    const before = p.hp;
    const heal = healAmount(name);
    p.hp = Math.min(p.hp + heal, p.max_hp);
    p.inventory.splice(idx, 1);
    gs.log = ["Drank " + name + "! Restored " + (p.hp - before) + " HP (" +
        heal + " attempted)."];
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
        shop_potions: Object.keys(available).map((n) => isPotion(n)),
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
    sellItem: sellItem,
    sellPrice: sellPrice,
    mapData: mapData,
    travel: travel,
    // Called from the inventory detail panel, never from the option list.
    inventoryEquip: inventoryEquip,
    inventoryUse: inventoryUse,
    equipRefusal: function (name) {
        const p = gs.player;
        if (!p) return null;
        const item = getItem(name);
        return item ? equipRefusal(p, item) : null;
    }
};
