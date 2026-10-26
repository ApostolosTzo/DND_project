// world_map.py - Location definitions, coordinates and connection graph.
//
// The map is GENERATED into js/game_data.js from world_map.py by
// tools/gen_js_data.py. Note the shops list per location: every class can
// walk into every one of them - the class only decides what is greyed out,
// never whether the door is open. See ARMORY_NPCS in shop.js.

const LOCATIONS = GAME_DATA.locations;
