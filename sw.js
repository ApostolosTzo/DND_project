/* ============================================================
   Service Worker for D&D Terminal PWA
   Caches the whole (fully client-side) game so it runs offline.
   ============================================================ */

const CACHE_VERSION = "dnd-pwa-v4";
const CACHE_NAME = CACHE_VERSION;

const CORE_ASSETS = [
  "./",
  "./index.html",
  "./manifest.json",
  "./icons/icon-192.png",
  "./icons/icon-512.png",
  "./icons/icon-maskable-512.png",
  "./icons/apple-touch-icon.png",
  "./js/dice.js",
  "./js/items.js",
  "./js/enemy.js",
  "./js/player.js",
  "./js/shop.js",
  "./js/world_map.js",
  "./js/saves.js",
  "./js/game.js"
];

// Install: pre-cache the app shell and all game scripts.
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(CORE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

// Activate: drop caches from older versions.
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(
        keys.filter((k) => k !== CACHE_NAME).map((k) => caches.delete(k))
      ))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const request = event.request;

  // Only handle same-origin GET requests; let everything else pass through.
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // Navigations: network first (so updates arrive), fall back to the
  // cached shell when the device is offline. Some proxies answer with an
  // error page (502/404) instead of failing the request, so treat any
  // non-OK response as "network unavailable" too.
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response && response.ok) {
            const copy = response.clone();
            caches.open(CACHE_NAME).then((cache) => cache.put("./index.html", copy));
            return response;
          }
          return caches.match("./index.html").then((cached) => cached || response);
        })
        .catch(() => caches.match("./index.html"))
    );
    return;
  }

  // Everything else (scripts, icons, manifest): cache first, then network.
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request).then((response) => {
        if (response && response.ok && response.type === "basic") {
          const copy = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(request, copy));
        }
        return response;
      });
    })
  );
});
