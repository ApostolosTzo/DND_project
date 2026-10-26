// The Player's Codex - shared page script (tools/shells/shared_page.js).
//
// ONE page script drives BOTH builds. Everything build-specific goes through
// the `Backend` seam, implemented by the adapter that loads before this file
// (tools/shells/pwa_adapter.js for the static PWA, flask_adapter.js for the
// Flask build):
//
//   Backend.init()                  start build loads (service worker, catalogue)
//   Backend.getState()/action()/... every mutator -> Promise<state>
//   Backend.createForm()            -> {races, classes}
//   Backend.locations()             -> the world-map locations
//   Backend.item(name)              -> unified catalogue entry (see below)
//   Backend.sellRows(s)             -> the shop Sell tab's rows
//   Backend.equipRefusal(s, name)   -> why Equip is refused, or null
//   Backend.consumeDamage(s)        -> one-shot floating-damage read
//
// The unified catalogue entry flattens Item objects (PWA) and the server's
// ITEM_DETAILS (Flask) into one shape: category, damage, type, two_handed,
// is_two_handed, element, properties, ac, kind, base_ac, description, heal,
// usable, stats_bonus, bonus, classes, any_class.
//
// Both builds render this file; neither shell contains page logic any more.
// Regenerate the shells with: py tools/gen_html_shells.py
let currentState = null;
let raceData = [];
let classData = [];
let mapLocations = null;
const MARK = "\u261E ";   // the manicule - the scribal pointing hand

async function loadMapData() {
    // Local in the PWA, fetched in Flask; both resolve before first paint.
    mapLocations = await Backend.locations();
}

async function travel(id) {
    render(await Backend.travel(id));
}

function roadPath(a, b) {
    const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
    const dx = b.x - a.x, dy = b.y - a.y;
    return "M " + a.x + " " + a.y + " Q " + (mx - dy * 0.16) + " " + (my + dx * 0.16) + " " + b.x + " " + b.y;
}

function tree(x, y, s, op) {
    return '<g opacity="' + op + '">' +
        '<rect x="' + (x - 1.4) + '" y="' + (y - 3) + '" width="2.8" height="7" fill="#6E6248"/>' +
        '<path d="M ' + x + ' ' + (y - 20 * s) + ' L ' + (x + 9 * s) + ' ' + (y - 1) + ' L ' + (x - 9 * s) + ' ' + (y - 1) + ' Z" fill="#2F6B54"/>' +
        '<path d="M ' + x + ' ' + (y - 20 * s) + ' L ' + (x + 9 * s) + ' ' + (y - 1) + ' L ' + x + ' ' + (y - 1) + ' Z" fill="#4A9A7C"/></g>';
}

function mountain(x, y, s, op) {
    return '<g opacity="' + op + '">' +
        '<path d="M ' + (x - 22 * s) + ' ' + y + ' L ' + x + ' ' + (y - 30 * s) + ' L ' + (x + 22 * s) + ' ' + y + ' Z" fill="#5A5240"/>' +
        '<path d="M ' + (x - 7 * s) + ' ' + (y - 16 * s) + ' L ' + x + ' ' + (y - 30 * s) + ' L ' + (x + 7 * s) + ' ' + (y - 16 * s) + ' Z" fill="#F6EFDC" opacity=".8"/></g>';
}

function nodeGlyph(type) {
    if (type === "town") {
        return '<g fill="#211A10">' +
            '<rect x="-8" y="-4" width="5.5" height="10"/>' +
            '<rect x="2.5" y="-4" width="5.5" height="10"/>' +
            '<rect x="-3" y="-1" width="6" height="7"/>' +
            '<rect x="-9.5" y="-7" width="2" height="3"/><rect x="-6.5" y="-7" width="2" height="3"/>' +
            '<rect x="1.5" y="-7" width="2" height="3"/><rect x="4.5" y="-7" width="2" height="3"/></g>';
    }
    if (type === "village") {
        return '<g fill="#211A10">' +
            '<path d="M 0 -8 L 8 0 L -8 0 Z"/>' +
            '<rect x="-5" y="0" width="10" height="6"/>' +
            '<rect x="-1.4" y="2" width="2.8" height="4" fill="#A07A1E"/></g>';
    }
    return '<g><path d="M -7 6 v-7 a7 7 0 0 1 14 0 v7 Z" fill="#211A10"/>' +
        '<circle cx="-2.6" cy="0" r="1.5" fill="#9B2418"/><circle cx="2.6" cy="0" r="1.5" fill="#9B2418"/></g>';
}

function drawMap(currentId) {
    const container = document.getElementById("map-container");
    if (!mapLocations || !currentId || !mapLocations[currentId]) {
        container.innerHTML = "";
        return;
    }
    const locs = mapLocations;
    const current = locs[currentId];
    const FILL = { town: "#A07A1E", village: "#2F6B54", dungeon: "#9B2418" };
    const STROKE = { town: "#7A5A12", village: "#245846", dungeon: "#7A1C13" };
    const reachable = (id) => id === currentId || current.connects_to.indexOf(id) !== -1;

    let svg = '<svg viewBox="0 0 520 360" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="World map">';
    svg += "<style>" +
        ".mn{transition:transform .18s ease;transform-box:fill-box;transform-origin:center}" +
        ".mn:hover{transform:scale(1.18)}" +
        ".mlabel{font-family:Georgia,'Iowan Old Style',serif;font-size:11px;font-weight:600}" +
        "@media (prefers-reduced-motion: reduce){.mn{transition:none}}" +
        "</style>";
    svg += '<defs>' +
        '<linearGradient id="sky" x1="0" y1="0" x2="0.3" y2="1">' +
            '<stop offset="0" stop-color="#F3EBD9"/><stop offset="1" stop-color="#E2D4B2"/></linearGradient>' +
        '<radialGradient id="vig" cx="0.5" cy="0.45" r="0.75">' +
            '<stop offset="0.55" stop-color="#6E6248" stop-opacity="0"/><stop offset="1" stop-color="#6E6248" stop-opacity="0.3"/></radialGradient>' +
        '<filter id="glow" x="-70%" y="-70%" width="240%" height="240%">' +
            '<feGaussianBlur stdDeviation="5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>' +
        "</defs>";

    svg += '<rect width="520" height="360" fill="url(#sky)" rx="4"/>';

    // --- scenery: hills, forest, river, mountains ---
    svg += '<g opacity="0.55">' +
        '<ellipse cx="150" cy="250" rx="130" ry="60" fill="#DCCCA4"/>' +
        '<ellipse cx="400" cy="120" rx="150" ry="70" fill="#DED0AC"/>' +
        '<ellipse cx="470" cy="330" rx="120" ry="50" fill="#D6C6A0"/></g>';

    svg += '<path d="M -12 58 C 70 92, 120 128, 176 196 S 268 292, 352 322 S 470 348, 540 332" ' +
        'stroke="#8FB3AC" stroke-width="15" fill="none" stroke-linecap="round" opacity="0.75"/>' +
        '<path d="M -12 58 C 70 92, 120 128, 176 196 S 268 292, 352 322 S 470 348, 540 332" ' +
        'stroke="#2F6B54" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.55"/>';

    svg += '<g>' +
        tree(300, 300, 0.85, 0.9) + tree(318, 314, 0.7, 0.8) + tree(286, 318, 0.75, 0.8) +
        tree(352, 262, 0.6, 0.7) + tree(268, 268, 0.55, 0.65) +
        tree(402, 92, 0.8, 0.85) + tree(428, 76, 0.65, 0.75) + tree(446, 104, 0.7, 0.8) +
        tree(140, 300, 0.7, 0.7) + tree(120, 258, 0.6, 0.6) +
        "</g>";

    svg += '<g>' +
        mountain(486, 300, 1, 0.95) + mountain(444, 322, 0.75, 0.85) + mountain(516, 286, 0.8, 0.8) +
        mountain(462, 250, 0.55, 0.6) +
        "</g>";

    // --- roads ---
    const drawn = new Set();
    for (const [id, loc] of Object.entries(locs)) {
        for (const target of loc.connects_to) {
            const key = [id, target].sort().join("-");
            if (drawn.has(key)) continue;
            drawn.add(key);
            const t = locs[target];
            if (!t) continue;
            const on = reachable(id) && reachable(target);
            const op = on ? 1 : 0.3;
            svg += '<path d="' + roadPath(loc, t) + '" stroke="#211A10" stroke-width="7" fill="none" opacity="' + (op * 0.55) + '" stroke-linecap="round"/>';
            svg += '<path d="' + roadPath(loc, t) + '" stroke="#A07A1E" stroke-width="2.5" fill="none" opacity="' + op +
                '" stroke-dasharray="2 7" stroke-linecap="round"/>';
        }
    }

    // --- nodes ---
    for (const [id, loc] of Object.entries(locs)) {
        const isCurrent = id === currentId;
        const canReach = reachable(id);
        const op = canReach ? 1 : 0.32;
        const r = isCurrent ? 11 : 9;
        const fill = FILL[loc.type] || "#6E6248";
        const stroke = STROKE[loc.type] || "#211A10";
        const labelY = loc.y < 200 ? loc.y - 20 : loc.y + 26;
        const pillW = loc.name.length * 6.7 + 14;
        const clickable = canReach && !isCurrent;

        // One group per node, and only the group carries the click. Previously
        // the visible circle sat on top of the invisible hit area and swallowed
        // the click, so tapping the middle of a marker did nothing while the ring
        // around it worked.
        const attrs = clickable
            ? ` class="mn" style="cursor:pointer" onclick="travel('${id}')"`
            : ` class="mn"`;

        svg += "<g" + attrs + " opacity=\"" + op + '" title="' + (clickable ? "Travel to " : "") + loc.name + '">';

        if (clickable) {
            // generous invisible hit area, easy to tap on a phone
            svg += '<circle cx="' + loc.x + '" cy="' + loc.y + '" r="' + (r + 13) + '" fill="transparent"/>';
        }
        if (isCurrent) {
            svg += '<circle cx="' + loc.x + '" cy="' + loc.y + '" r="' + (r + 4) + '" fill="' + fill + '" opacity="0.18"/>';
        }
        svg += '<circle cx="' + loc.x + '" cy="' + loc.y + '" r="' + r + '" fill="' + fill + '" stroke="' + stroke +
            '" stroke-width="2"' + (isCurrent ? ' filter="url(#glow)"' : "") + "/>";
        svg += '<g transform="translate(' + loc.x + ',' + (loc.y + 0.5) + ') scale(0.62)">' + nodeGlyph(loc.type) + "</g>";
        svg += '<rect x="' + (loc.x - pillW / 2) + '" y="' + (labelY - 11) + '" width="' + pillW + '" height="16" rx="8" fill="#EFE5CC" stroke="#A07A1E" stroke-width="0.75" opacity="0.95"/>';
        svg += '<text class="mlabel" x="' + loc.x + '" y="' + labelY + '" text-anchor="middle" fill="#211A10">' + loc.name + "</text>";
        svg += "</g>";
    }

    // pulsing ring for the current location, drawn under the labels
    const cur = current;
    svg += '<circle cx="' + cur.x + '" cy="' + cur.y + '" r="18" fill="none" stroke="' + (FILL[cur.type] || "#A07A1E") +
        '" stroke-width="2" opacity="0.45" pointer-events="none">' +
        '<animate attributeName="r" values="12;21;12" dur="2.4s" repeatCount="indefinite"/>' +
        '<animate attributeName="opacity" values="0.45;0.05;0.45" dur="2.4s" repeatCount="indefinite"/></circle>';

    svg += '<rect width="520" height="360" fill="url(#vig)" pointer-events="none" rx="4"/>';

    // --- caption + legend ---
    svg += '<g><rect x="10" y="10" width="190" height="40" rx="3" fill="#E2D4B2" stroke="#A07A1E" stroke-width="0.75" opacity="0.97"/>' +
        '<text x="20" y="27" font-family="Georgia,serif" font-size="12" font-weight="600" fill="#9B2418">You are at: ' + current.name + "</text>" +
        '<text x="20" y="42" font-family="Georgia,serif" font-size="10" fill="#6E6248">Tap a lit marker to travel</text></g>';

    const legend = [["Town", "#A07A1E"], ["Village", "#2F6B54"], ["Dungeon", "#9B2418"]];
    let lg = '<g><rect x="10" y="316" width="180" height="32" rx="3" fill="#E2D4B2" stroke="#A07A1E" stroke-width="0.75" opacity="0.97"/>';
    legend.forEach((l, i) => {
        lg += '<circle cx="' + (26 + i * 58) + '" cy="332" r="5" fill="' + l[1] + '"/>' +
            '<text x="' + (36 + i * 58) + '" y="336" font-family="Georgia,serif" font-size="10" fill="#211A10">' + l[0] + "</text>";
    });
    lg += "</g>";
    svg += lg;

    svg += "</svg>";
    container.innerHTML = svg;
}

async function fetchState() {
    render(await Backend.getState());
}

async function doAction(choice) {
    render(await Backend.action(choice));
}

async function doSave(name) {
    render(await Backend.save(name));
}

async function doForceSave() {
    render(await Backend.forceSave());
}

async function doLoadList() {
    render(await Backend.loadList());
}

async function doStart(data) {
    render(await Backend.start(data));
}

async function doShopBuy(item, qty) {
    render(await Backend.shopBuy(item, qty));
}

async function showCreateForm() {
    const d = await Backend.createForm();
    raceData = d.races;
    classData = d.classes;

    document.getElementById("screen-title").textContent = "CREATE CHARACTER";
    let html = '<div id="create-form">';
    html += '<label>Name</label><input type="text" id="char-name" value="Adventurer">';
    html += '<label>Race</label><select id="char-race" onchange="updateInfoBox()">';
    d.races.forEach(r => html += `<option value="${r[0]}">${r[1]}</option>`);
    html += '</select>';
    html += '<label>Class</label><select id="char-class" onchange="updateInfoBox()">';
    d.classes.forEach(c => html += `<option value="${c[0]}">${c[1]}</option>`);
    html += '</select>';
    html += '<div id="info-box"></div>';
    html += '<button onclick="submitCreate()">Begin Adventure</button>';
    html += '</div>';
    document.getElementById("screen-body").innerHTML = html;
    document.getElementById("options").innerHTML = "";
    document.getElementById("log").innerHTML = "";
    updateInfoBox();
}

function updateInfoBox() {
    const raceSel = document.getElementById("char-race");
    const classSel = document.getElementById("char-class");
    if (!raceSel || !classSel) return;

    const raceIdx = raceSel.selectedIndex;
    const classIdx = classSel.selectedIndex;
    const race = raceData[raceIdx];
    const cls = classData[classIdx];

    let html = '';
    if (race && race[2]) {
        html += `<div><span class="label">Race Bonus:</span> <span class="value">${race[2]}</span></div>`;
    }
    if (cls) {
        html += `<div><span class="label">HP:</span> <span class="value">${cls[2]}</span></div>`;
        html += `<div><span class="label">Primary:</span> <span class="value">${cls[3]}</span></div>`;
    }
    document.getElementById("info-box").innerHTML = html;
}

function submitCreate() {
    const name = document.getElementById("char-name").value || "Adventurer";
    const race = document.getElementById("char-race").value;
    const cls = document.getElementById("char-class").value;
    doStart({name, race, class: cls});
}

// -----------------------------
// Monster portraits
// Each monster gets a hand-drawn SVG. The --dmg custom property (0 = untouched,
// 1 = nearly dead) drives how twisted and washed out the sprite looks.
// -----------------------------

const MONSTER_ART = {
    "Zombie": `<g>
        <ellipse cx="60" cy="110" rx="32" ry="6" fill="#33333a" opacity=".35"/>
        <path d="M42 54 h36 v30 a18 18 0 0 1 -36 0 z" fill="#4a7c3f"/>
        <rect x="44" y="20" width="32" height="36" rx="7" fill="#5b9450"/>
        <circle cx="53" cy="35" r="4" fill="#10200e"/><circle cx="67" cy="35" r="4" fill="#10200e"/>
        <path d="M50 46 h20" stroke="#2b4a24" stroke-width="3" stroke-linecap="round"/>
        <path d="M42 62 L26 76" stroke="#5b9450" stroke-width="9" stroke-linecap="round"/>
        <path d="M78 62 L94 52" stroke="#5b9450" stroke-width="9" stroke-linecap="round"/>
    </g>`,
    "Skeleton": `<g>
        <ellipse cx="60" cy="110" rx="26" ry="5" fill="#33333a" opacity=".35"/>
        <path d="M60 56 v42" stroke="#e8e6d8" stroke-width="5" stroke-linecap="round"/>
        <path d="M46 66 h28 M46 78 h28 M48 90 h24" stroke="#e8e6d8" stroke-width="4" stroke-linecap="round"/>
        <path d="M60 56 L44 72 M60 56 L76 72" stroke="#e8e6d8" stroke-width="4" stroke-linecap="round"/>
        <rect x="44" y="14" width="32" height="36" rx="10" fill="#f2f0e2"/>
        <circle cx="53" cy="30" r="5" fill="#0b0b0c"/><circle cx="67" cy="30" r="5" fill="#0b0b0c"/>
        <path d="M50 42 h20" stroke="#0b0b0c" stroke-width="3"/>
        <path d="M54 42 v5 M60 42 v5 M66 42 v5" stroke="#0b0b0c" stroke-width="2"/>
    </g>`,
    "Spider": `<g>
        <ellipse cx="60" cy="106" rx="34" ry="6" fill="#33333a" opacity=".35"/>
        <path d="M60 74 C34 78 22 62 18 44 M60 74 C86 78 98 62 102 44
                 M60 80 C36 88 26 82 14 70 M60 80 C84 88 94 82 106 70
                 M60 72 C40 66 34 52 34 38 M60 72 C80 66 86 52 86 38"
              stroke="#3d2f52" stroke-width="4" fill="none" stroke-linecap="round"/>
        <ellipse cx="60" cy="80" rx="22" ry="18" fill="#3d2f52"/>
        <circle cx="60" cy="52" r="17" fill="#4e3d68"/>
        <circle cx="53" cy="49" r="4" fill="#c0392b"/><circle cx="67" cy="49" r="4" fill="#c0392b"/>
        <path d="M50 62 L58 66 M70 62 L62 66" stroke="#c0392b" stroke-width="3" stroke-linecap="round"/>
    </g>`,
    "Wolf": `<g>
        <ellipse cx="58" cy="112" rx="42" ry="6" fill="#33333a" opacity=".55"/>
        <path d="M18 60 C10 38 20 22 32 20 L30 40 L40 28 L48 40 L60 22 C74 26 84 42 78 60 Z" fill="#6f7681"/>
        <path d="M18 60 C12 42 20 26 30 22 L26 42 Z" fill="#474c55"/>
        <path d="M78 60 C86 42 78 26 66 22 L70 42 Z" fill="#474c55"/>
        <path d="M60 22 C72 26 80 40 76 56 L68 38 Z" fill="#8d95a2"/>
        <path d="M32 20 L34 36 L41 26 Z" fill="#33373e"/>
        <path d="M48 24 L46 38 L53 30 Z" fill="#33373e"/>
        <path d="M34 56 C42 66 58 68 70 56 C80 62 84 72 78 82 C70 96 42 98 30 84 C22 72 26 62 34 56 Z" fill="#7d8590"/>
        <path d="M38 70 C46 78 66 78 74 70 C70 90 42 92 38 70 Z" fill="#949ca8"/>
        <ellipse cx="56" cy="98" rx="14" ry="11" fill="#2b2f36"/>
        <ellipse cx="56" cy="93" rx="9" ry="6" fill="#17191e"/>
        <path d="M50 106 L56 114 L62 106 Z" fill="#101216"/>
        <path d="M40 58 l14 -5 l-13 10 z M70 58 l-14 -5 l13 10 z" fill="#f1c40f"/>
        <path d="M43 86 L50 86 L48 95 Z M62 86 L69 86 L67 95 Z" fill="#f4f4f0"/>
        <path d="M22 72 L6 80 M80 72 L96 80" stroke="#6f7681" stroke-width="7" stroke-linecap="round" opacity=".5"/>
    </g>`,
    "Goblin": `<g>
        <ellipse cx="60" cy="106" rx="26" ry="5" fill="#33333a" opacity=".35"/>
        <path d="M46 46 L18 26 L40 32 z M74 46 L102 26 L80 32 z" fill="#7cb342"/>
        <ellipse cx="60" cy="56" rx="26" ry="24" fill="#8bc34a"/>
        <circle cx="51" cy="52" r="5" fill="#f5f5f5"/><circle cx="69" cy="52" r="5" fill="#f5f5f5"/>
        <circle cx="51" cy="52" r="2.5" fill="#0b0b0c"/><circle cx="69" cy="52" r="2.5" fill="#0b0b0c"/>
        <path d="M60 60 l-7 8 h14 z" fill="#33691e"/>
        <path d="M48 70 h24" stroke="#33691e" stroke-width="3" stroke-linecap="round"/>
        <path d="M50 82 h20 v18 h-20 z" fill="#7cb342"/>
    </g>`,
    "Slime": `<g>
        <ellipse cx="60" cy="100" rx="38" ry="8" fill="#33333a" opacity=".3"/>
        <path d="M60 22 C86 22 96 62 96 78 C96 94 80 102 60 102 C40 102 24 94 24 78 C24 62 34 22 60 22 z" fill="#1abc9c" opacity=".85"/>
        <ellipse cx="46" cy="52" rx="9" ry="12" fill="#ffffff" opacity=".45"/>
        <circle cx="50" cy="72" r="6" fill="#0b3d34"/><circle cx="70" cy="72" r="6" fill="#0b3d34"/>
        <path d="M50 88 q10 8 20 0" stroke="#0b3d34" stroke-width="3" fill="none" stroke-linecap="round"/>
    </g>`,
    "Ghost": `<g>
        <ellipse cx="60" cy="108" rx="26" ry="5" fill="#33333a" opacity=".25"/>
        <path d="M60 18 C86 18 96 44 96 66 L96 96 L84 88 L72 98 L60 88 L48 98 L36 88 L24 96 L24 66 C24 44 34 18 60 18 z" fill="#dfe9f5" opacity=".92"/>
        <circle cx="50" cy="56" r="6" fill="#1a2a44"/><circle cx="70" cy="56" r="6" fill="#1a2a44"/>
        <ellipse cx="60" cy="76" rx="9" ry="12" fill="#1a2a44" opacity=".7"/>
    </g>`,
    "Demon Lord": `<g>
        <ellipse cx="60" cy="110" rx="40" ry="7" fill="#33333a" opacity=".4"/>
        <path d="M34 40 C20 18 34 8 44 20 L52 34 z M86 40 C100 18 86 8 76 20 L68 34 z" fill="#7b241c"/>
        <path d="M40 66 C40 40 80 40 80 66 C80 86 68 96 60 96 C52 96 40 86 40 66 z" fill="#c0392b"/>
        <path d="M46 60 l10 -4 l-10 8 z M74 60 l-10 -4 l10 8 z" fill="#f1c40f"/>
        <path d="M46 78 q14 8 28 0" stroke="#7b241c" stroke-width="4" fill="none" stroke-linecap="round"/>
        <path d="M40 70 L18 84 M80 70 L102 84" stroke="#c0392b" stroke-width="8" stroke-linecap="round"/>
    </g>`,
    "Elder Dragon": `<g>
        <ellipse cx="58" cy="114" rx="46" ry="7" fill="#33333a" opacity=".6"/>
        <path d="M30 40 C12 22 18 4 34 14 L46 32 Z M88 40 C106 22 100 4 84 14 L72 32 Z" fill="#6b5a08"/>
        <path d="M30 40 C20 26 22 14 32 16 L44 32 Z" fill="#8a7420"/>
        <path d="M30 34 C42 28 54 30 60 38 C68 30 80 30 92 36 L86 52 C74 48 66 48 60 54 C52 48 44 48 34 52 Z" fill="#8a9a3a"/>
        <path d="M28 52 C28 32 92 32 92 52 C92 76 76 92 60 92 C44 92 28 76 28 52 Z" fill="#6f7f24"/>
        <path d="M28 52 C34 40 50 34 60 34 C70 34 86 40 92 52 C84 44 70 40 60 40 C50 40 36 44 28 52 Z" fill="#93a63e"/>
        <path d="M36 56 C36 48 84 48 84 56 C84 74 74 88 60 88 C46 88 36 74 36 56 Z" fill="#7f8f2c"/>
        <path d="M42 62 C46 56 74 56 78 62 C74 70 70 74 60 74 C50 74 46 70 42 62 Z" fill="#5f6c1c"/>
        <path d="M34 68 C36 78 44 86 60 86 C76 86 84 78 86 68 C84 82 74 92 60 92 C46 92 36 82 34 68 Z" fill="#e8e4cf"/>
        <path d="M40 74 l5 11 l4 -10 Z M52 78 l5 12 l4 -12 Z M64 78 l5 12 l4 -12 Z M76 74 l5 11 l4 -10 Z" fill="#fdfdf6"/>
        <path d="M42 58 l13 -5 l-12 11 z M78 58 l-13 -5 l12 11 z" fill="#ffd633"/>
        <path d="M42 58 l13 -5 l-12 11 z M78 58 l-13 -5 l12 11 z" fill="none" stroke="#7a5c00" stroke-width="1.4"/>
        <circle cx="48" cy="56" r="2.2" fill="#3a2c00"/><circle cx="72" cy="56" r="2.2" fill="#3a2c00"/>
        <path d="M50 46 C54 42 66 42 70 46" stroke="#5f6c1c" stroke-width="2" fill="none" stroke-linecap="round"/>
        <circle cx="50" cy="49" r="1.6" fill="#8a9a3a"/><circle cx="70" cy="49" r="1.6" fill="#8a9a3a"/>
        <path d="M52 78 C56 84 64 84 68 78" stroke="#c9c3a4" stroke-width="2" fill="none" stroke-linecap="round"/>
        <path d="M28 62 L8 74 M92 62 L112 74" stroke="#6f7f24" stroke-width="7" stroke-linecap="round"/>
        <path d="M22 66 C14 60 10 66 14 72 M98 66 C106 60 110 66 106 72" stroke="#5f6c1c" stroke-width="4" fill="none" stroke-linecap="round"/>
    </g>`,
    "_default": `<g>
        <ellipse cx="60" cy="106" rx="30" ry="6" fill="#33333a" opacity=".35"/>
        <circle cx="60" cy="60" r="34" fill="#8e44ad"/>
        <circle cx="50" cy="54" r="5" fill="#fff"/><circle cx="70" cy="54" r="5" fill="#fff"/>
    </g>`
};

function monsterSvg(name) {
    const art = MONSTER_ART[name] || MONSTER_ART["_default"];
    return '<svg viewBox="0 0 120 120" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">' + art + "</svg>";
}

// Shows the enemy portrait during combat / on a live dungeon floor.
// The sprite lurches when hit and slowly degrades as its HP drops.
let lastEnemyHp = null;

function renderStage(s) {
    const stage = document.getElementById("combat-stage");
    const enemy = s.enemy;
    const showStage = !!enemy &&
        (s.screen === "combat" || s.screen === "combat_item" || s.screen === "dungeon_floor");

    document.body.classList.toggle("in-combat", !!(showStage || s.in_dungeon));

    if (!showStage) {
        stage.classList.remove("on");
        stage.innerHTML = "";
        lastEnemyHp = null;
        return false;
    }

    const dmg = enemy.max_hp > 0
        ? Math.max(0, Math.min(1, 1 - enemy.hp / enemy.max_hp))
        : 0;
    const hpPct = enemy.max_hp > 0 ? (enemy.hp / enemy.max_hp * 100) : 0;

    stage.classList.add("on");
    stage.innerHTML =
        '<div class="monster" style="--dmg:' + dmg.toFixed(3) + '">' +
            '<div class="monster-art">' + monsterSvg(enemy.name) + "</div>" +
            '<div class="monster-info">' +
                '<div class="monster-name">Lv.' + enemy.level + " " + enemy.name + "</div>" +
                '<div id="ehp-bar"><div id="ehp-fill" style="width:' + hpPct.toFixed(1) + '%"></div></div>' +
                '<div class="monster-hp">HP ' + enemy.hp + "/" + enemy.max_hp + " &nbsp; AC " + enemy.ac + "</div>" +
            "</div>" +
        "</div>" +
        '<div id="dmg-layer"></div>';

    if (lastEnemyHp !== null && enemy.hp < lastEnemyHp) {
        const art = stage.querySelector(".monster-art");
        art.classList.add("hit");
        art.addEventListener("animationend", function () { art.classList.remove("hit"); });
    }
    lastEnemyHp = enemy.hp;

    // A floating number over the health bar, only when the player actually
    // landed a hit. It fades on its own and is gone by the next exchange, so
    // the number on screen always belongs to the roll that just happened.
    // The adapter hands over the float exactly once per landed hit.
    const hit = Backend.consumeDamage(s);
    if (hit && hit.amount > 0) {
        const layer = stage.querySelector("#dmg-layer");
        const float = document.createElement("div");
        float.className = "dmg-float" + (hit.weak ? " weak" : "");
        float.textContent = "-" + hit.amount;
        layer.appendChild(float);
        float.addEventListener("animationend", function () { float.remove(); });
    }
    return true;
}

// -----------------------------
// Rendering
// -----------------------------

let selectedIndex = 0;

function clickOption(index) {
    if (!currentState || !currentState.options) return;
    // Sell-tab rows are drawn from the bag, not the server's options array, so
    // their data-opt indices route straight to the row's own click handler.
    // When no row claims the index, fall through - that index is the Back
    // entry (drawn in the top-left corner, outside #options).
    if (currentState.screen === "shop" && shopMode === "sell") {
        const row = document.querySelector('#options [data-opt="' + index + '"]');
        if (row) {
            row.click();
            return;
        }
    }
    if (!currentState.options[index]) return;
    selectedIndex = index;
    handleClick(currentState.screen, index);
}

function moveSelection(step) {
    // The back button lives outside #options but takes part in keyboard nav.
    const btns = document.querySelectorAll("[data-opt]");
    if (!btns.length) return;
    const list = Array.prototype.slice.call(btns);
    const current = list.findIndex((b) => b.classList.contains("selected"));
    const from = current === -1 ? selectedIndex : current;
    const next = (from + step + list.length) % list.length;
    list.forEach((b, i) => { b.classList.toggle("selected", i === next); });
    selectedIndex = Number(list[next].getAttribute("data-opt"));
    list[next].scrollIntoView({ block: "nearest" });
}

document.addEventListener("keydown", function (ev) {
    const tag = ev.target && ev.target.tagName;
    if (tag === "INPUT" || tag === "SELECT" || tag === "TEXTAREA") return;
    if (ev.key === "ArrowDown" || ev.key === "ArrowUp") {
        moveSelection(ev.key === "ArrowDown" ? 1 : -1);
        ev.preventDefault();
        return;
    }
    if (ev.key === "Enter") {
        clickOption(selectedIndex);
        ev.preventDefault();
        return;
    }
    const n = parseInt(ev.key, 10);
    if (n >= 1 && currentState && currentState.options && n <= currentState.options.length) {
        clickOption(n - 1);
    }
});

// Top-left back button: runs exactly whatever the trailing list entry runs.
document.getElementById("back-btn").addEventListener("click", function () {
    const i = backIndexFor(currentState || { options: [] });
    if (i === -1) return;
    selectedIndex = i;
    openShopItem = null;
    openInvItem = null;
    handleClick(currentState.screen, i);
});

// -----------------------------
// Shop list with inline item details
// Clicking an item expands a panel under it; "Buy" is always exactly one item
// (no quantity prompt) and the purchase is echoed into the chat log.
// -----------------------------

let openShopItem = null;
let shopMode = "buy";          // "buy" | "sell"
let pendingSell = null;        // {item, price, kind} waiting on a confirm

function itemStatRows(name) {
    const it = Backend.item(name);
    if (!it) return [];
    const rows = [];

    if (it.category === "weapon") {
        rows.push(["Damage", it.damage + " " + it.type]);
        if (it.two_handed > 0) rows.push(["Two-handed", "+" + it.two_handed + " damage per hit"]);
        const el = ELEMENT_TEXT[it.element];
        if (el) rows.push(["Element", el]);
        if (it.properties && it.properties.length) {
            rows.push(["Properties", it.properties.join(", ")]);
        }
    } else if (it.category === "armor") {
        const kind = it.kind === "shield" ? "shield" : it.kind + " armour";
        rows.push(["Armour", it.ac + " AC · " + kind]);
    } else {
        rows.push(["Effect", it.description || "—"]);
    }

    const who = classTagText(it);
    if (who) rows.push(["Usable by", who]);
    if (it.bonus && it.bonus.length) {
        rows.push(["Stat bonus", it.bonus.join(", ")]);
    }
    return rows;
}

// Works out the AC the player would have while wearing `item`, using the same
// formula as Player.calc_ac() so the preview can never lie.
//
// The equipped slots arrive in two shapes: the renderer passes playerJson()
// state where weapon/armor/offhand are name strings ("Chainmail"/"None"),
// while the tests pass the live Player whose slots hold item objects. Reading
// .base_ac off a string yields undefined - which used to render as
// "AC 16 -> undefined (NaN)" - so both shapes are resolved through
// Backend.item() first.
function acPreview(player, item) {
    if (!player || !item) return null;
    const slot = (v) => (typeof v === "string"
        ? (v && v !== "None" ? Backend.item(v) : null)
        : (v || null));
    const gear = { weapon: slot(player.weapon), armor: slot(player.armor), offhand: slot(player.offhand) };
    if (item.category === "armor") {
        if (item.kind === "shield") gear.offhand = item;
        else gear.armor = item;
    } else if (item.category === "weapon") {
        gear.weapon = item;
        // A two-handed weapon cannot keep a shield, so the preview drops it -
        // otherwise the panel would promise an illegal combination.
        if (item.is_two_handed) gear.offhand = null;
    }

    const bonus = {};
    ["weapon", "armor", "offhand"].forEach((slotName) => {
        const it = gear[slotName];
        if (it) {
            for (const st in it.stats_bonus) bonus[st] = (bonus[st] || 0) + it.stats_bonus[st];
        }
    });
    const dexMod = Math.floor((player.stats.DEX + (bonus.DEX || 0) - 10) / 2);

    let ac;
    if (gear.armor) {
        ac = gear.armor.base_ac;
        if (gear.armor.kind === "light") ac += dexMod;
        else if (gear.armor.kind === "medium") ac += Math.min(dexMod, 2);
    } else {
        ac = 10 + dexMod;
    }
    if (gear.offhand && gear.offhand.kind === "shield") ac += gear.offhand.base_ac;
    return ac;
}

// Plain-language description of each element rider, and who may wield what.
// Both read the catalogue directly, so they cannot drift from the game.
const ELEMENT_TEXT = {
    fire: "rolls to set the target alight, 2 rounds of 1d4 + INT (INT scales the chance)",
    ice: "rolls to freeze the target solid and steal its turn (INT scales the chance)",
    poison: "rolls to poison, 1 DEX per round until it dies (DEX scales the chance)",
    lightning: "rolls to strike, 2 rounds of 1d8 + WIS (WIS scales the chance)",
    dark: "always drains life, 3 rounds of 1d4 + 1 per 15 STR (no chance roll)"
};

function classTagText(it) {
    if (!it || it.category !== "weapon") return null;
    // any_class comes from the adapter, so this needs no JS catalogue.
    if (it.any_class) return "any class";
    return (it.classes || []).join(" or ");
}

function shopDetailHtml(name, price, player, locked, npcClass) {
    const it = Backend.item(name);
    const rows = itemStatRows(name);
    let extra = "";

    // Another class's weapon: show what it is, but never a price or a Buy
    // button, because the request would be refused anyway.
    if (locked) {
        return '<div class="shop-detail-info">' +
            '<div class="shop-detail-name">' + name + "</div>" +
            "<dl>" + rows.map((r) => "<dt>" + r[0] + "</dt><dd>" + r[1] + "</dd>").join("") + "</dl>" +
            '<p class="flavour locked-flavour">' +
            "Not your class's weapon. This is " + (npcClass || "another") + " stock \u2014 visit the " +
            npcClass + "'s own stall, or buy a different weapon here.</p>" +
            "</div>";
    }

    if (it && player) {
        if (it.category === "armor" || it.category === "weapon") {
            const now = player.ac;
            const then = acPreview(player, it);
            if (then !== null && then !== now) {
                const better = then > now;
                extra += '<p class="flavour">AC ' + now +
                    ' <span class="' + (better ? "good" : "") + '">&rarr; ' + then + "</span>" +
                    (better ? " (+" + (then - now) + ")" : " (" + (then - now) + ")") + "</p>";
            } else {
                extra += '<p class="flavour">AC stays ' + now + "</p>";
            }
        }
    }
    if (it && it.category === "item") {
        extra += '<p class="flavour">Use it from your inventory, or straight from combat.</p>';
    }

    return '<div class="shop-detail-info">' +
        '<div class="shop-detail-name">' + name + " \u2014 " + price + "g</div>" +
        "<dl>" + rows.map((r) => "<dt>" + r[0] + "</dt><dd>" + r[1] + "</dd>").join("") + "</dl>" +
        extra +
        "</div>";
}

function sellWarningText(kind) {
    if (kind === "weapon") {
        return "That is your last weapon - you will have nothing equipped!";
    }
    if (kind === "offhand") {
        return "That is your last shield or spare weapon - your off-hand will be empty!";
    }
    return "That is your last piece of armour - you will have nothing equipped!";
}


function renderShopSell(s, opts) {
    // Rows come from the adapter: the PWA groups its live Player's bag, Flask
    // reads the sell_* arrays show_shop() sent (player_json has no inventory).
    const gold = (s.player && s.player.gold) || 0;
    const rows = Backend.sellRows(s);

    const head = document.createElement("div");
    head.className = "shop-gold";
    head.textContent = "You have " + gold + "g \u2014 NPCs pay 20% under the shop price";
    opts.appendChild(head);

    rows.forEach((r) => {
        const row = document.createElement("div");
        row.className = "shop-row";

        if (r.price === null || r.price === undefined) {
            const b = document.createElement("button");
            b.className = "shop-item";
            b.setAttribute("data-opt", opts.querySelectorAll("[data-opt]").length);
            b.textContent = MARK + r.label + " \u2014 cannot be sold";
            b.disabled = true;
            row.appendChild(b);
            opts.appendChild(row);
            return;
        }

        const btn = document.createElement("button");
        btn.className = "shop-item";
        btn.setAttribute("data-opt", opts.querySelectorAll("[data-opt]").length);
        btn.textContent = MARK + r.label + (r.equipped ? " (equipped)" : "");
        btn.addEventListener("click", () => {
            if (r.last) {
                pendingSell = { item: r.name, price: r.price, kind: r.kind };
                renderOptions(currentState);
            } else {
                pendingSell = null;
                doSell(r.name);
            }
        });
        row.appendChild(btn);

        if (pendingSell && pendingSell.item === r.name) {
            const warn = document.createElement("div");
            warn.className = "shop-detail";
            warn.innerHTML = '<div class="shop-detail-info">' +
                '<div class="shop-detail-name danger">' + sellWarningText(r.kind) + "</div>" +
                '<p class="flavour">Selling it leaves that slot empty.</p></div>';

            const cancel = document.createElement("button");
            cancel.className = "shop-buy ghost";
            cancel.textContent = "Cancel";
            cancel.addEventListener("click", (ev) => {
                ev.stopPropagation();
                pendingSell = null;
                renderOptions(currentState);
            });
            const cont = document.createElement("button");
            cont.className = "shop-buy danger";
            cont.textContent = "Continue";
            cont.addEventListener("click", (ev) => {
                ev.stopPropagation();
                const target = pendingSell;
                pendingSell = null;
                doSell(target.item);
            });
            warn.appendChild(cancel);
            warn.appendChild(cont);
            row.appendChild(warn);
        }

        const sellBtn = document.createElement("button");
        sellBtn.className = "shop-sell";
        sellBtn.textContent = "Sell \u00b7 " + r.price + "g";
        sellBtn.addEventListener("click", (ev) => {
            ev.stopPropagation();
            pendingSell = null;
            doSell(r.name);
        });
        row.appendChild(sellBtn);
        opts.appendChild(row);
    });
}

async function doSell(name) {
    render(await Backend.sellItem(name));
}


// Everything on a screen, including the shop. index.html owns navigation;
function renderOptions(s) {
    const opts = document.getElementById("options");
    opts.innerHTML = "";
    opts.classList.remove("inv");
    opts.classList.toggle("shop", s.screen === "shop");
    if (selectedIndex >= s.options.length) selectedIndex = 0;

    // The shop draws its own rows so a panel can open under an item.
    if (s.screen === "shop" && s.shop_items) {
        const gold = s.player ? s.player.gold : 0;

        const tabs = document.createElement("div");
        tabs.className = "shop-tabs";
        const buyTab = document.createElement("button");
        buyTab.className = "shop-tab" + (shopMode === "buy" ? " active" : "");
        buyTab.textContent = "Buy";
        buyTab.addEventListener("click", () => { shopMode = "buy"; pendingSell = null; renderOptions(currentState); });
        const sellTab = document.createElement("button");
        sellTab.className = "shop-tab" + (shopMode === "sell" ? " active" : "");
        sellTab.textContent = "Sell";
        sellTab.addEventListener("click", () => { shopMode = "sell"; pendingSell = null; renderOptions(currentState); });
        tabs.appendChild(buyTab);
        tabs.appendChild(sellTab);
        opts.appendChild(tabs);

        if (shopMode === "sell") {
            renderShopSell(s, opts);
            renderBackButton(s);
            return;
        }

        // The shop puts the NPC's tagline in `body`; no other shop screen text
        // uses it, so a non-empty body here is always the greeting.
        if (s.body) {
            const note = document.createElement("div");
            note.className = "shop-npc-note";
            note.textContent = s.body;
            opts.appendChild(note);
        }

        const head = document.createElement("div");
        head.className = "shop-gold";
        head.textContent = "You have " + gold + "g — tap an item to see what it gives you";
        opts.appendChild(head);

        const backIndex = backIndexFor(s);
        s.options.forEach((label, i) => {
            // The back entry is drawn in the top-left corner, not down here.
            if (i === backIndex) return;
            const name = s.shop_items[i];
            const price = s.shop_prices[i];
            const isPotionItem = (s.shop_potions || [])[i] === true;
            // Another class's armory. The item is still listed and still opens,
            // so you can compare stats - it just cannot be bought here.
            const locked = (s.shop_usable || [])[i] === false;

            const row = document.createElement("div");
            row.className = "shop-row";

            const btn = document.createElement("button");
            btn.className = "shop-item" + (locked ? " locked" : "");
            btn.setAttribute("data-opt", i);
            btn.textContent = MARK + label;
            if (locked) {
                btn.setAttribute("aria-disabled", "true");
                btn.title = "Not your class's weapon";
            }
            btn.setAttribute("aria-expanded", openShopItem === i ? "true" : "false");
            btn.addEventListener("click", () => {
                selectedIndex = i;
                toggleShopItem(i);
            });
            row.appendChild(btn);

            if (locked) {
                const note = document.createElement("div");
                note.className = "shop-locked-note";
                note.textContent = "Not your class's weapon";
                row.appendChild(note);
            }

            if (openShopItem === i) {
                const panel = document.createElement("div");
                panel.className = "shop-detail";
                panel.innerHTML = shopDetailHtml(name, price, s.player, locked, s.shop_npc_class);

                // Potions stack, so they get a quantity stepper. Everything else
                // is a single tap - you do not buy four longswords at once.
                let qty = 1;
                let stepper = null;
                let buyBtn = null;
                let totalLabel = null;

                const syncBuy = () => {
                    const total = price * qty;
                    buyBtn.textContent = "Buy " + qty + " × · " + total + "g";
                    buyBtn.disabled = gold < total;
                    buyBtn.title = gold < total ? "Not enough gold" : "Buy " + qty + " × " + name;
                    if (totalLabel) {
                        totalLabel.textContent = total + "g total";
                        totalLabel.classList.toggle("short", gold < total);
                    }
                };

                const makeStepper = () => {
                    const box = document.createElement("div");
                    box.className = "shop-qty";
                    const label = document.createElement("span");
                    label.className = "shop-qty-label";
                    label.textContent = "Quantity:";
                    box.appendChild(label);

                    // "Max" is how many the player's gold can cover, capped so the
                    // list stays short on a rich character.
                    const maxAffordable = Math.max(1, Math.min(99, Math.floor(gold / price)));
                    const choices = [1, 5, 10, 20, maxAffordable];
                    const buttons = [];

                    const setQty = (n, btn) => {
                        qty = n;
                        buttons.forEach((b) => b.classList.toggle("active", b === btn));
                        syncBuy();
                    };

                    choices.forEach((n, i) => {
                        const b = document.createElement("button");
                        b.className = "qty-btn";
                        b.textContent = i === choices.length - 1 ? "Max " + n : String(n);
                        b.addEventListener("click", (ev) => { ev.stopPropagation(); setQty(n, b); });
                        box.appendChild(b);
                        buttons.push(b);
                    });
                    setQty(1, buttons[0]);

                    const total = document.createElement("span");
                    total.className = "qty-total";
                    total.textContent = price + "g total";
                    totalLabel = total;
                    box.appendChild(total);
                    return box;
                };

                buyBtn = document.createElement("button");
                buyBtn.className = "shop-buy";
                syncBuy();
                buyBtn.addEventListener("click", (ev) => {
                    ev.stopPropagation();
                    openShopItem = null;
                    doShopBuy(name, qty);
                });

                // A locked item gets its note in shopDetailHtml and no Buy
                // button at all, rather than a button that fails on click.
                if (locked) {
                    // nothing to add
                } else if (isPotionItem) {
                    stepper = makeStepper();
                    panel.appendChild(stepper);
                    panel.appendChild(buyBtn);
                } else {
                    buyBtn.textContent = "Buy · " + price + "g";
                    buyBtn.disabled = gold < price;
                    buyBtn.title = gold < price ? "Not enough gold" : "Buy one " + name;
                    panel.appendChild(buyBtn);
                }
                row.appendChild(panel);
            }
            opts.appendChild(row);
        });
        renderBackButton(s);
        return;
    }

    if (s.screen === "combat_item") {
        renderCombatItems(s, opts);
        renderBackButton(s);
        return;
    }

    if (s.screen === "inventory" && s.inv_items) {
        renderInventoryList(s, opts);
        renderBackButton(s);
        return;
    }

    const backIndex = backIndexFor(s);
    s.options.forEach((opt, i) => {
        if (i === backIndex) return;
        const btn = document.createElement("button");
        btn.setAttribute("data-opt", i);
        btn.textContent = MARK + opt;
        btn.classList.toggle("selected", i === selectedIndex);
        btn.addEventListener("click", () => { selectedIndex = i; handleClick(s.screen, i); });
        opts.appendChild(btn);
    });
    renderBackButton(s);
}

// -----------------------------
// Inventory: tap an item, then Equip or Use it
// -----------------------------
// Mirrors the shop panel exactly - selecting an entry never changes anything by
// itself, it just reveals the buttons.

let openInvItem = null;

function renderInventoryList(s, opts) {
    opts.classList.add("inv");
    const p = s.player;
    if (!p) return;

    const backIndex = backIndexFor(s);
    s.options.forEach((label, i) => {
        if (i === backIndex) return;
        const name = s.inv_items[i];
        const item = Backend.item(name);
        const it = item || {};

        const row = document.createElement("div");
        row.className = "shop-row";

        const btn = document.createElement("button");
        btn.className = "inv-item";
        btn.setAttribute("data-opt", i);
        btn.textContent = MARK + label;
        btn.setAttribute("aria-expanded", openInvItem === i ? "true" : "false");
        btn.addEventListener("click", () => {
            selectedIndex = i;
            openInvItem = (openInvItem === i) ? null : i;
            renderOptions(currentState);
        });
        row.appendChild(btn);

        if (openInvItem === i && item) {
            const panel = document.createElement("div");
            panel.className = "shop-detail";

            let extra = "";
            if (item.category === "weapon" || item.category === "armor") {
                const now = p.ac;
                const then = acPreview(p, item);
                if (then !== null && then !== now) {
                    extra += '<p class="flavour">AC ' + now +
                        ' <span class="' + (then > now ? "good" : "") + '">&rarr; ' + then + "</span></p>";
                }
            }
            const refusal = Backend.equipRefusal(s, name);
            if (refusal) {
                extra += '<p class="inv-blocked">' + refusal + "</p>";
            }
            panel.innerHTML = '<div class="shop-detail-info">' +
                '<div class="shop-detail-name">' + name + "</div>" +
                "<dl>" + itemStatRows(name).map((r) =>
                    "<dt>" + r[0] + "</dt><dd>" + r[1] + "</dd>").join("") + "</dl>" +
                extra + "</div>";

            const actions = document.createElement("div");
            actions.className = "inv-actions";

            if (item.category === "weapon" || item.category === "armor") {
                const eq = document.createElement("button");
                eq.className = "shop-buy";
                eq.textContent = "Equip";
                eq.disabled = !!refusal;
                eq.addEventListener("click", async (ev) => {
                    ev.stopPropagation();
                    openInvItem = null;
                    render(await Backend.inventoryEquip(name));
                });
                actions.appendChild(eq);
            }
            if (it.usable) {
                const use = document.createElement("button");
                use.className = "shop-buy heal";
                use.textContent = "Use (" + (it.heal || 0) + " HP)";
                use.addEventListener("click", async (ev) => {
                    ev.stopPropagation();
                    openInvItem = null;
                    render(await Backend.inventoryUse(name));
                });
                actions.appendChild(use);
            }
            if (!actions.childNodes.length) {
                const none = document.createElement("span");
                none.className = "inv-none";
                none.textContent = "Nothing you can do with this yet.";
                actions.appendChild(none);
            }
            panel.appendChild(actions);
            row.appendChild(panel);
        }
        opts.appendChild(row);
    });
}


// -----------------------------
// Combat: every item is listed, but only potions can be used
// -----------------------------
function renderCombatItems(s, opts) {
    const names = s.combat_items || [];
    const backIndex = backIndexFor(s);

    s.options.forEach((label, i) => {
        if (i === backIndex) return;
        const name = names[i];
        const usable = name ? !!(Backend.item(name) || {}).usable : false;

        const btn = document.createElement("button");
        btn.setAttribute("data-opt", i);
        btn.className = usable ? "" : "combat-item-disabled";
        btn.textContent = MARK + label;
        if (!usable) {
            btn.title = "Cannot be used in combat";
        } else {
            btn.addEventListener("click", () => { selectedIndex = i; doAction(i); });
        }
        opts.appendChild(btn);
    });
}

function toggleShopItem(i) {
    openShopItem = (openShopItem === i) ? null : i;
    renderOptions(currentState);
}

// -----------------------------
// Dice tray
// -----------------------------
// On the player's turn the tray shows the dice for each attack they may make
// and a Roll button. The roll itself is decided by the game, not here: the
// animation is theatre, and the authoritative number appears in the combat log
// a moment later. What the tray guarantees is that you can see *what* is about
// to be rolled before you commit the turn.

// Pips for the damage dice: 1-6 fit a 3x3 grid legibly, which is why a d20
// shows its own number instead.
const PIP_LAYOUT = {
    1: [4],
    2: [0, 8],
    3: [0, 4, 8],
    4: [0, 2, 6, 8],
    5: [0, 2, 4, 6, 8],
    6: [0, 2, 3, 5, 6, 8]
};

function dieEl(sides, value) {
    const el = document.createElement("div");
    el.className = "die";
    const shown = value ? ((value - 1) % sides) + 1 : 1;
    const on = PIP_LAYOUT[shown] || PIP_LAYOUT[1];
    for (let i = 0; i < 9; i++) {
        const pip = document.createElement("span");
        pip.className = "pip" + (on.indexOf(i) === -1 ? " off" : "");
        el.appendChild(pip);
    }
    return el;
}

function d20El(value) {
    const el = document.createElement("div");
    el.className = "die d20";
    el.textContent = value === null || value === undefined ? "?" : String(value);
    return el;
}

// Counts the dice in a "2d6" string so the tray can show the right number.
function diceParts(expr) {
    const m = /^(\d*)d(\d+)$/.exec(String(expr || "").trim());
    if (!m) return { count: 1, sides: 6, valid: false };
    return { count: parseInt(m[1] || "1", 10), sides: parseInt(m[2], 10), valid: true };
}

function signed(n) {
    return (n >= 0 ? "+" : "") + n;
}

let trayBusy = false;

function renderDiceTray(s) {
    const tray = document.getElementById("dice-tray");
    const attacks = s.attacks || [];
    const show = s.screen === "combat" && attacks.length > 0;

    if (!show) {
        tray.classList.remove("on");
        tray.innerHTML = "";
        return;
    }

    tray.classList.add("on");
    tray.innerHTML = "";

    const title = document.createElement("div");
    title.className = "dice-tray-title";
    title.textContent = "Your turn";
    tray.appendChild(title);

    const sub = document.createElement("div");
    sub.className = "dice-tray-sub";
    sub.textContent = s.enemy
        ? "vs " + s.enemy.name + " " + "·" + " AC " + s.enemy.ac + "  —  roll to attack"
        : "roll to attack";
    tray.appendChild(sub);

    attacks.forEach((atk, i) => {
        const hitParts = diceParts(atk.hit_die);
        const dmgParts = diceParts(atk.damage_die);

        const row = document.createElement("div");
        row.className = "dice-row" + (atk.offhand ? " offhand" : "");

        const stage = document.createElement("div");
        stage.className = "dice-stage";
        stage.appendChild(d20El(null));
        const d20 = stage.lastChild;
        for (let k = 0; k < Math.min(dmgParts.count, 3); k++) stage.appendChild(dieEl(dmgParts.sides, 0));
        row.appendChild(stage);

        const total = document.createElement("span");
        total.className = "dmg-total";
        row.appendChild(total);

        const info = document.createElement("div");
        info.className = "dice-info";
        const label = document.createElement("div");
        label.className = "dice-label";
        if (atk.offhand) {
            label.innerHTML = '<span class="off-tag">OFF-HAND</span>' + escapeHtml(atk.weapon);
        } else {
            label.textContent = atk.weapon;
        }
        const formula = document.createElement("div");
        formula.className = "dice-formula";
        formula.textContent = "to hit " + atk.hit_die + " " + signed(atk.hit_bonus) +
            "  ·  " + (atk.offhand ? "half damage " : "damage ") +
            (dmgParts.valid ? dmgParts.count + "d" + dmgParts.sides : "?") +
            " " + signed(atk.damage_bonus);
        info.appendChild(label);
        info.appendChild(formula);
        row.appendChild(info);

        const roll = document.createElement("button");
        roll.className = "roll-btn";
        roll.textContent = "Roll";
        roll.addEventListener("click", () => doRoll(i));
        row.appendChild(roll);

        tray.appendChild(row);
    });
}

function escapeHtml(text) {
    const d = document.createElement("div");
    d.textContent = String(text);
    return d.innerHTML;
}

// Pulls the numbers back out of the log line the attack just produced, so the
// dice can land on what actually happened rather than on a random face.
//   "... for 12 damage! ... (d20 + 2 + 3 = 17 vs AC 8)"
//   "... missed! (d20 + 2 + 3 = 11 vs AC 8)"
function parseAttackResult(lines) {
    for (let i = lines.length - 1; i >= 0 && i >= lines.length - 4; i--) {
        const line = lines[i] || "";
        const atk = /= (\d+) vs AC/.exec(line);
        if (!atk) continue;
        const dmg = /for (\d+) damage/.exec(line);
        return {
            hitTotal: parseInt(atk[1], 10),
            damage: dmg ? parseInt(dmg[1], 10) : null,
            weak: /WEAK to/.test(line)
        };
    }
    return null;
}

// Spins the dice, resolves the real attack, lands the dice on the true numbers,
// then hands over to the normal render. The delay is short enough not to drag
// and long enough that the result is readable before the log updates.
async function doRoll(index) {
    if (trayBusy) return;
    trayBusy = true;

    const tray = document.getElementById("dice-tray");
    const buttons = tray.querySelectorAll(".roll-btn");
    for (let i = 0; i < buttons.length; i++) buttons[i].disabled = true;

    const row = tray.querySelectorAll(".dice-row")[index];
    const d20 = row.querySelector(".die.d20");
    const dice = row.querySelectorAll(".die:not(.d20)");
    const totalEl = row.querySelector(".dmg-total");

    // Wild faces while it spins - these are never shown as a result.
    let ticks = 0;
    const flicker = setInterval(() => {
        ticks++;
        d20.textContent = String(1 + Math.floor(Math.random() * 20));
        dice.forEach((d) => { d.innerHTML = dieEl(6, 1 + Math.floor(Math.random() * 6)).innerHTML; });
        if (ticks >= 6) clearInterval(flicker);
    }, 95);

    const diceEls = [d20].concat(Array.prototype.slice.call(dice));
    diceEls.forEach((d, k) => {
        d.style.animationDelay = (k * 45) + "ms";
        d.classList.add("spinning");
    });

    // Let the tumble read, then ask the build for the real roll: the game
    // (local or server) decides it, this only lands the dice on the answer.
    await new Promise((r) => setTimeout(r, 660));
    clearInterval(flicker);

    const before = (currentState.log || []).length;
    const next = await Backend.playerAttack(index === 1);
    const added = (next.log || []).slice(before);
    const result = parseAttackResult(added);

    diceEls.forEach((d) => {
        d.classList.remove("spinning");
        d.classList.add("landed");
    });

    if (result) {
        d20.textContent = result.damage === null ? "MISS" : String(result.hitTotal);
        if (result.damage === null) {
            d20.classList.add("miss");
        } else {
            d20.classList.remove("miss");
            totalEl.textContent = "-" + result.damage;
            totalEl.classList.add("show");
        }
    }

    await new Promise((r) => setTimeout(r, 620));
    trayBusy = false;
    render(next);
}



function render(s) {
    const prevScreen = currentState ? currentState.screen : null;
    currentState = s;
    if (prevScreen !== s.screen) { selectedIndex = 0; openShopItem = null; openInvItem = null; }
    document.getElementById("screen-title").textContent = s.title || "";

    const body = document.getElementById("screen-body");
    // Don't overwrite the create form unless we're not in character creation
    if (s.screen !== "character_creation") {
        body.textContent = s.body || "";
    }

    const stageShown = renderStage(s);
    // The portrait already shows the monster's name, HP and AC - drop the
    // duplicate first line so the body just shows the hero.
    if (stageShown && body.textContent) {
        body.textContent = body.textContent.replace(/^[^\n]*\n+/, "");
    }

    renderOptions(s);
    renderDiceTray(s);

    // Log - every message in the batch stays, newest at the bottom
    const log = document.getElementById("log");
    log.innerHTML = "";
    (s.log || []).forEach(msg => {
        const p = document.createElement("p");
        const ts = new Date().toTimeString().slice(0, 8);
        p.textContent = `[${ts}] ${msg}`;
        log.appendChild(p);
    });
    log.scrollTop = log.scrollHeight;

    // Player sidebar
    if (s.player) {
        const p = s.player;
        document.getElementById("p-name").textContent = p.name;
        document.getElementById("p-class").textContent = p.race + " " + p.class;
        document.getElementById("p-level").textContent = p.level;
        document.getElementById("p-hp").textContent = p.hp + "/" + p.max_hp;
        document.getElementById("p-ac").textContent = p.ac;
        document.getElementById("p-gold").textContent = p.gold;
        document.getElementById("p-xp").textContent = p.xp + "/" + p.xp_to_next;
        document.getElementById("p-weapon").textContent = p.weapon;
        document.getElementById("p-offhand").textContent = p.offhand || "-";
        document.getElementById("p-armor").textContent = p.armor;

        const hpPct = p.max_hp > 0 ? (p.hp / p.max_hp * 100) : 0;
        document.getElementById("hp-fill").style.width = hpPct + "%";
        const xpPct = p.xp_to_next > 0 ? (p.xp / p.xp_to_next * 100) : 0;
        document.getElementById("xp-fill").style.width = xpPct + "%";
    }
    drawMap(s.current_location);
}

function handleClick(screen, index) {
    if (screen === "main_menu") {
        if (index === 0) showCreateForm();
        else if (index === 1) doLoadList();
    }
    else if (screen === "load_menu") {
        if (index === currentState.options.length - 1) fetchState();
        else doAction(index);
    }
    else if (screen === "town") {
        doAction(index);
    }
    else if (screen === "save_menu") {
        if (index === 0) {
            const name = currentState.options[0].replace("Save as '", "").replace("'", "");
            doSave(name);
        } else {
            doAction(1);
        }
    }
    else if (screen === "confirm_overwrite") {
        if (index === 0) {
            doForceSave();
        } else {
            fetchState();
        }
    }
    else if (screen === "combat" || screen === "combat_item") {
        doAction(index);
    }
    else if (screen === "game_over") {
        fetchState();
    }
    else if (screen === "stat_allocation") {
        doAction(index);
    }
    else if (screen === "shop_select") {
        doAction(index);
    }
    else if (screen === "shop") {
        // Keyboard and mouse now do exactly the same thing: both open the
        // inline panel. Only the trailing back entry runs its action.
        if (index === backIndexFor(currentState)) {
            doAction(index);
        } else {
            showBuy(index);
        }
    }
    else if (screen === "inventory") {
        if (index === backIndexFor(currentState)) {
            doAction(index);
        } else {
            doAction(index);   // opens the detail panel client-side
        }
    }
    else if (screen === "location") {
        doAction(index);
    }
    else if (screen === "dungeon_floor") {
        doAction(index);
    }
    else if (screen === "dungeon_victory") {
        doAction(index);
    }
    else if (screen === "dungeon") {
        doAction(index);
    }
    else if (screen === "quest_hub" || screen === "quest_npc") {
        doAction(index);
    }
}

function showBuy(index) {
    // Kept only so a stale keyboard path cannot 404: buying now happens in the
    // inline panel, exactly as it does with the mouse.
    toggleShopItem(index);
}

// -----------------------------
// Back button
// -----------------------------
// The trailing "(Back)" / "(Close)" entry of every list lives in the top-left
// corner instead of at the bottom. It stays in the options array so the
// keyboard still reaches it, but it is no longer drawn in the list.
function backIndexFor(s) {
    if (!s.options || !s.options.length) return -1;
    const last = s.options[s.options.length - 1];
    return /^\((Back|Close)\)/i.test(String(last).trim()) ? s.options.length - 1 : -1;
}

const backBtn = document.getElementById("back-btn");

function renderBackButton(s) {
    const i = backIndexFor(s);
    if (i === -1) {
        backBtn.style.display = "none";
        backBtn.removeAttribute("data-opt");
        return;
    }
    // An explicit value is required here: the stylesheet defaults the button to
    // display:none, so clearing the inline style would leave it hidden.
    backBtn.style.display = "inline-block";
    backBtn.setAttribute("data-opt", i);
    backBtn.classList.toggle("selected", selectedIndex === i);
    const label = String(s.options[i]).trim();
    backBtn.textContent = label.indexOf("Close") === -1 ? "← Back" : "← Close";
}

// Boot: the adapter starts its own loads, the map resolves, then the first
// state paints. The service worker (PWA) and catalogue (Flask) live in
// Backend.init()/ready(), not here.
Backend.init();
(async function () {
    await loadMapData();
    fetchState();
})();
