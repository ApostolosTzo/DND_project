// tools/shells/flask_adapter.js - the Backend seam for the Flask build.
//
// Loads before tools/shells/shared_page.js. Every mutator is a POST that
// returns the state JSON the shared script renders; the catalogue and the map
// are fetched once at init. Regenerate the shells with:
//   py tools/gen_html_shells.py

let ITEM_DETAILS = {};
let itemDetailsReady = false;
let mapReady = false;
// Every attack bumps attackSeq so the floating damage number can be told
// apart from a stale hit that is still sitting in the response state.
let attackSeq = 0;
let damageSeen = { seq: -1, key: null };

// The catalogue and the map both load asynchronously after the first paint,
// so every entry point waits for both before it renders - otherwise a panel
// can open against an empty catalogue and draw an item with no stats.
async function backendReady() {
    while (!itemDetailsReady || !mapReady) {
        await new Promise((r) => setTimeout(r, 25));
    }
}

async function get(path) {
    await backendReady();
    const r = await fetch(path);
    return r.json();
}

async function post(path, payload) {
    await backendReady();
    const r = await fetch(path, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload || {})
    });
    return r.json();
}

const Backend = {
    init() {
        fetch("/item_details")
            .then((r) => r.json())
            .then((d) => {
                ITEM_DETAILS = d.items || {};
                itemDetailsReady = true;
            });
    },

    getState: () => get("/state"),
    action: (choice) => post("/action", { choice }),
    save: (name) => post("/save", { name }),
    forceSave: () => post("/force_save", {}),
    loadList: () => get("/load_list"),
    start: (data) => post("/start", data),
    shopBuy: (item, qty) => post("/shop_buy", { item, qty }),
    sellItem: (name) => post("/sell", { item: name }),
    inventoryEquip: (name) => post("/inventory_equip", { item: name }),
    inventoryUse: (name) => post("/inventory_use", { item: name }),
    travel: (id) => post("/travel", { location: id }),
    createForm: () => get("/create_form"),

    async playerAttack(offhand) {
        attackSeq++;   // a fresh attack may float the same number again
        await backendReady();
        const r = await fetch("/attack", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ offhand: !!offhand })
        });
        return r.json();
    },

    // Not gated on backendReady(): the map fetch is what sets mapReady, and
    // shared boot awaits this before the first state paints.
    async locations() {
        const r = await fetch("/map_data");
        const d = await r.json();
        mapReady = true;
        return d.locations;
    },

    item: (name) => (ITEM_DETAILS.hasOwnProperty(name) ? ITEM_DETAILS[name] : null),

    // Sell rows arrive with the shop response as parallel arrays (player_json
    // carries no inventory), laid out by sell_listings() in game_server.py.
    sellRows(s) {
        const items = s.sell_items || [];
        return items.map((name, i) => ({
            name: name,
            label: (s.sell_labels || [])[i],
            price: (s.sell_prices || [])[i],
            kind: (s.sell_kinds || [])[i],
            equipped: !!(s.sell_equipped || [])[i],
            last: !!(s.sell_last || [])[i]
        }));
    },

    // inv_blocked is a name-keyed dict in the inventory response.
    equipRefusal(s, name) {
        const blocked = s.inv_blocked || {};
        return Object.prototype.hasOwnProperty.call(blocked, name) ? blocked[name] : null;
    },

    // The server never clears gs["last_damage"], so re-renders keep echoing
    // the last hit. Hand it over once per attack: same attack + same payload
    // is a re-render (suppressed), a new attack bumps attackSeq (floated).
    consumeDamage(s) {
        const hit = s.last_damage || null;
        if (!hit) return null;
        const key = JSON.stringify(hit);
        if (damageSeen.seq === attackSeq && damageSeen.key === key) return null;
        damageSeen = { seq: attackSeq, key: key };
        return hit;
    }
};
