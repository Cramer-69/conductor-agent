// Service Worker for PWA shell caching
const CACHE_NAME = 'conductor-v2';
const urlsToCache = [
	'/',
	'/static/app.js',
	'/static/manifest.json'
];

self.addEventListener('install', (event) => {
	event.waitUntil(
		caches.open(CACHE_NAME).then((cache) => cache.addAll(urlsToCache))
	);
	self.skipWaiting();
});

self.addEventListener('activate', (event) => {
	event.waitUntil(
		caches.keys().then((keys) => Promise.all(
			keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
		))
	);
	self.clients.claim();
});

self.addEventListener('fetch', (event) => {
	const requestUrl = new URL(event.request.url);
	if (
		event.request.method !== 'GET'
		|| requestUrl.origin !== self.location.origin
		|| !urlsToCache.includes(requestUrl.pathname)
	) {
		return;
	}

	event.respondWith(
		fetch(event.request)
			.then((response) => {
				if (response.ok) {
					const copy = response.clone();
					caches.open(CACHE_NAME).then((cache) => cache.put(event.request, copy));
				}
				return response;
			})
			.catch(() => caches.match(event.request))
	);
});
