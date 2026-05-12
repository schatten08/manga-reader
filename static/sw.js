const CACHE_NAME = 'manga-app-shell-v1';
const ASSETS = [
    '/',
    '/static/index.html',
    '/static/manifest.json',
    'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.4.120/pdf.worker.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/hammer.js/2.0.8/hammer.min.js'
];

self.addEventListener('install', (event) => {
    console.log('[Service Worker] Установлен, кэшируем системные файлы');
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
    );
});

self.addEventListener('fetch', (event) => {
    // Игнорируем запросы к нашему API, они обрабатываются фронтендом
    if (event.request.url.includes('/api/')) return;
    
    // Для каркаса приложения достаем файлы из кэша (если интернета нет)
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});