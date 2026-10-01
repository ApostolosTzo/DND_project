// save_load.py - Multi-save system, backed by localStorage instead of files.

const SAVES_KEY = "dnd_saves";

function _readAll() {
    try {
        const raw = localStorage.getItem(SAVES_KEY);
        return raw ? JSON.parse(raw) : {};
    } catch (e) {
        return {};
    }
}

function _writeAll(map) {
    try {
        localStorage.setItem(SAVES_KEY, JSON.stringify(map));
    } catch (e) {
        // Storage full or unavailable (e.g. private browsing) - saving silently fails.
    }
}

// Serializes the player to a plain JSON object and stores it under save_name.
function saveGame(player, save_name) {
    if (!save_name) {
        save_name = player.name + "_Lv" + player.level;
    }
    const data = {
        name: player.name,
        race: player.race,
        class_name: player.class_name,
        level: player.level,
        xp: player.xp,
        gold: player.gold,
        stats: Object.assign({}, player.stats),
        hp: player.hp,
        max_hp: player.max_hp,
        weapon: player.weapon ? player.weapon.name : null,
        armor: player.armor ? player.armor.name : null,
        shield: player.shield ? player.shield.name : null,
        inventory: player.inventory.map((item) => item.name),
        skill_points: player.skill_points
    };
    const all = _readAll();
    all[save_name] = data;
    _writeAll(all);
    return save_name;
}

function saveExists(save_name) {
    const all = _readAll();
    return Object.prototype.hasOwnProperty.call(all, save_name);
}

// Rebuilds a Player from a stored save.
function loadGame(save_name) {
    const data = _readAll()[save_name];
    if (!data) return null;

    const player = new Player(data.name, data.race, data.class_name, data.stats);
    player.level = data.level;
    player.xp = data.xp;
    player.gold = data.gold;
    player.hp = data.hp;
    player.max_hp = data.max_hp;
    player.inventory = [];
    if (data.weapon) player.equip_weapon(createItem(data.weapon));
    if (data.armor) player.equip_armor(createItem(data.armor));
    if (data.shield) {
        player.shield = createItem(data.shield);
        player.ac = player.calc_ac();
    }
    (data.inventory || []).forEach((item_name) => player.add_item(createItem(item_name)));
    player.skill_points = data.skill_points || 0;
    return player;
}

// Returns [save_name, character_name, race, class, level] for every save.
function listSaves() {
    const all = _readAll();
    return Object.keys(all).map((name) => {
        const data = all[name];
        if (data && data.name && data.class_name) {
            return [name, data.name, data.race, data.class_name, data.level];
        }
        return [name, name, "?", "?", 0];
    });
}
