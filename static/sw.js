self.addEventListener('install', (event) => {
    console.log('[Service Worker] Установлен');
    // В будущем здесь мы добавим кэширование PDF в IndexedDB
});

self.addEventListener('fetch', (event) => {
    // Пока просто пропускаем запросы насквозь.
    // Приложение уже будет восприниматься как PWA из-за наличия manifest и SW.
    event.respondWith(fetch(event.request));
});