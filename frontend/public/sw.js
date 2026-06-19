/* NORA service worker — minimal & auth-safe.
 *
 * Aturan keras agar TIDAK ganggu auth httpOnly cookie / data dynamic:
 *  - Hanya tangani GET same-origin. Non-GET (login/logout POST) dilepas ke browser.
 *  - /api/* TIDAK pernah disentuh → cookie + Set-Cookie utuh, jawaban selalu fresh.
 *  - Static immutable (/_next/static, /icons) → cache-first.
 *  - Navigation (HTML) → network-first, fallback /offline. TIDAK di-cache (dynamic + cookie).
 *  - Sisanya: tanpa respondWith → browser jalankan normal (credentials same-origin utuh).
 */
const CACHE = "nora-shell-v1";
const PRECACHE = ["/offline"];

self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((c) => c.addAll(PRECACHE)));
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches
      .keys()
      .then((keys) =>
        Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
      )
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // 1. Hanya GET same-origin. Sisanya lepas (auth POST, request cross-origin).
  if (request.method !== "GET" || url.origin !== self.location.origin) return;

  // 2. JANGAN sentuh API/auth — biar browser handle + cookie utuh.
  if (url.pathname.startsWith("/api/")) return;

  // 3. Static immutable: cache-first.
  if (
    url.pathname.startsWith("/_next/static/") ||
    url.pathname.startsWith("/icons/")
  ) {
    event.respondWith(
      caches.match(request).then(
        (hit) =>
          hit ||
          fetch(request).then((res) => {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(request, copy));
            return res;
          })
      )
    );
    return;
  }

  // 4. Navigation (HTML): network-first, fallback offline. TIDAK di-cache.
  if (request.mode === "navigate") {
    event.respondWith(fetch(request).catch(() => caches.match("/offline")));
    return;
  }

  // 5. Sisanya: tidak respondWith → browser jalankan normal (cookie utuh).
});
