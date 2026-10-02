// world_map.py - Location definitions, coordinates and connection graph.

const LOCATIONS = {
    "town": {
        name: "Town",
        x: 80,
        y: 180,
        type: "town",
        connects_to: ["village1", "village2"],
        // All four armories plus the universal stalls. Every class can walk
        // into every one of them - the class only decides what is greyed out,
        // never whether the door is open. See ARMORY_NPCS in shop.js.
        shops: ["Potion Merchant", "Weaponsmith", "Shadow Fence", "Temple",
                "Wizard", "Armorer", "Shield Smith"]
    },
    "village1": {
        name: "Village 1",
        x: 380,
        y: 310,
        type: "village",
        connects_to: ["town", "dungeon"],
        shops: ["Potion Merchant", "Weaponsmith", "Shadow Fence", "Armorer", "Shield Smith"]
    },
    "village2": {
        name: "Village 2",
        x: 380,
        y: 50,
        type: "village",
        connects_to: ["town"],
        shops: ["Potion Merchant"]
    },
    "dungeon": {
        name: "Dungeon",
        x: 470,
        y: 310,
        type: "dungeon",
        connects_to: ["village1"],
        shops: []
    }
};
