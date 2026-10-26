// shop.py - NPC shop definitions (stock, price and level gate).
//
// The stock, prices and unlock levels are GENERATED into js/game_data.js from
// shop.py by tools/gen_js_data.py - Python derives them once from the
// catalogue (unlock tiers, weapon scores, the 1.0x-3.0x rung spread) and the
// browser reads the result. The old line-for-line JS mirror of that derivation
// is gone: it was ~250 lines that had to agree with Python to the last
// Math.round, and every disagreement was a shop that sold something at a
// different level or price depending on which build you were playing.
//
// Only the hand-written query logic remains below.

// NPCs pay 20% under the cheapest price an item sells for.
const SELL_RATIO = GAME_DATA.sell_ratio;

// The unlock ladder: 1 -> 200, with growing gaps between rungs.
const UNLOCK_TIERS = GAME_DATA.unlock_tiers;

// [NPC name, class, tagline shown as the shop's greeting]
const ARMORY_NPCS = GAME_DATA.armory_npcs;

// Everything the shops stock, in display order:
//   { npc: { class, note, items: { name: { price, min_level } } } }
const SHOP_NPCS = GAME_DATA.shops;

// Which class an NPC caters to, or null when it serves everybody.
const NPC_CLASS = {};
const NPC_NOTE = {};
Object.keys(SHOP_NPCS).forEach((npc) => {
    NPC_CLASS[npc] = SHOP_NPCS[npc].class;
    NPC_NOTE[npc] = SHOP_NPCS[npc].note;
});

// What an NPC pays for one of these, or null if nobody sells it.
function sellPrice(itemName) {
    const item = createItem(itemName);
    if (!item || isMaterial(item)) return null;
    let cheapest = null;
    Object.keys(SHOP_NPCS).forEach((s) => {
        const entry = SHOP_NPCS[s].items[itemName];
        if (entry && (cheapest === null || entry.price < cheapest)) cheapest = entry.price;
    });
    if (cheapest === null) return null;
    return Math.floor(cheapest * SELL_RATIO);
}
