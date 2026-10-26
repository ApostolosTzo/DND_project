// tools/shells/pwa_adapter.js - the Backend seam for the static PWA build.
//
// Loads after js/*.js (Game, the live gs state and the catalogue helpers are
// globals) and before tools/shells/shared_page.js. Nothing here renders: it
// hands the shared script states, catalogue entries and sell rows in the one
// shape both builds agree on. Regenerate the shells with:
//   py tools/gen_html_shells.py

/* global Game, gs, getItem, isPotion, healAmount, twoHandedBonus, isTwoHanded,
   elementOf, itemClasses, ALL_CLASSES, sellPrice */

// One catalogue entry in the shared shape. The PWA's Item objects carry
// different field names than the server's ITEM_DETAILS, so everything the
// shared script reads (damage/type/kind/base_ac/...) is normalised here.
function pwaItem(name) {
    const it = getItem(name);
    if (!it) return null;
    const weapon = it.category === "weapon";
    const classes = weapon ? itemClasses(it) : [];
    const bonus = it.stats_bonus || {};
    return {
        category: it.category,
        damage: it.damage_dice,
        type: String(it.damage_type).replace(/_/g, " "),
        two_handed: weapon ? twoHandedBonus(it) : 0,
        is_two_handed: weapon ? isTwoHanded(it) : false,
        element: weapon ? elementOf(it) : null,
        properties: it.properties,
        kind: it.armor_type,
        ac: it.base_ac,
        base_ac: it.base_ac,
        stats_bonus: bonus,
        description: it.description || it.effect,
        heal: healAmount(name),
        usable: isPotion(name),
        bonus: Object.keys(bonus).map((k) => k + " +" + bonus[k]),
        classes: classes,
        any_class: classes.length === ALL_CLASSES.length
    };
}

// Sell-tab rows straight off the live Player. Mirrors the shop logic the PWA
// used to carry inline: equipped gear first (only when the bag holds no copy),
// then the bag grouped by name, with `last` deciding whether the row asks for
// a confirmation before selling the player out of a slot.
function pwaSellRows(s) {
    const p = gs.player;
    if (!p) return [];
    const grouped = {};
    p.inventory.forEach((item) => {
        (grouped[item.name] = grouped[item.name] || []).push(item);
    });
    const kindOf = (it) => it.category === "weapon" ? "weapon"
        : (it.category === "item" ? "item"
            : (it.armor_type === "shield" ? "offhand" : "armor"));
    // How many of this name exist counting the js inventory (which excludes
    // equipped gear) plus the item sitting in `slot`.
    const owned = (name, slot) => p.inventory.filter((i) => i.name === name).length +
        (p[slot] && p[slot].name === name ? 1 : 0);

    const rows = [];
    ["weapon", "armor", "offhand"].forEach((slot) => {
        const it = p[slot];
        if (it && !grouped[it.name]) {
            const kind = kindOf(it);
            rows.push({
                name: it.name, label: it.name, price: sellPrice(it.name),
                kind: kind, equipped: true,
                last: kind !== "item" && owned(it.name, slot) <= 1
            });
        }
    });
    Object.keys(grouped).forEach((name) => {
        const list = grouped[name];
        const it = list[0];
        const kind = kindOf(it);
        const slot = kind === "weapon" ? "weapon" : (kind === "offhand" ? "offhand" : "armor");
        rows.push({
            name: name,
            label: list.length > 1 ? name + " x" + list.length : name,
            price: sellPrice(name),
            kind: kind, equipped: false,
            last: kind !== "item" && owned(name, slot) <= 1
        });
    });
    return rows;
}

const Backend = {
    init() {
        // The PWA is fully local - the only startup work is registering the
        // service worker so the game installs and plays offline.
        if ("serviceWorker" in navigator) {
            window.addEventListener("load", function () {
                navigator.serviceWorker.register("sw.js").catch(function (err) {
                    console.warn("Service worker registration failed:", err);
                });
            });
        }
    },

    // Every mutator is a plain sync call into Game; `await` on a non-promise
    // is a no-op, so the shared script stays build-agnostic.
    getState: () => Game.getState(),
    action: (choice) => Game.action(choice),
    save: (name) => Game.save(name),
    forceSave: () => Game.forceSave(),
    loadList: () => Game.loadList(),
    start: (data) => Game.start(data),
    shopBuy: (item, qty) => Game.shopBuy(item, qty),
    sellItem: (name) => Game.sellItem(name),
    inventoryEquip: (name) => Game.inventoryEquip(name),
    inventoryUse: (name) => Game.inventoryUse(name),
    playerAttack: (offhand) => Game.playerAttack(offhand),
    travel: (id) => Game.travel(id),
    createForm: () => Game.createForm(),
    locations: () => Game.mapData().locations,

    item: pwaItem,
    sellRows: pwaSellRows,
    equipRefusal: (s, name) => Game.equipRefusal(name),

    // Hand the floating number over exactly once per landed hit: the float
    // lives on gs, so nulling it stops any later render of the same state
    // from repeating the damage.
    consumeDamage() {
        const hit = gs.last_damage || null;
        gs.last_damage = null;
        return hit;
    }
};
